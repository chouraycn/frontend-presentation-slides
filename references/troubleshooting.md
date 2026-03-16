# Frontend Slides — Troubleshooting Guide

## Common Issues & Solutions

---

### 1. Fonts Not Loading

**Symptoms:** Text falls back to system fonts; layout looks broken.

**Causes & Fixes:**

| Cause | Fix |
|-------|-----|
| No internet connection | Add system font fallbacks: `font-family: 'Space Grotesk', -apple-system, sans-serif;` |
| Typo in Google Fonts URL | Double-check the import URL; copy directly from fonts.google.com |
| Font name mismatch | Ensure CSS `font-family` exactly matches the loaded family name |
| Font not preloaded | Add `<link rel="preconnect" href="https://fonts.googleapis.com">` before the stylesheet |

**Quick fix — embed a web-safe fallback stack:**
```css
--font-heading: 'Playfair Display', Georgia, 'Times New Roman', serif;
--font-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

**ForAI White specific fallbacks:**
```css
--font-head: 'DM Serif Display', Georgia, serif;
--font-body: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
```

**Claude Warmth specific fallbacks:**
```css
--font-head: 'Lora', Georgia, 'Times New Roman', serif;
--font-body: 'Source Sans Pro', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

---

### 2. Animations Not Triggering

**Symptoms:** Elements stay invisible (opacity: 0) and never animate in.

**Diagnosis checklist:**
1. Is the Intersection Observer correctly observing `.slide` elements?
2. Does the callback add `.visible` to `[data-animate]` children?
3. Is the threshold too high (try `0.1` instead of `0.5`)?
4. Are elements hidden because the parent has `overflow: hidden` clipping the observer?

**Fix:**
```js
// Correct observer setup
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.querySelectorAll('[data-animate]').forEach((el, i) => {
        setTimeout(() => el.classList.add('visible'), i * 120);
      });
    }
  });
}, { threshold: 0.2 }); // Lower threshold

document.querySelectorAll('.slide').forEach(s => observer.observe(s));
```

**Check CSS:** Make sure `.visible` classes are defined for ALL `data-animate` values used:
```css
/* Default */
[data-animate].visible { opacity: 1; transform: translateY(0); }

/* Scale variant */
[data-animate="scale"].visible { opacity: 1; transform: scale(1); }
```

---

### 3. Scroll Snap Not Snapping Correctly

**Symptoms:** Slides don't snap cleanly; partial slides visible; can scroll past slide boundaries.

**Critical rules:**
```css
/* Container — MUST have these exact properties */
.slides-container {
  height: 100vh;
  overflow-y: scroll;
  scroll-snap-type: y mandatory;
  scroll-behavior: smooth;
}

/* Each slide — MUST have these */
.slide {
  height: 100vh;      /* not min-height */
  scroll-snap-align: start;
  overflow: hidden;   /* CRITICAL: prevents content overflow breaking snap */
  flex-shrink: 0;     /* Add this if using flex container */
}
```

**Body/HTML:**
```css
html, body {
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden; /* Prevent double scrollbars */
}
```

---

### 4. Content Overflow (Text/Images Spilling Outside Slide)

**Symptoms:** Content extends beyond the visible slide area.

**Prevention rules:**
- All font sizes must use `clamp()`: `font-size: clamp(1rem, 2.5vw, 1.5rem);`
- Images: `max-height: 45vh; max-width: 80%; object-fit: contain;`
- Long text blocks: `max-width: 70ch;`
- Verify layout at 1280×720 viewport

**Quick audit:**
```js
// Run in browser console to find overflowing elements
document.querySelectorAll('*').forEach(el => {
  if (el.offsetHeight > el.parentElement?.offsetHeight) {
    console.warn('Overflow detected:', el);
  }
});
```

---

### 5. Mobile Compatibility Issues

**Symptoms:** Layout broken on phones; touch navigation not working; animations janky.

**Mobile-specific fixes:**
```css
/* Disable heavy animations on mobile */
@media (max-width: 768px) {
  .particle, .bg-animation { display: none; }
  [data-animate] { transition-duration: 0.3s; }
}

/* Fix iOS scroll snap */
.slides-container {
  -webkit-overflow-scrolling: touch;
}

/* Fix iOS viewport height (accounts for Safari toolbar) */
.slide {
  height: 100svh; /* svh = Small Viewport Height */
  min-height: -webkit-fill-available;
}
```

**Touch events — minimum implementation:**
```js
let touchStartY = 0;
container.addEventListener('touchstart', e => touchStartY = e.touches[0].clientY, { passive: true });
container.addEventListener('touchend', e => {
  const delta = touchStartY - e.changedTouches[0].clientY;
  if (Math.abs(delta) > 50) delta > 0 ? goToSlide(current + 1) : goToSlide(current - 1);
});
```

---

### 6. Keyboard Navigation Not Working

**Symptoms:** Arrow keys don't change slides; focus not managed.

**Fix — complete keyboard handler:**
```js
document.addEventListener('keydown', (e) => {
  const actions = {
    ArrowRight: () => goToSlide(current + 1),
    ArrowDown:  () => goToSlide(current + 1),
    ArrowLeft:  () => goToSlide(current - 1),
    ArrowUp:    () => goToSlide(current - 1),
    ' ':        () => goToSlide(current + 1),
    Home:       () => goToSlide(0),
    End:        () => goToSlide(slides.length - 1),
  };
  if (actions[e.key]) {
    e.preventDefault();
    actions[e.key]();
  }
});
```

---

### 7. Performance Issues (Janky Animations)

**Symptoms:** Animations stutter; slide transitions lag.

**Rules:**
- Only animate `opacity` and `transform` — never `width`, `height`, `top`, `left`, `margin`
- Add `will-change: transform, opacity;` to elements that animate
- Disable particle effects on mobile (see #5)
- Use `transform: translateZ(0)` to promote layers for GPU rendering

```css
.slide {
  transform: translateZ(0); /* Force GPU layer */
}

[data-animate] {
  will-change: opacity, transform;
}
```

---

### 8. PPT Extraction Failures

**Symptoms:** `extract_pptx.py` errors or produces incomplete output.

| Error | Fix |
|-------|-----|
| `python-pptx` not installed | Run: `pip3 install python-pptx Pillow` |
| File not found | Check the path — use absolute path if relative fails |
| Password-protected PPT | Remove password in PowerPoint first |
| Corrupted PPTX | Try opening and re-saving in PowerPoint/LibreOffice |
| Images not extracted | Ensure Pillow is installed alongside python-pptx |

**Verify installation:**
```bash
python3 -c "import pptx; print('python-pptx OK')"
python3 -c "from PIL import Image; print('Pillow OK')"
```

---

### 9. Accessibility Issues

**Missing ARIA / semantic structure — checklist:**
```html
<!-- Required on every slide -->
<section class="slide" 
  role="region" 
  aria-label="Slide 1: Introduction"
  aria-roledescription="slide">

<!-- Active slide marker -->
<button class="dot" aria-current="true">...</button>

<!-- Reduced motion -->
<style>
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
```

---

### 10. Chinese Text Rendering Issues

**Symptoms:** Chinese characters display as boxes or fall back to ugly fonts.

**Fix:**
```html
<!-- Add to <head> — load Chinese font -->
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
```

```css
/* Always include SC fallbacks */
:root {
  --font-heading: 'Space Grotesk', 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  --font-body: 'DM Sans', 'Noto Sans SC', 'PingFang SC', sans-serif;
}

/* Improve CJK line spacing */
.slide { line-height: 1.8; }
h1, h2, h3 { line-height: 1.4; }
```

---

### 11. ForAI White — Dot-Grid Texture Not Visible

**Symptoms:** The `.bg-dots` or `.bg-grid` texture is invisible or overpowers the content.

**Cause:** The `::before` pseudo-element needs a low opacity and must not intercept pointer events.

**Fix:**
```css
.bg-dots::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle, rgba(0,0,0,0.08) 1px, transparent 1px);
  background-size: 28px 28px;
  pointer-events: none; /* CRITICAL: prevents interaction blocking */
  z-index: 0;
}

/* Ensure slide content sits above the texture */
.bg-dots .slide-content {
  position: relative;
  z-index: 1;
}
```

Adjust opacity from `0.08` (subtle) to `0.04` (barely visible) or `0.14` (prominent) to taste.

---

### 12. ForAI White — Inverted Slide Text Hard to Read

**Symptoms:** On the `#0a0a0a` background slide, body text appears grey or washed out instead of white.

**Fix:** Ensure inverted slides override the ink variable:
```css
.slide-inverted {
  background: var(--bg-invert, #0a0a0a);
  color: #ffffff;
}

.slide-inverted h1,
.slide-inverted h2,
.slide-inverted p,
.slide-inverted .eyebrow {
  color: #ffffff;
}

/* Hairline borders need to lighten on dark bg */
.slide-inverted .testimonial-block {
  border-left-color: rgba(255, 255, 255, 0.4);
}
```

---

### 13. Claude Warmth — Light/Dark Rhythm Broken

**Symptoms:** The deck loses the alternating cream/dark visual rhythm; consecutive slides share the same background color.

**Expected pattern:** Cover (cream) → Story (cream) → Values (cream) → Journey (cream) → Impact (dark) → Team (cream) → Next (cream) → Close (dark or cream)

**Fix:** Each dark slide must explicitly set `background` and override text variables:
```css
.slide-dark {
  background: var(--bg-dark, #1C1917);
}

.slide-dark h1, .slide-dark h2, .slide-dark h3 {
  color: var(--text-on-dark, #F6F0E8);
}

.slide-dark p, .slide-dark li {
  color: var(--text-on-dark-secondary, #A8A29E);
}
```

Make sure the `:root` defines both `--bg-dark` and `--bg` (the cream base), and that each `.slide` applies the correct class.

---

### 14. Template Quick-Start — Wrong Components Used

**Symptoms:** Copied a component from another template (e.g., `.big-stat` from Pitch Deck) into ForAI White — it looks visually inconsistent.

**Rule:** Each template has its own component set. Do not mix components across templates without restyling.

| Template | Key exclusive components |
|----------|--------------------------|
| Pitch Deck | `.big-stat`, `.team-grid`, `.accent` |
| Tech Talk | `pre.code-block`, `.bench-table`, `.steps-list` |
| Quarterly Report | `.okr-list`, `.metrics-grid`, `.badge`, `.risk-table` |
| Product Launch | `.hero-quote`, `.pricing-grid`, `.features-grid` |
| Claude Warmth | `.pull-quote`, `.timeline`, `.impact-stat`, `.people-grid` |
| ForAI White | `.work-item`, `.stat-block`, `.process-list`, `.client-grid`, `.eyebrow`, `.bg-dots`, `.corner-mark` |

When adapting a component to a new template, strip its original color/font variables and replace with the target template's `:root` variables.

---

### 15. Pash Orange — Orange Invert Slide Too Harsh / Text Unreadable

**Symptoms:** On the `.bg-orange` background (cover or CTA), body text is invisible or blends into the orange.

**Cause:** The template uses `#FF5C00` as a full-bleed background, and text colors are not overriding to white automatically.

**Fix:**
```css
.bg-orange {
  background: #FF5C00;
  color: #ffffff;
}

.bg-orange h1,
.bg-orange h2,
.bg-orange p,
.bg-orange .subtitle,
.bg-orange .eyebrow {
  color: #ffffff;
}

/* Ensure buttons invert on orange bg */
.bg-orange .btn-primary {
  background: #ffffff;
  color: #FF5C00;
}
```

**Contrast check:** `#ffffff` on `#FF5C00` yields a ratio of ~3.1:1 — acceptable for large display text (WCAG AA Large). For small body text, increase to `#0a0a0a` (ratio ~8.5:1).

---

### 16. Hhart Red — Bebas Neue Not Loading / Heading Falls Back to Wrong Font

**Symptoms:** Cover or section headings look like regular Inter/Arial instead of the intended bold condensed display style.

**Cause:** Bebas Neue requires an explicit Google Fonts import. If the deck is opened offline or the CDN is blocked, it silently falls back to the next stack font.

**Fix — add the import:**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap" rel="stylesheet">
```

**Robust fallback stack:**
```css
:root {
  --font-display: 'Bebas Neue', 'Impact', 'Arial Narrow', 'Arial Black', sans-serif;
}
```

**Offline / self-hosted fix:** Download `BebasNeue-Regular.ttf` from Google Fonts, embed as base64 or inline with `@font-face`:
```css
@font-face {
  font-family: 'Bebas Neue';
  src: url('fonts/BebasNeue-Regular.ttf') format('truetype');
  font-display: swap;
}
```

---

### 17. Hhart Red — Red Background Sections Show Low-Contrast Text

**Symptoms:** On `.bg-red` slides (cover, quote, CTA), secondary text (subtitles, captions, author lines) is hard to read — red on near-red grey.

**Cause:** `--text-secondary` is defined globally as semi-transparent white, but on the red background the contrast ratio dips below WCAG AA.

**Fix — locally override text colors inside red sections:**
```css
.bg-red p,
.bg-red .subtitle,
.bg-red .attr,
.bg-red .eyebrow {
  color: rgba(255, 255, 255, 0.88); /* bump opacity */
}

/* Or use a fixed white for maximum legibility */
.bg-red .pull-quote .attr {
  color: #f0f0f0;
}
```

**Stat values on red bg:** Keep `stat-value` in white (`#ffffff`) rather than `var(--accent)` — red-on-red renders invisible.
```css
.bg-red .stat-value {
  color: #ffffff;
}
```
