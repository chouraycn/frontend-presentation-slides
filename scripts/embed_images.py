#!/usr/bin/env python3
"""
embed_images.py — Embed local images into a slide HTML as base64 data URIs.
═══════════════════════════════════════════════════════════════════════════════
Scans a presentation HTML file for <img src="..."> tags that reference local
files (not URLs), converts each image to a base64 data URI, and inlines them
directly into the HTML. The result is a fully self-contained file that can be
shared, archived, or opened offline without the original image assets.

Also handles CSS `background-image: url(...)` references in <style> blocks.

Usage:
    python3 scripts/embed_images.py <input.html> [options]

Examples:
    python3 scripts/embed_images.py presentation.html
    python3 scripts/embed_images.py deck.html -o deck-embedded.html
    python3 scripts/embed_images.py deck.html --list            # show images only
    python3 scripts/embed_images.py deck.html --resize 1920     # resize before embedding
    python3 scripts/embed_images.py deck.html --quality 85      # JPEG quality for resized images

Options:
    --output, -o   Output file path (default: <input_stem>-embedded.html)
    --list         List all image references found, don't embed
    --resize W     Resize images wider than W pixels to W (preserves aspect ratio)
                   Requires: pip3 install Pillow
    --quality Q    JPEG/WebP quality 1–95 when --resize is used (default: 88)
    --skip-missing Silently skip images that can't be found (default: warn and skip)
    --verbose, -v  Print each image as it is processed

Requirements:
    pip3 install beautifulsoup4
    # Optional (for --resize):
    pip3 install Pillow

Notes:
    - Only local image paths are embedded (http/https/data: URIs are left as-is)
    - Supported formats: png, jpg/jpeg, gif, webp, svg, ico, bmp, avif
    - Image paths are resolved relative to the HTML file's directory
    - The embedded HTML will be larger than the original (base64 ~33% overhead)
"""

import argparse
import base64
import io
import mimetypes
import re
import sys
from pathlib import Path


# ── MIME type map for common image formats ────────────────────────────────────

MIME_MAP = {
    ".png":  "image/png",
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif":  "image/gif",
    ".webp": "image/webp",
    ".svg":  "image/svg+xml",
    ".ico":  "image/x-icon",
    ".bmp":  "image/bmp",
    ".avif": "image/avif",
}


def get_mime(path):
    ext = Path(path).suffix.lower()
    return MIME_MAP.get(ext) or mimetypes.guess_type(str(path))[0] or "application/octet-stream"


def is_local(src):
    """Return True if src is a local file path (not a URL or data URI)."""
    if not src:
        return False
    src = src.strip()
    return not (src.startswith("http://") or src.startswith("https://")
                or src.startswith("data:") or src.startswith("//"))


def resolve_path(src, base_dir):
    """Resolve an image src relative to the HTML file's directory."""
    src_path = Path(src)
    if src_path.is_absolute():
        return src_path
    return (base_dir / src).resolve()


# ── Image loading (with optional resize) ─────────────────────────────────────

def load_and_encode(img_path, max_width=None, quality=88, verbose=False):
    """
    Load an image file, optionally resize it, and return (mime_type, base64_str).
    Returns (None, None) on error.
    """
    img_path = Path(img_path)
    if not img_path.exists():
        return None, None

    mime = get_mime(img_path)

    # SVG: just read as text and base64-encode directly (no Pillow needed)
    if mime == "image/svg+xml":
        raw = img_path.read_bytes()
        return mime, base64.b64encode(raw).decode("ascii")

    # For resize mode, we need Pillow
    if max_width:
        try:
            from PIL import Image
        except ImportError:
            print("  ⚠️  Pillow not installed — skipping resize for this image")
            print("     Run: pip3 install Pillow")
            max_width = None  # Fall through to plain read

    if max_width:
        try:
            from PIL import Image
            img = Image.open(img_path)
            w, h = img.size
            if w > max_width:
                new_h = int(h * max_width / w)
                img = img.resize((max_width, new_h), Image.LANCZOS)
                if verbose:
                    print(f"     ↩ Resized {w}×{h} → {max_width}×{new_h}")
            buf = io.BytesIO()
            # Save format
            fmt = img.format or "PNG"
            save_kwargs = {}
            if fmt in ("JPEG", "JPG"):
                save_kwargs["quality"] = quality
                save_kwargs["optimize"] = True
            elif fmt == "WEBP":
                save_kwargs["quality"] = quality
            img.save(buf, format=fmt, **save_kwargs)
            raw = buf.getvalue()
        except Exception as e:
            print(f"  ⚠️  Pillow error on {img_path.name}: {e} — using raw file")
            raw = img_path.read_bytes()
    else:
        raw = img_path.read_bytes()

    b64 = base64.b64encode(raw).decode("ascii")
    return mime, b64


# ── HTML patching ─────────────────────────────────────────────────────────────

# Matches: src="path/to/image.ext" or src='...'
IMG_SRC_RE = re.compile(
    r'(<img\b[^>]*?\bsrc=)(["\'])([^"\']+)\2',
    re.IGNORECASE
)

# Matches CSS: url("path") or url('path') or url(path) — local only
CSS_URL_RE = re.compile(
    r'url\((["\']?)([^"\'()]+)\1\)',
    re.IGNORECASE
)

# Matches <source srcset="..."> or srcset="..."
SRCSET_RE = re.compile(
    r'(\bsrcset=)(["\'])([^"\']+)\2',
    re.IGNORECASE
)


def embed_img_tags(html, base_dir, max_width, quality, skip_missing, verbose, stats):
    """Replace <img src="local/path"> with base64 data URIs."""
    def replace_src(match):
        prefix = match.group(1)
        quote = match.group(2)
        src = match.group(3)

        if not is_local(src):
            return match.group(0)  # Keep URLs/data URIs as-is

        img_path = resolve_path(src, base_dir)
        if not img_path.exists():
            if not skip_missing:
                print(f"  ⚠️  Image not found: {src} (resolved: {img_path})")
            stats["missing"] += 1
            return match.group(0)

        mime, b64 = load_and_encode(img_path, max_width, quality, verbose)
        if b64 is None:
            stats["errors"] += 1
            return match.group(0)

        size_kb = len(b64) * 3 / 4 / 1024
        if verbose:
            print(f"  ✓ {src} ({size_kb:.0f} KB embedded)")
        stats["embedded"] += 1
        stats["total_kb"] += size_kb

        data_uri = f"data:{mime};base64,{b64}"
        return f"{prefix}{quote}{data_uri}{quote}"

    return IMG_SRC_RE.sub(replace_src, html)


def embed_css_urls(html, base_dir, max_width, quality, skip_missing, verbose, stats):
    """Replace url(local/path) in inline <style> blocks with base64 data URIs."""
    # Only process inside <style>...</style> to avoid false positives
    def process_style_block(style_match):
        style_content = style_match.group(0)

        def replace_url(m):
            quote = m.group(1)
            src = m.group(2).strip()

            if not is_local(src):
                return m.group(0)

            img_path = resolve_path(src, base_dir)
            if not img_path.exists():
                if not skip_missing:
                    print(f"  ⚠️  CSS image not found: {src}")
                stats["missing"] += 1
                return m.group(0)

            mime, b64 = load_and_encode(img_path, max_width, quality, verbose)
            if b64 is None:
                stats["errors"] += 1
                return m.group(0)

            size_kb = len(b64) * 3 / 4 / 1024
            if verbose:
                print(f"  ✓ CSS url({src}) ({size_kb:.0f} KB embedded)")
            stats["embedded"] += 1
            stats["total_kb"] += size_kb

            data_uri = "data:" + mime + ";base64," + b64
            return "url('" + data_uri + "')"

        return CSS_URL_RE.sub(replace_url, style_content)

    return re.sub(r'<style[^>]*>.*?</style>', process_style_block, html, flags=re.DOTALL | re.IGNORECASE)


def list_images(html, base_dir):
    """Print all local image references found in the HTML."""
    found = []

    for match in IMG_SRC_RE.finditer(html):
        src = match.group(3)
        if is_local(src):
            found.append(("img src", src))

    for match in CSS_URL_RE.finditer(html):
        src = match.group(2).strip()
        if is_local(src):
            found.append(("css url", src))

    print(f"🖼️  Found {len(found)} local image reference(s):")
    for kind, src in found:
        img_path = resolve_path(src, base_dir)
        exists = "✓" if img_path.exists() else "✗ not found"
        size_str = ""
        if img_path.exists():
            size_kb = img_path.stat().st_size / 1024
            size_str = f"  ({size_kb:.0f} KB)"
        print(f"  [{kind:8s}] {src}{size_str}  {exists}")


# ── Main ──────────────────────────────────────────────────────────────────────

def embed_images(
    input_path,
    output_path=None,
    list_only=False,
    max_width=None,
    quality=88,
    skip_missing=False,
    verbose=False,
):
    input_path = Path(input_path)
    if not input_path.exists():
        print(f"❌ File not found: {input_path}")
        sys.exit(1)

    html = input_path.read_text(encoding="utf-8")
    base_dir = input_path.parent

    if list_only:
        list_images(html, base_dir)
        return

    stats = {"embedded": 0, "missing": 0, "errors": 0, "total_kb": 0.0}

    print(f"🖼️  Embedding images in: {input_path.name}")
    if max_width:
        print(f"   Resize max-width: {max_width}px  quality: {quality}")

    html = embed_img_tags(html, base_dir, max_width, quality, skip_missing, verbose, stats)
    html = embed_css_urls(html, base_dir, max_width, quality, skip_missing, verbose, stats)

    # Determine output path
    if output_path is None:
        out_path = input_path.with_stem(input_path.stem + "-embedded")
    else:
        out_path = Path(output_path)

    out_path.write_text(html, encoding="utf-8")

    orig_kb = input_path.stat().st_size / 1024
    out_kb = out_path.stat().st_size / 1024

    print(f"\n✅ Done!")
    print(f"   Input   : {input_path} ({orig_kb:.0f} KB)")
    print(f"   Output  : {out_path} ({out_kb:.0f} KB)")
    print(f"   Embedded: {stats['embedded']} image(s)  (+{stats['total_kb']:.0f} KB of base64)")
    if stats["missing"]:
        print(f"   Missing : {stats['missing']} image(s) skipped (file not found)")
    if stats["errors"]:
        print(f"   Errors  : {stats['errors']} image(s) failed to encode")
    print(f"\n   The output file is fully self-contained — no external image files needed.")


def main():
    parser = argparse.ArgumentParser(
        description="Embed local images into a slide HTML as base64 data URIs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/embed_images.py out.html
  python3 scripts/embed_images.py deck.html -o deck-share.html
  python3 scripts/embed_images.py deck.html --list
  python3 scripts/embed_images.py deck.html --resize 1920 --quality 85
        """
    )
    parser.add_argument("input", help="Path to the HTML presentation file")
    parser.add_argument("--output", "-o", help="Output file path (default: <input_stem>-embedded.html)")
    parser.add_argument("--list", action="store_true", dest="list_only",
                        help="List local image references only, do not embed")
    parser.add_argument("--resize", type=int, metavar="W",
                        help="Max image width in pixels; images wider than this are resized (requires Pillow)")
    parser.add_argument("--quality", type=int, default=88, metavar="Q",
                        help="JPEG/WebP quality 1–95 when resizing (default: 88)")
    parser.add_argument("--skip-missing", action="store_true",
                        help="Silently skip images that cannot be found (default: print warning)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print each image as it is processed")
    args = parser.parse_args()

    embed_images(
        args.input,
        output_path=args.output,
        list_only=args.list_only,
        max_width=args.resize,
        quality=args.quality,
        skip_missing=args.skip_missing,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
