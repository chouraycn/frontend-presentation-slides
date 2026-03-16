# Frontend Presentation Slides

> A WorkBuddy / CodeBuddy skill for creating **zero-dependency, animation-rich HTML presentations** — entirely in the browser, no npm, no build tools.

---

## What It Does

- **New deck from scratch** — describe your topic, get a fully animated HTML presentation
- **Convert PPT/PPTX** — upload a PowerPoint file, get a pixel-perfect web version
- **8 handcrafted templates** — choose by visual style, not abstract descriptions
- **Smart template detection** — automatically picks the best template from content + color signals
- **Presenter mode** — speaker notes, timer, fullscreen navigation built-in
- **PDF export** — one-click export via Puppeteer or browser print

---

## Templates

| Style Name | Best For | Key Colors |
|---|---|---|
| **Dark Elegance** | Investor decks, fundraising, luxury brands | Navy `#0d0d1a` + Gold `#c9a84c` |
| **Vibrant Energy** | Tech talks, conferences, AI startups | Deep purple `#0a0014` + Violet `#7c3aed` + Pink `#ec4899` |
| **Clean Minimal** | Business reviews, OKR reports, internal decks | Warm white `#fafaf8` + Blue `#2563eb` |
| **Claude Warmth** | Brand storytelling, culture decks, warm narratives | Cream `#F6F0E8` + Terracotta `#DA7756` |
| **Warm Inspire** | Product launches, feature reveals, dramatic reveals | Dark amber `#110800` + Gold `#f59e0b` |
| **ForAI White** | Design portfolios, agency pitches, minimal editorial | Pure white `#ffffff` + Ink `#0a0a0a` |
| **Pash Orange** | Agency / studio pitches, orange brand identity | White `#FFFFFF` + Pure orange `#FF5C00` |
| **Hhart Red Power** | Creative studio pitches, red brand, photography | Near-black `#0a0a0a` + Crimson `#C8102E` |

Open `assets/index.html` locally to browse all templates visually.

---

## Installation

In WorkBuddy / CodeBuddy, install this skill directly from the Marketplace, or add it manually:

```bash
# Option A: from Marketplace (search "frontend-presentation-slides")

# Option B: clone this repo into your skills folder
git clone https://github.com/chouray/frontend-presentation-slides \
  ~/.codebuddy/skills/frontend-presentation-slides
```

---

## Usage

Just ask in natural language. The skill auto-detects the right mode:

```
Make me a 10-slide investor pitch deck for a B2B SaaS product
```
```
Convert my attached keynote.pptx to a web presentation
```
```
Create a tech talk using the Vibrant Energy template, topic: Rust for beginners
```
```
使用橙色配色做一个品牌故事演示文稿
```

### Trigger words

`制作幻灯片` · `创建演示文稿` · `做PPT` · `生成slides` · `PPT转HTML` · `pitch deck` · `网页版幻灯片` · `演讲者模式` · `presenter mode` · `投资人演讲` · `融资路演` · `技术分享` · `季度报告` · `产品发布`

---

## Repository Structure

```
frontend-presentation-slides/
├── SKILL.md                          # Skill definition (WorkBuddy entry point)
├── .codebuddy-plugin/
│   └── plugin.json                   # Plugin manifest for Marketplace
├── assets/
│   ├── index.html                    # Visual template gallery
│   ├── templates/                    # 8 ready-to-use HTML templates
│   │   ├── template-pitch-deck.html
│   │   ├── template-tech-talk.html
│   │   ├── template-quarterly-report.html
│   │   ├── template-claude-warmth.html
│   │   ├── template-product-launch.html
│   │   ├── template-forai-white.html
│   │   ├── template-pash-orange.html
│   │   └── template-hhart-red.html
│   ├── style-previews/               # Single-slide style preview pages
│   └── demos/                        # Feature demos (charts, presenter mode)
├── scripts/
│   ├── generate_slides.py            # Core AI → HTML generator
│   ├── extract_pptx.py               # PPTX → slide JSON extractor
│   ├── export_pdf.py                 # HTML → PDF via Puppeteer
│   ├── inline_fonts.py               # Inline web fonts for offline use
│   └── charts.js                     # Chart rendering helpers
└── references/                       # Design guidelines & animation references
```

---

## Scripts Reference

| Script | Purpose | Requires |
|---|---|---|
| `scripts/generate_slides.py` | Convert AI-structured slide JSON → HTML | Python 3.10+ |
| `scripts/extract_pptx.py` | Parse .pptx and emit structured slide data | `python-pptx` |
| `scripts/export_pdf.py` | Headless-Chrome PDF export | `pyppeteer` or `playwright` |
| `scripts/inline_fonts.py` | Embed Google Fonts inline for offline HTML | Python 3.10+ |
| `scripts/charts.js` | Chart.js / D3 chart generation helpers | Node.js 16+ |

---

## Core Design Principles

1. **Zero dependencies** — every output is a single `.html` file with inline CSS and JS
2. **Show, don't tell** — style previews let users pick aesthetics visually, not via text descriptions
3. **Unique design** — no "AI aesthetic"; each template feels handcrafted
4. **Production-ready** — well-commented, accessible, performant code

---

## Smart Template Detection

The skill's `detect_template` engine scores content against 8 templates using:

- **Keyword signals** — topic-specific vocabulary (financial terms, tech stack, design language…)
- **Structural signals** — slide types, chart count, CTA presence
- **Color signals** (Fix-6) — explicit color fields (`palette`, `bg_color`, `accent_color`) and hex/rgb values are parsed and mapped to the nearest template's color identity

---

## License

MIT © chouray
