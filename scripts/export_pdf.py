#!/usr/bin/env python3
"""
export_pdf.py — Export HTML Slide Deck to PDF
══════════════════════════════════════════════════════════════════════════════
Converts a single-file HTML presentation into a paginated PDF.
Supports three export backends (auto-selected based on availability):

  1. Playwright (headless Chromium)  — best quality, recommended
  2. Puppeteer via Node.js           — alternative if Playwright unavailable
  3. WeasyPrint                      — CSS-only fallback (no JS execution)

Install requirements:
    # Option A — Playwright (recommended)
    pip install playwright
    playwright install chromium

    # Option B — Puppeteer via npx (Node.js required)
    npx puppeteer  # or: npm install -g puppeteer-cli

    # Option C — WeasyPrint fallback
    pip install weasyprint

Usage:
    python3 scripts/export_pdf.py <input.html> [options]

Examples:
    python3 scripts/export_pdf.py my_deck.html
    python3 scripts/export_pdf.py my_deck.html --output slides.pdf
    python3 scripts/export_pdf.py my_deck.html --backend playwright --wait 2
    python3 scripts/export_pdf.py my_deck.html --page-size A4 --landscape
    python3 scripts/export_pdf.py my_deck.html --open

Options:
    --output, -o     Output PDF path (default: <input_stem>.pdf)
    --backend        Export backend: auto | playwright | puppeteer | weasyprint
    --page-size      Paper size: A4 | Letter | 16x9 (1920x1080) | custom WxH (mm)
                     Default: 16x9  (1920×1080px → 508×285.75mm)
    --landscape      Force landscape orientation (default: on for 16x9)
    --margin         Page margin in mm (default: 0)
    --wait           Extra seconds to wait for JS animations to settle (default: 1.5)
    --scale          Page scale factor for Playwright (default: 1.0)
    --open           Open PDF after export
    --verbose, -v    Print progress

Page size aliases:
    16x9   → 508mm × 285.75mm  (default — matches 1920×1080 aspect)
    4x3    → 254mm × 190.5mm
    A4     → 210mm × 297mm
    Letter → 216mm × 279mm
══════════════════════════════════════════════════════════════════════════════
"""

import argparse
import os
import subprocess
import sys
import tempfile
import json
from pathlib import Path
from textwrap import dedent

# ── Page size presets (mm) ────────────────────────────────────────────────────
PAGE_SIZES = {
    '16x9':   (508.0,   285.75),  # 1920×1080 in mm at 96dpi
    '4x3':    (254.0,   190.5),
    'a4':     (210.0,   297.0),
    'letter': (215.9,   279.4),
    'a3':     (297.0,   420.0),
}

def parse_page_size(value: str) -> tuple[float, float]:
    """Parse page size from alias or 'WxH' string (mm)."""
    low = value.lower()
    if low in PAGE_SIZES:
        return PAGE_SIZES[low]
    if 'x' in low:
        parts = low.split('x')
        return (float(parts[0]), float(parts[1]))
    print(f'  ⚠  Unknown page size "{value}", defaulting to 16x9.')
    return PAGE_SIZES['16x9']

# ── Backend detection ─────────────────────────────────────────────────────────

def detect_backend() -> str:
    """Auto-detect the best available export backend."""
    try:
        import playwright
        return 'playwright'
    except ImportError:
        pass
    result = subprocess.run(['node', '--version'], capture_output=True)
    if result.returncode == 0:
        # Check if puppeteer is available as a Node module
        np = subprocess.run(
            ['node', '-e', "require('puppeteer'); process.exit(0);"],
            capture_output=True, timeout=10
        )
        if np.returncode == 0:
            return 'puppeteer'
        # Check for puppeteer-cli (npm install -g puppeteer-cli)
        np2 = subprocess.run(['puppeteer', '--version'], capture_output=True)
        if np2.returncode == 0:
            return 'puppeteer-cli'
    try:
        import weasyprint
        return 'weasyprint'
    except ImportError:
        pass
    return 'none'

# ── Playwright backend ────────────────────────────────────────────────────────

def export_playwright(html_path: Path, pdf_path: Path, width_mm: float, height_mm: float, margin: float, wait: float, scale: float, verbose: bool):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit('❌  Playwright not installed. Run: pip install playwright && playwright install chromium')

    if verbose:
        print('  ↳ Backend: Playwright (headless Chromium)')

    url = html_path.resolve().as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        if verbose:
            print(f'  ↳ Opening: {url}')
        page.goto(url, wait_until='networkidle')
        page.wait_for_timeout(int(wait * 1000))

        # Inject CSS to ensure all slides are visible for printing
        page.add_style_tag(content="""
            @media print {
                .slides-container {
                    overflow: visible !important;
                    height: auto !important;
                }
                .slide {
                    height: 100vh !important;
                    page-break-after: always !important;
                    scroll-snap-align: none !important;
                    break-after: page !important;
                }
                .progress-bar, .nav-dots, .slide-counter {
                    display: none !important;
                }
                * {
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                }
            }
        """)

        # Also inject print trigger styles directly (not relying on @media print for Playwright)
        page.evaluate("""
            document.querySelectorAll('[data-animate]').forEach(el => {
                el.classList.add('visible');
            });
        """)
        page.wait_for_timeout(500)

        page.pdf(
            path=str(pdf_path),
            width=f'{width_mm}mm',
            height=f'{height_mm}mm',
            print_background=True,
            margin={'top': f'{margin}mm', 'right': f'{margin}mm', 'bottom': f'{margin}mm', 'left': f'{margin}mm'},
            scale=scale,
        )
        browser.close()

# ── Puppeteer (Node.js) backend ───────────────────────────────────────────────

def export_puppeteer(html_path: Path, pdf_path: Path, width_mm: float, height_mm: float, margin: float, wait: float, verbose: bool):
    if verbose:
        print('  ↳ Backend: Puppeteer (Node.js)')

    # Write a temporary puppeteer script
    script = f"""
const puppeteer = require('puppeteer');
(async () => {{
  const browser = await puppeteer.launch({{ headless: 'new', args: ['--no-sandbox'] }});
  const page = await browser.newPage();
  await page.setViewport({{ width: 1920, height: 1080 }});
  await page.goto('file://{html_path.resolve()}', {{ waitUntil: 'networkidle0' }});
  await new Promise(r => setTimeout(r, {int(wait * 1000)}));
  await page.addStyleTag({{ content: `
    @media print {{
      .slides-container {{ overflow: visible !important; height: auto !important; }}
      .slide {{ height: 100vh !important; page-break-after: always !important; break-after: page !important; scroll-snap-align: none !important; }}
      .progress-bar, .nav-dots, .slide-counter {{ display: none !important; }}
      * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
    }}
  ` }});
  await page.evaluate(() => {{
    document.querySelectorAll('[data-animate]').forEach(el => el.classList.add('visible'));
  }});
  await new Promise(r => setTimeout(r, 500));
  await page.pdf({{
    path: '{pdf_path.resolve()}',
    width: '{width_mm}mm',
    height: '{height_mm}mm',
    printBackground: true,
    margin: {{ top: '{margin}mm', right: '{margin}mm', bottom: '{margin}mm', left: '{margin}mm' }}
  }});
  await browser.close();
}})().catch(e => {{ console.error(e); process.exit(1); }});
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(script)
        tmp_js = f.name

    try:
        result = subprocess.run(['node', tmp_js], capture_output=True, text=True)
        if result.returncode != 0:
            print(f'  ❌ Puppeteer error:\n{result.stderr}')
            sys.exit(1)
    finally:
        os.unlink(tmp_js)

# ── WeasyPrint backend ────────────────────────────────────────────────────────

def export_weasyprint(html_path: Path, pdf_path: Path, width_mm: float, height_mm: float, margin: float, verbose: bool):
    try:
        import weasyprint
    except ImportError:
        sys.exit('❌  WeasyPrint not installed. Run: pip install weasyprint')

    if verbose:
        print('  ↳ Backend: WeasyPrint (CSS-only, no JS)')
        print('  ⚠  Note: WeasyPrint does not execute JavaScript. Animations and dynamic content will not render.')

    css_override = weasyprint.CSS(string=f"""
        @page {{
            size: {width_mm}mm {height_mm}mm;
            margin: {margin}mm;
        }}
        .slides-container {{ overflow: visible !important; height: auto !important; }}
        .slide {{
            height: {height_mm}mm !important;
            page-break-after: always !important;
            break-after: page !important;
            scroll-snap-align: none !important;
        }}
        .progress-bar, .nav-dots, .slide-counter {{ display: none !important; }}
        [data-animate] {{ opacity: 1 !important; transform: none !important; }}
        * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
    """)

    doc = weasyprint.HTML(filename=str(html_path))
    doc.write_pdf(str(pdf_path), stylesheets=[css_override])

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Export HTML slide deck to PDF.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('input', help='Path to HTML slide deck')
    parser.add_argument('--output', '-o', default=None, help='Output PDF path')
    parser.add_argument('--backend', choices=['auto', 'playwright', 'puppeteer', 'weasyprint'], default='auto')
    parser.add_argument('--page-size', default='16x9', help='Page size: 16x9 | A4 | Letter | WxH (mm)')
    parser.add_argument('--landscape', action='store_true', help='Force landscape orientation')
    parser.add_argument('--margin', type=float, default=0.0, help='Page margin in mm')
    parser.add_argument('--wait', type=float, default=1.5, help='Seconds to wait after page load')
    parser.add_argument('--scale', type=float, default=1.0, help='Page scale factor (Playwright only)')
    parser.add_argument('--open', action='store_true', help='Open PDF after export')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    html_path = Path(args.input)
    if not html_path.exists():
        sys.exit(f'❌  File not found: {html_path}')

    pdf_path = Path(args.output) if args.output else html_path.with_suffix('.pdf')
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    # Page size
    w, h = parse_page_size(args.page_size)
    # For 16x9 and 4x3, landscape is default; for A4/Letter portrait is default
    is_wide = w > h
    if args.landscape and not is_wide:
        w, h = h, w
    elif not args.landscape and not is_wide and args.page_size.lower() in ('16x9', '4x3'):
        pass  # already landscape

    if args.verbose:
        print(f'📄  Exporting: {html_path}')
        print(f'  ↳ Output:    {pdf_path}')
        print(f'  ↳ Page size: {w:.1f}mm × {h:.1f}mm')
        print(f'  ↳ Margin:    {args.margin}mm')

    # Backend selection
    backend = args.backend
    if backend == 'auto':
        backend = detect_backend()
        if args.verbose:
            print(f'  ↳ Auto-detected backend: {backend}')

    if backend == 'none':
        print(dedent("""
            ❌  No export backend found. Install one of:

            Option A (recommended): Playwright
              pip install playwright
              playwright install chromium

            Option B: Puppeteer (requires Node.js)
              npm install -g puppeteer-cli  or  npx puppeteer

            Option C: WeasyPrint (CSS-only, no JS)
              pip install weasyprint
        """))
        sys.exit(1)

    if backend == 'playwright':
        export_playwright(html_path, pdf_path, w, h, args.margin, args.wait, args.scale, args.verbose)
    elif backend in ('puppeteer', 'puppeteer-cli'):
        export_puppeteer(html_path, pdf_path, w, h, args.margin, args.wait, args.verbose)
    elif backend == 'weasyprint':
        export_weasyprint(html_path, pdf_path, w, h, args.margin, args.verbose)
    else:
        sys.exit(f'❌  Unknown backend: {backend}')

    size_kb = pdf_path.stat().st_size // 1024
    print(f'✅  Exported: {pdf_path}  ({size_kb}KB)')

    if args.open:
        if sys.platform == 'darwin':
            subprocess.run(['open', str(pdf_path)])
        elif sys.platform == 'linux':
            subprocess.run(['xdg-open', str(pdf_path)])
        elif sys.platform == 'win32':
            os.startfile(str(pdf_path))

if __name__ == '__main__':
    main()
