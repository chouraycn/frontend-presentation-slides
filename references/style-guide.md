# Frontend Slides Style Guide

## Mood → Style Mapping

| Mood | Color Palette | Typography | Animation Style | Background | Template |
|------|--------------|------------|-----------------|------------|----------|
| Impressive / Premium | Deep navy + gold | Serif heading + clean sans | Slow fade, large scale | Dark gradient | `template-pitch-deck.html` |
| Exciting / Electric | Vibrant gradient (purple→pink) | Bold condensed + geometric | Spring bounce, slide-in | Noise texture / particles | `template-tech-talk.html` |
| Calm / Focused | Soft neutrals (cream, slate) | Minimal sans-serif | Subtle fade-up | Solid color or subtle grid | `template-quarterly-report.html` |
| Inspiring / Dramatic | Warm tones (amber, terracotta) | Humanist serif + rounded sans | Gentle bloom, stagger | Organic texture | `template-product-launch.html` |
| Inspiring / Warm | Cream + terracotta-orange | Serif + humanist sans | Ease-out stagger | Warm orbs + dark contrast sections | `template-claude-warmth.html` |
| Calm / Editorial | Pure white + ink black | Editorial serif (italic) + geometric sans | Clean fade-up | Dot-grid / hairline texture | `template-forai-white.html` |
| Confident / Agency | White + pure orange `#FF5C00` | Bebas Neue (display) + DM Serif Display + DM Sans | Bold slide-in, scale-up | Dot-grid + asymmetric layout | `template-pash-orange.html` |
| Bold / Studio / Red | Near-black `#0a0a0a` + crimson red `#C8102E` | Barlow Condensed 800 (display) + Barlow 300/400 (body) | Hard cut, scale-up, slide-in | Full-bleed red accent sections + corner mark | `template-hhart-red.html` |

---

## CSS Animation Patterns

### Fade Up (most common, use as default)
```css
[data-animate] {
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}
[data-animate].visible {
  opacity: 1;
  transform: translateY(0);
}
```

### Scale In
```css
[data-animate="scale"] {
  opacity: 0;
  transform: scale(0.85);
  transition: opacity 0.5s ease, transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}
[data-animate="scale"].visible {
  opacity: 1;
  transform: scale(1);
}
```

### Slide From Left
```css
[data-animate="slide-left"] {
  opacity: 0;
  transform: translateX(-40px);
  transition: opacity 0.5s ease, transform 0.5s ease;
}
[data-animate="slide-left"].visible {
  opacity: 1;
  transform: translateX(0);
}
```

### Blur In
```css
[data-animate="blur"] {
  opacity: 0;
  filter: blur(8px);
  transition: opacity 0.7s ease, filter 0.7s ease;
}
[data-animate="blur"].visible {
  opacity: 1;
  filter: blur(0);
}
```

### Stagger children (apply to parent)
```js
// In Intersection Observer callback:
entry.target.querySelectorAll('[data-animate]').forEach((el, i) => {
  setTimeout(() => el.classList.add('visible'), i * 120);
});
```

---

## Background Patterns

### Gradient Mesh
```css
background: radial-gradient(ellipse at 20% 50%, #1a1a2e 0%, transparent 50%),
            radial-gradient(ellipse at 80% 20%, #16213e 0%, transparent 50%),
            radial-gradient(ellipse at 50% 80%, #0f3460 0%, transparent 50%),
            #0a0a1a;
```

### Noise Texture (via CSS)
```css
background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
```

### Subtle Grid
```css
background-image: linear-gradient(rgba(255,255,255,.03) 1px, transparent 1px),
                  linear-gradient(90deg, rgba(255,255,255,.03) 1px, transparent 1px);
background-size: 60px 60px;
```

### Dot Grid
```css
background-image: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
background-size: 30px 30px;
```

---

## Font Pairings (Google Fonts via CDN)

| Style | Heading Font | Body Font | Import | Used in template |
|-------|-------------|-----------|--------|-----------------|
| Corporate | Playfair Display | Inter | Both on Google Fonts | `template-pitch-deck.html` |
| Tech / Modern | Space Grotesk | DM Sans | Both on Google Fonts | `template-tech-talk.html` |
| Bold / Impact | Bebas Neue | Nunito | Both on Google Fonts | — |
| Elegant | Cormorant Garamond | Lato | Both on Google Fonts | — |
| Minimal | Plus Jakarta Sans | Plus Jakarta Sans | Single family | `template-quarterly-report.html` |
| Warm Serif | Cormorant Garamond (italic) | Nunito | Both on Google Fonts | `template-product-launch.html` |
| Brand Warmth | Lora | Source Sans Pro | Both on Google Fonts | `template-claude-warmth.html` |
| Editorial Minimal | DM Serif Display (italic) | DM Sans | Both on Google Fonts | `template-forai-white.html` |
| Chinese-friendly | Noto Serif SC | Noto Sans SC | Both on Google Fonts | — |

Import pattern:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
```

For Chinese presentations, always add Noto Sans SC as fallback:
```css
font-family: 'Space Grotesk', 'Noto Sans SC', sans-serif;
```

---

## Color Palette Recipes

### Dark Elegance (Impressive)
```css
:root {
  --bg: #0d0d1a;
  --surface: #1a1a2e;
  --accent: #c9a84c;
  --text-primary: #f0ece0;
  --text-secondary: #9b96a8;
}
```

### Vibrant Energy (Exciting)
```css
:root {
  --bg: #0f0f23;
  --surface: #1a0533;
  --accent: #7c3aed;
  --accent2: #ec4899;
  --text-primary: #ffffff;
  --text-secondary: #c4b5fd;
}
```

### Clean Focus (Calm)
```css
:root {
  --bg: #fafaf8;
  --surface: #f0ede6;
  --accent: #2563eb;
  --text-primary: #1c1917;
  --text-secondary: #78716c;
}
```

### Warm Inspire (Inspiring)
```css
:root {
  --bg: #1a0f00;
  --surface: #2d1b00;
  --accent: #f59e0b;
  --accent2: #ef4444;
  --text-primary: #fef3c7;
  --text-secondary: #d97706;
}
```

### Claude Warmth (Brand-inspired · Light)
Inspired by claude.com — warm cream backgrounds, terracotta-orange accents, mixed light/dark sections.

```css
:root {
  /* Backgrounds */
  --bg:            #F6F0E8;   /* warm cream page base */
  --bg-card:       #FDFAF5;   /* near-white card surface */
  --bg-dark:       #1C1917;   /* rich brown-black for contrast sections */
  --bg-mid:        #EDE5D8;   /* warm sand secondary surface */

  /* Brand */
  --accent:        #DA7756;   /* Claude terracotta-orange (primary CTA, highlights) */
  --accent2:       #C9A96E;   /* warm gold (secondary accent) */
  --accent3:       #7A9E7E;   /* muted sage green (positive/success) */
  --accent4:       #7B6EA0;   /* soft plum (variety accent) */

  /* Typography */
  --text-primary:  #1C1917;
  --text-secondary:#57534E;
  --text-tertiary: #A8A29E;
  --surface:       #FDFAF5;   /* alias for cards on light bg */
}
```

Preview file: `assets/style-previews/style-preview-claude-warmth.html`

Key characteristics:
- Hero slide: cream bg + large orbs (blurred radial gradients) + concentric circle geometry
- Feature slide: near-black (#1C1917) background with frosted-glass cards — strong contrast
- Stats slide: white card surface with warm shadow system
- Quote/Transition slide: dark background + oversized quotation mark — demonstrates the light→dark→light→dark narrative rhythm that characterizes Claude Warmth decks
- Typography: Lora (headings, serif) + Source Sans Pro (body); −0.03em letter-spacing on headings, `clamp()` everywhere
- Animations: `cubic-bezier(0.16, 1, 0.3, 1)` ease-out + spring variant for scale
- Suitable moods: Calm / Focused, Inspiring / Warm, brand storytelling, all-hands

**Template file:** `assets/templates/template-claude-warmth.html` — 8-slide production-ready deck.
Slide structure: Cover → Opening Story → Values → Timeline → Impact Stats → People Grid → What's Next → Close.
Key components: `.pull-quote`, `.value-card`, `.timeline`, `.impact-stat`, `.people-grid`.

---

### ForAI White (Editorial Minimalism · Light)
Inspired by [forai.design](https://forai.design/) — pure white canvas, editorial typography, generous whitespace, dot-grid textures.

```css
:root {
  /* Backgrounds */
  --bg:           #ffffff;    /* pure white page base */
  --bg-muted:     #f7f7f5;    /* barely-there off-white surface */
  --bg-invert:    #0a0a0a;    /* ink black for inverted slides */

  /* Ink */
  --ink:          #0a0a0a;    /* primary text + strokes */
  --ink-mid:      #4a4a4a;    /* secondary text */
  --ink-light:    #9a9a9a;    /* tertiary / labels */
  --ink-hairline: #e8e8e8;    /* borders and dividers */

  /* Optional accent colors (off by default) */
  --accent-warm:  #e85d26;    /* warm orange — use sparingly */
  --accent-cool:  #1a56db;    /* cobalt blue — use sparingly */

  /* Typography */
  --font-head: 'DM Serif Display', Georgia, serif;
  --font-body: 'DM Sans', system-ui, sans-serif;

  /* Spacing scale */
  --gap-xs: 8px;
  --gap-sm: 16px;
  --gap-md: 32px;
  --gap-lg: 56px;
  --gap-xl: 96px;
}
```

Key characteristics:
- Background: `#ffffff` with subtle dot-grid or line-grid texture overlays (via `::before` pseudo-element)
- Typography: DM Serif Display italic for editorial punch; DM Sans for clean body copy
- Signature detail: dot-grid background (`radial-gradient` 28px spacing) on hero and CTA slides
- Inverted slide: full `#0a0a0a` background with white text — one per deck for dramatic contrast
- Borders over fills: components use 1px `--ink-hairline` borders rather than color blocks
- Numbering system: `01 / 09` style zero-padded counters throughout
- Corner marks: `::after` L-bracket decoration on selected slides (editorial magazine feel)
- Animations: clean `fadeUp` (24px translateY) and `slideLeft` — no spring/bounce
- Suitable moods: Calm / Focused, design-forward, editorial, agency/studio presentations

**Template file:** `assets/templates/template-forai-white.html` — 9-slide production-ready deck.
Slide structure: Cover → About → Numbers → Work 01 → Work 02 → Testimonial (inverted) → Process → Clients → CTA.
Key components: `.work-item`, `.stat-block`, `.process-list`, `.testimonial-block`, `.client-grid`, `.tag`, `.eyebrow`, `.bg-dots`, `.bg-grid`, `.corner-mark`, `.btn-primary`, `.btn-outline`, `.btn-arrow`.

---

### Pash Orange (Agency Bold · Dark)
Inspired by high-energy agency and brand identity decks — near-black canvas with pure orange `#FF5C00` as the power accent.

Key characteristics:
- Background: near-black `#0a0a0a` with subtle dot-grid texture
- Typography: Bebas Neue for display headlines (condensed, all-caps); DM Serif Display for secondary; DM Sans for body
- Signature detail: asymmetric corner-mark decorations; large-scale typographic hierarchy
- Orange invert slide: full `#FF5C00` background for CTA / highlight moments
- Animations: bold `slide-in` + `scale-up`; no soft easing — everything pops immediately
- Suitable moods: Confident / Agency, brand pitches, creative portfolio, studio work

**Template file:** `assets/templates/template-pash-orange.html`
Key components: `.stat-block`, `.stats-row`, `.btn-primary`, `.testimonial-block`, `.corner-mark`, `.bg-dots`, `.bg-black`, `.bg-mid`, `.bg-orange`.

---

### Hhart Red (Bold Editorial · Dark)
Inspired by editorial design, campaign work, and brand manifestos — near-black with full-bleed crimson red as the power accent.

```css
:root {
  /* Backgrounds */
  --bg:           #0a0a0a;    /* near-black page base */
  --bg-mid:       #161616;    /* slightly lighter surface */
  --bg-red:       #C8102E;    /* crimson red — full-bleed accent sections */

  /* Typography */
  --text-primary:   #ffffff;
  --text-secondary: rgba(255,255,255,0.65);
  --text-tertiary:  rgba(255,255,255,0.35);

  /* Accent */
  --accent:       #C8102E;    /* primary highlight, stat values, divider bars */
  --accent2:      #e8314a;    /* lighter red for gradients / hover */

  /* Font stack */
  --font-display: 'Barlow Condensed', 'Arial Narrow', Impact, sans-serif;  /* condensed bold display */
  --font-body:    'Barlow', 'Inter', system-ui, sans-serif;  /* body copy */
}
```

Key characteristics:
- Background: near-black `#0a0a0a` with minimal decoration
- Typography: Barlow Condensed 800 for ultra-bold condensed display text; Barlow 300/400 for structured body copy
- Signature detail: full-bleed crimson red sections (`bg-red`) for covers, CTAs, and quote slides; corner-mark decorations
- Red stat values: numbers rendered in `var(--accent)` for maximum punch
- Pull-quote style: large tracked text with decorative horizontal rules
- Animations: hard cut + `scale-up` — editorial snap, no gentle fades
- Suitable moods: Bold / Studio / Red, editorial, campaign launches, brand power decks, sports/action brands

**Template file:** `assets/templates/template-hhart-red.html`
Key components: `.pull-quote`, `.attr`, `.stat-block`, `.stat-row`, `.stat-value`, `.stat-label`, `.btn-primary`, `.corner-mark`, `.bg-dark`, `.bg-mid`, `.bg-red`.

---

### Hero / Title Slide
```html
<section class="slide" role="region" aria-label="Title slide">
  <div class="slide-content centered">
    <p class="eyebrow" data-animate>Category · Date</p>
    <h1 data-animate>Main Title</h1>
    <p class="subtitle" data-animate>Supporting tagline or description</p>
  </div>
</section>
```

### Two-Column
```html
<section class="slide">
  <div class="slide-content two-col">
    <div class="col-left" data-animate="slide-left">
      <h2>Left Content</h2>
    </div>
    <div class="col-right" data-animate="slide-left">
      <!-- image or stats -->
    </div>
  </div>
</section>
```

### Stat / Highlight Slide
```html
<section class="slide">
  <div class="slide-content">
    <div class="stats-grid">
      <div class="stat-item" data-animate>
        <span class="stat-number">98%</span>
        <span class="stat-label">Satisfaction Rate</span>
      </div>
      <!-- repeat -->
    </div>
  </div>
</section>
```

### List / Bullet Points
```html
<section class="slide">
  <div class="slide-content">
    <h2 data-animate>Key Points</h2>
    <ul class="feature-list">
      <li data-animate><strong>Point 1</strong> — supporting detail</li>
      <li data-animate><strong>Point 2</strong> — supporting detail</li>
    </ul>
  </div>
</section>
```

---

## Navigation Chrome

### Progress Bar
```html
<div class="progress-bar" id="progressBar" role="progressbar" aria-valuemin="0" aria-valuemax="100"></div>
```
```css
.progress-bar {
  position: fixed; top: 0; left: 0; height: 3px;
  background: var(--accent); width: 0%;
  transition: width 0.3s ease; z-index: 100;
}
```

### Navigation Dots
```html
<nav class="nav-dots" aria-label="Slide navigation"></nav>
```
```js
// Generate dots from slide count
const nav = document.querySelector('.nav-dots');
slides.forEach((_, i) => {
  const dot = document.createElement('button');
  dot.setAttribute('aria-label', `Go to slide ${i + 1}`);
  dot.onclick = () => goToSlide(i);
  nav.appendChild(dot);
});
```

### Slide Counter
```html
<div class="slide-counter" aria-live="polite">
  <span id="currentSlide">1</span> / <span id="totalSlides">10</span>
</div>
```

---

## Optional Enhancements

### 3D Tilt on Hover (desktop only)
```js
document.querySelectorAll('.card').forEach(card => {
  card.addEventListener('mousemove', (e) => {
    const rect = card.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    card.style.transform = `perspective(600px) rotateY(${x * 12}deg) rotateX(${-y * 12}deg)`;
  });
  card.addEventListener('mouseleave', () => {
    card.style.transform = '';
  });
});
```

### Particle Background (use sparingly, only for tech/energy styles)
```js
function createParticles(container, count = 40) {
  for (let i = 0; i < count; i++) {
    const p = document.createElement('span');
    p.className = 'particle';
    p.style.cssText = `
      left: ${Math.random() * 100}%;
      top: ${Math.random() * 100}%;
      animation-delay: ${Math.random() * 4}s;
      animation-duration: ${3 + Math.random() * 4}s;
      width: ${1 + Math.random() * 2}px;
      height: ${1 + Math.random() * 2}px;
    `;
    container.appendChild(p);
  }
}
```

### Typewriter Effect (for hero titles)
```js
function typewriter(el, text, speed = 60) {
  el.textContent = '';
  let i = 0;
  const timer = setInterval(() => {
    el.textContent += text[i++];
    if (i >= text.length) clearInterval(timer);
  }, speed);
}
```

---

## Data Visualization Module

Use `scripts/charts.js` to add zero-dependency, animated SVG charts to any slide.
All charts inherit CSS custom properties from `:root` for automatic theme integration.

### Setup — include charts.js inline

Copy the contents of `scripts/charts.js` into your HTML file before `</body>`:

```html
<!-- Paste contents of scripts/charts.js here -->
<script>
  /* === charts.js inline === */
  // ... (full file content)
</script>
```

Or load it externally during development (not for final single-file output):
```html
<script src="scripts/charts.js"></script>
```

---

### Chart Container CSS

Add these utility classes to your `:root` / base styles once:

```css
/* ── Chart containers ── */
.chart-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-container svg {
  max-width: 100%;
  max-height: 100%;
}

/* Chart slide layouts */
.slide-chart-full .slide-content {
  width: 80%;
  max-width: 700px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.slide-chart-split .slide-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: center;
  width: 88%;
  max-width: 1000px;
}

.slide-chart-trio .slide-content {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  align-items: start;
  width: 92%;
  max-width: 1100px;
}
```

---

### Layout Pattern: Full-Width Chart Slide

Best for: single bar/line chart as the main message.

```html
<section class="slide slide-chart-full" role="region" aria-label="Revenue chart slide">
  <div class="slide-content">
    <h2 data-animate>Quarterly Revenue Growth</h2>
    <p class="subtitle" data-animate>Year-over-year comparison across all product lines</p>
    <div id="revenueChart" class="chart-container" style="height: 300px;" data-animate></div>
  </div>
</section>

<script>
  // Runs after SlidePresentation initializes
  SlideCharts.bar('#revenueChart', {
    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
    datasets: [
      { label: '2024', values: [42, 58, 55, 71], color: 'var(--accent)' },
      { label: '2025', values: [55, 72, 68, 91], color: 'var(--accent2)' },
    ]
  }, { animDuration: 700, showGrid: true });
</script>
```

---

### Layout Pattern: Text + Chart Split

Best for: pairing a key insight with supporting data.

```html
<section class="slide slide-chart-split" role="region" aria-label="Market share slide">
  <div class="slide-content">
    <!-- Left: narrative -->
    <div class="col-text">
      <p class="eyebrow" data-animate>Market Position</p>
      <h2 data-animate>We hold <span style="color:var(--accent)">34%</span> of the market</h2>
      <p data-animate>Up from 21% two years ago — the fastest growth in our category.</p>
    </div>
    <!-- Right: chart -->
    <div id="marketDonut" class="chart-container" style="height: 280px;" data-animate></div>
  </div>
</section>

<script>
  SlideCharts.donut('#marketDonut', {
    segments: [
      { label: 'Us',         value: 34 },
      { label: 'Competitor A', value: 28 },
      { label: 'Competitor B', value: 21 },
      { label: 'Others',     value: 17 },
    ]
  }, { centerValue: '34%', centerLabel: 'Market Share', animDuration: 800 });
</script>
```

---

### Layout Pattern: Three KPI Charts

Best for: dashboard-style slides comparing three metrics side by side.

```html
<section class="slide slide-chart-trio" role="region" aria-label="KPI overview slide">
  <div class="slide-content">
    <div class="kpi-card" data-animate>
      <p class="kpi-label">User Retention</p>
      <div id="kpiProgress1" style="width:100%;"></div>
    </div>
    <div class="kpi-card" data-animate>
      <p class="kpi-label">NPS Score</p>
      <div id="kpiProgress2" style="width:100%;"></div>
    </div>
    <div class="kpi-card" data-animate>
      <p class="kpi-label">Conversion Rate</p>
      <div id="kpiProgress3" style="width:100%;"></div>
    </div>
  </div>
</section>

<style>
.kpi-card {
  background: var(--surface);
  border-radius: 12px;
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.kpi-label {
  color: var(--text-secondary);
  font-size: clamp(0.75rem, 1.5vw, 0.875rem);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin: 0;
}
</style>

<script>
  SlideCharts.progress('#kpiProgress1', {
    items: [{ label: '30-day', value: 82, sublabel: '+4% vs last month' }]
  }, { barHeight: 10, showPercentage: true });

  SlideCharts.progress('#kpiProgress2', {
    items: [{ label: 'Score', value: 71, max: 100 }]
  }, { barHeight: 10 });

  SlideCharts.progress('#kpiProgress3', {
    items: [{ label: 'Trial → Paid', value: 12.4, max: 100 }]
  }, { barHeight: 10 });
</script>
```

---

### Layout Pattern: Ranking / Leaderboard

Best for: competitor comparison, feature adoption, or top-N lists.

```html
<section class="slide" role="region" aria-label="Ranking slide">
  <div class="slide-content" style="width: 72%; max-width: 680px;">
    <h2 data-animate>Top Channels by Revenue</h2>
    <div id="channelRank" style="width:100%; margin-top: 24px;" data-animate></div>
  </div>
</section>

<script>
  SlideCharts.horizontalBar('#channelRank', {
    items: [
      { label: 'Direct',   value: 480000 },
      { label: 'Organic',  value: 310000 },
      { label: 'Referral', value: 224000 },
      { label: 'Paid',     value: 168000 },
      { label: 'Social',   value: 94000  },
    ]
  }, { showRank: true, barHeight: 30, animDuration: 600 });
</script>
```

---

### Layout Pattern: Trend Line Slide

Best for: showing growth over time, before/after, or projections.

```html
<section class="slide" role="region" aria-label="Growth trend slide">
  <div class="slide-content" style="width: 80%; max-width: 720px; display:flex; flex-direction:column; gap:16px;">
    <h2 data-animate>ARR Growth Trajectory</h2>
    <div id="arrTrend" class="chart-container" style="height: 280px;" data-animate></div>
  </div>
</section>

<script>
  SlideCharts.area('#arrTrend', {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
    datasets: [{
      label: 'ARR ($M)',
      values: [1.2, 1.8, 2.1, 2.9, 3.4, 4.1, 4.8, 5.9],
    }]
  }, { smooth: true, dots: true, animDuration: 900 });
</script>
```

---

### Layout Pattern: Multi-Metric Progress (Skills / Specs)

Best for: team capabilities, product feature completion, or survey results.

```html
<section class="slide" role="region" aria-label="Capabilities slide">
  <div class="slide-content" style="width: 72%; max-width: 620px; display:flex; flex-direction:column; gap: 20px;">
    <h2 data-animate>Our Technical Stack</h2>
    <div id="skillBars" style="width:100%;" data-animate></div>
  </div>
</section>

<script>
  SlideCharts.progress('#skillBars', {
    items: [
      { label: 'AI / ML',        value: 92, color: 'var(--accent)',  sublabel: 'Core competency' },
      { label: 'Cloud Infra',    value: 85, color: 'var(--accent2)', sublabel: 'AWS + GCP' },
      { label: 'Data Platform',  value: 78, sublabel: 'Real-time pipeline' },
      { label: 'Mobile',         value: 64, sublabel: 'iOS + Android' },
      { label: 'Blockchain',     value: 41, sublabel: 'Exploring' },
    ]
  }, { barHeight: 14, animDuration: 700 });
</script>
```

---

### Triggering Charts on Slide Enter

Charts render immediately when the page loads. To delay rendering until a slide
is scrolled into view (for performance and dramatic effect), use the
Intersection Observer pattern:

```js
// Initialize charts lazily when their slide enters viewport
const chartObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    const slide = entry.target;

    // Bar chart example
    const barEl = slide.querySelector('[data-chart="bar"]');
    if (barEl && !barEl.dataset.rendered) {
      barEl.dataset.rendered = 'true';
      SlideCharts.bar(barEl, JSON.parse(barEl.dataset.chartData), JSON.parse(barEl.dataset.chartOptions || '{}'));
    }

    // Donut chart example
    const donutEl = slide.querySelector('[data-chart="donut"]');
    if (donutEl && !donutEl.dataset.rendered) {
      donutEl.dataset.rendered = 'true';
      SlideCharts.donut(donutEl, JSON.parse(donutEl.dataset.chartData));
    }
  });
}, { threshold: 0.4 });

document.querySelectorAll('.slide').forEach(s => chartObserver.observe(s));
```

Embed chart data as JSON in `data-chart-data` attributes for cleaner markup:

```html
<div
  data-chart="bar"
  data-chart-data='{"labels":["A","B","C"],"datasets":[{"label":"X","values":[10,20,15]}]}'
  data-chart-options='{"animDuration":600}'
  class="chart-container"
  style="height:260px;"
></div>
```

---

### Chart + Theme Compatibility

All chart colors use CSS custom properties. They automatically adapt to any theme:

| CSS Variable | Role in Charts |
|---|---|
| `--accent` | Primary dataset / fill color |
| `--accent2` | Secondary dataset color |
| `--chart3` – `--chart6` | Additional datasets (optional, defaults provided) |
| `--text-primary` | Axis labels, titles |
| `--text-secondary` | Grid lines, value labels, legend text |
| `--surface` | Bar track background, card fills |
| `--bg` | Donut center fill |

To add chart-specific colors to any theme palette:

```css
:root {
  /* existing theme vars ... */
  --chart3: #10b981;  /* emerald */
  --chart4: #f59e0b;  /* amber */
  --chart5: #3b82f6;  /* blue */
  --chart6: #ef4444;  /* red */
}
```

---

### Layout Pattern: Radar / Spider Chart

Best for: multi-dimensional comparisons — competitive analysis, skill matrices, product attributes.

```html
<section class="slide" role="region" aria-label="Competitive analysis slide">
  <div class="slide-content" style="width:80%;max-width:800px;display:flex;flex-direction:column;gap:16px;">
    <h2 data-animate>How We Compare</h2>
    <p class="subtitle" data-animate>Across five key product dimensions</p>
    <div id="radarChart" class="chart-container" style="height:360px;" data-animate></div>
  </div>
</section>

<script>
  SlideCharts.radar('#radarChart', {
    axes: ['Performance', 'Reliability', 'Cost', 'Support', 'Scalability'],
    datasets: [
      { label: 'Our Product', data: [90, 85, 70, 95, 80], color: 'var(--accent)' },
      { label: 'Competitor A', data: [70, 90, 85, 60, 75], color: 'var(--accent2)' }
    ],
    max: 100, levels: 5, filled: true, showDots: true, showLegend: true, animDuration: 900
  });
</script>
```

**Radar + Text Split** — chart on the right, narrative on the left:

```html
<section class="slide slide-chart-split" role="region">
  <div class="slide-content">
    <div class="col-text">
      <p class="eyebrow" data-animate>Team Capabilities</p>
      <h2 data-animate>Full-stack <span style="color:var(--accent)">depth</span> across every layer</h2>
      <ul class="feature-list">
        <li data-animate>Backend: distributed systems at scale</li>
        <li data-animate>Frontend: design-systems thinking</li>
      </ul>
    </div>
    <div id="teamRadar" class="chart-container" style="height:300px;" data-animate></div>
  </div>
</section>
```

**Design tips for radar charts**:
- Keep axis count to 5–8. Below 4 it's a polygon; above 8 it's hard to read.
- Use `filled: true` for single-dataset (area feel); for 3+ datasets consider `filled: false` to avoid color muddle.
- Radar works best on dark backgrounds — the filled polygons pop against `--bg`.
- On light themes (Clean Focus), use low-opacity fills: `color: 'rgba(37, 99, 235, 0.2)'`.

---

## Keyboard Shortcuts Reference

| Key | Action |
|-----|--------|
| `ArrowRight` / `ArrowDown` / `Space` | Next slide |
| `ArrowLeft` / `ArrowUp` / `Shift+Space` | Previous slide |
| `Home` | First slide |
| `End` | Last slide |
| `F` | Toggle fullscreen |
| `Escape` | Exit fullscreen |
