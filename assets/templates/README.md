# Slide Template Library

Eight production-ready, zero-dependency HTML presentation templates. Each is a single self-contained file — open in any browser, no setup required.

All templates include:
- **Presenter Mode v2** — bidirectional navigation (← →), laser pointer (`L` key), blackout screen (`B` key)
- **Mobile-responsive CSS** — breakpoints at 900 px and 640 px
- **Print / PDF styles** — `@media print` with `page-break-after: always` and exact color preservation

---

## Preview ↔ Template Map

Each template has a matching style-preview file in `assets/style-previews/`. Use previews to let users pick a visual direction before filling in content.

| Template file | Preview file | Style name | Palette | Mood |
|---|---|---|---|---|
| `template-pitch-deck.html` | `style-preview-pitch-deck.html` | Dark Elegance | Deep navy + gold | Impressive / Premium |
| `template-tech-talk.html` | `style-preview-tech-talk.html` | Vibrant Energy | Purple-black + pink/violet | Exciting / Electric |
| `template-quarterly-report.html` | `style-preview-quarterly-report.html` | Clean Minimal | Off-white + blue | Calm / Focused |
| `template-claude-warmth.html` | `style-preview-claude-warmth.html` | Claude Warmth | Cream + terracotta | Inspiring / Warm |
| `template-product-launch.html` | `style-preview-product-launch.html` | Warm Inspire | Dark amber + orange | Bold / Dramatic |
| `template-forai-white.html` | `style-preview-forai-white.html` | ForAI White | Pure white + ink black | Editorial / Minimal |
| `template-pash-orange.html` | `style-preview-pash-orange.html` | Pash Orange | White + pure orange `#FF5C00` | Confident / Agency |
| `template-hhart-red.html` | `style-preview-hhart-red.html` | Hhart Red Power | Near-black + crimson `#C8102E` | Bold / Studio / Red Brand |
| `template-healthcare.html` | `style-preview-healthcare.html` | Clinical Trust | Arctic white + teal `#0891b2` | Calm / Credible / Medical |
| `template-finance.html` | `style-preview-finance.html` | Bloomberg Dark | Deep charcoal + amber `#f59e0b` | Data-Dense / Authoritative |
| `template-education.html` | `style-preview-education.html` | Campus Bright | Sky blue + coral `#f97316` | Playful / Engaging / Learning |

**Workflow**: Point users at 2–3 previews that match their mood → they pick one → open the matching template → fill in content.

---

## Template Catalog

### 1. `template-pitch-deck.html` — Investor Pitch Deck
**Use when**: Fundraising, investor presentations, startup demos, partnership proposals

| Property | Value |
|----------|-------|
| **Style** | Dark Elegance |
| **Colors** | Deep navy `#0a0f1e` + gold `#c9a84c` |
| **Fonts** | Playfair Display (headings) + Inter (body) |
| **Slide count** | 8 slides |
| **Mood** | Impressive / Confident |

**Slide structure**:
1. **Cover** — Company name, tagline, presenter info
2. **Problem** — Pain point with supporting stats
3. **Solution** — Product value proposition
4. **Market** — TAM / SAM / SOM breakdown
5. **Traction** — Key metrics and growth stats (`big-stat` component)
6. **Team** — Founders grid (`team-grid` component)
7. **The Ask** — Funding amount and use of funds (`card` components)
8. **Close** — Contact and call to action

**Custom components**:
- `.big-stat` — Large number + label + supporting text. Use for ARR, users, growth rates.
- `.team-grid` — Responsive grid of team member cards with avatar, name, and title.
- `.card` — Bordered content block with title and body, used for funding allocation breakdown.
- `.accent` — Gold-colored inline highlight for key words.

**Quick customization**:
```css
/* In :root {} at top of file */
--clr-bg: #0a0f1e;        /* Main background */
--clr-accent: #c9a84c;    /* Gold accent color */
--clr-text: #e8e0d4;      /* Body text */
--font-head: 'Playfair Display', Georgia, serif;
--font-body: 'Inter', system-ui, sans-serif;
```

---

### 2. `template-tech-talk.html` — Technical Conference Talk
**Use when**: Engineering talks, tech conferences, open-source demos, architecture walkthroughs

| Property | Value |
|----------|-------|
| **Style** | Vibrant Energy |
| **Colors** | Deep purple `#0d0221` + pink gradient `#ff6b9d` |
| **Fonts** | Space Grotesk (headings) + DM Sans (body) + JetBrains Mono (code) |
| **Slide count** | 9 slides |
| **Mood** | Exciting / Energetic |

**Slide structure**:
1. **Hook** — Provocative opening statement
2. **Context** — Why this problem matters (`card-grid` with root cause analysis)
3. **Our Approach** — Solution overview with `steps-list`
4. **Code Deep Dive** — Code example with `pre.code-block`
5. **Benchmarks** — Performance comparison `bench-table`
6. **Pitfalls** — What to watch out for (`card-grid`)
7. **Takeaways** — Key lessons (`steps-list` with star icons)
8. **Resources** — Links and further reading (`card-grid`)
9. **Q&A** — Speaker contact

**Custom components**:
- `pre.code-block` — Monospace code block with syntax-highlight `<span>` classes: `.kw` (keyword), `.fn` (function), `.str` (string), `.cmt` (comment). Background `#1a0533`.
- `.bench-table` — Comparison table. Add `class="highlight"` to a `<tr>` to mark the winning row.
- `.steps-list` — Numbered step list with CSS counter-based numbering. Set `--steps-color` for accent.
- `.card-grid` — 2×2 or 3-column grid of `.card` elements.

**Quick customization**:
```css
--clr-bg: #0d0221;
--clr-accent: #ff6b9d;
--clr-accent-2: #a855f7;
--font-head: 'Space Grotesk', sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

---

### 3. `template-quarterly-report.html` — Quarterly Business Review
**Use when**: Q-reviews, board updates, OKR check-ins, business performance summaries

| Property | Value |
|----------|-------|
| **Style** | Clean Focus |
| **Colors** | White `#ffffff` + blue `#2563eb` (light theme) |
| **Fonts** | Plus Jakarta Sans |
| **Slide count** | 8 slides |
| **Mood** | Calm / Focused |

**Slide structure**:
1. **Cover** — Quarter, company, presenter
2. **Executive Summary** — Top-line summary with 3 key takeaways
3. **OKR Status** — Progress bars per objective (`okr-list`)
4. **Key Metrics** — 4-column metrics grid (`metrics-grid`)
5. **Wins & Misses** — Two-column win/miss list (`item-list`)
6. **Initiatives** — Status cards for key projects (`card-grid` + `.badge`)
7. **Risks & Mitigations** — Risk table (`risk-table`)
8. **Next Quarter** — Priorities and goals

**Custom components**:
- `.metrics-grid` — 4-column card grid. Each card: big number, label, delta (green/red). Best for ARR, DAU, NPS, conversion rate.
- `.okr-list` — OKR rows with CSS `--progress` variable controlling fill width. Each row: objective text + percentage bar.
  ```html
  <div class="okr-item" style="--progress: 72%">
    <span class="okr-label">Launch new pricing page</span>
    <span class="okr-percent">72%</span>
    <div class="okr-bar"><div class="okr-fill"></div></div>
  </div>
  ```
- `.badge` — Status pill. Classes: `.green` (on track), `.amber` (at risk), `.red` (off track), `.blue` (informational).
- `.risk-table` — Table with columns: Risk, Impact, Likelihood, Mitigation. Style rows with `.high` / `.medium` / `.low` class on `<tr>`.
- `.item-list.wins` / `.item-list.misses` — Bullet lists with green checkmarks / red X icons.

**Quick customization**:
```css
--clr-bg: #ffffff;
--clr-bg-2: #f8fafc;
--clr-accent: #2563eb;
--clr-text: #1e293b;
--clr-success: #16a34a;
--clr-danger: #dc2626;
--clr-warning: #d97706;
```

---

### 4. `template-product-launch.html` — Product Launch Event
**Use when**: New product announcements, feature reveals, launch events, keynote-style demos

| Property | Value |
|----------|-------|
| **Style** | Warm Inspire |
| **Colors** | Deep amber `#1a0a00` + orange `#f97316` |
| **Fonts** | Cormorant Garamond (italic headings) + Nunito (body) |
| **Slide count** | 8 slides |
| **Mood** | Inspiring / Moving |

**Slide structure**:
1. **Teaser** — Cryptic product hint to build anticipation
2. **Problem + Quote** — Customer pain point with a hero quote (`hero-quote`)
3. **Reveal** — Product name and hero visual
4. **Features** — 3-column feature cards (`features-grid`)
5. **Impact Numbers** — Large metric highlights (`big-number`)
6. **Testimonials** — Customer quotes (`testimonial`)
7. **Pricing** — 3-tier pricing table (`pricing-grid`)
8. **CTA** — Sign up / try now

**Custom components**:
- `.hero-quote` — Large centered quote block with left amber border, attribution below. For customer testimonials or problem-framing statements.
- `.features-grid` — 3-column grid of `.feature-card`. Each card: icon area, title, description.
- `.big-number` — XL metric display: large number + unit, label below, optional trend delta.
- `.testimonial` — Quote card with customer text, avatar placeholder, name and company.
- `.pricing-grid` — 3-column pricing cards. Add class `.featured` to center card for "recommended" highlight with colored border and background.
  ```html
  <div class="pricing-card featured">...</div>
  ```

**Quick customization**:
```css
--clr-bg: #1a0a00;
--clr-accent: #f97316;
--clr-accent-light: #fed7aa;
--font-head: 'Cormorant Garamond', Georgia, serif;
--font-body: 'Nunito', 'Varela Round', sans-serif;
```

---

### 5. `template-claude-warmth.html` — Brand Storytelling / General Purpose
**Use when**: Brand narratives, team retrospectives, internal all-hands, warm storytelling, general-purpose decks that don't fit the other four templates

| Property | Value |
|----------|-------|
| **Style** | Claude Warmth |
| **Colors** | Cream `#fdf8f2` + terracotta `#c4622d` (light warm theme) |
| **Fonts** | Lora (headings, serif) + Source Sans Pro (body) |
| **Slide count** | 8 slides |
| **Mood** | Inspiring / Moving |

**Slide structure**:
1. **Cover** — Title, subtitle, presenter / event date
2. **Opening Story** — Narrative hook with pull quote (`pull-quote`)
3. **Our Values** — 3-column values cards (`value-card`)
4. **The Journey** — Timeline milestones (`timeline`)
5. **Impact** — Large metric highlights with warm styling (`impact-stat`)
6. **Team / Community** — People grid (`people-grid`)
7. **What's Next** — Future directions with vision statement
8. **Close** — Thank-you / call to action with contact

**Custom components**:
- `.pull-quote` — Large italic blockquote with terracotta left border. For opening stories and memorable customer statements.
- `.value-card` — Card with icon area, title, and body copy. `background: var(--clr-card)` (warm off-white). 3-column grid.
- `.timeline` — Vertical timeline with alternating left/right layout. Each `timeline-item` has year, title, and description.
- `.impact-stat` — Full-width stat highlight: oversized number in terracotta, label in muted text below.
- `.people-grid` — Responsive grid of `.person` cards with circular avatar area, name, and role.

**Quick customization**:
```css
/* In :root {} at top of file */
--clr-bg: #fdf8f2;         /* Warm cream background */
--clr-accent: #c4622d;     /* Terracotta accent */
--clr-accent-light: #f4a574; /* Soft apricot */
--clr-card: #fff8f0;       /* Card fill */
--clr-text: #2c1a0e;       /* Deep warm brown */
--font-head: 'Lora', Georgia, serif;
--font-body: 'Source Sans Pro', system-ui, sans-serif;
```

---

### 6. `template-forai-white.html` — Design Studio / Creative Agency
**Use when**: Design portfolios, agency pitches, product design reviews, brand presentations, creative studio decks

| Property | Value |
|----------|-------|
| **Style** | ForAI White |
| **Colors** | Pure white `#ffffff` + ink black `#0a0a0a` + muted grey `#f7f7f5` |
| **Fonts** | DM Serif Display (headings, italic) + DM Sans (body) |
| **Slide count** | 9 slides |
| **Mood** | Calm / Focused / Design-forward |

Inspired by [forai.design](https://forai.design/) — editorial minimalism with generous whitespace, dot-grid textures, and confident black-on-white typography.

**Slide structure**:
1. **Cover** — Headline + tagline with dot-grid background texture
2. **About** — Two-column: positioning statement + service list
3. **Numbers** — 4-column stat grid with large display numbers
4. **Work 01** — Featured case study with work-item layout (visual + info)
5. **Work 02** — Two-card case study grid
6. **Testimonial** — Inverted black slide with bordered blockquote
7. **Process** — Two-column: framing copy + numbered week-by-week timeline
8. **Clients** — Centered logo/client grid with social proof
9. **CTA** — Closing slide with dot-grid + contact

**Custom components**:
- `.work-item` — Two-column card: visual placeholder (left) + title, tags, stats (right).
- `.stat-block` — Large display stat: number, label, description. Use for metrics at a glance.
- `.process-list` / `.process-item` — Bordered row list with step number + title + description.
- `.testimonial-block` — Left-bordered blockquote with attribution line.
- `.client-grid` / `.client-cell` — 1px-gap mosaic grid of client name cells.
- `.tag` — Minimal bordered pill for categorization.
- `.btn-primary` / `.btn-outline` / `.btn-arrow` — CTA button variants.
- `.bg-dots` — Dot-grid background texture (via `::before` pseudo).
- `.bg-grid` — Fine line-grid background texture.
- `.corner-mark` — Decorative corner bracket (bottom-right, via `::after`).
- `.eyebrow` — All-caps micro label with letter-spacing.
- `.divider` / `.divider-short` — Hairline / short ink dividers.

**Quick customization**:
```css
/* In :root {} at top of file */
--bg:           #ffffff;      /* Page background */
--bg-invert:    #0a0a0a;      /* Inverted slide bg */
--ink:          #0a0a0a;      /* Primary text + accent */
--accent-warm:  #e85d26;      /* Optional warm accent color */
--accent-cool:  #1a56db;      /* Optional cool accent color */
--font-head: 'DM Serif Display', Georgia, serif;
--font-body: 'DM Sans', system-ui, sans-serif;
```

To add a brand accent color, replace `--ink` with your color on specific components:
```css
.eyebrow { color: var(--accent-warm); }
.divider-short { background: var(--accent-warm); }
```

---

### 7. `template-pash-orange.html` — Agency / Studio Editorial
**Use when**: Agency pitches, design studio decks, brand presentations, creative portfolio showcases, editorial-style keynotes

| Property | Value |
|----------|-------|
| **Style** | Pash Orange |
| **Colors** | White `#ffffff` + pure orange `#FF5C00` |
| **Fonts** | Bebas Neue (display, all-caps) + DM Serif Display (headings) + DM Sans (body) |
| **Slide count** | 9 slides |
| **Mood** | Impressive / Confident / Design-forward |

Inspired by [pash.website](https://www.pash.website/) — editorial minimalism with bold uppercase typography, dot-grid textures, asymmetric grid layouts, and a confident orange-on-white identity. Slide 08 inverts to full orange for maximum impact.

**Slide structure**:
1. **Cover** — All-caps headline + tagline with L-bracket corner marks
2. **Manifesto** — Full-screen editorial statement, asymmetric layout
3. **About** — 3:2 asymmetric two-column: positioning copy + service list
4. **Work 01** — Featured case study with image placeholder + info grid
5. **Work 02** — Two-card horizontal case study grid
6. **Numbers** — 4-column stat grid with oversized display counters
7. **Process** — Two-column: framing copy + numbered week-by-week steps
8. **Testimonial** — Inverted full-orange slide with large pull quote
9. **CTA** — Closing slide with dot-grid + L-bracket + contact

**Custom components**:
- `.counter` — Zero-filled editorial counter (`001 / 002`) for section labeling.
- `.work-item` — Two-column case study card: visual placeholder + title, tags, stats.
- `.stat-block` — Oversized display stat in Bebas Neue: number + label.
- `.process-list` / `.process-item` — Bordered row list with step number + title + description.
- `.pull-quote` — Large italic blockquote on orange background with attribution.
- `.bg-dots` — Dot-grid background texture via `::before` pseudo-element.
- `.corner-mark` — Decorative L-bracket corners (Cover and CTA slides).
- `.eyebrow` — All-caps micro label with `0.2em` letter-spacing.
- `.tag` — Minimal bordered pill for project categorization.
- `.btn-primary` / `.btn-outline` — CTA button variants.
- `.bg-orange` — Full orange background section (Slide 08 testimonial).

**Quick customization**:
```css
/* In :root {} at top of file */
--bg:           #FFFFFF;    /* White canvas */
--bg-invert:    #FF5C00;    /* Invert slide — swap to your brand color */
--orange:       #FF5C00;    /* Primary accent */
--ink:          #0a0a0a;    /* Primary text */
--font-display: 'Bebas Neue', Impact, sans-serif;
--font-heading: 'DM Serif Display', Georgia, serif;
--font-body:    'DM Sans', system-ui, sans-serif;
```

---

### 8. `template-hhart-red.html` — Creative Studio / Red Brand
**Use when**: Creative studio pitches, photography studio decks, red-brand identity presentations, bold agency keynotes, high-contrast editorial decks

| Property | Value |
|----------|-------|
| **Style** | Hhart Red Power |
| **Colors** | Near-black `#0a0a0a` + crimson `#C8102E` |
| **Fonts** | Barlow Condensed 800 (display, all-caps) + Barlow 300/400/600 (body) |
| **Slide count** | 9 slides |
| **Mood** | Bold / Confident / Studio-grade |

Inspired by [hhart.studio](https://www.hhart.studio/) — geometric minimalism, black canvas, crimson red, wide-tracked uppercase sans-serif, maximum contrast, confident negative space.

**Slide structure**:
1. **Cover** — All-caps display headline + tagline with L-bracket corner marks
2. **Manifesto** — Full-screen editorial statement with outlined + filled text layers
3. **About** — 3:2 asymmetric two-column: positioning copy + service list
4. **Work 01** — Featured case study with 2:3 asymmetric layout (visual + info)
5. **Work 02** — Two-card horizontal case study grid
6. **Numbers** — 4-column stat grid with oversized Barlow Condensed red values
7. **Process** — Two-column: framing copy + four-step numbered process list
8. **Testimonial** — Inverted full-crimson slide with large all-caps pull quote
9. **CTA** — Closing dark slide with dot-grid + L-bracket + contact

**Custom components**:
- `.display` — Barlow Condensed 800 all-caps display type: `clamp(5rem, 12vw, 13rem)`, `line-height: 0.88`.
- `.manifesto-text` — Full-screen editorial statement with `.line-outline` (stroke-only) and `.line-red` (solid crimson) variants.
- `.stat-row` / `.stat-block` — Dark card grid: `.stat-value` in crimson, `.stat-label` in muted uppercase.
- `.work-card` — Dark bordered project card with outline-stroke work number and `.work-tags`.
- `.work-visual` — 16:10 visual placeholder with red top-left bracket and gradient overlay.
- `.service-list` / `.service-item` — Borderline list with red dot prefix.
- `.pull-quote` — All-caps Barlow Condensed bold quote on full-crimson bg with `.attr` attribution.
- `.process-list` / `.process-item` — Numbered row list with step number + title + description.
- `.bg-red` — Full crimson background section (Slide 08 testimonial).
- `.bg-glow` — Red ambient glow radial gradient (Numbers slide).
- `.bg-dots` — Dot-grid background texture via `::before` pseudo-element.
- `.corner-mark` — Decorative L-bracket corners in crimson (Cover and CTA slides).
- `.eyebrow` — All-caps micro label with `0.26em` letter-spacing.
- `.tag` / `.tag.dark` — Minimal bordered pill for project categorization.
- `.red-bar` — 4px left vertical accent stripe.
- `.divider-red` — Short 40×2px crimson divider bar.
- `.r` — Inline crimson text accent class.
- `.btn-primary` / `.btn-outline` — CTA button variants.

**Quick customization**:
```css
/* In :root {} at top of file */
--bg:           #0a0a0a;    /* Near-black canvas */
--bg-mid:       #111111;    /* Slightly lighter surface */
--red:          #C8102E;    /* Primary crimson — swap to your brand color */
--ink:          #F2F0EE;    /* Primary text on dark */
--font-display: 'Barlow Condensed', 'Arial Narrow', Impact, sans-serif;
--font-body:    'Barlow', system-ui, sans-serif;
```

---

## Common Patterns (All Templates)

### Navigation
All templates use `SlidePresentation` class with:
- **Arrow keys** ← → — previous / next slide
- **Space** / **Shift+Space** — next / previous
- **Home** / **End** — first / last slide
- **Swipe** / **scroll** — touch and trackpad support
- **Click nav dots** — jump to any slide

### Presenter Mode (v2)
Press `[P]` to open the Presenter View (fully self-contained — no external file dependency).

The Presenter View shows:
- **Current slide** large preview (left panel)
- **Next slide** preview (top-right)
- **Speaker notes** (bottom-right)
- **Elapsed timer** — click to reset; turns yellow at 20 min, red at 30 min

**Controls from the presenter window:**

| Action | Button | Keyboard |
|--------|--------|----------|
| Previous slide | ← | `ArrowLeft` |
| Next slide | → | `ArrowRight` / `Space` |
| Toggle laser pointer | 🔴 Laser | `L` |
| Toggle blackout screen | ⬛ Blackout | `B` |

**Laser pointer**: hover the mouse over the current slide preview to project a red dot onto the audience screen in real time.

**Blackout**: sends a full-screen black overlay to the audience window; click the audience screen or press `B` again to cancel.

Both windows stay in sync via the BroadcastChannel API — no server required. See `assets/demos/presenter-mode-demo.html` for the annotated integration reference.

### Adding Charts
Paste the contents of `scripts/charts.js` before `</body>`, then call:
```js
document.addEventListener('DOMContentLoaded', () => {
  // Charts are typically triggered by IntersectionObserver
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !entry.target.dataset.chartDone) {
        entry.target.dataset.chartDone = '1';
        SlideCharts.bar('#my-chart', { /* ... */ });
      }
    });
  }, { threshold: 0.4 });
  document.querySelectorAll('.slide-with-chart').forEach(s => observer.observe(s));
});
```

### Speaker Notes
Add `data-notes` to any `.slide` element:
```html
<section class="slide" data-notes="Pause here. Ask audience: who has faced this problem?">
```

Notes are displayed in the Presenter View notes panel.

### Offline / No Internet
Run `python3 scripts/inline_fonts.py template-pitch-deck.html` to produce an offline-ready version with all fonts Base64-inlined. See `scripts/inline_fonts.py` for full usage.

---

## Choosing a Template

| Scenario | Template |
|----------|----------|
| Raising a seed / Series A round | Pitch Deck |
| Speaking at a developer conference | Tech Talk |
| Monthly / quarterly business review | Quarterly Report |
| Announcing a new product or feature | Product Launch |
| Internal team update or retrospective | Quarterly Report (light colors work well) |
| Sales proposal to enterprise client | Pitch Deck (swap colors to match client brand) |
| Workshop or tutorial | Tech Talk (remove code slide, adjust steps) |
| Nonprofit / impact report | Product Launch (warm tones suit storytelling) |
| Brand narrative / company story | Claude Warmth |
| All-hands or team retrospective | Claude Warmth |
| General-purpose / doesn't fit others | Claude Warmth (safe default) |
| Design portfolio / agency pitch | ForAI White |
| Creative studio / brand presentation | ForAI White |
| Product design review | ForAI White |
| Minimal editorial style deck | ForAI White |
| Agency pitch / editorial minimalism | Pash Orange |
| Brand/studio deck with white bg + orange | Pash Orange |
| Design pitch with high-contrast identity | Pash Orange |
| Creative studio pitch with red brand identity | Hhart Red Power |
| Photography studio / visual arts presentation | Hhart Red Power |
| Red brand deck / bold manifesto keynote | Hhart Red Power |
| High-contrast dark editorial with red accent | Hhart Red Power |
| Medical / clinical research / hospital presentation | Healthcare |
| Pharma / biotech / health policy | Healthcare |
| Financial analysis / investment report / fund update | Finance |
| Trading strategy / market outlook / earnings report | Finance |
| Course intro / training workshop / school report | Education |
| Onboarding material / e-learning module | Education |

---

### 9. `template-healthcare.html` — Medical & Clinical Presentations
**Use when**: Clinical research, hospital reports, pharma presentations, health policy briefs, medical conference talks

| Property | Value |
|----------|-------|
| **Style** | Clinical Trust |
| **Colors** | Arctic white `#f0f9ff` + teal `#0891b2` + navy `#0c4a6e` |
| **Fonts** | Inter (body) + Source Serif 4 (headings — readable at small sizes) |
| **Slide count** | 9 slides |
| **Mood** | Calm / Credible / Evidence-driven |

**Slide structure**:
1. **Cover** — Study/report title, institution, presenter, date
2. **Background** — Clinical context and unmet need
3. **Objectives** — Primary and secondary endpoints (`endpoint-list`)
4. **Methodology** — Study design with patient flow diagram placeholder
5. **Results** — Key findings with data tables and significance stars (`results-table`)
6. **Safety Profile** — Adverse event summary (`ae-grid`)
7. **Discussion** — Interpretation and limitations two-column
8. **Conclusions** — Numbered key takeaways (`conclusion-list`)
9. **References / Q&A** — Bibliography and contact

**Custom components**:
- `.endpoint-list` — Primary/secondary endpoint rows with `.primary` / `.secondary` badge prefixes.
- `.results-table` — Clinical data table with `.sig` class for p-value cells (teal highlight), `.ns` for non-significant, footnote row support.
- `.ae-grid` — 2×N adverse event card grid: event name, incidence %, severity badge.
- `.conclusion-list` — Large-numbered conclusion list; numbers rendered in teal display type.
- `.badge.primary` / `.badge.secondary` / `.badge.tertiary` — Endpoint classification pills.
- `.caution-box` — Amber warning callout for safety notices and contraindications.

**Quick customization**:
```css
/* In :root {} at top of file */
--clr-bg:      #f0f9ff;    /* Arctic white — change to #ffffff for pure white */
--clr-accent:  #0891b2;    /* Teal — swap to your institution's brand color */
--clr-navy:    #0c4a6e;    /* Deep navy for headings */
--clr-text:    #1e293b;
--clr-success: #059669;    /* Positive result */
--clr-danger:  #dc2626;    /* Safety alert */
--clr-warning: #d97706;    /* Caution */
--font-head: 'Source Serif 4', Georgia, serif;
--font-body: 'Inter', system-ui, sans-serif;
```

---

### 10. `template-finance.html` — Financial Analysis & Investment Reports
**Use when**: Investment reports, fund updates, earnings analysis, market outlook, trading strategy decks, PE/VC deal reviews

| Property | Value |
|----------|-------|
| **Style** | Bloomberg Dark |
| **Colors** | Deep charcoal `#111827` + amber `#f59e0b` + green `#10b981` / red `#ef4444` |
| **Fonts** | IBM Plex Mono (numbers/data) + IBM Plex Sans (body) |
| **Slide count** | 9 slides |
| **Mood** | Data-Dense / Authoritative / Terminal-style |

**Slide structure**:
1. **Cover** — Fund/report name, period, analyst, disclaimer line
2. **Executive Summary** — 3-column key metrics bar (`kpi-bar`) + thesis bullets
3. **Market Overview** — Macro snapshot with mini sparkline placeholders
4. **Portfolio / Position Analysis** — Holdings table (`holdings-table`) with P&L columns
5. **Performance Attribution** — Waterfall breakdown (`waterfall-chart` placeholder)
6. **Risk Metrics** — VaR, Sharpe, drawdown grid (`risk-grid`)
7. **Sector / Allocation** — Donut chart placeholder + allocation table
8. **Outlook & Positioning** — Bull/Bear scenario two-column
9. **Disclosures** — Legal boilerplate + contact

**Custom components**:
- `.kpi-bar` — Horizontal strip of 4–6 KPI cells: metric name, value, delta (green up / red down). Terminal-style borders.
- `.holdings-table` — Dense data table: ticker, name, weight, cost, price, P&L%, P&L$. Rows with `.gain` / `.loss` class for green/red row coloring.
- `.risk-grid` — 3×2 card grid for risk metrics: Sharpe, VaR, Max DD, Beta, Corr, Volatility.
- `.waterfall-bar` — CSS-only horizontal waterfall item: positive (green), negative (red), total (amber).
- `.scenario-col` — Bull/Bear/Base scenario card with color-coded header and bullet list.
- `.disclaimer` — Small-print legal text block with reduced opacity.
- `.ticker` — Monospace ticker symbol with amber color.
- `.delta-up` / `.delta-down` — Inline P&L delta spans with arrow prefix.

**Quick customization**:
```css
/* In :root {} at top of file */
--clr-bg:      #111827;    /* Dark charcoal — swap to #0f172a for deeper dark */
--clr-surface: #1f2937;    /* Card / table row background */
--clr-accent:  #f59e0b;    /* Amber — your firm's brand color */
--clr-gain:    #10b981;    /* Positive P&L */
--clr-loss:    #ef4444;    /* Negative P&L */
--clr-text:    #f9fafb;
--clr-muted:   #9ca3af;
--font-data: 'IBM Plex Mono', 'Courier New', monospace;
--font-body: 'IBM Plex Sans', system-ui, sans-serif;
```

---

### 11. `template-education.html` — Training, Workshops & Course Decks
**Use when**: Course introductions, training workshops, onboarding sessions, school/university lectures, e-learning module slides

| Property | Value |
|----------|-------|
| **Style** | Campus Bright |
| **Colors** | Sky blue `#e0f2fe` + cobalt `#0284c7` + coral `#f97316` |
| **Fonts** | Nunito (display — rounded, friendly) + Noto Sans (body — CJK-ready) |
| **Slide count** | 9 slides |
| **Mood** | Playful / Engaging / Accessible |

**Slide structure**:
1. **Cover** — Course/module name, instructor, session number
2. **Learning Objectives** — Numbered objective list (`objective-list`)
3. **Agenda** — Session roadmap with time estimates (`agenda-track`)
4. **Concept 1** — Heading + body + visual placeholder, `callout-box` for key definition
5. **Concept 2** — Two-column: explanation + example code / diagram
6. **Exercise** — Interactive task card (`exercise-card`) with step-by-step instructions
7. **Common Mistakes** — `mistake-list` with ✗ / ✓ correction pairs
8. **Summary** — Key takeaway cards (`takeaway-grid`)
9. **Resources & Next Steps** — Reading list + homework prompt

**Custom components**:
- `.objective-list` — Large-numbered learning objective rows with cobalt circle numbers.
- `.agenda-track` — Timeline-style agenda: time slot, topic, duration pill. Highlight active row with `.active` class.
- `.callout-box` — Bordered definition / key-concept box with coral left accent and label badge.
- `.exercise-card` — Coral-header card with numbered exercise steps and estimated time badge.
- `.mistake-list` — Two-column correction list: `.wrong` row (red ✗ prefix) + `.right` row (green ✓ prefix).
- `.takeaway-grid` — 2×2 or 3-column grid of `.takeaway-card` (rounded, sky-blue bg, icon area).
- `.progress-chips` — Row of session number chips to show position in course (`.done`, `.active`, `.todo`).
- `.badge.time` — Duration pill (e.g., "10 min") for agenda items and exercises.

**Quick customization**:
```css
/* In :root {} at top of file */
--clr-bg:       #e0f2fe;   /* Sky blue — swap to #ffffff for neutral bg */
--clr-accent:   #0284c7;   /* Cobalt blue — your institution color */
--clr-accent-2: #f97316;   /* Coral — activity / exercise highlight */
--clr-text:     #0f172a;
--clr-success:  #16a34a;
--clr-danger:   #dc2626;
--font-head: 'Nunito', 'Varela Round', system-ui, sans-serif;
--font-body: 'Noto Sans', 'PingFang SC', system-ui, sans-serif;
```

---

## JSON Content Schema

Each template ships with a companion `.json` file (e.g. `template-pitch-deck.json`) that defines the slide content structure. These files are used by `scripts/generate_slides.py` to generate a filled presentation from structured content — without hand-editing HTML.

### Root object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | ✓ | Deck title used in `<title>` and the first slide heading |
| `template` | string | ✓ | Template key — one of: `claude-warmth` `pitch-deck` `product-launch` `quarterly-report` `tech-talk` `forai-white` `pash-orange` `hhart-red` |
| `lang` | string | — | HTML `lang` attribute (default: `zh-CN`) |
| `slides` | array | ✓ | Ordered array of slide objects (see Slide Types below) |

### Slide Types

Every slide object must have a `type` field. All other fields are optional unless marked ✓.

---

#### `title` — Hero cover / CTA slide

| Field | Type | Description |
|-------|------|-------------|
| `title` | string ✓ | Main heading (supports `\n` for line breaks) |
| `subtitle` | string | Subtitle / supporting line |
| `eyebrow` | string | Small label above the heading (e.g. `"Series A · 2025"`) |
| `notes` | string | Speaker notes (shown in Presenter View) |

---

#### `text` — Heading + paragraph

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Section heading |
| `body` | string | Paragraph body text |
| `notes` | string | Speaker notes |

---

#### `bullets` — Heading + bulleted list

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Slide heading |
| `items` | string[] ✓ | Array of bullet strings |
| `notes` | string | Speaker notes |

---

#### `two-col` — Two-column layout

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Slide heading |
| `left` | object | `{ title, body }` — left column content |
| `right` | object | `{ title, body }` — right column content |
| `notes` | string | Speaker notes |

---

#### `stats` — Big number statistics grid

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Slide heading |
| `stats` | object[] ✓ | Array of `{ value, label, trend? }` objects. `trend`: `"up"` `"down"` `"neutral"` |
| `notes` | string | Speaker notes |

---

#### `features` — Feature cards grid

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Slide heading |
| `subtitle` | string | Supporting sub-heading |
| `items` | object[] ✓ | Array of `{ icon, title, desc }` objects |
| `notes` | string | Speaker notes |

---

#### `quote` — Pull quote / testimonial

| Field | Type | Description |
|-------|------|-------------|
| `quote` | string ✓ | The quote text (no surrounding `""` needed) |
| `author` | string | Attribution — `"Name · Role · Company"` |
| `notes` | string | Speaker notes |

---

#### `chart` — Data visualization

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Slide heading |
| `chart_type` | string ✓ | One of: `bar` `line` `area` `donut` `hbar` `progress` `radar` `sankey` `treemap` |
| `chart_data` | object ✓ | Passed directly to `SlideCharts.*()` — see `scripts/charts.js` for full API |
| `chart_options` | object | Optional chart config overrides (e.g. `{ "showGrid": true }`) |
| `notes` | string | Speaker notes |

---

#### `image` — Full-width image

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Optional overlay heading |
| `image_url` | string ✓ | URL or relative path to image |
| `caption` | string | Caption text below the image |
| `notes` | string | Speaker notes |

---

#### `cta` — Call to action close slide

| Field | Type | Description |
|-------|------|-------------|
| `title` | string ✓ | CTA heading |
| `subtitle` | string | Supporting line |
| `primary_cta` | string | Primary button label |
| `secondary_cta` | string | Secondary link label |
| `url` | string | URL displayed on slide |
| `offer` | string | Optional urgency line (e.g. `"Early access: first 3 months free"`) |
| `notes` | string | Speaker notes |

---

#### `divider` — Section break

| Field | Type | Description |
|-------|------|-------------|
| `label` | string ✓ | Large section label text |
| `notes` | string | Speaker notes |

---

### Common fields (any slide type)

| Field | Type | Description |
|-------|------|-------------|
| `bg` | string | Override the auto-resolved background CSS class (e.g. `"bg-dark"`, `"slide-cover"`). Bypasses template rhythm logic. Use only when you need a non-default background. |
| `notes` | string | Speaker notes string. Rendered in the Presenter View notes panel. Supports plain text; avoid HTML. |

---

### Minimal valid example

```json
{
  "title": "My Deck",
  "template": "claude-warmth",
  "lang": "zh-CN",
  "slides": [
    {
      "type": "title",
      "title": "Hello World",
      "subtitle": "A minimal test deck",
      "notes": "Wave at the audience."
    },
    {
      "type": "bullets",
      "title": "Key Points",
      "items": ["Point one", "Point two", "Point three"]
    },
    {
      "type": "quote",
      "quote": "The best way to predict the future is to build it.",
      "author": "Alan Kay"
    }
  ]
}
```

Run with:
```bash
python3 scripts/generate_slides.py my-deck.json --output my-deck.html --open
```
