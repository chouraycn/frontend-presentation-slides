#!/usr/bin/env python3
"""
export_video.py — Export HTML Slide Deck to MP4 Video
══════════════════════════════════════════════════════════════════════════════
Records an animated MP4 of each slide by driving a headless browser
(Playwright) and stitching frames with FFmpeg.

Ideal for:
  - Social media (LinkedIn, X, WeChat)
  - Asynchronous review (send a video instead of a file)
  - Conference recordings

Pipeline:
  1. Playwright advances through each slide, waiting for animations
  2. Screenshots each slide (PNG frames)
  3. FFmpeg stitches frames into MP4 with optional crossfade transitions

Usage:
    python3 scripts/export_video.py <input.html> [options]

Examples:
    python3 scripts/export_video.py presentation.html
    python3 scripts/export_video.py deck.html --output reel.mp4
    python3 scripts/export_video.py deck.html --duration 5 --fps 30
    python3 scripts/export_video.py deck.html --transition fade --trans-dur 0.5
    python3 scripts/export_video.py deck.html --size 1080x1920   # Vertical (Stories)
    python3 scripts/export_video.py deck.html --open             # Open video after export
    python3 scripts/export_video.py deck.html --no-transition    # Hard cut between slides
    python3 scripts/export_video.py deck.html --slide-durations "8,4,4,4,6,4,10"  # Per-slide timing

Options:
    --output, -o       Output .mp4 path (default: <input_stem>.mp4)
    --duration, -d     Seconds each slide is shown (default: 4)
    --slide-durations  Per-slide durations as comma-separated values, e.g. "6,4,4,8,4"
                       Overrides --duration for specific slides; uses --duration as fallback
    --fps              Frames per second (default: 30)
    --size             Video dimensions WxH (default: 1920x1080)
    --transition       Transition effect: fade | none (default: fade)
    --trans-dur        Transition duration in seconds (default: 0.4)
    --wait             Extra seconds to wait for JS animations (default: 1.2)
    --quality          FFmpeg CRF value 0–51, lower=better (default: 18)
    --open             Open video after export
    --keep-frames      Keep extracted PNG frames (for debugging)
    --verbose, -v      Print per-slide progress

Requirements:
    pip install playwright
    playwright install chromium
    ffmpeg  (must be in PATH — brew install ffmpeg / apt install ffmpeg)
══════════════════════════════════════════════════════════════════════════════
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


# ── Dependency checks ─────────────────────────────────────────────────────────

def check_deps():
    errors = []
    try:
        import playwright  # noqa: F401
    except ImportError:
        errors.append(("playwright", "pip install playwright && playwright install chromium"))

    if not shutil.which("ffmpeg"):
        errors.append(("ffmpeg", "brew install ffmpeg  (macOS)  OR  apt install ffmpeg  (Linux)"))

    if errors:
        print("❌ Missing dependencies:")
        for dep, install in errors:
            print(f"   {dep}: {install}")
        sys.exit(1)


# ── Browser helpers ───────────────────────────────────────────────────────────

def get_slide_count(page):
    """Ask the page how many slides it has."""
    count = page.evaluate("() => document.querySelectorAll('.slide').length")
    if not count:
        count = page.evaluate("() => document.querySelectorAll('section').length")
    return count or 0


def navigate_to_slide(page, index):
    """Use keyboard or JS to navigate to a specific slide index."""
    # Try JS navigation first (most reliable across templates)
    result = page.evaluate(f"""
    () => {{
        // Try SlidePresentation global
        if (window.presentation && window.presentation.goTo) {{
            window.presentation.goTo({index});
            return true;
        }}
        // Try goToSlide global
        if (typeof goToSlide === 'function') {{
            goToSlide({index});
            return true;
        }}
        // Fallback: scroll-snap — scroll to Nth section
        const slides = document.querySelectorAll('.slide, section');
        if (slides[{index}]) {{
            slides[{index}].scrollIntoView({{behavior: 'instant'}});
            return true;
        }}
        return false;
    }}
    """)
    return result


def screenshot_slide(page, frame_path, width, height):
    """Take a full-page screenshot cropped to slide dimensions."""
    page.screenshot(path=str(frame_path), clip={"x": 0, "y": 0, "width": width, "height": height})


# ── FFmpeg helpers ────────────────────────────────────────────────────────────

def build_ffmpeg_cmd(frames_dir, frame_count, output_path, fps, duration,
                     transition, trans_dur, quality, width, height):
    """
    Build an FFmpeg command to stitch frames into a video.

    Strategy:
      - Each frame is held for `duration` seconds
      - `duration` can be a float (all slides) or a list[float] (per-slide)
      - If transition='fade', use xfade filter between clips
      - Output: H.264 MP4, yuv420p (max compatibility)
    """
    frames = sorted(frames_dir.glob("frame_*.png"))
    n = len(frames)

    # Resolve per-slide durations
    if isinstance(duration, (list, tuple)):
        # Pad or truncate to match actual frame count
        durations = list(duration) + [duration[-1]] * max(0, n - len(duration))
        durations = durations[:n]
    else:
        durations = [float(duration)] * n

    if transition == "none" or n == 1:
        # Simple: concat image clips via concat demuxer
        concat_file = frames_dir / "concat.txt"
        with open(concat_file, "w") as f:
            for frame, dur in zip(frames, durations):
                f.write(f"file '{frame.resolve()}'\n")
                f.write(f"duration {dur}\n")
            # FFmpeg requires last entry to repeat
            if frames:
                f.write(f"file '{frames[-1].resolve()}'\n")

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
                   f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,fps={fps}",
            "-c:v", "libx264", "-crf", str(quality),
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(output_path)
        ]
        return cmd

    # Fade transitions via xfade
    td = float(trans_dur)

    # Inputs: each frame held for its own duration + transition overlap
    inputs = []
    for frame, dur in zip(frames, durations):
        inputs += ["-loop", "1", "-t", str(dur + td), "-i", str(frame.resolve())]

    # Scale filter for each input
    filter_parts = []
    for i in range(n):
        filter_parts.append(
            f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,fps={fps},format=yuv420p[s{i}]"
        )

    # xfade chain — offset accumulates with actual per-slide durations
    prev_label = "s0"
    accumulated = 0.0
    for i in range(1, n):
        accumulated += durations[i - 1] - td * (1 if i > 1 else 0)
        offset = round(accumulated, 3)
        out_label = f"v{i}" if i < n - 1 else "vout"
        filter_parts.append(
            f"[{prev_label}][s{i}]xfade=transition=fade:duration={td}:offset={offset}[{out_label}]"
        )
        prev_label = out_label

    filtergraph = ";".join(filter_parts)

    cmd = (
        ["ffmpeg", "-y"]
        + inputs
        + [
            "-filter_complex", filtergraph,
            "-map", "[vout]",
            "-c:v", "libx264", "-crf", str(quality),
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            str(output_path)
        ]
    )
    return cmd


# ── Main export function ──────────────────────────────────────────────────────

def export_video(input_path, output_path=None, duration=4, slide_durations=None,
                 fps=30, size="1920x1080", transition="fade", trans_dur=0.4,
                 wait=1.2, quality=18, open_after=False,
                 keep_frames=False, verbose=False):
    from playwright.sync_api import sync_playwright

    input_path = Path(input_path).resolve()
    if not input_path.exists():
        print(f"❌ File not found: {input_path}")
        sys.exit(1)

    # Parse dimensions
    try:
        width, height = (int(x) for x in size.lower().split("x"))
    except ValueError:
        print(f"❌ Invalid --size format: '{size}'. Use WxH, e.g. 1920x1080")
        sys.exit(1)

    if output_path is None:
        output_path = input_path.with_suffix(".mp4")
    else:
        output_path = Path(output_path)

    frames_dir = Path(tempfile.mkdtemp(prefix="slide-frames-"))

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            ctx = browser.new_context(
                viewport={"width": width, "height": height},
                device_scale_factor=1,
            )
            page = ctx.new_page()

            if verbose:
                print(f"🌐 Loading: {input_path.name}")

            page.goto(f"file://{input_path}", wait_until="networkidle")
            page.wait_for_timeout(int(wait * 1000))

            slide_count = get_slide_count(page)
            if slide_count == 0:
                print("⚠️  No slides detected. Is this a frontend-slides HTML?")
                sys.exit(1)

            if verbose:
                print(f"   {slide_count} slides found — capturing frames…")

            # Resolve per-slide duration list
            if slide_durations:
                dur_list = slide_durations + [duration] * max(0, slide_count - len(slide_durations))
                dur_list = dur_list[:slide_count]
            else:
                dur_list = [float(duration)] * slide_count

            for i in range(slide_count):
                navigate_to_slide(page, i)
                page.wait_for_timeout(int(wait * 1000))

                frame_path = frames_dir / f"frame_{i:04d}.png"
                screenshot_slide(page, frame_path, width, height)

                if verbose:
                    print(f"   📸 Slide {i+1}/{slide_count} ({dur_list[i]}s) → {frame_path.name}")

            browser.close()

        if verbose:
            print(f"\n🎬 Stitching {slide_count} frames with FFmpeg…")
            if transition != "none":
                print(f"   Transition: {transition}, duration: {trans_dur}s")

        cmd = build_ffmpeg_cmd(
            frames_dir, slide_count, output_path,
            fps, dur_list, transition, trans_dur, quality, width, height
        )

        ffmpeg_verbose = subprocess.DEVNULL if not verbose else None
        result = subprocess.run(cmd, stderr=ffmpeg_verbose)

        if result.returncode != 0:
            print("❌ FFmpeg failed. Run with --verbose to see details.")
            sys.exit(1)

        size_mb = round(output_path.stat().st_size / (1024 * 1024), 1)
        total_secs = sum(dur_list)
        print(f"✅ Video exported → {output_path}")
        print(f"   Duration : {total_secs:.1f}s  |  {slide_count} slides")
        print(f"   Size     : {width}×{height}, {fps}fps, {size_mb} MB")

        if open_after:
            opener = "open" if sys.platform == "darwin" else ("xdg-open" if sys.platform.startswith("linux") else "start")
            subprocess.Popen([opener, str(output_path)])

    finally:
        if not keep_frames:
            shutil.rmtree(frames_dir, ignore_errors=True)
        else:
            print(f"   Frames kept at: {frames_dir}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Export an HTML slide presentation to an MP4 video",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/export_video.py presentation.html
  python3 scripts/export_video.py deck.html --duration 6 --transition fade
  python3 scripts/export_video.py deck.html --size 1080x1920 --output reel.mp4
  python3 scripts/export_video.py deck.html --no-transition --fps 24
  python3 scripts/export_video.py deck.html --open
        """
    )
    parser.add_argument("input", help="Path to the HTML presentation file")
    parser.add_argument("--output", "-o", help="Output .mp4 path (default: <input_stem>.mp4)")
    parser.add_argument("--duration", "-d", type=float, default=4,
                        help="Seconds each slide is shown (default: 4)")
    parser.add_argument("--slide-durations", metavar="S1,S2,...",
                        help="Per-slide durations (comma-separated, e.g. '8,4,4,6'). "
                             "Overrides --duration for specified slides; uses --duration as fallback.")
    parser.add_argument("--fps", type=int, default=30,
                        help="Frames per second (default: 30)")
    parser.add_argument("--size", default="1920x1080",
                        help="Video dimensions WxH (default: 1920x1080)")
    parser.add_argument("--transition", choices=["fade", "none"], default="fade",
                        help="Transition between slides: fade or none")
    parser.add_argument("--no-transition", action="store_const", const="none",
                        dest="transition", help="Hard cut between slides (no transition)")
    parser.add_argument("--trans-dur", type=float, default=0.4,
                        help="Transition duration in seconds (default: 0.4)")
    parser.add_argument("--wait", type=float, default=1.2,
                        help="Seconds to wait per slide for animations (default: 1.2)")
    parser.add_argument("--quality", type=int, default=18,
                        help="FFmpeg CRF quality 0–51 (default: 18, lower=better)")
    parser.add_argument("--open", action="store_true", dest="open_after",
                        help="Open the video after export")
    parser.add_argument("--keep-frames", action="store_true",
                        help="Keep PNG frame files for debugging")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print progress")
    args = parser.parse_args()

    check_deps()

    # Parse per-slide durations if provided
    slide_durations = None
    if args.slide_durations:
        try:
            slide_durations = [float(x.strip()) for x in args.slide_durations.split(",")]
        except ValueError:
            print(f"❌ Invalid --slide-durations format. Use comma-separated numbers, e.g. '6,4,4,8'")
            sys.exit(1)

    export_video(
        args.input,
        output_path=args.output,
        duration=args.duration,
        slide_durations=slide_durations,
        fps=args.fps,
        size=args.size,
        transition=args.transition,
        trans_dur=args.trans_dur,
        wait=args.wait,
        quality=args.quality,
        open_after=args.open_after,
        keep_frames=args.keep_frames,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
