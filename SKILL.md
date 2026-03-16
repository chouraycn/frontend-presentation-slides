---
name: frontend-presentation-slides
description: "Create zero-dependency, animation-rich HTML presentations that run entirely in the browser. This skill should be used when the user wants to build a presentation, convert a PPT/PPTX to web slides, or create slides for a talk, pitch, or product demo. Helps non-designers discover their preferred aesthetic through visual exploration rather than abstract descriptions. Trigger words: 制作幻灯片、创建演示文稿、做PPT、生成slides、PPT转HTML、网页版幻灯片、做一个演讲稿、产品发布会slide、技术分享slide、chouray、pitch deck、将pptx转换为网页、演讲者模式、presenter mode、模板、快速生成幻灯片、Dark Elegance、Vibrant Energy、Clean Minimal、Claude Warmth、Warm Inspire、ForAI White、Pash Orange、投资人演讲、融资路演、技术分享、季度报告、产品发布、品牌故事、设计作品集、橙色品牌。"
---

# Frontend Slides

Create stunning, zero-dependency, animation-rich HTML presentations — from scratch, from a template, or by converting PowerPoint files.

## Core Philosophy

- **Zero dependencies**: Single HTML file with inline CSS/JS. No npm, no build tools.
- **Show, don't tell**: Generate visual style previews for users to choose from, not abstract descriptions.
- **Unique design**: Avoid generic "AI aesthetic." Every deck should feel handcrafted.
- **Production-ready**: Well-commented code, accessible, performant.

---

## Phase 0: Detect Mode

First, determine what the user needs:

- **Mode A** — New presentation from scratch → go to Phase 1
- **Mode B** — Convert an existing PPT/PPTX file → go to Phase 4
- **Mode C** — Enhance or modify an existing HTML presentation → read the file and improve it
- **Mode D** — Use an existing template → go to Phase 0D

  Eight templates are available. If the user specifies one, jump directly to the matching sub-mode:

  | Sub-mode | Template | Style name | Best for |
  |---|---|---|---|
  | **D1** | `template-pitch-deck.html` | Dark Elegance | Investor decks, fundraising, luxury brands |
  | **D2** | `template-tech-talk.html` | Vibrant Energy | Tech talks, conferences, startups |
  | **D3** | `template-quarterly-report.html` | Clean Minimal | Business reviews, OKR reports, internal decks |
  | **D4** | `template-claude-warmth.html` | Claude Warmth | Brand storytelling, culture decks, warm narratives |
  | **D5** | `template-product-launch.html` | Warm Inspire | Product launches, feature reveals, dramatic reveals |
  | **D6** | `template-forai-white.html` | ForAI White | Design portfolios, agency pitches, minimal editorial |
  | **D7** | `template-pash-orange.html` | Pash Orange | Agency / studio pitches, orange brand identity |
  | **D8** | `template-hhart-red.html` | Hhart Red Power | Creative studio pitches, red brand identity, photography studio |

  > Not sure which to pick? Open `assets/index.html` for a visual gallery — let the user choose by look.

### Phase 0D: Template Quick-Start

When user asks to "use a template", "quickly create a [type] deck", or their scenario clearly matches one of the eight templates:

1. **Match the template** based on use case:

   | Sub-mode | Use case | Template file | Style name | Colors |
   |---|---|---|---|---|
   | D1 | Fundraising / investor deck | `assets/templates/template-pitch-deck.html` | Dark Elegance | navy `#0d0d1a` + gold `#c9a84c` |
   | D2 | Technical talk / conference | `assets/templates/template-tech-talk.html` | Vibrant Energy | deep purple `#0a0014` + violet `#7c3aed` + pink `#ec4899` |
   | D3 | Business review / OKR report | `assets/templates/template-quarterly-report.html` | Clean Minimal | warm white `#fafaf8` + blue `#2563eb` |
   | D4 | Brand storytelling / warm narrative | `assets/templates/template-claude-warmth.html` | Claude Warmth | cream `#F6F0E8` + terracotta `#DA7756` |
   | D5 | Product reveal / launch event | `assets/templates/template-product-launch.html` | Warm Inspire | dark amber `#110800` + gold `#f59e0b` + orange `#fb923c` |
   | D6 | Design portfolio / minimal editorial | `assets/templates/template-forai-white.html` | ForAI White | pure white `#ffffff` + ink `#0a0a0a` |
   | D7 | Agency / studio pitch / orange brand | `assets/templates/template-pash-orange.html` | Pash Orange | white `#FFFFFF` + pure orange `#FF5C00` |
   | D8 | Creative studio / red brand / photography | `assets/templates/template-hhart-red.html` | Hhart Red Power | near-black `#0a0a0a` + crimson `#C8102E` |

   > When unsure, direct the user to `assets/index.html` — the visual gallery lets them pick by look rather than description.

2. **Read the template file** to understand its slide structure and components.

3. **Ask for content**: Request the user's actual content to fill into the template, or offer to use placeholder content if they want to see it first.

4. **Customize**: Replace placeholder content, adjust colors via `:root {}` CSS variables, and deliver the final file. Refer to `assets/templates/README.md` for each template's exact CSS variable names and component reference.

5. **Skip Phase 1 and Phase 2** — templates already have a defined structure and style. Go directly to **Phase 3** (content customization and generation) and then **Phase 5** (delivery).

See `assets/templates/README.md` for full template catalog and component reference.
See `assets/index.html` for the interactive visual gallery of all templates.

---

## Phase 1: Content Discovery (Mode A only)

Ask the user three questions (can be combined into one message):

1. **Purpose** — What is this presentation for? (pitch / tutorial / conference talk / internal demo / other)
2. **Length** — Roughly how many slides? (short: 5–8 / medium: 10–15 / long: 20+)
3. **Content readiness** — Do you have all content ready, rough notes, or just a topic?

Adapt the workflow based on answers. If the user only has a topic, help them structure it first.

### Phase 1.5: Narrative Structure (if user has only a topic or rough notes)

When the user lacks a full outline, **do not free-form generate slides**. Instead, match their use case to one of these proven narrative skeletons, then fill in their specific content:

---

**Skeleton A — Investor / Fundraising Pitch** (10–14 slides)
> Cover → Problem → Market Size → Solution → Why Now → Product Demo / Screenshots → Business Model → Traction & Metrics → Go-to-Market → Competition → Team → Ask / Use of Funds → Thank You

_Best for: Series A/B, angel round, Demo Day. Key rule: lead with pain, not product._

---

**Skeleton B — Technical Talk / Conference** (8–12 slides)
> Cover → The Problem Everyone Recognizes → Why Existing Solutions Fail → Our Approach / Key Insight → Architecture / How It Works → Live Demo / Code Walkthrough → Results & Benchmarks → Lessons Learned / Gotchas → What's Next → Q&A / Repo Link

_Best for: developer conferences, internal tech sharing, open source announcements. Key rule: one concrete insight per slide._

---

**Skeleton C — Quarterly / OKR Business Review** (10–16 slides)
> Cover → Quarter Summary (3 numbers) → OKR Scorecard → Key Achievement Deep-Dive → Miss Analysis + Root Cause → Competitive Landscape Update → Customer / Revenue Metrics → Team Health → Risks & Mitigations → Next Quarter Priorities → Resource Ask (if any) → Appendix

_Best for: leadership all-hands, board updates, cross-team reviews. Key rule: bad news before good news builds credibility._

---

**Skeleton D — Product Launch / Feature Reveal** (8–12 slides)
> Cover (tension / mystery) → The Pain (user story) → The Old Way → The New World (product reveal) → Feature 1 Hero → Feature 2 Hero → Feature 3 Hero → Pricing / Availability → Social Proof / Beta Feedback → Call to Action → Thank You

_Best for: internal launches, press events, sales enablement. Key rule: show before tell — screenshots/video first, explanation second._

---

**Skeleton E — Brand Story / Culture Deck** (10–15 slides)
> Cover → Mission Statement → The World We Want to Change → Our Origin Story → Core Values (one per slide or grid) → How We Work → People / Team → Impact So Far → Community / Partners → Join Us / CTA

_Best for: recruiting, investor relations, partner onboarding. Key rule: every slide should answer "why does this matter to a human."_

---

**Skeleton F — Internal Demo / Stakeholder Update** (6–10 slides)
> Cover → Context / Why We Built This → What We Built (3-sentence summary) → Demo Walkthrough → Key Metrics / Success Criteria → Risks & Open Questions → Next Steps + Timeline → Ask / Decision Needed

_Best for: sprint reviews, internal showcases, approval gates. Key rule: always end with a concrete ask or decision._

---

**Skeleton G — Educational / Tutorial** (8–15 slides)
> Cover → Learning Objectives → Pre-requisites / Who This Is For → Concept 1 (with visual) → Concept 2 → Concept 3 → Hands-on Exercise / Example → Common Mistakes → Summary → Further Reading / Resources

_Best for: workshops, onboarding, documentation-as-slides. Key rule: one concept per slide, always include a visual or code example._

---

**How to use skeletons:**
1. Identify which skeleton best matches the user's purpose
2. Present the skeleton to the user and confirm it fits
3. Ask the user to fill in each slot with their real content (one sentence per slot is enough)
4. Use the filled skeleton as the outline for Phase 3 generation — not free-form AI improvisation

---

## Phase 2: Style Discovery (Visual Exploration)

This is the "show, don't tell" core. **Never skip this phase.**

### Step 2a — Mood selection

Ask the user which feeling they want to convey (multiple choice OK):
- 🎯 Impressive / Confident
- ⚡ Exciting / Energetic
- 🧘 Calm / Focused
- 💡 Inspiring / Moving

### Step 2b — Present style previews

Eight named previews are available in `assets/style-previews/`. Each is a faithful 3-slide taste of its corresponding template:

| # | Preview file | Style name | Mood | Best for |
|---|---|---|---|---|
| D1 | `style-preview-pitch-deck.html` | Dark Elegance | Impressive / Premium | Investor decks, luxury brands |
| D2 | `style-preview-tech-talk.html` | Vibrant Energy | Exciting / Electric | Tech talks, conferences, startups |
| D3 | `style-preview-quarterly-report.html` | Clean Minimal | Calm / Focused | Business reviews, OKR reports |
| D4 | `style-preview-claude-warmth.html` | Claude Warmth | Inspiring / Warm | Brand storytelling, culture decks |
| D5 | `style-preview-product-launch.html` | Warm Inspire | Inspiring / Dramatic | Product launches, feature reveals |
| D6 | `style-preview-forai-white.html` | ForAI White | Calm / Editorial | Design portfolios, agency pitches |
| D7 | `style-preview-pash-orange.html` | Pash Orange | Confident / Agency | Agency/studio pitches, orange brand identity |
| D8 | `style-preview-hhart-red.html` | Hhart Red Power | Bold / Studio / Red | Creative studio, photography, red brand |

**Decision logic:**

- **If the user selected a mood in Step 2a** → recommend the 2–3 previews that best match that mood (use the Mood column above), ask them to pick one, then proceed to **Phase 3**.
- **If the user's mood is unclear or they want to browse** → present the full table above, ask them to open any that appeal and pick one, then proceed to **Phase 3**.
- **If none of the 8 styles fit** → generate a custom preview HTML inline and present it directly via `preview_url` (do **not** create new files in `assets/style-previews/`). Custom preview rules:
  - Show 2–3 sample slides with real-looking content
  - Use a completely distinct visual identity (not just a color swap)
  - Include entrance animations so the user can see motion
  - Keep file size under 50 KB

### Step 2c — Collect feedback

Guide the user to open the preview files. Ask:
- Which style resonates most?
- Any elements to mix or modify?
- Any colors, fonts, or vibes to avoid?

---

## Phase 2.5: Data Visualization Planning (if applicable)

If the presentation contains data, statistics, comparisons, or trends, ask:

> "Does any slide need charts or data visualization? (Bar chart / Line chart / Donut / Progress bars / Horizontal ranking / Radar chart)"

If yes, identify which slides need charts and what data to display. Then:

1. **Choose chart types** based on data nature:
   - Comparisons across categories → `SlideCharts.bar()`
   - Trends over time (single series) → `SlideCharts.line()` or `SlideCharts.area()`
   - Trends over time (multiple series, e.g. A vs B) → `SlideCharts.line()` with `datasets` array
   - Part-to-whole / market share → `SlideCharts.donut()`
   - Rankings / top-N lists → `SlideCharts.horizontalBar()`
   - KPIs / completion rates / skills → `SlideCharts.progress()`
   - Multi-dimensional comparison / skill profiles / competitive radar → `SlideCharts.radar()`

2. **Radar chart usage** (`SlideCharts.radar()`):
   ```js
   SlideCharts.radar('#chart-el', {
     axes: ['Speed', 'Reliability', 'Cost', 'Support', 'Scalability'],
     datasets: [
       { label: 'Our Product', values: [90, 85, 70, 95, 80], color: '#6366f1' },
       { label: 'Competitor',  values: [70, 90, 85, 60, 75], color: '#f43f5e' }
     ],
     max: 100,      // axis maximum (default 100)
     levels: 5,     // concentric rings (default 5)
     filled: true,  // fill polygon area (default true)
     showDots: true,
     showLegend: true
   });
   ```
   Best used for: competitive analysis, skill/competency matrices, product feature comparisons.

3. **Multi-dataset line chart**:
   ```js
   SlideCharts.line('#chart-el', {
     labels: ['Q1', 'Q2', 'Q3', 'Q4'],
     datasets: [
       { label: 'Revenue', values: [120, 145, 160, 210], color: '#6366f1' },
       { label: 'Costs',   values: [80,  90,  95,  100], color: '#f43f5e' }
     ]
   });
   ```

4. **Inline `scripts/charts.js`** into the final HTML file (paste the full file content before `</body>`). This keeps the zero-dependency, single-file principle.

5. **Use chart slide layouts** from `references/style-guide.md` (section: Data Visualization Module):
   - Full-width chart: `slide-chart-full`
   - Text + chart split: `slide-chart-split`
   - Three KPIs side by side: `slide-chart-trio`
   - Ranking / leaderboard: `horizontalBar` pattern
   - Trend line: `area` pattern
   - Radar / spider web: use `slide-chart-full` or `slide-chart-split`

6. **Trigger charts lazily** via IntersectionObserver so they animate when the slide enters viewport (see "Triggering Charts on Slide Enter" in style-guide.md).

---

## Phase 3: Generate the Presentation

Build the full HTML presentation based on Phase 1 content and Phase 2 chosen style.

### Output

- Primary file: `presentation.html` (or `[descriptive-name].html`)
- `assets/` folder only if images are extracted from PPT or user-provided

### Required HTML Architecture

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Presentation Title]</title>
  <style>
    /* ── 1. CSS Custom Properties (Theme) ── */
    /* ── 2. Base Reset & Typography ── */
    /* ── 3. Slide Container & Layout ── */
    /* ── 4. Animation Classes ── */
    /* ── 5. Component Styles ── */
    /* ── 6. Responsive Breakpoints ── */
    /* ── 7. Accessibility (prefers-reduced-motion) ── */
  </style>
</head>
<body>
  <!-- slides here -->
  <script>
    /* ── SlidePresentation controller ── */
    /* ── Intersection Observer for scroll animations ── */
    /* ── Optional enhancements ── */
  </script>
</body>
</html>
```

### Required JavaScript: SlidePresentation Class

Implement a `SlidePresentation` class that handles:
- Keyboard navigation: Arrow keys (←→), Space/Shift+Space, Home/End
- Touch/swipe support (min 50px threshold)
- Mouse wheel navigation (debounced)
- Progress bar update
- Navigation dots (clickable)
- Current slide index tracking

### Required CSS: Scroll-Snap Layout

```css
html, body { height: 100%; margin: 0; overflow: hidden; }
.slides-container {
  height: 100vh;
  overflow-y: scroll;
  scroll-snap-type: y mandatory;
  scroll-behavior: smooth;
}
.slide {
  height: 100vh;
  scroll-snap-align: start;
  overflow: hidden; /* CRITICAL: always set this */
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

### Slide Transition Upgrade (View Transitions API)

When building a new presentation or enhancing an existing one, upgrade the slide navigation to use **CSS View Transitions** for cinematic slide-to-slide transitions. This creates a smooth cross-fade + directional shift between slides instead of an abrupt jump.

**Add this CSS to the generated presentation:**
```css
/* ── View Transitions API — cinematic slide transitions ── */
/* Supported in Chrome 111+, Safari 18+, Edge 111+. Falls back gracefully. */
::view-transition-old(slide-content) {
  animation: vt-slide-out 0.38s cubic-bezier(0.4, 0, 0.2, 1) both;
}
::view-transition-new(slide-content) {
  animation: vt-slide-in 0.38s cubic-bezier(0.4, 0, 0.2, 1) both;
}
/* Forward (next slide): old slides out left, new slides in from right */
[data-direction="forward"]::view-transition-old(slide-content) {
  animation-name: vt-slide-out-left;
}
[data-direction="forward"]::view-transition-new(slide-content) {
  animation-name: vt-slide-in-right;
}
/* Backward (prev slide): reverse */
[data-direction="backward"]::view-transition-old(slide-content) {
  animation-name: vt-slide-out-right;
}
[data-direction="backward"]::view-transition-new(slide-content) {
  animation-name: vt-slide-in-left;
}
@keyframes vt-slide-out-left  { to   { opacity: 0; transform: translateX(-5%) scale(0.97); } }
@keyframes vt-slide-in-right  { from { opacity: 0; transform: translateX(5%) scale(0.97);  } }
@keyframes vt-slide-out-right { to   { opacity: 0; transform: translateX(5%) scale(0.97);  } }
@keyframes vt-slide-in-left   { from { opacity: 0; transform: translateX(-5%) scale(0.97); } }
/* Fallback for browsers without View Transitions */
@keyframes vt-slide-out { to   { opacity: 0; transform: translateY(6px);  } }
@keyframes vt-slide-in  { from { opacity: 0; transform: translateY(-6px); } }

/* view-transition-name must be set on the active slide content */
.slide.active .slide-content { view-transition-name: slide-content; }

/* Respect reduced motion */
@media (prefers-reduced-motion: reduce) {
  ::view-transition-old(slide-content),
  ::view-transition-new(slide-content) {
    animation: none;
  }
}
```

**Update the `goTo()` function to use View Transitions:**
```js
function goTo(targetIdx) {
  const idx = Math.max(0, Math.min(targetIdx, total - 1));
  if (idx === current) return;
  const direction = idx > current ? 'forward' : 'backward';
  document.documentElement.dataset.direction = direction;

  const doTransition = () => {
    // Remove active class from old slide
    slides[current]?.classList.remove('active');
    // Perform the slide switch (your existing translateY logic)
    slides.forEach((s, j) => { s.style.transform = `translateY(${(j - idx) * 100}vh)`; });
    // Add active class to new slide
    slides[idx].classList.add('active');
    // Trigger element animations
    slides[idx].querySelectorAll('[data-animate]').forEach((el, j) => {
      el.classList.remove('visible');
      setTimeout(() => el.classList.add('visible'), j * 130);
    });
    updateChrome(idx);
  };

  // Use View Transitions API if available
  if (document.startViewTransition) {
    document.startViewTransition(doTransition);
  } else {
    doTransition();
  }
}
// Initialize: mark first slide as active
slides[0]?.classList.add('active');
```

```js
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.querySelectorAll('[data-animate]').forEach((el, i) => {
        setTimeout(() => el.classList.add('visible'), i * 120);
      });
    }
  });
}, { threshold: 0.3 });
document.querySelectorAll('.slide').forEach(s => observer.observe(s));
```

### Content Sizing Rules

- All font sizes: use `clamp()` — e.g., `clamp(1rem, 2.5vw, 1.5rem)`
- Images: `max-height: 45vh; max-width: 80%; object-fit: contain;`
- After ANY modification, verify content fits at 1280×720

### Code Quality Requirements

- Every CSS section has a comment header
- Semantic HTML: `<section>`, `<h1>–<h3>`, `<ul>`, `<figure>`, `<blockquote>`
- ARIA: `role="main"`, `aria-label` on slides, `aria-current="true"` on active
- `@media (prefers-reduced-motion: reduce)` — disable all animations

---

## Phase 4: PPT Conversion (Mode B only)

> **CRITICAL RULE — Slide Count Fidelity**: The HTML output **MUST contain exactly the same number of slides as the original PPT**. Every PPT slide maps to exactly one HTML `<section class="slide">`. **Never merge, combine, split, skip, or omit any slide** — not even blank slides, section dividers, or slides with only an image. The slide count is a hard constraint, not a suggestion.

### Step 4a — Extract PPT content

Run the extraction script:

```bash
python3 scripts/extract_pptx.py <input.pptx> --output .claude-design/pptx-extracted/
```

This produces:
- `slides.json` — structured slide data (title, body, notes, layout)
- `images/` — extracted images

After extraction, note the `total_slides` count from `slides.json`. This number is the **target slide count** for the HTML output. Verify the final HTML has exactly this many `<section class="slide">` elements before delivery.

### Step 4b — Confirm content structure

Read `total_slides` from `slides.json` and **state it explicitly** to the user upfront:
> "Extracted **N slides** from `filename.pptx`. The final HTML will contain exactly N slides."

Then show a compact per-slide summary (slide number, layout type, title). **Do NOT ask whether to combine or remove slides.** Only ask:
- Are there any slides where the content looks garbled or missing that you'd like to correct?
- Any slides needing special treatment (e.g., a slide that's entirely a full-bleed image)?

Reordering, combining, or omitting slides requires **explicit user instruction**. Default is always: preserve every slide.

### Step 4c — Template selection (ask the user before generating)

After showing the slide summary, **pause and ask the user to choose a template** before generating any HTML. Present the eight options as a clear comparison table, and point them to the visual gallery if they want to see screenshots:

> "I've extracted **N slides** from your PPT. Before I generate the HTML, please pick a template style — each one is a complete, zero-dependency presentation with full Presenter Mode:
>
> | # | Template | Style | Colors | Best for |
> |---|----------|-------|--------|----------|
> | 1 | **Dark Elegance** | Pitch Deck | Deep navy + gold | Investor decks, fundraising |
> | 2 | **Vibrant Energy** | Tech Talk | Purple-black + pink | Tech talks, conferences |
> | 3 | **Clean Minimal** | Quarterly Report | Off-white + blue | Business reviews, OKRs |
> | 4 | **Claude Warmth** | Brand Story | Cream + terracotta | Storytelling, all-hands |
> | 5 | **Warm Inspire** | Product Launch | Dark amber + orange | Product reveals, launches |
> | 6 | **ForAI White** | Design Studio | Pure white + ink | Portfolios, agency pitches |
> | 7 | **Pash Orange** | Agency Editorial | White + pure orange | Studio pitches, brand decks |
> | 8 | **Hhart Red Power** | Studio Red | Near-black + crimson | Creative studio, red brand |
>
> 👉 Want to see visuals first? Open `assets/index.html` in your browser for the interactive style gallery.
>
> Just reply with a number (1–8) or style name, and I'll start generating."

**Wait for the user's reply before proceeding to Step 4d.** Do not auto-select a template or skip this step.

If the user's PPT content clearly signals a theme (e.g., a fundraising deck → Dark Elegance, a dev conference talk → Vibrant Energy), you may suggest a recommendation alongside the table, but still require explicit confirmation.

### Step 4d — Generate HTML

**Option A — Use the automated pipeline (recommended, guarantees slide count)**

```bash
python3 scripts/generate_slides.py .claude-design/pptx-extracted/slides.json \
  --template <chosen-template> --output presentation.html --verbose
```

`generate_slides.py` detects the PPTX-extracted format automatically (via `layout` /
`body_paragraphs` fields), calls `_normalise_pptx()` to convert every slide, and
**aborts with an error** if the output count doesn't match `total_slides`.
Check the printed slide count in the success line, e.g.:
`✅  Generated: presentation.html  (24 slides, 312KB)` — verify this matches the PPT.

**Option B — Manual HTML generation**

Convert extracted content to the chosen HTML style following these rules:

1. **One slide in PPT = one `<section class="slide">` in HTML** — no exceptions.
2. Iterate through `slides.json` in order. For each entry, generate one `<section>`. Use
   the `body_paragraphs`, `tables`, `smartart`, and `images` fields — **not** a `content`
   field (which does not exist in the extract output).
3. If a slide has no extractable text (image-only, blank, or SmartArt-only), still generate
   a `<section>` for it — use the image if available, or a styled placeholder.
4. Preserve all original content. Use extracted images in `assets/`.

**⛔ MANDATORY pre-delivery verification (applies to both options)**

Before delivering the file, run this count check and confirm the numbers match:

```js
// Open browser console on the generated file and run:
document.querySelectorAll('.slide').length
```

Then compare against `total_slides` from `slides.json`:
```bash
python3 -c "import json; d=json.load(open('.claude-design/pptx-extracted/slides.json')); print('PPT slides:', d['total_slides'])"
```

**If the counts differ, DO NOT deliver the file.** Fix missing slides and re-verify.
Report the verified count to the user: `"HTML: N slides ✓ (matches PPT)"`.

---

## Phase 4.5: Font Offline Tool (Optional)

When a presentation uses Google Fonts and needs to work **without internet access** (e.g., conference venue with no Wi-Fi), use the font inlining tool:

```bash
python3 scripts/inline_fonts.py presentation.html --output presentation-offline.html
```

What it does:
- Detects Google Fonts `<link>` tags in the HTML
- Downloads font CSS and WOFF2 files
- Base64-encodes fonts and inlines them as `@font-face` rules
- Removes the original CDN links
- Outputs a fully self-contained HTML file

Options:
```bash
# List detected fonts without modifying anything
python3 scripts/inline_fonts.py presentation.html --list

# Include CJK (Chinese/Japanese/Korean) font subsets (large files!)
python3 scripts/inline_fonts.py presentation.html --cjk

# Custom output path
python3 scripts/inline_fonts.py presentation.html --output path/to/output.html
```

**System font fallbacks**: If the user doesn't want to run the tool, the script also documents
fallback stacks (e.g., "Inter" → `-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`).
These can be manually added to the `:root {}` CSS as a `--font-body` override.

Requirements: `pip install requests beautifulsoup4`

---

## Phase 5: Delivery

1. Delete the `.claude-design/` temporary directory
2. Open `[filename].html` in the browser: `open presentation.html`
3. Provide a brief usage summary:
   - Navigate: Arrow keys / Space / swipe / scroll / click dots
   - Customize: Edit CSS variables in `:root {}` at the top of the file
   - Full screen: F11 or browser fullscreen
   - Presenter mode: Press `[P]` to open the Presenter View

---

## Phase 6: Presenter Mode

Every presentation built with this skill supports a **Presenter Mode** that uses the BroadcastChannel API for real-time two-window synchronization — no server required.

### How to use

1. Open the presentation in a browser tab (the **audience display** — put this on the projector)
2. Press `[P]` to open the **Presenter View** in a new window
3. The presenter view shows:
   - Current slide (large preview, left)
   - Next slide preview (top right)
   - Speaker notes (bottom right)
   - Elapsed time counter (click to reset; turns yellow at 20 min, red at 30 min)
   - **← → navigation buttons** to advance/go back from the presenter window
   - **Laser pointer** (button or `L` key): move mouse over the current slide preview to project a red dot on the audience screen
   - **Blackout** (button or `B` key): toggle a black screen on the audience display; click the audience screen to cancel
4. Navigate from either window — both stay in sync

### How to add Presenter Mode to a new presentation

The full implementation is in `assets/demos/presenter-mode-demo.html`. The key pieces to add:

**1. Add the BroadcastChannel broadcaster to the main SlidePresentation class:**
```js
const presenterChannel = new BroadcastChannel('slide-sync');

// In goToSlide():
presenterChannel.postMessage({ type: 'slide-change', index: newIndex, total: slides.length });

// On load:
presenterChannel.postMessage({ type: 'init', index: currentIndex, total: slides.length,
  sourceUrl: location.href });

// Handle incoming navigate commands:
presenterChannel.onmessage = (e) => {
  if (e.data.type === 'navigate') goToSlide(e.data.index);
  if (e.data.type === 'request-init') {
    presenterChannel.postMessage({ type: 'init', index: currentIndex,
      total: slides.length, sourceUrl: location.href });
  }
};
```

**2. Add the `[P]` key shortcut** to open the presenter view in a new window:
```js
if (e.key === 'p' || e.key === 'P') openPresenterView();
```

**3. The Presenter View HTML** is self-contained inline template (see `presenter-mode-demo.html`
for the complete `<script id="presenter-view-html" type="text/plain">` template block).
It uses CSS Grid: `3fr 2fr` columns, `1fr 1fr` rows for the 2×2 layout.

### Speaker notes format

Add notes as `data-notes` attribute on each `.slide`:
```html
<section class="slide" data-notes="Key talking point: emphasize the 3x ROI. Pause here for questions.">
  <!-- slide content -->
</section>
```

The presenter view reads `slide.dataset.notes` and displays it in the notes panel.

---

## Proactive Quality Checks (Auto-Heal)

After ANY modification or generation, **automatically run all checks below** — do not wait for the user to report issues. Fix detected problems silently before delivery.

### Check 1 — Overflow Audit
Run this in browser console (or generate it as an inline self-check script):
```js
(function overflowAudit() {
  const results = [];
  document.querySelectorAll('.slide').forEach((slide, i) => {
    if (slide.scrollHeight > slide.clientHeight + 4) {
      results.push(`Slide ${i+1}: scrollHeight=${slide.scrollHeight} > clientHeight=${slide.clientHeight}`);
    }
    slide.querySelectorAll('*').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.bottom > slide.getBoundingClientRect().bottom + 8) {
        results.push(`  └ ${el.tagName}.${el.className.split(' ')[0]} overflows bottom`);
      }
    });
  });
  if (results.length) {
    console.warn('⚠ Overflow detected:\n' + results.join('\n'));
  } else {
    console.log('✅ No overflow detected');
  }
  return results;
})();
```

**Auto-fix rules when overflow is detected:**
- Long body text: reduce `max-width` to 680px and add `font-size: clamp(0.85rem, 1.3vw, 0.95rem)`
- Too many bullet items (>6): split into two slides automatically
- Image too tall: add `max-height: 40vh; object-fit: contain`
- Stats row with 4+ items: switch to `grid-template-columns: repeat(2, 1fr)` on mobile

### Check 2 — Contrast Audit
Verify text contrast meets WCAG AA (4.5:1 for body, 3:1 for large headings):
```js
// Known risky combinations to check manually:
const riskPairs = [
  { bg: '#FF5C00', text: 'subtitle/body', minRatio: 3.1 },  // Pash Orange cover
  { bg: '#C8102E', text: 'attr/eyebrow',  minRatio: 3.0 },  // Hhart Red bg-red
  { bg: '#f59e0b', text: 'body text',     minRatio: 4.5 },  // Product Launch accent
];
// If any risky slide type is present, add explicit color overrides:
// .bg-orange .subtitle { color: #fff; }
// .bg-red .attr { color: rgba(255,255,255,0.88); }
```

**Auto-fix rule:** When a dark-theme template has subtitle/body text on a colored background, always add an explicit `color: #fff` or `color: rgba(255,255,255,0.88)` override.

### Check 3 — Slide Count Verification
Before delivery, confirm the generated HTML contains the expected number of slides:
```js
const count = document.querySelectorAll('.slide').length;
console.log(`Slide count: ${count}`);
// For Mode B (PPT conversion): compare against total_slides from slides.json
// For Mode A/D: compare against the outline array length
```

If counts don't match: **do not deliver**. Debug and fix before sending.

### Check 4 — Animation Integrity
Ensure `.visible` CSS rules exist for all `data-animate` variants used:
```js
const variants = new Set();
document.querySelectorAll('[data-animate]').forEach(el => {
  variants.add(el.getAttribute('data-animate') || 'default');
});
// Verify these CSS classes are defined: [data-animate].visible, [data-animate="scale"].visible, etc.
console.log('Animation variants used:', [...variants]);
```

**Auto-fix:** If a `data-animate="X"` variant is used but has no `.visible` rule, add the missing CSS.

### Check 5 — CJK Font Stack
If the deck contains Chinese/Japanese/Korean text (detected via `\u4e00–\u9fff` range), verify:
- `<html lang="zh-CN">` (or `ja`, `ko`) is set
- Font stack includes `'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei'` fallbacks
- `line-height: 1.8` is applied to `.slide p, .slide li`

**Auto-fix:** If CJK text is present but font stack lacks CJK fallbacks, inject the correct fallbacks into `:root`.

---

> **Delivery gate:** All 5 checks must pass (or be auto-fixed) before the file is presented to the user. Never deliver a deck with known overflow, contrast, or count issues.

---

## Reference Files

- `references/style-guide.md` — Style-mood mappings, CSS animation patterns, font pairings, color palettes, **data visualization layouts** (see "Data Visualization Module" section), radar chart layout patterns
- `references/troubleshooting.md` — Common issues and solutions
- `scripts/extract_pptx.py` — PPT content extraction script (v2). Extracts text, tables, SmartArt, images, speaker notes, and layout hints. Produces `slides.json` + `images/` directory.
- `scripts/charts.js` — Zero-dependency SVG chart engine v2.0. Provides `SlideCharts.bar()`, `.line()`, `.area()`, `.donut()`, `.horizontalBar()`, `.progress()`, `.radar()`, `.sankey()`. All chart functions return a **ChartInstance** with `update(newData)`, `setOptions(newOpts)`, `loadURL(url)`, `listenPostMessage()` for dynamic updates. Sankey (flow/Sankey diagram) accepts `{ nodes: string[], links: [{source, target, value}] }` and renders a layered flow diagram with SVG cubic-bezier links and gradient coloring. **Inline this file's contents** into the final HTML — do not load it as an external script in production.
- `scripts/generate_slides.py` — AI content generation pipeline. Accepts a JSON outline **or a topic description via `--expand`** and outputs a complete single-file HTML presentation. Two usage modes: (1) outline mode: `python3 scripts/generate_slides.py outline.json --template claude-warmth --output out.html`; (2) expand mode: `python3 scripts/generate_slides.py --expand "主题描述" --slides 10 --template claude-warmth --output out.html` — automatically calls an LLM (Anthropic → OpenAI → codebuddy CLI fallback chain) to generate a full outline from the topic, then renders the HTML. `--slides N` controls the number of slides (default 10, max 20). Supported `--template` choices: `claude-warmth`, `pitch-deck`, `product-launch`, `quarterly-report`, `tech-talk`, `forai-white`, `pash-orange`, `hhart-red`.
- `scripts/export_pdf.py` — PDF export tool. Supports three backends (Playwright, Puppeteer, WeasyPrint) with auto-detection. Page size options: `16x9` (default, 1920×1080), `4x3`, `A4`, `Letter`, or custom `WxH` in mm. Key options: `--backend {auto|playwright|puppeteer|weasyprint}`, `--landscape` (force landscape), `--margin MM` (page margin in mm, default 0), `--wait SECS` (wait for JS animations to settle, default 1.5), `--scale FACTOR` (Playwright only), `--open` (open PDF after export). Usage: `python3 scripts/export_pdf.py my_deck.html --page-size 16x9 --wait 2 --open`
- `scripts/inline_fonts.py` — Font offline tool. Detects Google Fonts CDN links, downloads WOFF2 files, Base64-encodes them, and outputs a self-contained HTML. Run: `python3 scripts/inline_fonts.py input.html`. Use `--list` to inspect detected fonts without modifying the file (no network access required for `--list` mode).
- `scripts/parse_html.py` — **Reverse-edit tool** (new). Parses a finished HTML presentation back into the JSON outline format consumed by `generate_slides.py`. Enables a two-way editing workflow: HTML → JSON → edit → regenerate. Usage: `python3 scripts/parse_html.py deck.html --pretty` → produces `deck.json`. Flags: `--output` (custom path), `--pretty` (indent JSON), `--stats` (slide-count summary only), `--verbose` (print each slide as parsed). Requires: `pip3 install beautifulsoup4`.
- `scripts/embed_images.py` — **Image inlining tool** (new). Converts all local `<img src="...">` and CSS `background-image: url(...)` references into base64 data URIs, making the HTML fully self-contained for sharing/archiving. Usage: `python3 scripts/embed_images.py deck.html`. Flags: `--output` (custom path), `--list` (list images only), `--resize W` (max-width resize; requires Pillow), `--quality Q` (JPEG quality 1–95, default 88), `--skip-missing`, `--verbose`. Requires: `pip3 install beautifulsoup4`; optional: `pip3 install Pillow` for resize.
- `setup.html` — **Interactive config wizard** (new). Open in any browser for a 3-step visual configurator: choose visual style → fill in content details → copy the generated CLI command. No install required. Located at the project root.
- `assets/demos/presenter-mode-demo.html` — Full Presenter Mode demo and reference implementation. Press `[P]` to see the two-window sync in action.
- `assets/templates/` — Template library with **8** ready-to-customize presentations (pitch-deck, tech-talk, quarterly-report, product-launch, claude-warmth, forai-white, pash-orange, hhart-red). All templates include v2 Presenter Mode (bidirectional navigation, laser pointer, blackout), mobile responsive CSS, and print/PDF styles. See `assets/templates/README.md` for catalog.

### Two-Way Editing Workflow

When a user wants to edit an existing HTML presentation, offer this workflow:

```bash
# Step 1: Parse HTML back to editable JSON
python3 scripts/parse_html.py my_deck.html --pretty
# → Produces my_deck.json with all slide content

# Step 2: User edits my_deck.json in any text editor
# (change text, reorder slides, add/remove items)

# Step 3: Regenerate HTML from the edited JSON
python3 scripts/generate_slides.py my_deck.json --template claude-warmth --output my_deck.html --open

# Step 4 (optional): Make fully self-contained for sharing
python3 scripts/embed_images.py my_deck.html
python3 scripts/inline_fonts.py my_deck-embedded.html --output my_deck-final.html
```

### When to suggest each post-processing tool

| Scenario | Tool |
|---|---|
| User wants to share the deck via email / Slack | `embed_images.py` + `inline_fonts.py` |
| User wants to edit slide text without AI | `parse_html.py` → edit JSON → `generate_slides.py` |
| Presentation will be shown offline (no Wi-Fi) | `inline_fonts.py --cjk` (if CJK text) |
| User wants a PDF for printing / email attachment | `export_pdf.py` |
| User is new and unsure how to start | Open `setup.html` in browser |

