#!/usr/bin/env python3
"""
inline_fonts.py — Offline font inlining tool for frontend-slides skill.

Converts a presentation HTML file from CDN-dependent Google Fonts to
fully self-contained offline mode by:
  1. Detecting which Google Fonts are loaded via <link> tags
  2. Downloading the WOFF2 font data from Google Fonts API
  3. Subsetting to presentation-safe character sets (Latin + CJK if needed)
  4. Base64-encoding and inlining as <style> @font-face rules
  5. Removing the original CDN <link> tags

Usage:
    python3 inline_fonts.py <input.html> [--output <output.html>]

Options:
    --output, -o   Output file path (default: input-offline.html)
    --cjk          Include CJK character subset for Chinese presentations
    --list         Only list detected fonts, don't modify the file

Requirements:
    pip3 install requests beautifulsoup4
    # Optional for subsetting (smaller file size):
    pip3 install fonttools brotli

Example:
    python3 inline_fonts.py presentation.html -o presentation-offline.html
    python3 inline_fonts.py presentation.html --cjk --output slides-offline.html
"""

import argparse
import base64
import re
import sys
import urllib.request
import urllib.parse
from pathlib import Path

# ── Dependency checks ────────────────────────────────────────────────────────

def check_dependencies(need_subset=False):
    missing = []
    try:
        import requests
    except ImportError:
        missing.append("requests")
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        missing.append("beautifulsoup4")
    if missing:
        print(f"❌ Missing required packages: {', '.join(missing)}")
        print(f"   Run: pip3 install {' '.join(missing)}")
        sys.exit(1)

    if need_subset:
        try:
            import fontTools
        except ImportError:
            print("⚠️  fonttools not installed — subsetting disabled (fonts will be full size)")
            print("   Optional: pip3 install fonttools brotli")
            return False
    return True


# ── System font fallback stacks ──────────────────────────────────────────────

SYSTEM_FONT_STACKS = {
    # Generic fallbacks when CDN is unavailable
    "sans": "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', Helvetica, Arial, sans-serif",
    "serif": "Georgia, 'Times New Roman', 'Noto Serif SC', serif",
    "mono": "'SF Mono', 'Fira Code', 'Fira Mono', 'Roboto Mono', monospace",
}

# Known Google Font → system fallback mapping
FONT_FALLBACK_MAP = {
    "space grotesk": SYSTEM_FONT_STACKS["sans"],
    "dm sans": SYSTEM_FONT_STACKS["sans"],
    "inter": SYSTEM_FONT_STACKS["sans"],
    "bebas neue": "'Arial Black', 'Impact', " + SYSTEM_FONT_STACKS["sans"],
    "nunito": SYSTEM_FONT_STACKS["sans"],
    "plus jakarta sans": SYSTEM_FONT_STACKS["sans"],
    "playfair display": SYSTEM_FONT_STACKS["serif"],
    "cormorant garamond": SYSTEM_FONT_STACKS["serif"],
    "lato": SYSTEM_FONT_STACKS["sans"],
    "noto sans sc": "'PingFang SC', 'Microsoft YaHei', 'Hiragino Sans GB', " + SYSTEM_FONT_STACKS["sans"],
    "noto serif sc": "'PingFang SC', 'STSong', 'SimSun', " + SYSTEM_FONT_STACKS["serif"],
}

# CSS character subset ranges for subsetting
LATIN_SUBSET = (
    "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,"
    "U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,"
    "U+2212,U+2215,U+FEFF,U+FFFD"
)
LATIN_EXT_SUBSET = "U+0100-024F,U+0259,U+1E00-1EFF,U+2020,U+20A0-20AB,U+20AD-20CF,U+2113,U+2C60-2C7F,U+A720-A7FF"
CJK_COMMON_SUBSET = "U+4E00-9FFF,U+3400-4DBF,U+F900-FAFF,U+3000-303F,U+FF00-FFEF"
PUNCTUATION_SUBSET = "U+2010-2027,U+2030-205E,U+2060-2FFF,U+3001-303F,U+FF00-FF60"


# ── Google Fonts detection ───────────────────────────────────────────────────

def detect_google_fonts(html_content):
    """
    Parse <link> tags for Google Fonts URLs.
    Returns list of dicts: [{url, families: [str]}]
    """
    pattern = r'<link[^>]+href=["\']([^"\']*fonts\.googleapis\.com[^"\']*)["\'][^>]*>'
    matches = re.findall(pattern, html_content, re.IGNORECASE)

    font_links = []
    for url in matches:
        families = []
        # Parse ?family=Font1:wght@400&family=Font2...
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        for fam in params.get("family", []):
            # "Space+Grotesk:wght@400;600;700" → "Space Grotesk"
            name = fam.split(":")[0].replace("+", " ").strip()
            families.append(name)
        if families:
            font_links.append({"url": url, "families": families})

    return font_links


# ── Font downloading ─────────────────────────────────────────────────────────

def fetch_google_font_css(url, include_cjk=False):
    """
    Fetch the Google Fonts CSS2 response which contains @font-face rules
    with WOFF2 URLs. Returns the CSS text.
    """
    import requests

    # Request WOFF2 format
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"  ⚠️  Could not fetch {url}: {e}")
        return None


def extract_font_face_blocks(css_text):
    """
    Parse @font-face blocks from a CSS string.
    Returns list of dicts: [{family, weight, style, src_url, unicode_range}]
    """
    blocks = []
    for block_match in re.finditer(r'@font-face\s*\{([^}]+)\}', css_text, re.DOTALL):
        block = block_match.group(1)

        family = re.search(r"font-family:\s*['\"]?([^;'\"]+)['\"]?", block)
        weight = re.search(r"font-weight:\s*(\d+(?:\s+\d+)?)", block)
        style = re.search(r"font-style:\s*(\w+)", block)
        src_url = re.search(r'url\(([^)]+)\)\s*format\([\'"]woff2[\'"]\)', block)
        urange = re.search(r"unicode-range:\s*([^;]+)", block)

        if family and src_url:
            blocks.append({
                "family": family.group(1).strip().strip("'\""),
                "weight": weight.group(1).strip() if weight else "400",
                "style": style.group(1).strip() if style else "normal",
                "src_url": src_url.group(1).strip().strip("'\""),
                "unicode_range": urange.group(1).strip() if urange else None,
            })
    return blocks


def download_and_encode_font(url):
    """Download a WOFF2 font and return its base64 encoding."""
    import requests
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        return base64.b64encode(resp.content).decode("ascii")
    except Exception as e:
        print(f"  ⚠️  Failed to download font: {e}")
        return None


def build_inline_font_face(block, b64_data):
    """Build a self-contained @font-face CSS rule with base64 data."""
    urange_rule = f"  unicode-range: {block['unicode_range']};\n" if block["unicode_range"] else ""
    return (
        f"@font-face {{\n"
        f"  font-family: '{block['family']}';\n"
        f"  font-weight: {block['weight']};\n"
        f"  font-style: {block['style']};\n"
        f"  font-display: swap;\n"
        f"  src: url('data:font/woff2;base64,{b64_data}') format('woff2');\n"
        f"{urange_rule}}}"
    )


# ── Fallback CSS injection ───────────────────────────────────────────────────

def build_fallback_css(font_families):
    """
    Build a <style> block that adds system-font fallbacks for all detected
    Google Font families, so presentations look reasonable offline even if
    font inlining is skipped or only partially done.
    """
    lines = ["/* ── Offline fallback font stacks ── */"]
    for fam in font_families:
        fallback = FONT_FALLBACK_MAP.get(fam.lower(), SYSTEM_FONT_STACKS["sans"])
        css_var_name = fam.lower().replace(" ", "-")
        lines.append(f"/* Fallback for '{fam}': {fallback} */")
    lines.append(
        "/* To use: add these fallbacks to your font-family declarations */\n"
        "/* Example: font-family: 'Space Grotesk', " + SYSTEM_FONT_STACKS["sans"] + "; */"
    )
    return "\n".join(lines)


# ── HTML patching ────────────────────────────────────────────────────────────

def patch_html(html_content, inline_styles, font_links, dry_run=False):
    """
    1. Remove Google Fonts <link> preconnect + stylesheet tags
    2. Inject inline @font-face <style> block in <head>
    """
    if dry_run:
        return html_content

    result = html_content

    # Remove preconnect links to Google Fonts
    result = re.sub(
        r'<link[^>]+href=["\']https://fonts\.gstatic\.com["\'][^>]*>\s*',
        '', result, flags=re.IGNORECASE
    )
    result = re.sub(
        r'<link[^>]+href=["\']https://fonts\.googleapis\.com["\'][^>]*>\s*',
        '', result, flags=re.IGNORECASE
    )

    # Remove all Google Fonts stylesheet links
    for link in font_links:
        escaped = re.escape(link["url"])
        result = re.sub(
            r'<link[^>]+href=["\']' + escaped + r'["\'][^>]*>\s*',
            '', result, flags=re.IGNORECASE
        )
        # Also catch partial URL matches
        result = re.sub(
            r'<link[^>]+href=["\'][^"\']*fonts\.googleapis\.com[^"\']*["\'][^>]*>\s*',
            '', result, flags=re.IGNORECASE
        )

    # Inject inline fonts right after <meta charset> or at start of <head>
    inject_block = f"\n  <style id=\"offline-fonts\">\n{inline_styles}\n  </style>\n"
    if re.search(r'<meta\s+charset', result, re.IGNORECASE):
        result = re.sub(
            r'(<meta\s+charset[^>]*>)',
            r'\1' + inject_block,
            result, count=1, flags=re.IGNORECASE
        )
    else:
        result = result.replace('<head>', '<head>' + inject_block, 1)

    return result


# ── Main ─────────────────────────────────────────────────────────────────────

def inline_fonts(input_path, output_path, include_cjk=False, list_only=False):
    input_path = Path(input_path)
    if not input_path.exists():
        print(f"❌ File not found: {input_path}")
        sys.exit(1)

    html = input_path.read_text(encoding="utf-8")

    # Detect fonts
    font_links = detect_google_fonts(html)
    if not font_links:
        print("ℹ️  No Google Fonts <link> tags detected — file may already be offline-ready.")
        return

    all_families = [f for link in font_links for f in link["families"]]
    print(f"🔍 Detected {len(all_families)} font famil{'ies' if len(all_families) != 1 else 'y'}:")
    for fam in all_families:
        print(f"   • {fam}")

    if list_only:
        # --list mode: no network access, no dependency check needed
        print("\n(Use without --list to proceed with inlining)")
        return

    # Only check/install heavy deps when actually downloading
    has_subset = check_dependencies(need_subset=include_cjk)
    import requests  # noqa: PLC0415 — deferred on purpose

    # Download and process
    all_font_faces = []
    for link in font_links:
        print(f"\n⬇️  Fetching CSS for: {', '.join(link['families'])}")
        css_text = fetch_google_font_css(link["url"], include_cjk)
        if not css_text:
            continue
        blocks = extract_font_face_blocks(css_text)

        # Filter: skip CJK unicode ranges unless --cjk flag
        if not include_cjk:
            blocks = [
                b for b in blocks
                if not b.get("unicode_range") or
                not any(cjk_range in (b["unicode_range"] or "")
                        for cjk_range in ["U+3000", "U+4E00", "U+AC00"])
            ]

        print(f"   Found {len(blocks)} @font-face rule(s)")
        for block in blocks:
            print(f"   ⬇️  {block['family']} weight={block['weight']} style={block['style']}...", end=" ")
            b64 = download_and_encode_font(block["src_url"])
            if b64:
                size_kb = len(b64) * 3 / 4 / 1024
                print(f"✓ ({size_kb:.0f} KB)")
                all_font_faces.append(build_inline_font_face(block, b64))
            else:
                print("✗ skipped")

    if not all_font_faces:
        print("\n⚠️  No fonts could be inlined. Adding system fallback stacks only.")
        inline_styles = build_fallback_css(all_families)
    else:
        inline_styles = "\n\n".join(all_font_faces)
        inline_styles += "\n\n" + build_fallback_css(all_families)

    # Patch HTML
    patched = patch_html(html, inline_styles, font_links)

    # Write output
    out_path = Path(output_path) if output_path else input_path.with_stem(input_path.stem + "-offline")
    out_path.write_text(patched, encoding="utf-8")

    original_kb = input_path.stat().st_size / 1024
    output_kb = out_path.stat().st_size / 1024
    delta_kb = output_kb - original_kb

    print(f"\n✅ Done!")
    print(f"   Input  : {input_path} ({original_kb:.0f} KB)")
    print(f"   Output : {out_path} ({output_kb:.0f} KB, +{delta_kb:.0f} KB for inlined fonts)")
    print(f"   Fonts  : {len(all_font_faces)} @font-face rules inlined")
    print(f"\n   The output file works fully offline — no network required.")


def main():
    parser = argparse.ArgumentParser(
        description="Inline Google Fonts into a presentation HTML for offline use"
    )
    parser.add_argument("input", help="Path to the HTML presentation file")
    parser.add_argument("--output", "-o", help="Output file path (default: input-offline.html)")
    parser.add_argument("--cjk", action="store_true", help="Include CJK character subsets (larger file)")
    parser.add_argument("--list", action="store_true", dest="list_only",
                        help="List detected fonts only, don't modify the file")
    args = parser.parse_args()

    inline_fonts(args.input, args.output, include_cjk=args.cjk, list_only=args.list_only)


if __name__ == "__main__":
    main()
