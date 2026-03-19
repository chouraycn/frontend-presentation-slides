#!/usr/bin/env python3
"""
patch_templates.py — Inject charts.js v2.1 compatibility CSS into all templates.
Run once: python3 scripts/patch_templates.py
"""
from pathlib import Path

COMPAT_CSS = """
    /* ── SlideCharts v2.1 compatibility layer ──────────────────────────── */
    /* Ensures charts.js CSS variables resolve correctly in ALL templates  */
    :root {
      --chart3:  var(--chart3-raw, #10b981);
      --chart4:  var(--chart4-raw, #f59e0b);
      --chart5:  var(--chart5-raw, #3b82f6);
      --chart6:  var(--chart6-raw, #ef4444);
    }

    /* text-primary / text-secondary fallbacks for LIGHT-THEME templates  */
    /* forai-white uses --ink; quarterly-report uses default dark; etc.   */
    :root {
      --text-primary:   var(--text-primary-override,
                          var(--fg, var(--ink, var(--color-text, #1a1a1a))));
      --text-secondary: var(--text-secondary-override,
                          var(--ink-2, var(--muted, var(--color-muted, #666))));
      --surface:        var(--surface-override,
                          var(--bg-muted, var(--card-bg, rgba(255,255,255,0.06))));
      --bg:             var(--bg-override,
                          var(--background, var(--page-bg, #fff)));
    }

    /* Chart slide layout helpers */
    .chart-container {
      width: 100%; height: 100%;
      display: flex; align-items: center; justify-content: center;
    }
    .sc-chart-full {
      display: flex; flex-direction: column;
      gap: 16px; width: 80%; max-width: 740px;
    }
    .sc-chart-split {
      display: grid;
      grid-template-columns: 1fr 1.3fr;
      gap: 52px;
      align-items: center;
      width: min(92%, 1060px);
    }
    .sc-chart-text-col  { display: flex; flex-direction: column; gap: 14px; }
    .sc-chart-chart-col { display: flex; align-items: center; justify-content: center; min-height: 260px; }
    @media (max-width: 768px) {
      .sc-chart-split { grid-template-columns: 1fr; gap: 24px; }
    }
    /* ─────────────────────────────────────────────────────────────────── */
"""

TEMPLATES_DIR = Path(__file__).parent.parent / "assets" / "templates"

count = 0
for f in sorted(TEMPLATES_DIR.glob("template-*.html")):
    content = f.read_text(encoding="utf-8")
    if "SlideCharts v2.1" in content:
        print(f"  SKIP (already patched): {f.name}")
        continue
    # Find the LAST </style> tag to avoid issues with multiple style blocks
    idx = content.rfind("</style>")
    if idx == -1:
        print(f"  SKIP (no </style>): {f.name}")
        continue
    new_content = content[:idx] + COMPAT_CSS + content[idx:]
    f.write_text(new_content, encoding="utf-8")
    print(f"  PATCHED: {f.name}")
    count += 1

print(f"\nDone. {count} templates updated.")
