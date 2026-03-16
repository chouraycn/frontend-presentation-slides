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
| `template-pitch-deck.html` | `style-preview-a.html` | Dark Elegance | Deep navy + gold | Impressive / Premium |
| `template-tech-talk.html` | `style-preview-b.html` | Vibrant Energy | Purple-black + pink/violet | Exciting / Electric |
| `template-quarterly-report.html` | `style-preview-c.html` | Clean Minimal | Off-white + blue | Calm / Focused |
| `template-claude-warmth.html` | `style-preview-claude.html` | Claude Warmth | Cream + terracotta | Inspiring / Warm |
| `template-product-launch.html` | `style-preview-product-launch.html` | Warm Inspire | Dark amber + orange | Bold / Dramatic |
| `template-forai-white.html` | `style-preview-forai-white.html` | ForAI White | Pure white + ink black | Editorial / Minimal |
| `template-pash-orange.html` | `style-preview-pash-orange.html` | Pash Orange | White + pure orange `#FF5C00` | Confident / Agency |
| `template-hhart-red.html` | `style-preview-hhart-red.html` | Hhart Red Power | Near-black + crimson `#C8102E` | Bold / Studio / Red Brand |

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
