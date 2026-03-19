#!/usr/bin/env python3
"""
generate_slides.py — AI Slide Content Pipeline
═══════════════════════════════════════════════════════════════════════════════
Converts structured content (JSON outline or extracted PPTX data) into a
fully-rendered, ready-to-present HTML slide deck by filling a chosen template.

Usage:
    python3 scripts/generate_slides.py <input> [options]

Examples:
    # From a JSON outline:
    python3 scripts/generate_slides.py outline.json --template claude-warmth --output out.html

    # From PPTX-extracted JSON (output of extract_pptx.py):
    python3 scripts/generate_slides.py slides.json --template pitch-deck --output my_deck.html

    # Expand a brief topic into a full deck with LLM:
    python3 scripts/generate_slides.py --expand "大模型时代的产品设计原则" --slides 10 --output ai_product.html
    python3 scripts/generate_slides.py --expand "2025年度品牌战略复盘" --template quarterly-report --lang zh-CN
    python3 scripts/generate_slides.py --expand "Intro to Rust" --template tech-talk --slides 12 --lang en

    # Specify title:
    python3 scripts/generate_slides.py outline.json -t quarterly-report -o report.html --title "Q4 2025 Results"

    # Preview only (dry-run: print generated HTML to stdout):
    python3 scripts/generate_slides.py outline.json --dry-run

Options:
    --template, -t  Template name (default: auto-detect from content)
                    Choices: claude-warmth | pitch-deck | product-launch
                             quarterly-report | tech-talk
                             forai-white | pash-orange | hhart-red
    --output, -o    Output file path (default: <input_stem>_slides.html)
    --title         Deck title shown in <title> and slide 1 heading
    --lang          Language code for html[lang] attribute (default: zh-CN)
    --open          Open output in default browser after generation
    --dry-run       Print HTML to stdout instead of writing a file
    --verbose, -v   Print progress messages
    --expand TOPIC  Instead of a JSON file, generate a full deck from a brief topic
                    description using an LLM. Requires ANTHROPIC_API_KEY or
                    OPENAI_API_KEY env var, OR the `codebuddy` CLI in PATH.
    --slides N      Number of slides to generate with --expand (default: 10, max: 20)

Input JSON format (outline):
───────────────────────────────────────────────────────────────────────────────
{
  "title": "My Presentation Title",
  "subtitle": "Optional subtitle",
  "author": "Author Name",
  "date": "2025-01",
  "template": "claude-warmth",   ← optional, overridden by --template flag
  "slides": [
    {
      "type": "title",            ← slide layout type (see SLIDE TYPES below)
      "title": "Main Heading",
      "subtitle": "Supporting line",
      "eyebrow": "Category · Date",
      "notes": "Speaker notes here"
    },
    {
      "type": "text",
      "title": "Section Heading",
      "body": "Paragraph text here. Can be plain text or Markdown-lite."
    },
    {
      "type": "bullets",
      "title": "Key Points",
      "items": ["Point 1", "Point 2 — detail", "Point 3"]
    },
    {
      "type": "two-col",
      "title": "Comparison",
      "left": { "title": "Left Col", "body": "Text..." },
      "right": { "title": "Right Col", "body": "Text..." }
    },
    {
      "type": "stats",
      "title": "Traction",
      "stats": [
        { "value": "4.2M", "label": "Users" },
        { "value": "98%",  "label": "Satisfaction" },
        { "value": "3×",   "label": "Faster" }
      ]
    },
    {
      "type": "features",
      "title": "Core Features",
      "subtitle": "Built for teams",
      "items": [
        { "icon": "✦", "title": "Feature 1", "desc": "Description" },
        { "icon": "◈", "title": "Feature 2", "desc": "Description" },
        { "icon": "⬡", "title": "Feature 3", "desc": "Description" }
      ]
    },
    {
      "type": "quote",
      "quote": "The actual quote text in their own words.",
      "author": "Name · Role · Company"
    },
    {
      "type": "chart",
      "title": "Revenue Growth",
      "chart_type": "bar",         ← bar | line | area | donut | hbar | progress | radar | sankey | treemap
      "chart_data": {              ← passed directly to SlideCharts.*()
        "labels": ["Q1","Q2","Q3","Q4"],
        "datasets": [{"label":"Revenue","values":[42,68,55,91]}]
      },
      "chart_options": { "showGrid": true }
    },
    {
      "type": "image",
      "title": "Visual Slide",
      "image_url": "https://example.com/image.png",
      "caption": "Optional caption text"
    },
    {
      "type": "cta",
      "title": "Get Started",
      "subtitle": "Ready to build?",
      "primary_cta": "Start for Free",
      "secondary_cta": "Book a Demo",
      "url": "yourproduct.com",
      "offer": "Early access: first 3 months free"
    },
    {
      "type": "divider",
      "label": "Section Two"
    }
  ]
}

SLIDE TYPES:
    title       — Hero cover slide (big heading, subtitle, eyebrow, optional tag)
    text        — Heading + paragraph body text
    bullets     — Heading + bulleted list
    two-col     — Side-by-side two-column layout
    stats       — Big number statistics grid
    features    — Feature cards (3 or 6 per row)
    quote       — Oversized pull-quote
    chart       — Data visualization via charts.js (bar/line/area/donut/hbar/progress/radar/sankey/treemap)
    image       — Full-width image with optional caption
    cta         — Call to action close slide
    divider     — Section break with large label

TEMPLATE AUTO-DETECTION RULES:
    Deck has code/tech content → tech-talk
    Deck has pricing/investor keywords → pitch-deck
    Deck has bold editorial/manifesto/campaign keywords → hhart-red
    Deck has agency/studio/portfolio/creative keywords → pash-orange
    Deck has minimal/editorial/whitespace/typography keywords → forai-white
    Deck has >2 chart slides → quarterly-report
    Deck has feature cards + CTA → product-launch
    Default / brand story → claude-warmth
═══════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import subprocess
from pathlib import Path
from textwrap import dedent
from html import escape as he

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
TEMPLATES_DIR = PROJECT_ROOT / 'assets' / 'templates'
CHARTS_JS     = SCRIPT_DIR / 'charts.js'

TEMPLATE_FILES = {
    'claude-warmth':    TEMPLATES_DIR / 'template-claude-warmth.html',
    'pitch-deck':       TEMPLATES_DIR / 'template-pitch-deck.html',
    'product-launch':   TEMPLATES_DIR / 'template-product-launch.html',
    'quarterly-report': TEMPLATES_DIR / 'template-quarterly-report.html',
    'tech-talk':        TEMPLATES_DIR / 'template-tech-talk.html',
    'forai-white':      TEMPLATES_DIR / 'template-forai-white.html',
    'pash-orange':      TEMPLATES_DIR / 'template-pash-orange.html',
    'hhart-red':        TEMPLATES_DIR / 'template-hhart-red.html',
}

# ── Auto-detect template from slide content ───────────────────────────────────

def detect_template(slides: list) -> str:
    """Score-based template detection from slide content.

    Each template accumulates weighted match points; the highest scorer wins.
    Ties are broken by a fixed priority order (same as before).

    Fix summary
    -----------
    [Fix-1] Substring boundary protection
        Short / common English words (arr, mrr, force, client, movement …) are
        wrapped in \\b word-boundary patterns via re.search so they cannot match
        in the middle of unrelated words (e.g. "arr" inside "narrative").
        Longer unambiguous phrases (≥8 chars, no realistic substring clash) keep
        the cheaper `in` test.

    [Fix-2] Chinese keyword precision
        Removed the catch-all '设计' token (would fire on virtually any Chinese
        deck). Replaced with tighter phrases: '极简设计', '版式设计', '排版设计'.
        '白色' also removed (too common); kept '极简' and '排版'.

    [Fix-3] Priority preserved, hhart-red vs pitch-deck safe
        'revolution'/'disruption' appear in VC pitches, but pitch-deck scores
        higher on explicit financial signals (pricing, ARR, investor …) so it
        wins before hhart-red when both fire. No priority change needed.

    [Fix-4] product-launch structural detection broadened
        Now also accepts slides whose *body/bullets text* contains the phrases
        "feature" or "call to action" / "get started" / "sign up" — not only
        slides typed exactly "features" / "cta".

    [Fix-5] Score-based selection replaces first-match cascade
        Every template collects integer points (see SCORES dict).
        Weighted scoring lets a deck with many pash-orange signals beat a deck
        that barely touched one keyword, even if that keyword was checked first.
        Falls back to claude-warmth when no template reaches MIN_SCORE = 2.

    [Fix-6] Color-palette signal detection
        Scans every slide for explicit color preferences expressed via dedicated
        fields (``color``, ``palette``, ``color_scheme``, ``bg_color``,
        ``accent_color``, ``theme_color``) as well as inline color mentions in
        title / body / notes.

        Each colour family maps to the template whose visual identity it matches:

          Colour family              → Template          Palette identity
          ─────────────────────────────────────────────────────────────
          red / crimson / scarlet   → hhart-red          near-black + crimson
          orange / amber / fire     → pash-orange        black + pure orange
            (but if dark-amber w/ strong product signals → product-launch)
          white / ivory / minimal   → forai-white        pure white + ink
          navy / blue / cobalt      → pitch-deck         deep navy + gold
          purple / violet / indigo  → tech-talk          deep purple + pink
          warm / terracotta / cream → claude-warmth      cream + terracotta
          gray / grey / silver      → quarterly-report   off-white + blue-grey
          dark / black / midnight   → (boosts dark-theme templates by +1 each)

        Color signals contribute COLOR_WEIGHT = 3 points — enough to tip a close
        keyword race but not enough to override a clearly content-matched winner.

        When a slide contains *only* color signals and nothing else, color alone
        determines the winner (3 ≥ MIN_SCORE = 2).

        Hex / rgb colour values are parsed and mapped to the nearest hue family
        using a simple HSV-based hue bucket lookup, so ``#e63946`` or
        ``rgb(230,57,70)`` is correctly recognised as "red".
    """
    import re
    import colorsys

    texts = json.dumps(slides, ensure_ascii=False).lower()
    types = [s.get('type', '') for s in slides]

    # ── helpers ──────────────────────────────────────────────────────────────

    def _kw(word: str) -> bool:
        """Substring match (safe for long/unambiguous tokens)."""
        return word in texts

    def _wb(word: str) -> bool:
        """Word-boundary match (Fix-1: protects short tokens)."""
        return bool(re.search(r'\b' + re.escape(word) + r'\b', texts))

    def _count(words, boundary=False) -> int:
        """Count how many distinct keywords from a list appear in texts."""
        check = _wb if boundary else _kw
        return sum(1 for w in words if check(w))

    # ── per-template keyword groups ───────────────────────────────────────────

    # tech-talk: code-syntax tokens already have spaces/punctuation as natural
    # boundaries; 'code' / 'terminal' are long enough to be unambiguous.
    TECH_LONG   = ['code', 'terminal', 'snippet', 'import ', 'const ', 'def ', 'class ', 'function']
    # no boundary check needed — spaces in 'import ' etc. act as anchors

    # pitch-deck: 'arr' and 'mrr' MUST use word boundaries (Fix-1)
    PRICING_LONG  = ['pricing', 'price', 'valuation', 'funding', 'investor', 'revenue']
    PRICING_SHORT = ['arr', 'mrr']   # word-boundary guarded

    # hhart-red: 'force' and 'movement' need boundary (Fix-1)
    HHART_LONG  = ['manifesto', 'campaign', 'brand power', 'bold statement',
                   'disruption', 'disrupting', 'revolution', 'fearless']
    HHART_SHORT = ['headline', 'force', 'movement']   # word-boundary guarded

    # pash-orange: 'client' needs boundary (Fix-1); 'creative' is 8 chars, safe
    PASH_LONG   = ['agency', 'studio', 'portfolio', 'creative', 'showcase',
                   'branding', 'identity', 'design system', 'case study',
                   'our work', '我们的作品', '案例', '创意', '品牌识别']
    PASH_SHORT  = ['client']   # word-boundary guarded

    # forai-white: removed '设计' / '白色' (Fix-2); tightened Chinese tokens.
    # Precise CN compound words ('极简设计', '版式设计', '排版设计') are strong
    # signals on their own — weight them as 2 pts each so a single match
    # already clears MIN_SCORE = 2.
    FORAI_LONG  = ['minimalist', 'whitespace', 'white space', 'typography',
                   'clean design', 'design forward', 'publication', 'editorial',
                   '极简', '排版']
    FORAI_STRONG = ['极简设计', '版式设计', '排版设计']   # 2 pts each
    FORAI_SHORT = ['minimal']   # word-boundary guarded

    # ── structural signals ────────────────────────────────────────────────────

    chart_count = sum(1 for t in types if t == 'chart')

    # Fix-4: product-launch — accept both typed slides AND textual mentions
    has_features_type = any(t == 'features' for t in types)
    has_cta_type      = any(t == 'cta'      for t in types)
    has_features_text = _kw('feature')   # "features", "key features", "feature list" …
    has_cta_text      = any(_kw(p) for p in ('call to action', 'get started', 'sign up', 'try now', 'free trial'))
    product_launch_score = (
        (2 if has_features_type else (1 if has_features_text else 0))
        + (2 if has_cta_type     else (1 if has_cta_text      else 0))
    )

    # ── Fix-6: colour-palette signal detection ────────────────────────────────
    #
    # Step A — collect colour strings from dedicated palette fields + inline text.
    # Step B — convert hex/rgb values to hue-family names.
    # Step C — accumulate COLOR_WEIGHT points onto the matching template.

    COLOR_WEIGHT = 3   # pts per colour family hit — tips close races, won't overpower clear content wins

    # Colour keyword groups: (family_name, [keywords])
    # Keywords are matched case-insensitively against colour field values AND
    # the full text blob (for inline mentions like "use a red theme").
    COLOR_FAMILIES: list[tuple[str, list[str]]] = [
        # (family,             keyword patterns)
        ('red',     ['red', 'crimson', 'scarlet', 'cherry', '红色', '深红', '绯红', 'rouge', 'carmine']),
        ('orange',  ['orange', '橙色', '橙', 'fire', 'tangerine', 'coral']),
        ('amber',   ['amber', 'dark amber', '琥珀', 'burnt orange']),
        ('white',   ['white', 'ivory', '白色', '纯白', 'snow', 'clean', 'bright', 'light theme', '浅色']),
        ('navy',    ['navy', 'cobalt', '深蓝', '海军蓝', 'midnight blue', 'dark blue', 'indigo blue']),
        ('purple',  ['purple', 'violet', '紫色', '紫', 'lavender', 'mauve', 'magenta', 'pink purple']),
        ('warm',    ['warm', 'terracotta', 'cream', 'beige', 'sand', '暖色', '米色', '土色', 'sepia']),
        ('gray',    ['gray', 'grey', 'silver', '灰色', '灰', 'slate', 'muted', 'neutral', '中性']),
        ('dark',    ['dark', 'black', 'midnight', 'dark mode', '暗色', '深色', '黑色', '夜间']),
        ('blue',    ['blue', '蓝色', '蓝', 'azure', 'teal', 'cyan', 'sky blue']),
    ]

    # Hue-degree → colour family (HSV hue in [0, 360))
    # Buckets cover the visible spectrum; achromatic colours (S<0.15 or V<0.15)
    # are mapped separately.
    def _hue_to_family(h: float, s: float, v: float) -> str | None:
        if v < 0.15:
            return 'dark'          # very dark / black
        if s < 0.15:
            if v > 0.85:
                return 'white'     # very light desaturated → white
            return 'gray'          # mid-grey
        # Chromatic: bucket by hue
        if h < 15 or h >= 345:
            return 'red'
        if h < 40:
            return 'orange'        # orange–amber
        if h < 65:
            return 'amber'         # yellow–amber
        if h < 80:
            return 'warm'          # yellow-green (warm)
        if h < 165:
            return 'blue'          # green–cyan → treat as blue (no "green" template)
        if h < 200:
            return 'blue'
        if h < 255:
            return 'navy'          # blue → navy  (200–254°)
        if h < 315:
            return 'purple'        # purple / violet (255–314°)
        return 'red'               # magenta/red-purple → red

    def _parse_color_value(val: str) -> str | None:
        """Parse a hex or rgb() colour value and return its hue-family name."""
        val = val.strip().lower()
        # hex: #rrggbb or #rgb
        m = re.match(r'#([0-9a-f]{3,6})', val)
        if m:
            h = m.group(1)
            if len(h) == 3:
                h = h[0]*2 + h[1]*2 + h[2]*2
            if len(h) == 6:
                r, g, b = int(h[0:2], 16)/255, int(h[2:4], 16)/255, int(h[4:6], 16)/255
                hue, sat, bright = colorsys.rgb_to_hsv(r, g, b)
                return _hue_to_family(hue * 360, sat, bright)
        # rgb(r, g, b) or rgba(r, g, b, a)
        m = re.match(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', val)
        if m:
            r, g, b = int(m.group(1))/255, int(m.group(2))/255, int(m.group(3))/255
            hue, sat, bright = colorsys.rgb_to_hsv(r, g, b)
            return _hue_to_family(hue * 360, sat, bright)
        return None

    # Fields to scan for colour intent in each slide dict
    COLOR_FIELDS = ('color', 'palette', 'color_scheme', 'bg_color', 'accent_color',
                    'theme_color', 'accent', 'background', 'theme', 'style')

    # Gather all colour-field values + scan full text for explicit colour phrases
    colour_hits: dict[str, int] = {}   # family → count of slides / mentions

    for slide in slides:
        for field in COLOR_FIELDS:
            val = str(slide.get(field, '')).strip().lower()
            if not val:
                continue
            # Try hex/rgb parse first
            family = _parse_color_value(val)
            if family:
                colour_hits[family] = colour_hits.get(family, 0) + 1
                continue
            # Keyword match against family lists
            for fam, keywords in COLOR_FAMILIES:
                if any(kw in val for kw in keywords):
                    colour_hits[fam] = colour_hits.get(fam, 0) + 1
                    break

    # Also detect inline colour intent phrases in the full text
    # (e.g. "use a red and black color scheme" in a notes/description field)
    # Only count once per family (not per occurrence) to avoid amplifying noisy text.
    for fam, keywords in COLOR_FAMILIES:
        for kw in keywords:
            if kw in texts:
                colour_hits[fam] = colour_hits.get(fam, 0) + 1
                break

    # Map colour families → template bonus points
    # colour_to_template: family → (template, pts)
    # Dark is a modifier, not a direct template pointer.
    COLOUR_MAP: dict[str, str] = {
        'red':    'hhart-red',
        'orange': 'pash-orange',
        'amber':  'product-launch',   # dark amber = product-launch palette
        'white':  'forai-white',
        'navy':   'pitch-deck',
        'blue':   'pitch-deck',
        'purple': 'tech-talk',
        'warm':   'claude-warmth',
        'gray':   'quarterly-report',
    }

    # Compute colour bonus per template
    colour_bonus: dict[str, int] = {}
    dark_boost = colour_hits.get('dark', 0)

    for fam, cnt in colour_hits.items():
        tpl = COLOUR_MAP.get(fam)
        if tpl:
            colour_bonus[tpl] = colour_bonus.get(tpl, 0) + cnt * COLOR_WEIGHT

    # 'dark' boosts ALL dark-theme templates (+1 per dark-signal)
    if dark_boost:
        for dark_tpl in ('hhart-red', 'pash-orange', 'product-launch', 'pitch-deck', 'tech-talk'):
            colour_bonus[dark_tpl] = colour_bonus.get(dark_tpl, 0) + dark_boost

    # ── score accumulation (Fix-5 + Fix-6) ───────────────────────────────────
    #
    # Keyword matches = 1 pt each.
    # Structural signals (chart_count, product_launch) contribute directly.
    # Colour signals = COLOR_WEIGHT pts per family hit.
    # Templates need MIN_SCORE to be considered.

    MIN_SCORE = 2   # require at least 2 signals before committing

    scores: dict[str, int] = {
        'tech-talk':        _count(TECH_LONG),
        'pitch-deck':       _count(PRICING_LONG) + _count(PRICING_SHORT, boundary=True),
        'hhart-red':        _count(HHART_LONG)   + _count(HHART_SHORT,  boundary=True),
        'pash-orange':      _count(PASH_LONG)     + _count(PASH_SHORT,  boundary=True),
        'forai-white':      _count(FORAI_LONG) + _count(FORAI_SHORT, boundary=True)
                            + _count(FORAI_STRONG) * 2,  # Fix-2: precise CN phrases = 2 pts each
        'quarterly-report': chart_count,           # 1 pt per chart slide (need ≥2)
        'product-launch':   product_launch_score,
        'claude-warmth':    0,                     # always the fallback
    }

    # Merge colour bonuses into scores (Fix-6)
    for tpl, bonus in colour_bonus.items():
        if tpl in scores:
            scores[tpl] += bonus

    # Priority tie-break order (same as original cascade)
    PRIORITY = [
        'tech-talk', 'pitch-deck', 'hhart-red', 'pash-orange',
        'forai-white', 'quarterly-report', 'product-launch', 'claude-warmth',
    ]

    best = max(PRIORITY, key=lambda t: (scores[t], -PRIORITY.index(t)))
    if scores[best] < MIN_SCORE:
        return 'claude-warmth'
    return best


# ═══════════════════════════════════════════════════════════════════════════════
# PER-TEMPLATE PALETTE CONFIG
#
# Each palette defines:
#   bg_cover   — CSS class for cover/title/CTA slides (hero background)
#   bg_primary — CSS class for standard content slides
#   bg_alt     — CSS class for alternate content slides
#   bg_dark    — CSS class for dark/inverted slides
#   is_dark_theme — True if the template is dark-on-dark (pitch-deck, tech-talk, product-launch)
#   slide_label_tpl — Template for the slide number label HTML (use {num} {total} placeholders)
# ═══════════════════════════════════════════════════════════════════════════════

PALETTES = {
    # Cream + terracotta — alternates light / dark
    'claude-warmth': {
        'bg_cover':   'bg-dark-warm',     # dark warm for cover (circle decos)
        'bg_primary': 'bg-light',         # cream
        'bg_alt':     'bg-dark',          # rich brown-black
        'bg_dark':    'bg-dark',
        'is_dark_theme': False,
        'slide_label': '',                # claude-warmth has no slide-label element
    },
    # Deep navy + gold — all dark
    'pitch-deck': {
        'bg_cover':   'slide-cover',
        'bg_primary': 'slide-dark',
        'bg_alt':     'slide-surface',
        'bg_dark':    'slide-dark',
        'is_dark_theme': True,
        'slide_label': '<span class="slide-label">{num} / {total}</span>',
    },
    # Dark amber + orange — all dark
    'product-launch': {
        'bg_cover':   'bg-teaser',
        'bg_primary': 'bg-dark',
        'bg_alt':     'bg-surface',
        'bg_dark':    'bg-dark',
        'bg_reveal':  'bg-reveal',
        'is_dark_theme': True,
        'slide_label': '',
    },
    # Off-white + blue — all light
    'quarterly-report': {
        'bg_cover':   'slide-cover',
        'bg_primary': 'slide-white',
        'bg_alt':     'slide-surface',
        'bg_dark':    'slide-cover',
        'is_dark_theme': False,
        'slide_label': '<span class="slide-label">{num}</span>',
    },
    # Deep purple + pink — all dark
    'tech-talk': {
        'bg_cover':   'bg-hero',
        'bg_primary': 'bg-dark',
        'bg_alt':     'bg-surface',
        'bg_dark':    'bg-dark',
        'bg_code':    'bg-code',
        'is_dark_theme': True,
        'slide_label': '<span class="slide-label">{num}</span>',
    },
    # Pure white + ink — all light, with invert option
    'forai-white': {
        'bg_cover':   'bg-dots corner-mark',
        'bg_primary': '',               # no class = plain white
        'bg_alt':     'slide-muted bg-grid',
        'bg_dark':    'slide-invert',
        'is_dark_theme': False,
        'slide_label': '',              # forai-white uses slide-num spans (handled separately)
    },
    # White + pure orange — all light, with orange invert option
    'pash-orange': {
        'bg_cover':   'bg-black bg-dots corner-mark',
        'bg_primary': 'bg-black',
        'bg_alt':     'bg-mid',
        'bg_dark':    'bg-orange',
        'is_dark_theme': True,
        'slide_label': '',
    },
    # Near-black + crimson red — bold condensed editorial
    'hhart-red': {
        'bg_cover':   'bg-red corner-mark',
        'bg_primary': 'bg-dark',
        'bg_alt':     'bg-mid',
        'bg_dark':    'bg-red',
        'is_dark_theme': True,
        'slide_label': '',
    },
}

# Which slide types get the "alternate" bg (rather than primary) to create rhythm
_ALT_BG_TYPES = frozenset({'stats', 'divider'})
# Types that always use cover bg
_COVER_BG_TYPES = frozenset({'title', 'cta'})
# Types that use dark bg
_DARK_BG_TYPES = frozenset({'quote'})


def _resolve_bg(slide_type: str, idx: int, palette: dict, explicit_bg: str | None) -> str:
    """Resolve the correct background class for a slide."""
    if explicit_bg:
        return explicit_bg
    if slide_type in _COVER_BG_TYPES:
        return palette['bg_cover']
    if slide_type in _DARK_BG_TYPES:
        return palette['bg_dark']
    if slide_type in _ALT_BG_TYPES:
        return palette['bg_alt']
    # Alternate primary / alt for regular slides
    if idx % 2 == 0:
        return palette['bg_primary']
    return palette['bg_alt']


def _slide_label_html(palette: dict, num: int, total: int) -> str:
    tpl = palette.get('slide_label', '')
    if not tpl:
        return ''
    return tpl.replace('{num}', f'{num:02d}').replace('{total}', f'{total:02d}')


def _is_dark_bg(bg_class: str, palette: dict) -> bool:
    """Heuristic: is this bg class a dark background?"""
    dark_keywords = ('dark', 'invert', 'cover', 'hero', 'teaser', 'reveal', 'black', 'orange', 'surface', 'code')
    bc = bg_class.lower()
    if palette.get('is_dark_theme'):
        # In a dark theme, every bg except explicit light is dark
        light_keywords = ('white', 'muted', 'light', 'mid')
        return not any(k in bc for k in light_keywords)
    return any(k in bc for k in dark_keywords)


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPLATE-AWARE SLIDE RENDERERS
# Each renderer uses the correct CSS classes for the chosen template.
# ═══════════════════════════════════════════════════════════════════════════════

def _render_slide_open(bg_class: str, label_html: str, aria_label: str, notes: str) -> str:
    """Emit the opening <section> tag + optional slide-label."""
    parts = [f'  <section class="slide {bg_class}" role="region" aria-label="{he(aria_label)}"']
    if notes:
        parts.append(f' data-notes="{he(notes)}"')
    parts.append('>')
    if label_html:
        parts.append(f'\n    {label_html}')
    return ''.join(parts)


def _slide_image_html(s: dict) -> str:
    """Generate image HTML for slides that have extracted images (BUG FIX).
    
    This enables images to be displayed on any slide type, not just pure-image slides.
    """
    img = s.get('image')
    if not img:
        return ''
    # Escape the image path for safe HTML insertion
    safe_img = he(img)
    return f'\n      <figure data-animate style="margin-top:20px;"><img src="{safe_img}" alt="Slide content" style="max-width:100%;max-height:40vh;object-fit:contain;border-radius:8px;"/></figure>'


def render_title(s: dict, palette: dict, idx: int, total: int) -> str:
    title    = he(s.get('title', '[Title]'))
    subtitle = he(s.get('subtitle', ''))
    eyebrow  = he(s.get('eyebrow', ''))
    notes    = s.get('notes', '')
    bg       = _resolve_bg('title', idx, palette, s.get('bg'))
    is_dark  = _is_dark_bg(bg, palette)
    label    = _slide_label_html(palette, idx + 1, total)
    head_cls = '' if is_dark else 'style="color:var(--text-primary,inherit)"'

    eyebrow_html = ''
    if eyebrow:
        eyebrow_cls = 'eyebrow-dark' if is_dark else 'eyebrow-light'
        eyebrow_html = f'<p class="eyebrow {eyebrow_cls}" data-animate>{eyebrow}</p>'

    subtitle_html = ''
    if subtitle:
        sub_cls = 'subtitle-dark' if is_dark else 'subtitle'
        subtitle_html = f'<p class="{sub_cls}" data-animate style="max-width:560px;font-size:clamp(1rem,1.8vw,1.25rem);">{subtitle}</p>'

    # Template-specific decorations
    deco = _cover_deco(palette)

    return dedent(f"""\
{_render_slide_open(bg, label, title, notes)}
{deco}    <div class="slide-content centered">
      {eyebrow_html}
      <h1 data-animate>{title}</h1>
      {subtitle_html}
      <div class="divider" data-animate></div>
    </div>
  </section>""")


def render_text(s: dict, palette: dict, idx: int, total: int) -> str:
    title  = he(s.get('title', ''))
    body   = he(s.get('body', ''))
    notes  = s.get('notes', '')
    bg     = _resolve_bg('text', idx, palette, s.get('bg'))
    is_dark = _is_dark_bg(bg, palette)
    label  = _slide_label_html(palette, idx + 1, total)
    h2_cls = '' if is_dark else ''
    sub_cls = 'subtitle-dark' if is_dark else 'subtitle'

    body_html = ''
    if body:
        body_html = f'<p class="{sub_cls}" data-animate style="font-size:clamp(0.9rem,1.6vw,1.1rem);line-height:1.85;max-width:740px;">{body}</p>'

    # BUG FIX: Include extracted image if present
    img_html = _slide_image_html(s)

    return dedent(f"""\
{_render_slide_open(bg, label, title, notes)}
    <div class="slide-content" style="max-width:780px;">
      <h2 data-animate>{title}</h2>
      <div class="divider" data-animate></div>
      {body_html}{img_html}
    </div>
  </section>""")


def render_bullets(s: dict, palette: dict, idx: int, total: int) -> str:
    title  = he(s.get('title', ''))
    items  = s.get('items', [])
    notes  = s.get('notes', '')
    bg     = _resolve_bg('bullets', idx, palette, s.get('bg'))
    is_dark = _is_dark_bg(bg, palette)
    label  = _slide_label_html(palette, idx + 1, total)

    # Different list styles per template
    tpl = palette.get('_tpl', 'claude-warmth')
    if tpl == 'quarterly-report':
        # item-list style (white cards)
        lis = '\n'.join(f'      <li data-animate>{he(str(it))}</li>' for it in items)
        list_html = f'<ul class="item-list">\n{lis}\n      </ul>'
    elif tpl == 'tech-talk':
        # steps-list style
        lis = '\n'.join(f'      <li data-animate>{he(str(it))}</li>' for it in items)
        list_html = f'<ul class="steps-list">\n{lis}\n      </ul>'
    else:
        # feature-list style (works across most templates)
        dark_cls = 'dark' if is_dark else ''
        lis = '\n'.join(f'      <li data-animate>{he(str(it))}</li>' for it in items)
        list_html = f'<ul class="feature-list {dark_cls}">\n{lis}\n      </ul>'

    # BUG FIX: Include extracted image if present
    img_html = _slide_image_html(s)

    return dedent(f"""\
{_render_slide_open(bg, label, title, notes)}
    <div class="slide-content" style="max-width:740px;">
      <h2 data-animate>{title}</h2>
      <div class="divider" data-animate></div>
      {list_html}{img_html}
    </div>
  </section>""")


def render_two_col(s: dict, palette: dict, idx: int, total: int) -> str:
    title   = he(s.get('title', ''))
    left    = s.get('left', {})
    right   = s.get('right', {})
    notes   = s.get('notes', '')
    bg      = _resolve_bg('two-col', idx, palette, s.get('bg'))
    is_dark = _is_dark_bg(bg, palette)
    label   = _slide_label_html(palette, idx + 1, total)
    sub_cls = 'subtitle-dark' if is_dark else 'subtitle'

    l_title = he(left.get('title', ''))
    l_body  = he(left.get('body', ''))
    r_title = he(right.get('title', ''))
    r_body  = he(right.get('body', ''))

    l_title_html = f'<h3 data-animate style="margin-bottom:10px;">{l_title}</h3>' if l_title else ''
    r_title_html = f'<h3 data-animate style="margin-bottom:10px;">{r_title}</h3>' if r_title else ''

    # BUG FIX: Include extracted image if present
    img_html = _slide_image_html(s)

    return dedent(f"""\
{_render_slide_open(bg, label, title, notes)}
    <div class="slide-content two-col">
      <div>
        <h2 data-animate>{title}</h2>
        <div class="divider" data-animate style="margin:12px 0;"></div>
        {l_title_html}
        <p class="{sub_cls}" data-animate>{l_body}</p>
      </div>
      <div data-animate="slide-left">
        {r_title_html}
        <p class="{sub_cls}">{r_body}</p>
        {img_html}
      </div>
    </div>
  </section>""")


def render_stats(s: dict, palette: dict, idx: int, total: int) -> str:
    title  = he(s.get('title', ''))
    stats  = s.get('stats', [])
    notes  = s.get('notes', '')
    bg     = _resolve_bg('stats', idx, palette, s.get('bg'))
    is_dark = _is_dark_bg(bg, palette)
    label  = _slide_label_html(palette, idx + 1, total)
    tpl    = palette.get('_tpl', 'claude-warmth')

    # Different stat rendering per template
    if tpl == 'quarterly-report':
        # metrics-grid style
        cards = '\n'.join(
            f'        <div class="metric-card" data-animate>'
            f'<div class="metric-value">{he(str(st.get("value","?")))}</div>'
            f'<p style="font-size:0.8rem;color:var(--text-secondary);">{he(str(st.get("label","")))}</p>'
            f'</div>'
            for st in stats
        )
        stats_html = f'<div class="metrics-grid">\n{cards}\n      </div>'
    elif tpl in ('forai-white', 'pash-orange'):
        # stat-block style
        cards = '\n'.join(
            f'        <div class="stat-block" data-animate>'
            f'<div class="stat-num">{he(str(st.get("value","?")))}</div>'
            f'<div class="stat-label">{he(str(st.get("label","")))}</div>'
            f'</div>'
            for st in stats
        )
        stats_html = f'<div class="stats-row" style="gap:40px;flex-wrap:wrap;">\n{cards}\n      </div>'
    elif tpl == 'hhart-red':
        # stat-row / stat-block grid (dark cards, red values)
        cards = '\n'.join(
            f'        <div class="stat-block" data-animate>'
            f'<div class="stat-value">{he(str(st.get("value","?")))}</div>'
            f'<div class="stat-label">{he(str(st.get("label","")))}</div>'
            f'</div>'
            for st in stats
        )
        col_count = min(len(stats), 4)
        stats_html = (
            f'<div class="stat-row" style="grid-template-columns:repeat({col_count},1fr);" data-animate="scale">\n'
            f'{cards}\n      </div>'
        )
    else:
        # big-stat / stat-item style (pitch-deck, claude-warmth, product-launch, tech-talk)
        stat_cls = 'dark' if is_dark else 'light'
        items_html = '\n'.join(
            f'        <div class="stat-item" data-animate>'
            f'<div class="big-stat" style="color:var(--accent);">{he(str(st.get("value","?")))}</div>'
            f'<div class="big-stat-label">{he(str(st.get("label","")))}</div>'
            f'</div>'
            for st in stats
        )
        stats_html = f'<div class="stats-row">\n{items_html}\n      </div>'

    # BUG FIX: Include extracted image if present
    img_html = _slide_image_html(s)

    return dedent(f"""\
{_render_slide_open(bg, label, title, notes)}
    <div class="slide-content">
      <h2 data-animate>{title}</h2>
      <div class="divider" data-animate></div>
      {stats_html}{img_html}
    </div>
  </section>""")


def render_features(s: dict, palette: dict, idx: int, total: int) -> str:
    title    = he(s.get('title', ''))
    subtitle = he(s.get('subtitle', ''))
    items    = s.get('items', [])
    notes    = s.get('notes', '')
    bg       = _resolve_bg('features', idx, palette, s.get('bg'))
    is_dark  = _is_dark_bg(bg, palette)
    label    = _slide_label_html(palette, idx + 1, total)
    tpl      = palette.get('_tpl', 'claude-warmth')

    # feature-card structure
    grid_cls = 'features-grid' if tpl == 'product-launch' else 'feature-grid'
    cards = '\n'.join(
        f'        <div class="feature-card" data-animate>'
        f'<div class="feature-icon">{he(str(it.get("icon","✦")))}</div>'
        f'<div class="feature-title">{he(str(it.get("title","")))}</div>'
        f'<p class="feature-desc">{he(str(it.get("desc","")))}</p>'
        f'</div>'
        for it in items
    )

    subtitle_html = ''
    if subtitle:
        sub_cls = 'subtitle-dark' if is_dark else 'subtitle'
        subtitle_html = f'<p class="{sub_cls}" data-animate>{subtitle}</p>'

    # BUG FIX: Include extracted image if present
    img_html = _slide_image_html(s)

    return dedent(f"""\
{_render_slide_open(bg, label, title, notes)}
    <div class="slide-content centered" style="max-width:1060px;">
      <h2 data-animate>{title}</h2>
      {subtitle_html}
      <div class="{grid_cls}" style="margin-top:8px;">
{cards}
      </div>
      {img_html}
    </div>
  </section>""")


def render_quote(s: dict, palette: dict, idx: int, total: int) -> str:
    quote  = he(s.get('quote', ''))
    author = he(s.get('author', ''))
    notes  = s.get('notes', '')
    bg     = _resolve_bg('quote', idx, palette, s.get('bg'))
    label  = _slide_label_html(palette, idx + 1, total)
    tpl    = palette.get('_tpl', 'claude-warmth')
    is_dark = _is_dark_bg(bg, palette)

    # Template-specific quote rendering
    # BUG FIX: Include extracted image if present
    img_html = _slide_image_html(s)
    
    if tpl == 'product-launch':
        author_html = f'<cite class="subtitle" data-animate style="font-style:normal;font-size:0.82rem;">— {author}</cite>' if author else ''
        return dedent(f"""\
{_render_slide_open(bg, label, 'Quote', notes)}
    <div class="slide-content centered" style="max-width:760px;">
      <div class="hero-quote" data-animate>"{quote}"</div>
      {author_html}
      {img_html}
    </div>
  </section>""")
    elif tpl in ('forai-white', 'pash-orange'):
        author_html = f'<p class="testimonial-cite" data-animate style="font-size:0.82rem;margin-top:12px;opacity:0.6;">— {author}</p>' if author else ''
        return dedent(f"""\
{_render_slide_open(bg, label, 'Quote', notes)}
    <div class="slide-content centered" style="max-width:740px;">
      <div class="testimonial-block" data-animate>
        <blockquote>"{quote}"</blockquote>
        {author_html}
      </div>
      {img_html}
    </div>
  </section>""")
    elif tpl == 'hhart-red':
        author_html = f'<span class="attr">— {author}</span>' if author else ''
        return dedent(f"""\
{_render_slide_open('bg-red corner-mark', label, 'Quote', notes)}
    <div class="slide-content centered" style="max-width:820px;">
      <div class="divider" style="background:rgba(255,255,255,0.2)" data-animate="fade"></div>
      <div class="pull-quote" data-animate>
        &#8220;{quote}&#8221;
        {author_html}
      </div>
      <div class="divider" style="background:rgba(255,255,255,0.2);margin-top:24px" data-animate="fade"></div>
      {img_html}
    </div>
  </section>""")
    else:
        text_cls = 'on-dark' if is_dark else ''
        author_html = f'<p class="quote-cite" data-animate style="margin-top:12px;">— {author}</p>' if author else ''
        return dedent(f"""\
{_render_slide_open(bg, label, 'Quote', notes)}
    <div class="quote-mark">&#8220;</div>
    <div class="slide-content centered" style="max-width:740px;">
      <p class="quote-text {text_cls}" data-animate>&#8220;{quote}&#8221;</p>
      {author_html}
      {img_html}
    </div>
  </section>""")


def render_chart(s: dict, palette: dict, idx: int, total: int) -> str:
    title        = he(s.get('title', ''))
    chart_type   = s.get('chart_type', 'bar')
    chart_data   = json.dumps(s.get('chart_data', {}))
    chart_options = json.dumps(s.get('chart_options', {}))
    notes        = s.get('notes', '')
    body         = he(s.get('body', ''))   # optional text panel for chart-split
    layout       = s.get('layout', 'chart-full')  # chart-full | chart-split
    bg           = _resolve_bg('chart', idx, palette, s.get('bg'))
    is_dark      = _is_dark_bg(bg, palette)
    label        = _slide_label_html(palette, idx + 1, total)
    chart_id     = f"chart_{abs(hash(title + chart_type)) % 100000}"
    method_map   = {
        'bar': 'bar', 'line': 'line', 'area': 'area',
        'donut': 'donut', 'hbar': 'horizontalBar',
        'progress': 'progress', 'radar': 'radar', 'sankey': 'sankey',
        'treemap': 'treemap',
        # v2.1 new chart types
        'waterfall': 'waterfall', 'bullet': 'bullet',
        'scatter': 'scatter', 'bubble': 'scatter', 'gauge': 'gauge',
    }
    method = method_map.get(chart_type, 'bar')
    sub_cls = 'subtitle-dark' if is_dark else 'subtitle'

    # Chart init script (shared between layouts)
    init_script = dedent(f"""\
  <script>
    (function(){{
      var _rendered_{chart_id} = false;
      function _draw_{chart_id}(){{
        if(_rendered_{chart_id})return;
        if(typeof SlideCharts==='undefined'){{setTimeout(_draw_{chart_id},100);return;}}
        _rendered_{chart_id}=true;
        SlideCharts.{method}('#{chart_id}', {chart_data}, {chart_options});
      }}
      (function(){{
        var el=document.getElementById('{chart_id}');
        if(!el)return;
        var slide=el.closest('.slide');
        if(!slide||!window.IntersectionObserver){{_draw_{chart_id}();return;}}
        var obs=new IntersectionObserver(function(entries,o){{
          if(entries[0].isIntersecting){{o.disconnect();_draw_{chart_id}();}}
        }},{{threshold:0.3}});
        obs.observe(slide);
      }})();
    }})();
  </script>""")

    # BUG FIX: Include extracted image if present (for slides that have both chart and image)
    img_html = _slide_image_html(s)

    if layout == 'chart-split' and body:
        # Two-column: text left, chart right
        return dedent(f"""\
{_render_slide_open(bg, label, f'{title} chart', notes)}
    <div class="slide-content sc-chart-split">
      <div class="sc-chart-text-col">
        <h2 data-animate>{title}</h2>
        <div class="divider" data-animate></div>
        <p class="{sub_cls}" data-animate style="font-size:clamp(0.88rem,1.5vw,1rem);line-height:1.8;">{body}</p>
        {img_html}
      </div>
      <div class="sc-chart-chart-col">
        <div id="{chart_id}" class="chart-container" style="height:100%;min-height:260px;" data-animate></div>
      </div>
    </div>
  </section>
{init_script}""")

    # Default: chart-full
    return dedent(f"""\
{_render_slide_open(bg, label, f'{title} chart', notes)}
    <div class="slide-content sc-chart-full" style="display:flex;flex-direction:column;gap:16px;width:80%;max-width:740px;">
      <h2 data-animate>{title}</h2>
      <div id="{chart_id}" class="chart-container" style="height:300px;" data-animate></div>
      {img_html}
    </div>
  </section>
{init_script}""")


def render_image(s: dict, palette: dict, idx: int, total: int) -> str:
    title   = he(s.get('title', ''))
    url     = he(s.get('image_url', ''))
    caption = he(s.get('caption', ''))
    notes   = s.get('notes', '')
    bg      = _resolve_bg('image', idx, palette, s.get('bg'))
    label   = _slide_label_html(palette, idx + 1, total)

    title_html   = f'<h2 data-animate style="margin-bottom:8px;">{title}</h2>' if title else ''
    caption_html = f'<p style="font-size:0.82rem;opacity:0.6;margin-top:6px;" data-animate>{caption}</p>' if caption else ''

    return dedent(f"""\
{_render_slide_open(bg, label, title or 'Image', notes)}
    <div class="slide-content centered">
      {title_html}
      <img src="{url}" alt="{caption or title}" data-animate
           style="max-width:100%;max-height:55vh;border-radius:12px;object-fit:contain;"/>
      {caption_html}
    </div>
  </section>""")


def render_cta(s: dict, palette: dict, idx: int, total: int) -> str:
    title     = he(s.get('title', 'Get Started'))
    subtitle  = he(s.get('subtitle', ''))
    primary   = he(s.get('primary_cta', 'Start Now'))
    secondary = he(s.get('secondary_cta', ''))
    url       = he(s.get('url', ''))
    offer     = he(s.get('offer', ''))
    notes     = s.get('notes', '')
    bg        = _resolve_bg('cta', idx, palette, s.get('bg'))
    is_dark   = _is_dark_bg(bg, palette)
    label     = _slide_label_html(palette, idx + 1, total)
    tpl       = palette.get('_tpl', 'claude-warmth')

    deco = _cover_deco(palette)

    # Button styles per template
    if tpl in ('quarterly-report',):
        btn_primary = f'<a href="#" style="display:inline-block;background:white;color:var(--accent);border-radius:8px;padding:12px 28px;font-size:0.92rem;font-weight:700;text-decoration:none;">{primary}</a>'
    elif tpl in ('forai-white',):
        btn_primary = f'<button class="btn-primary" data-animate>{primary}</button>'
    elif tpl in ('pash-orange', 'hhart-red'):
        btn_primary = f'<button class="btn-primary" data-animate>{primary}</button>'
    else:
        btn_primary = f'<div style="background:var(--accent);color:#fff;border-radius:10px;padding:12px 32px;font-size:0.95rem;font-weight:700;display:inline-block;cursor:pointer;" data-animate>{primary}</div>'

    secondary_html = ''
    if secondary:
        secondary_html = f'<div style="background:transparent;border:1.5px solid currentColor;opacity:0.6;border-radius:10px;padding:12px 28px;font-size:0.92rem;font-weight:500;display:inline-block;cursor:pointer;" data-animate>{secondary}</div>'

    subtitle_html = f'<p class="subtitle" data-animate style="max-width:480px;">{subtitle}</p>' if subtitle else ''
    url_html      = f'<p data-animate style="font-size:0.78rem;opacity:0.45;margin-top:8px;">{url}</p>' if url else ''
    offer_html    = f'<p data-animate style="font-size:0.82rem;opacity:0.7;margin-top:8px;">{offer}</p>' if offer else ''

    return dedent(f"""\
{_render_slide_open(bg, label, 'CTA', notes)}
{deco}    <div class="slide-content centered" style="max-width:700px;">
      <h1 data-animate>{title}</h1>
      {subtitle_html}
      <div data-animate style="display:flex;gap:14px;flex-wrap:wrap;justify-content:center;margin-top:12px;">
        {btn_primary}
        {secondary_html}
      </div>
      {offer_html}
      {url_html}
    </div>
  </section>""")


def render_divider(s: dict, palette: dict, idx: int, total: int) -> str:
    label_text = he(s.get('label', ''))
    notes      = s.get('notes', '')
    bg         = _resolve_bg('divider', idx, palette, s.get('bg'))
    is_dark    = _is_dark_bg(bg, palette)
    label      = _slide_label_html(palette, idx + 1, total)
    h2_style   = 'color:var(--accent)' if not is_dark else ''

    return dedent(f"""\
{_render_slide_open(bg, label, f'Section: {label_text}', notes)}
    <div class="slide-content centered">
      <div class="divider" data-animate style="width:60px;"></div>
      <h2 data-animate style="font-size:clamp(2rem,5vw,4rem);letter-spacing:-0.03em;margin-top:16px;{h2_style}">{label_text}</h2>
      <div class="divider" data-animate style="width:60px;"></div>
    </div>
  </section>""")


# ── Template-specific decorative elements ─────────────────────────────────────

def _cover_deco(palette: dict) -> str:
    """Return decorative HTML elements for cover/CTA slides."""
    tpl = palette.get('_tpl', 'claude-warmth')
    if tpl == 'claude-warmth':
        return (
            '    <div class="circle-deco circle-deco-1"></div>\n'
            '    <div class="circle-deco circle-deco-2"></div>\n'
            '    <div class="orb orb-terracotta"></div>\n'
        )
    if tpl == 'forai-white':
        return ''  # bg-dots class handles decoration
    if tpl in ('pash-orange', 'hhart-red'):
        return ''  # corner-mark class handles decoration
    return ''


# ── Slide type dispatch ────────────────────────────────────────────────────────

RENDERERS = {
    'title':    render_title,
    'text':     render_text,
    'bullets':  render_bullets,
    'two-col':  render_two_col,
    'stats':    render_stats,
    'features': render_features,
    'quote':    render_quote,
    'chart':    render_chart,
    'image':    render_image,
    'cta':      render_cta,
    'divider':  render_divider,
    # 'end' is produced by parse_html.py for thank-you/closing slides;
    # map it to render_cta so it renders as a proper closing slide.
    'end':      render_cta,
}


# ── Template loading & injection ──────────────────────────────────────────────

def load_template_shell(template_name: str) -> str | None:
    path = TEMPLATE_FILES.get(template_name)
    if path and path.exists():
        with open(path, encoding='utf-8') as f:
            return f.read()
    return None


def extract_slide_shell(html: str) -> tuple[str, str]:
    """
    Split template HTML into before-<main> and after-</main>.
    Returns (before_with_open_tag, after_close_tag)
    """
    main_open  = re.search(r'<main\b[^>]*>', html, re.IGNORECASE)
    main_close = html.rfind('</main>')
    if not main_open or main_close == -1:
        return html, ''
    before   = html[:main_open.start()]
    open_tag = html[main_open.start():main_open.end()]
    after    = html[main_close + len('</main>'):]
    return before + open_tag, after


# ── Charts.js inline loading ───────────────────────────────────────────────────

def load_charts_js() -> str:
    if CHARTS_JS.exists():
        with open(CHARTS_JS, encoding='utf-8') as f:
            return f.read()
    return '/* charts.js not found — place scripts/charts.js next to this script */'


# ── Main generation function ───────────────────────────────────────────────────

def generate(content: dict, template_name: str | None = None,
             title_override: str | None = None,
             lang: str = 'zh-CN', verbose: bool = False) -> str:
    """Given parsed outline content dict, return a complete single-file HTML string."""
    slides_data = content.get('slides', [])
    if not slides_data:
        sys.exit('❌  Input JSON has no "slides" array.')

    # Resolve template
    tpl_name = template_name or content.get('template') or detect_template(slides_data)
    if verbose:
        print(f'  ↳ Template: {tpl_name}')

    palette = dict(PALETTES.get(tpl_name, PALETTES['claude-warmth']))
    palette['_tpl'] = tpl_name  # inject template name so renderers can branch

    total = len(slides_data)

    # Render each slide using per-template-aware renderers
    slide_html_parts = []
    for idx, s in enumerate(slides_data):
        slide_type = s.get('type', 'text')
        renderer = RENDERERS.get(slide_type, render_text)
        slide_html_parts.append(renderer(s, palette, idx, total))

    slides_html = '\n\n'.join(slide_html_parts)

    # Load template shell
    tpl_html = load_template_shell(tpl_name)

    if tpl_html:
        before, after = extract_slide_shell(tpl_html)
        output = before + '\n\n' + slides_html + '\n\n</main>\n' + after
    else:
        if verbose:
            print(f'  ⚠  Template file not found for "{tpl_name}", using minimal fallback.')
        output = _build_minimal_html(slides_html, tpl_name, lang)

    # Patch <title> and lang
    deck_title = title_override or content.get('title', 'Presentation')
    output = re.sub(r'<title>[^<]*</title>', f'<title>{he(deck_title)}</title>', output, count=1)
    output = re.sub(r'<html\s[^>]*lang="[^"]*"', f'<html lang="{lang}"', output, count=1)

    # Inline charts.js
    # Strategy: replace an explicit <script src="scripts/charts.js"> tag when present;
    # otherwise always inject before </body> — even if template comments mention
    # "charts.js" or "SlideCharts" as prose/example text.
    charts_js = load_charts_js()
    charts_block = f'\n<script>\n/* === charts.js inline === */\n{charts_js}\n</script>\n'
    _src_tag = '<script src="scripts/charts.js"></script>'
    if _src_tag in output:
        # Template has an explicit external script tag → replace it
        output = output.replace(_src_tag, charts_block)
    elif '</body>' in output:
        # Always inject before </body>; charts.js is idempotent if already present
        output = output.replace('</body>', charts_block + '</body>', 1)

    # Patch total slide count span
    output = re.sub(r'(<span id="totalSlides">)\d*(</span>)', fr'\g<1>{total}\g<2>', output)

    # ── forai-white: inject & renumber .slide-num spans ──
    if tpl_name == 'forai-white':
        total_str = str(total).zfill(2)

        def _inject_slide_num_if_missing(m: re.Match) -> str:
            section_html = m.group(0)
            if 'slide-num' in section_html:
                return section_html
            return re.sub(
                r'(<div[^>]*class="slide-content[^"]*")',
                r'<span class="slide-num"></span>\n    \1',
                section_html, count=1,
            )

        output = re.sub(
            r'<section[^>]*class="slide[^"]*"[^>]*>.*?</section>',
            _inject_slide_num_if_missing,
            output, flags=re.DOTALL,
        )

        slide_idx = [0]

        def _renumber_slide_num(m: re.Match) -> str:
            slide_idx[0] += 1
            nn = str(slide_idx[0]).zfill(2)
            return f'{m.group(1)}{nn} / {total_str}{m.group(3)}'

        output = re.sub(
            r'(<span[^>]*class="slide-num"[^>]*>)([^<]*)(</span>)',
            _renumber_slide_num, output,
        )

    return output


def _build_minimal_html(slides_html: str, template_name: str, lang: str) -> str:
    """Minimal standalone fallback HTML when template file is missing."""
    return dedent(f"""\
<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Presentation</title>
  <style>
    :root {{
      --bg:#F6F0E8;--bg-dark:#1C1917;--accent:#DA7756;--accent2:#C9A96E;
      --text-primary:#1C1917;--text-secondary:#57534E;--text-tertiary:#A8A29E;
      --text-on-dark:#F5F0E8;--text-sec-dark:#A8A29E;--surface:#FDFAF5;
      --font-heading:'Inter',-apple-system,sans-serif;--font-body:'Inter',-apple-system,sans-serif;
    }}
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
    html,body{{height:100%;overflow:hidden;background:var(--bg);color:var(--text-primary);}}
    h1{{font-size:clamp(2.4rem,5vw,4rem);font-weight:800;letter-spacing:-0.03em;line-height:1.05;}}
    h2{{font-size:clamp(1.6rem,3.2vw,3rem);font-weight:700;letter-spacing:-0.025em;}}
    h3{{font-size:clamp(1rem,1.8vw,1.5rem);font-weight:600;}}
    p{{font-size:clamp(0.9rem,1.4vw,1rem);line-height:1.75;}}
    .slides-container{{height:100vh;overflow:hidden;position:relative;}}
    .slide{{height:100vh;overflow:hidden;position:absolute;top:0;left:0;width:100%;display:flex;align-items:center;justify-content:center;transition:transform 0.6s cubic-bezier(0.16,1,0.3,1);}}
    .slide-content{{width:min(84%,960px);display:flex;flex-direction:column;gap:20px;position:relative;z-index:1;}}
    .slide-content.centered{{text-align:center;align-items:center;}}
    .slide-content.two-col{{display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:center;width:min(92%,1100px);}}
    .bg-light{{background:#F6F0E8;}}
    .bg-card{{background:#FDFAF5;}}
    .bg-dark{{background:#1C1917;}}
    .bg-dark-warm{{background:#1C1917;background-image:radial-gradient(ellipse at 50% 60%,rgba(218,119,86,.12) 0%,transparent 55%);}}
    .bg-surface{{background:linear-gradient(135deg,#2d1f00 0%,#1C1917 100%);}}
    .bg-light-sand{{background:#EDE5D8;}}
    .slide-cover{{background:linear-gradient(135deg,#0d0d1a,#16161e);}}
    .slide-dark{{background:#0d0d1a;}}
    .slide-surface{{background:linear-gradient(135deg,#161626,#0d0d1a);}}
    .slide-white{{background:#ffffff;}}
    .slide-invert{{background:#0a0a0a;color:#fff;}}
    .bg-hero{{background:radial-gradient(ellipse at 20% 40%,rgba(124,58,237,0.25) 0%,transparent 50%),#0b0b1e;}}
    .bg-teaser{{background:radial-gradient(ellipse at 50% 60%,rgba(245,158,11,0.18) 0%,transparent 55%),#110800;}}
    .bg-reveal{{background:radial-gradient(ellipse at 50% 50%,rgba(245,158,11,0.25) 0%,transparent 60%),#110800;}}
    .eyebrow{{font-size:clamp(.62rem,.95vw,.75rem);text-transform:uppercase;letter-spacing:.18em;font-weight:600;}}
    .eyebrow-light{{color:var(--accent);}} .eyebrow-dark{{color:var(--accent2);}}
    .subtitle{{color:var(--text-secondary);}} .subtitle-dark{{color:var(--text-sec-dark);}}
    .on-dark{{color:var(--text-on-dark);}} .accent-text{{color:var(--accent);}}
    .feature-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;}}
    .features-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;}}
    .feature-card{{background:var(--surface);border-radius:14px;padding:24px 20px;border:1px solid rgba(218,119,86,.12);display:flex;flex-direction:column;gap:12px;}}
    .feature-icon{{width:38px;height:38px;border-radius:9px;background:rgba(218,119,86,.1);border:1px solid rgba(218,119,86,.2);display:flex;align-items:center;justify-content:center;font-size:16px;}}
    .feature-title{{font-size:1rem;font-weight:600;}} .feature-desc{{font-size:.85rem;line-height:1.6;opacity:0.7;}}
    .stats-row{{display:flex;gap:48px;flex-wrap:wrap;}} .stat-item{{display:flex;flex-direction:column;gap:4px;}}
    .big-stat{{font-size:clamp(2.8rem,6vw,5rem);font-weight:800;letter-spacing:-0.04em;line-height:1;color:var(--accent);}}
    .big-stat-label{{font-size:.82rem;font-weight:500;letter-spacing:.04em;text-transform:uppercase;opacity:0.7;}}
    .quote-mark{{font-family:Georgia,serif;font-size:12rem;line-height:.7;color:rgba(218,119,86,.15);position:absolute;top:40px;left:40px;pointer-events:none;font-weight:700;user-select:none;}}
    .quote-text{{font-size:clamp(1.35rem,2.8vw,2rem);font-weight:600;letter-spacing:-.02em;line-height:1.4;}}
    .quote-cite{{font-size:.82rem;opacity:0.5;margin-top:8px;}}
    .feature-list{{list-style:none;display:flex;flex-direction:column;gap:12px;}}
    .feature-list li{{display:flex;align-items:flex-start;gap:12px;font-size:clamp(.88rem,1.4vw,1rem);line-height:1.6;}}
    .feature-list li::before{{content:'';flex-shrink:0;width:6px;height:6px;border-radius:50%;background:var(--accent);margin-top:8px;}}
    .divider{{width:48px;height:3px;border-radius:2px;background:linear-gradient(90deg,var(--accent),var(--accent2));}}
    .circle-deco{{position:absolute;border-radius:50%;pointer-events:none;border:1px solid rgba(218,119,86,.12);}}
    .circle-deco-1{{width:520px;height:520px;top:50%;left:50%;transform:translate(-50%,-50%);}}
    .circle-deco-2{{width:360px;height:360px;top:50%;left:50%;transform:translate(-50%,-50%);border-color:rgba(218,119,86,.08);}}
    .orb{{position:absolute;border-radius:50%;filter:blur(80px);pointer-events:none;opacity:0.25;}}
    .orb-terracotta{{background:#DA7756;width:340px;height:340px;top:-80px;right:-80px;}}
    .chart-container{{width:100%;height:100%;display:flex;align-items:center;justify-content:center;}}
    /* ── SlideCharts layout helpers ── */
    .sc-chart-full{{display:flex;flex-direction:column;gap:16px;width:80%;max-width:740px;}}
    .sc-chart-split{{display:grid;grid-template-columns:1fr 1.3fr;gap:52px;align-items:center;width:min(92%,1060px);}}
    .sc-chart-text-col{{display:flex;flex-direction:column;gap:14px;}}
    .sc-chart-chart-col{{display:flex;align-items:center;justify-content:center;min-height:260px;}}
    /* ── charts.js compat: light-theme overrides ── */
    :root{{
      --chart3:  #10b981;
      --chart4:  #f59e0b;
      --chart5:  #3b82f6;
      --chart6:  #ef4444;
    }}
    [data-animate]{{opacity:0;transform:translateY(22px);transition:opacity .65s cubic-bezier(.16,1,.3,1),transform .65s cubic-bezier(.16,1,.3,1);}}
    [data-animate="scale"]{{transform:scale(.88);}}
    [data-animate="slide-left"]{{opacity:0;transform:translateX(-32px);}}
    [data-animate].visible{{opacity:1;transform:none;}}
    .progress-bar{{position:fixed;top:0;left:0;height:2px;background:linear-gradient(90deg,var(--accent),var(--accent2));width:0%;transition:width .3s ease;z-index:100;}}
    .nav-dots{{position:fixed;right:18px;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;gap:8px;z-index:100;}}
    .nav-dots button{{width:6px;height:6px;border-radius:50%;border:none;background:rgba(218,119,86,.2);cursor:pointer;transition:background .2s,transform .2s;padding:0;}}
    .nav-dots button.active{{background:var(--accent);transform:scale(1.6);}}
    .slide-counter{{position:fixed;bottom:16px;right:18px;font-size:11px;color:var(--text-tertiary);z-index:100;}}
    #presenterBtn{{position:fixed;bottom:16px;left:18px;background:rgba(253,250,245,.9);border:1px solid rgba(218,119,86,.2);color:var(--text-secondary);font-size:11px;padding:5px 10px;border-radius:5px;cursor:pointer;z-index:100;}}
    @media (max-width:640px){{.feature-grid,.features-grid{{grid-template-columns:1fr;}}.slide-content.two-col{{grid-template-columns:1fr;}}.stats-row{{gap:28px;}}}}
  </style>
</head>
<body>
<div class="progress-bar" id="progressBar" role="progressbar" aria-valuemin="0" aria-valuemax="100"></div>
<nav class="nav-dots" id="navDots" aria-label="Slide navigation"></nav>
<div class="slide-counter"><span id="currentSlide">1</span> / <span id="totalSlides">?</span></div>
<button id="presenterBtn">演讲者视图 [P]</button>
<main class="slides-container" id="slidesContainer" role="main">

{slides_html}

</main>
<script>
  const container=document.getElementById('slidesContainer');
  const slides=Array.from(container.querySelectorAll('.slide'));
  const total=slides.length; let current=0;
  document.getElementById('totalSlides').textContent=total;
  const CHANNEL='slides-presenter-sync'; let bc=null; try{{bc=new BroadcastChannel(CHANNEL);}}catch(e){{}}
  const dotsEl=document.getElementById('navDots');
  slides.forEach((_,i)=>{{const b=document.createElement('button');b.setAttribute('aria-label',`Slide ${{i+1}}`);b.onclick=()=>goTo(i);dotsEl.appendChild(b);}});
  function updateChrome(i){{current=i;document.getElementById('currentSlide').textContent=i+1;const pct=total>1?(i/(total-1))*100:100;document.getElementById('progressBar').style.width=pct+'%';dotsEl.querySelectorAll('button').forEach((b,j)=>b.classList.toggle('active',j===i));slides.forEach((s,j)=>s.setAttribute('aria-current',j===i?'true':'false'));if(bc)bc.postMessage({{type:'slide-change',payload:{{index:i,total,notes:slides[i]?.dataset?.notes||''}}}});}}
  function goTo(i){{const idx=Math.max(0,Math.min(i,total-1));slides[idx].scrollIntoView({{behavior:'smooth'}});}}
  const obs=new IntersectionObserver((entries)=>{{entries.forEach(e=>{{if(!e.isIntersecting)return;const i=slides.indexOf(e.target);if(i<0)return;updateChrome(i);e.target.querySelectorAll('[data-animate]').forEach((el,j)=>{{setTimeout(()=>el.classList.add('visible'),j*130);}});}});}},{{threshold:0.55}});
  slides.forEach(s=>obs.observe(s));
  document.addEventListener('keydown',e=>{{if(['INPUT','TEXTAREA'].includes(e.target.tagName))return;if(['ArrowRight','ArrowDown',' '].includes(e.key)){{e.preventDefault();goTo(current+1);}}else if(['ArrowLeft','ArrowUp'].includes(e.key)){{e.preventDefault();goTo(current-1);}}else if(e.key==='Home'){{e.preventDefault();goTo(0);}}else if(e.key==='End'){{e.preventDefault();goTo(total-1);}}else if(e.key.toLowerCase()==='f'){{if(!document.fullscreenElement)document.documentElement.requestFullscreen?.();else document.exitFullscreen?.();}}}});
  let touchY=0; container.addEventListener('touchstart',e=>{{touchY=e.touches[0].clientY;}},{{passive:true}}); container.addEventListener('touchend',e=>{{const d=touchY-e.changedTouches[0].clientY;if(Math.abs(d)>50)goTo(current+(d>0?1:-1));}},{{passive:true}});
  let wl=false; container.addEventListener('wheel',e=>{{if(wl)return;wl=true;goTo(current+(e.deltaY>0?1:-1));setTimeout(()=>wl=false,800);}},{{passive:true}});
  if(bc)bc.addEventListener('message',e=>{{if(e.data?.type==='request-init')bc.postMessage({{type:'init',payload:{{index:current,total,notes:slides[current]?.dataset?.notes||''}}}});if(e.data?.type==='navigate')goTo(e.data.payload.index);}});
  updateChrome(0); setTimeout(()=>{{slides[0].querySelectorAll('[data-animate]').forEach((el,i)=>setTimeout(()=>el.classList.add('visible'),100+i*130));}},200);
</script>
</body>
</html>""")


# ── CLI entrypoint ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Generate a slide deck HTML from a JSON outline, PPTX-extracted JSON, or a topic (--expand).',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('input', nargs='?', default=None, help='Path to JSON outline file (omit when using --expand)')
    parser.add_argument('--expand', metavar='TOPIC', default=None,
                        help='Generate a full deck from a brief topic description using an LLM')
    parser.add_argument('--slides', type=int, default=10,
                        help='Number of slides to generate with --expand (default: 10, max: 20)')
    parser.add_argument('--template', '-t', choices=list(TEMPLATE_FILES.keys()), default=None,
                        help='Template name (auto-detected if omitted)')
    parser.add_argument('--output', '-o', default=None, help='Output HTML file path')
    parser.add_argument('--title', default=None, help='Override deck title')
    parser.add_argument('--lang', default='zh-CN', help='HTML lang attribute value')
    parser.add_argument('--open', action='store_true', help='Open output in browser')
    parser.add_argument('--dry-run', action='store_true', help='Print HTML to stdout only')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    # ── --expand mode: generate outline from topic with LLM ──────────────────
    if args.expand:
        if args.verbose:
            print(f'🤖  Expanding topic: "{args.expand}"')
        n_slides = max(4, min(20, args.slides))
        content = _expand_topic(args.expand, n_slides, args.template, args.lang, args.verbose)
        input_stem = re.sub(r'[^\w\u4e00-\u9fff]+', '_', args.expand)[:40]
    else:
        # ── Load input ────────────────────────────────────────────────────────
        if not args.input:
            parser.error('Provide an input JSON file, or use --expand TOPIC to generate from a topic.')
        input_path = Path(args.input)
        if not input_path.exists():
            sys.exit(f'❌  File not found: {input_path}')

        if args.verbose:
            print(f'📂  Loading: {input_path}')

        with open(input_path, encoding='utf-8') as f:
            raw_text = f.read()
        try:
            content = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            lines = raw_text.splitlines()
            err_line = exc.lineno - 1
            start = max(0, err_line - 2)
            end = min(len(lines), err_line + 3)
            context = '\n'.join(
                f'  {"→ " if i == err_line else "  "}{i+1}: {lines[i]}'
                for i, _ in enumerate(lines[start:end], start=start)
            )
            sys.exit(
                f'❌  JSON parse error in {input_path}:\n'
                f'    {exc.msg} at line {exc.lineno}, column {exc.colno}\n'
                f'\n{context}\n'
                f'\n  Tip: validate with:  python3 -m json.tool {input_path}'
            )

        # Handle both raw outline and PPTX-extracted format
        if content.get('slides') and isinstance(content['slides'][0], dict):
            first = content['slides'][0]
            is_pptx_format = (
                'layout' in first or
                'body_paragraphs' in first or
                ('number' in first and 'type' not in first)
            )
            if is_pptx_format:
                source_total = content.get('total_slides', len(content['slides']))
                if args.verbose:
                    print(f'  ↳ Detected PPTX-extracted format ({source_total} slides), normalising…')
                content['slides'] = _normalise_pptx(content['slides'])
                if len(content['slides']) != source_total:
                    sys.exit(
                        f'❌  Slide count mismatch after normalisation: '
                        f'expected {source_total}, got {len(content["slides"])}. Aborting.'
                    )

                # Inject theme colours from PPTX into slides so detect_template
                # can use them (Fix-6 in detect_template already scans 'theme_color').
                # We propagate the accent1 colour (primary brand colour) to every
                # slide; if accent1 is absent, fall back to dk1.
                pptx_theme = content.get('theme_colors') or {}
                _theme_hex = (
                    pptx_theme.get('accent1') or
                    pptx_theme.get('dk1') or
                    pptx_theme.get('dk2')
                )
                if _theme_hex:
                    if args.verbose:
                        print(f'  ↳ PPTX theme colour: {_theme_hex} (injected into slides)')
                    for _s in content['slides']:
                        if not _s.get('theme_color'):   # don't overwrite if user set it
                            _s['theme_color'] = _theme_hex

        input_stem = input_path.stem

    if args.verbose:
        print(f'  ↳ {len(content.get("slides",[]))} slides')

    # ── Direction 5: Smart Chart Enrichment ──────────────────────────────────
    # Automatically insert companion chart slides after numeric stats slides.
    # Can be suppressed per-slide with "skip_chart": true in the JSON.
    _before = len(content.get('slides', []))
    content['slides'] = _enrich_charts(content.get('slides', []))
    _after = len(content.get('slides', []))
    if args.verbose and _after > _before:
        print(f'  ↳ _enrich_charts: inserted {_after - _before} companion chart slide(s)')

    # Generate
    html = generate(content, args.template, args.title, args.lang, args.verbose)

    if args.dry_run:
        print(html)
        return

    # Determine output path
    if args.output:
        out_path = Path(args.output)
    else:
        out_path = Path(input_stem + '_slides.html')

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'✅  Generated: {out_path}  ({len(content.get("slides",[]))} slides, {len(html)//1024}KB)')

    if args.open:
        import webbrowser
        webbrowser.open(out_path.resolve().as_uri())


def _expand_topic(topic: str, n_slides: int, template: str | None,
                  lang: str, verbose: bool) -> dict:
    """
    Use an LLM to expand a brief topic description into a full slide outline (dict).

    Resolution order (first available wins):
      1. ANTHROPIC_API_KEY  → Anthropic Messages API  (claude-3-5-haiku-latest)
      2. OPENAI_API_KEY     → OpenAI Chat API          (gpt-4o-mini)
      3. codebuddy CLI      → `codebuddy -p <prompt>`  (any locally configured model)

    Returns a dict matching our outline JSON schema:
      { title, subtitle, author, date, template, slides: [...] }
    """
    is_chinese = lang.startswith('zh') or _detect_cjk(topic)
    lang_hint   = '用中文回复。' if is_chinese else 'Reply in English.'
    slide_types = (
        '"title","text","bullets","two-col","stats","features","quote","chart","image","cta","divider"'
    )
    chart_types_hint = (
        'chart_type choices: bar|line|area|donut|hbar|progress|radar|sankey|treemap|waterfall|bullet|scatter|gauge. '
        'For financial delta analysis use waterfall; for target-vs-actual KPI use bullet; '
        'for correlation data use scatter; for single metric completion use gauge.'
    )
    template_hint = f'Preferred template: "{template}".' if template else ''
    prompt = dedent(f"""\
        You are a professional presentation designer. Create a complete slide deck outline in JSON.

        Topic: {topic}
        Slides: exactly {n_slides}
        {lang_hint}
        {template_hint}

        {chart_types_hint}

        Return ONLY valid JSON — no markdown fences, no explanations.
        The JSON must follow this schema exactly:

        {{
          "title": "Deck Title",
          "subtitle": "Optional subtitle",
          "author": "",
          "date": "{_today_str()}",
          "slides": [
            // Allowed types: {slide_types}
            // title slide example:
            {{"type":"title","title":"Main Title","subtitle":"Subtitle","eyebrow":"Category · Date"}},
            // bullets example:
            {{"type":"bullets","title":"Section","items":["Point 1","Point 2","Point 3"]}},
            // stats example:
            {{"type":"stats","title":"Key Metrics","stats":[{{"value":"95%","label":"Satisfaction"}},{{"value":"2.4M","label":"Users"}}]}},
            // two-col example:
            {{"type":"two-col","title":"Comparison","left":{{"title":"Before","body":"..."}},"right":{{"title":"After","body":"..."}}}},
            // features example:
            {{"type":"features","title":"Features","items":[{{"icon":"✦","title":"Feat 1","desc":"Desc"}},{{"icon":"◈","title":"Feat 2","desc":"Desc"}}]}},
            // divider example:
            {{"type":"divider","label":"Section Title"}},
            // cta example:
            {{"type":"cta","title":"Get Started","subtitle":"Ready?","primary_cta":"Start Now"}},
            // chart-full example (chart fills the slide):
            {{"type":"chart","title":"Revenue Growth","chart_type":"bar","layout":"chart-full",
              "chart_data":{{"labels":["Q1","Q2","Q3","Q4"],"datasets":[{{"label":"Revenue","values":[42,68,55,91]}}]}}}},
            // chart-split example (text left, chart right — great for storytelling):
            {{"type":"chart","title":"Revenue Growth","chart_type":"line","layout":"chart-split",
              "body":"说明文字或分析洞察写在这里，最多 80 字。",
              "chart_data":{{"labels":["Q1","Q2","Q3","Q4"],"datasets":[{{"label":"Revenue","values":[42,68,55,91]}}]}}}}
          ]
        }}

        Guidelines:
        - First slide must be type "title"
        - Last slide should be type "cta" or "divider"
        - Vary slide types for visual rhythm
        - Keep text concise and impactful — this is a presentation, not a document
        - For Chinese topics, use Chinese content throughout
        - Items arrays should have 3-5 items max
        - Body text max 80 characters per paragraph
        - When a "stats" or "comparison" slide would benefit from a data visualization, prefer "chart" type with appropriate chart_type
        - Use "chart-split" layout when you want to pair a chart with an insight sentence
    """).strip()

    raw = None
    source = None

    # ── Strategy 1: Anthropic API ─────────────────────────────────────────────
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if api_key and raw is None:
        try:
            import urllib.request, urllib.error
            payload = json.dumps({
                'model': 'claude-3-5-haiku-latest',
                'max_tokens': 4096,
                'messages': [{'role': 'user', 'content': prompt}],
            }).encode()
            req = urllib.request.Request(
                'https://api.anthropic.com/v1/messages',
                data=payload,
                headers={
                    'Content-Type': 'application/json',
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01',
                },
                method='POST',
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
            raw = result['content'][0]['text'].strip()
            source = 'Anthropic API'
        except Exception as e:
            if verbose:
                print(f'  ⚠  Anthropic API failed: {e}')

    # ── Strategy 2: OpenAI API ────────────────────────────────────────────────
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key and raw is None:
        try:
            import urllib.request, urllib.error
            payload = json.dumps({
                'model': 'gpt-4o-mini',
                'max_tokens': 4096,
                'messages': [
                    {'role': 'system', 'content': 'You are a professional presentation designer.'},
                    {'role': 'user', 'content': prompt},
                ],
            }).encode()
            req = urllib.request.Request(
                'https://api.openai.com/v1/chat/completions',
                data=payload,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}',
                },
                method='POST',
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
            raw = result['choices'][0]['message']['content'].strip()
            source = 'OpenAI API'
        except Exception as e:
            if verbose:
                print(f'  ⚠  OpenAI API failed: {e}')

    # ── Strategy 3: codebuddy CLI ─────────────────────────────────────────────
    if raw is None:
        # Search common install locations in addition to PATH
        _codebuddy_candidates = [
            'codebuddy',
            os.path.expanduser('~/.local/bin/codebuddy'),
            os.path.expanduser('~/.npm-global/bin/codebuddy'),
            '/usr/local/bin/codebuddy',
            '/opt/homebrew/bin/codebuddy',
        ]
        _cb_bin = None
        for _c in _codebuddy_candidates:
            if os.path.isfile(_c) and os.access(_c, os.X_OK):
                _cb_bin = _c
                break
        if _cb_bin is None:
            # Fallback: let subprocess PATH resolution try
            _cb_bin = 'codebuddy'
        try:
            result = subprocess.run(
                [_cb_bin, '-p', prompt, '--output-format', 'text'],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0 and result.stdout.strip():
                raw = result.stdout.strip()
                source = 'codebuddy CLI'
            else:
                if verbose and result.stderr:
                    print(f'  ⚠  codebuddy CLI stderr: {result.stderr[:200]}')
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            if verbose:
                print(f'  ⚠  codebuddy CLI failed: {e}')

    # ── Strategy 4: built-in template generator (no API key required) ─────────
    if raw is None:
        print(
            '\n[WARNING] No LLM backend available (ANTHROPIC_API_KEY / OPENAI_API_KEY not set, '
            'codebuddy CLI not found).\n'
            '          Falling back to built-in outline template — content is GENERIC PLACEHOLDER.\n'
            '          Re-run with a real API key or refine the generated content manually.\n'
        )
        raw = _builtin_outline(topic, n_slides, lang)
        source = 'built-in template'

    if verbose:
        print(f'  ↳ LLM response received via {source} ({len(raw)} chars)')

    # ── Parse JSON from LLM output ────────────────────────────────────────────
    # Strip markdown code fences if present
    raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.MULTILINE)
    raw = re.sub(r'\s*```$', '', raw, flags=re.MULTILINE)
    raw = raw.strip()

    # Find the outermost JSON object
    brace_start = raw.find('{')
    brace_end   = raw.rfind('}')
    if brace_start != -1 and brace_end > brace_start:
        raw = raw[brace_start:brace_end + 1]

    try:
        outline = json.loads(raw)
    except json.JSONDecodeError as exc:
        if verbose:
            print(f'  Raw LLM output (first 500 chars):\n{raw[:500]}')
        sys.exit(
            f'❌  LLM returned invalid JSON: {exc.msg} at line {exc.lineno}, col {exc.colno}.\n'
            f'    Try running again — LLM output is non-deterministic.'
        )

    # Basic validation / repair
    if 'slides' not in outline:
        sys.exit('❌  LLM JSON is missing required "slides" array.')
    if not outline.get('title'):
        outline['title'] = topic

    if verbose:
        print(f'  ↳ Parsed {len(outline["slides"])} slides from LLM output')

    return outline


def _builtin_outline(topic: str, n_slides: int, lang: str) -> str:
    """
    Built-in fallback outline generator — no LLM required.

    Produces a structurally valid JSON outline with placeholder content
    derived from the topic string. Used when no API key or CLI is available.
    The output is intentionally generic; users should refine content manually
    or re-run with a real LLM backend once credentials are configured.
    """
    is_zh = lang.startswith('zh') or _detect_cjk(topic)
    today = _today_str()

    if is_zh:
        lbl_intro      = '简介'
        lbl_background = '背景与现状'
        lbl_core       = '核心内容'
        lbl_analysis   = '深度分析'
        lbl_data       = '数据与成果'
        lbl_challenges = '挑战与机遇'
        lbl_cases      = '典型案例'
        lbl_future     = '未来展望'
        lbl_summary    = '总结'
        lbl_action     = '行动建议'
        lbl_close      = '感谢'
        cta_title      = '立即行动'
        cta_sub        = '请联系我们了解更多'
        cta_btn        = '了解更多'
        div_body       = f'{topic} — 深度解析'
        item_pfx       = ['关键要点一：相关概念与定义', '关键要点二：发展历程与趋势',
                          '关键要点三：核心价值与意义', '关键要点四：实践路径与方法',
                          '关键要点五：挑战与应对策略']
        body_text      = (f'{topic}正在深刻改变行业格局。'
                          f'通过系统性研究与实践探索，'
                          f'我们发现其中蕴含着巨大的价值与潜力。')
        stats_items    = [
            {'value': '85%', 'label': '采用增长率'},
            {'value': '3.2×', 'label': '效率提升'},
            {'value': '$240B', 'label': '市场规模'},
        ]
        features_items = [
            {'icon': '✦', 'title': '核心优势', 'desc': '深度整合，释放价值'},
            {'icon': '◈', 'title': '技术支撑', 'desc': '前沿技术，持续演进'},
            {'icon': '⬡', 'title': '场景落地', 'desc': '行业实践，验证效果'},
        ]
        quote_text  = f'{topic}不仅是技术革新，更是思维方式的根本转变。'
        quote_auth  = '行业专家'
        eyebrow_txt = f'{topic} · {today}'
    else:
        lbl_intro      = 'Introduction'
        lbl_background = 'Background & Context'
        lbl_core       = 'Core Concepts'
        lbl_analysis   = 'Deep Dive'
        lbl_data       = 'Data & Results'
        lbl_challenges = 'Challenges & Opportunities'
        lbl_cases      = 'Case Studies'
        lbl_future     = 'Future Outlook'
        lbl_summary    = 'Summary'
        lbl_action     = 'Action Plan'
        lbl_close      = 'Thank You'
        cta_title      = 'Get Started'
        cta_sub        = 'Reach out to learn more'
        cta_btn        = 'Learn More'
        div_body       = f'{topic} — In Depth'
        item_pfx       = ['Key Point 1: Core definitions and concepts',
                          'Key Point 2: Historical context and trends',
                          'Key Point 3: Value proposition',
                          'Key Point 4: Implementation approaches',
                          'Key Point 5: Challenges and mitigation']
        body_text      = (f'{topic} is reshaping the industry landscape. '
                          f'Through systematic research and hands-on practice, '
                          f'we have uncovered significant value and untapped potential.')
        stats_items    = [
            {'value': '85%', 'label': 'Adoption Growth'},
            {'value': '3.2×', 'label': 'Efficiency Gain'},
            {'value': '$240B', 'label': 'Market Size'},
        ]
        features_items = [
            {'icon': '✦', 'title': 'Core Advantage', 'desc': 'Deep integration, unlocking value'},
            {'icon': '◈', 'title': 'Technology', 'desc': 'Cutting-edge, continuously evolving'},
            {'icon': '⬡', 'title': 'Real-World Use', 'desc': 'Proven in production environments'},
        ]
        quote_text  = f'{topic} is not just a technology shift — it\'s a fundamental change in thinking.'
        quote_auth  = 'Industry Expert'
        eyebrow_txt = f'{topic} · {today}'

    # ── Build slide sequence based on requested n_slides ─────────────────────
    # We have a fixed "library" of slide archetypes; we pick the first n_slides
    # from this library (always starting with title, always ending with cta).
    library = [
        # 0 — always title
        {'type': 'title', 'title': topic, 'subtitle': body_text[:80], 'eyebrow': eyebrow_txt},
        # 1
        {'type': 'text',    'title': lbl_background, 'body': body_text},
        # 2
        {'type': 'bullets', 'title': lbl_core,       'items': item_pfx[:4]},
        # 3
        {'type': 'divider', 'label': div_body},
        # 4
        {'type': 'features', 'title': lbl_core, 'subtitle': body_text[:60], 'items': features_items},
        # 5
        {'type': 'stats',   'title': lbl_data,       'stats': stats_items},
        # 6
        {'type': 'two-col', 'title': lbl_analysis,
         'left':  {'title': lbl_challenges, 'body': item_pfx[4]},
         'right': {'title': lbl_future,     'body': item_pfx[1]}},
        # 7
        {'type': 'quote',   'quote': quote_text, 'author': quote_auth},
        # 8
        {'type': 'bullets', 'title': lbl_action,  'items': item_pfx[:3]},
        # 9
        {'type': 'bullets', 'title': lbl_summary, 'items': item_pfx[2:5]},
        # 10 — always cta (last)
        {'type': 'cta', 'title': cta_title, 'subtitle': cta_sub,
         'primary_cta': cta_btn},
    ]

    # Pin slide 0 (title) and last slot (cta).
    # Fill middle slots from library[1..-2], cycling if n_slides > len(library).
    if n_slides <= 2:
        slides = [library[0], library[-1]]
    else:
        middle_needed = n_slides - 2
        middle_pool   = library[1:-1]
        import itertools
        middle = list(itertools.islice(itertools.cycle(middle_pool), middle_needed))
        slides = [library[0]] + middle + [library[-1]]

    outline = {
        'title':    topic,
        'subtitle': '',
        'author':   '',
        'date':     today,
        'slides':   slides,
    }
    return json.dumps(outline, ensure_ascii=False)


def _detect_cjk(text: str) -> bool:
    """Heuristic: does the string contain CJK characters?"""
    return any('\u4e00' <= ch <= '\u9fff' for ch in text)


def _today_str() -> str:
    from datetime import date
    return date.today().strftime('%Y-%m')


def _normalise_pptx(raw_slides: list) -> list:
    """
    Convert PPTX-extracted slides (output of extract_pptx.py) to our outline format.

    CRITICAL: Every input slide maps to EXACTLY ONE output entry.
    No slides are merged, skipped, or omitted — not even blank ones.
    """
    PPTX_LAYOUT_TO_TYPE = {
        'title':        'title',
        'section':      'divider',
        'statement':    'text',
        'image-text':   'image',
        'content-list': 'bullets',
        'table':        'table',   # preserve table structure (was incorrectly 'bullets')
        'chart':        'chart',
        'content':      'bullets',
        'two-col':      'two-col',
        'stats':        'stats',
    }

    result = []
    for i, s in enumerate(raw_slides):
        slide_num   = s.get('number', i + 1)
        pptx_layout = s.get('layout', 'content')
        slide_title = s.get('title') or f'Slide {slide_num}'
        notes       = s.get('notes') or ''

        # ── body_paragraphs → flat list of text strings ──────────────────────
        body_paras = s.get('body_paragraphs', [])
        body_texts = [
            p['text'] if isinstance(p, dict) else str(p)
            for p in body_paras
            if (p.get('text') if isinstance(p, dict) else str(p)).strip()
        ]

        # ── tables → bullet-friendly rows ────────────────────────────────────
        table_lines = []
        for tbl in (s.get('tables') or []):
            if tbl.get('headers'):
                table_lines.append(' | '.join(tbl['headers']))
            for row in (tbl.get('rows') or []):
                if any(cell.strip() for cell in row):
                    table_lines.append(' | '.join(row))

        # ── SmartArt → bullet items ───────────────────────────────────────────
        smartart_texts = [str(t) for t in (s.get('smartart') or []) if str(t).strip()]

        # ── Primary image (first extracted image) ────────────────────────────
        images        = s.get('images') or []
        primary_image = images[0] if images else None

        # ── Determine slide type ─────────────────────────────────────────────
        # Start with layout-based mapping, then apply smart overrides.
        # NOTE: the title-force for i==0 is applied LAST so that smart
        # promotions (stats) can still take effect on cover slides that
        # happen to contain numeric data.
        slide_type = PPTX_LAYOUT_TO_TYPE.get(pptx_layout, 'bullets')

        # IMPROVED: Better handling of mixed content
        # Priority: table > image > text/bullets
        # If there are actual tables, prioritize table type
        has_tables = bool(s.get('tables'))
        if has_tables and table_lines:
            slide_type = 'table'
        # Override to 'image' only when there's a primary image AND very little text
        # For mixed image+text, keep as mixed content rather than throwing away text
        elif primary_image and not body_texts and not table_lines and not smartart_texts:
            slide_type = 'image'
        
        # Collect all text items before stats detection
        all_items = body_texts + table_lines + smartart_texts

        # Smart type promotion: if content looks like stats (few items with numeric values)
        # Apply before title-force so a numeric first slide can become stats when appropriate
        if slide_type == 'bullets' and len(all_items) <= 4 and all_items:
            import re as _re
            numeric_pat = _re.compile(r'\b\d[\d,\.%×xX+\-]*[KMBTkmbt%]?\b')
            if sum(1 for it in all_items if numeric_pat.search(it)) >= 2:
                slide_type = 'stats'

        # Force first slide to title when layout suggests it (applied after promotions,
        # but only if the slide wasn't already promoted to a more specific type)
        if i == 0 and pptx_layout in ('title', 'content', 'statement') and slide_type not in ('stats', 'image'):
            slide_type = 'title'

        # ── Build outline entry ───────────────────────────────────────────────
        entry: dict = {
            'type':  slide_type,
            'title': slide_title,
            'notes': notes,
        }

        # ── Always include primary image if available (BUG FIX) ────────────────
        # Previously images were only shown for pure-image slides.
        # Now all slide types can access the extracted image.
        if primary_image:
            entry['image'] = primary_image

        if slide_type == 'title':
            subtitle = s.get('subtitle') or (body_texts[0] if body_texts else '')
            entry['subtitle'] = subtitle[:180] if subtitle else ''
            entry['eyebrow'] = s.get('eyebrow') or ''

        elif slide_type == 'divider':
            entry['label'] = slide_title

        elif slide_type == 'image':
            entry['image_url'] = primary_image or ''
            # IMPROVED: Preserve ALL body text, not just first 2
            # Use newline separation for clarity, no character limit
            if body_texts:
                entry['caption'] = '\n'.join(body_texts)
            if smartart_texts:
                caption_parts = (entry.get('caption', '') or '').split('\n')
                caption_parts.extend(smartart_texts)
                entry['caption'] = '\n'.join(caption_parts)

        elif slide_type == 'stats':
            # Parse "value label" pairs, where value is a numeric token.
            # Fix: find the numeric token first (right side), rest is label.
            import re as _re2
            _num_pat = _re2.compile(
                r'(?<!\w)(\d[\d,\.]*(?:[KMBTkmbt%×xX]|\s*[KMBTkmbt%×xX])?(?:\+|\-)?)\b'
            )
            parsed_stats = []
            for it in all_items:
                it_s = it.strip()
                m = _num_pat.search(it_s)
                if m:
                    value = m.group(0).strip()
                    label = (it_s[:m.start()] + it_s[m.end():]).strip()
                    parsed_stats.append({'value': value, 'label': label or it_s})
                else:
                    # No numeric part found — put entire text as value
                    parsed_stats.append({'value': it_s, 'label': ''})
            entry['stats'] = parsed_stats

        elif slide_type == 'two-col':
            mid = len(all_items) // 2 or 1
            entry['left']  = {'title': '', 'body': ' '.join(all_items[:mid])}
            entry['right'] = {'title': '', 'body': ' '.join(all_items[mid:])}

        elif slide_type == 'table':
            # Preserve structured table data from the PPTX extraction.
            # Use the first table on the slide; fall back to bullet list if none.
            raw_tables = s.get('tables') or []
            if raw_tables:
                first = raw_tables[0]
                entry['headers'] = first.get('headers') or []
                entry['rows']    = first.get('rows') or []
                # IMPROVED: Include ALL remaining body text and smartart as full caption (no truncation)
                # This ensures mixed table+text content doesn't lose text items
                caption_parts = []
                if body_texts:
                    caption_parts.extend(body_texts)
                if smartart_texts:
                    caption_parts.extend(smartart_texts)
                if caption_parts:
                    entry['caption'] = '\n'.join(caption_parts)
            else:
                # No structured table data — fall back to bullets
                # IMPROVED: Include items from other sources (smartart, etc)
                entry['type']  = 'bullets'
                entry['items'] = all_items if all_items else ['']

        else:
            # bullets / text
            if all_items:
                if slide_type == 'text' or (len(all_items) == 1 and slide_type != 'bullets'):
                    entry['type'] = 'text'
                    entry['body'] = all_items[0]
                else:
                    entry['type']  = 'bullets'
                    entry['items'] = all_items
            else:
                # Blank slide — still emit a placeholder so slide count is preserved
                entry['type'] = 'text'
                entry['body'] = ''

        result.append(entry)

    return result


def _enrich_charts(slides: list) -> list:
    """
    Direction 5 — Smart Chart Enrichment
    ═══════════════════════════════════════════════════════════════════════════════
    Scans the slide list for "stats" slides that contain parseable numeric values
    and automatically inserts a companion chart slide immediately after each one.

    Rules:
    - Only applies to slides with type == "stats"
    - Requires at least 2 stat items where the value is a pure number (int/float),
      possibly with common suffixes like K/M/B/% — but NOT percentage suffix alone,
      because percentage bars are already shown in progress-style stats layouts
    - Auto-selects chart type:
        · All values are percentages (%) → donut chart
        · Otherwise → horizontal bar chart (hbar), great for labelled comparisons
    - The companion slide is flagged with "_auto_chart": True so the caller can
      identify and optionally suppress it
    - If the stats slide already has a "chart_data" key, skip (user-defined chart)
    - If the stats slide has "skip_chart": True, skip it

    Returns a new list with companion chart slides injected.
    """
    import re as _re

    _pure_num_pat = _re.compile(
        r'^(?P<num>[\d,]+(?:\.\d+)?)(?P<suffix>\s*[KMBkmb%]|\s*万|\s*亿)?$',
        _re.UNICODE,
    )

    def _parse_numeric(value_str: str):
        """
        Try to parse a stat value string into a float.
        Returns (float_val, suffix) or (None, None) if not parseable.
        """
        v = str(value_str).strip().replace(',', '')
        m = _pure_num_pat.match(v)
        if not m:
            return None, None
        num = float(m.group('num'))
        suffix = (m.group('suffix') or '').strip().lower()
        # Scale multipliers
        scale = {'k': 1e3, 'm': 1e6, 'b': 1e9, '万': 1e4, '亿': 1e8}.get(suffix, 1)
        return num * scale, suffix

    result = []
    for slide in slides:
        result.append(slide)

        # Only process stats slides without a user-defined chart override
        if slide.get('type') != 'stats':
            continue
        if slide.get('chart_data'):
            continue
        if slide.get('skip_chart'):
            continue

        stats = slide.get('stats', [])
        if not stats:
            continue

        # Parse all stat values
        parsed = []
        for st in stats:
            val_str = str(st.get('value', '')).strip()
            num, suffix = _parse_numeric(val_str)
            if num is not None:
                parsed.append({'label': st.get('label', val_str), 'num': num, 'suffix': suffix, 'raw': val_str})

        # Need at least 2 parseable numeric stats (lowered from 3 for better usability)
        if len(parsed) < 2:
            continue

        # Decide chart type
        all_pct = all(p['suffix'] == '%' for p in parsed)
        has_pct = any(p['suffix'] == '%' for p in parsed)

        # Mixed units (some % some absolute) → not meaningful to chart, skip
        if has_pct and not all_pct:
            continue

        if all_pct:
            chart_type = 'donut'
        else:
            # Check value spread: if max/min > 1000x, use progress (relative %)
            # rather than hbar where one bar would dwarf all others
            vals = [p['num'] for p in parsed]
            v_min = min(v for v in vals if v > 0) if any(v > 0 for v in vals) else 1
            v_max = max(vals)
            if v_max / v_min > 1000:
                # Values too spread: normalise to relative percentages, use progress
                chart_type = 'progress'
                total_sum = sum(vals) or 1
                # Override values to percentage of total
                for p in parsed:
                    p['display_pct'] = round(p['num'] / total_sum * 100, 1)
            else:
                chart_type = 'hbar'

        # Build chart_data
        labels = [p['label'] or p['raw'] for p in parsed]

        if chart_type == 'donut':
            values = [p['num'] for p in parsed]
            chart_data = {
                'labels': labels,
                'datasets': [{'label': slide.get('title', ''), 'values': values}],
            }
        elif chart_type == 'progress':
            # Normalised to percentage of total sum
            values = [p['display_pct'] for p in parsed]
            chart_data = {
                'labels': labels,
                'datasets': [{'label': slide.get('title', ''), 'values': values}],
            }
        else:
            # hbar — horizontal bar, great for labelled stat comparisons
            values = [p['num'] for p in parsed]
            chart_data = {
                'labels': labels,
                'datasets': [{'label': slide.get('title', ''), 'values': values}],
            }

        # Build the companion chart slide
        chart_slide = {
            'type': 'chart',
            'title': slide.get('title', ''),
            'chart_type': chart_type,
            'chart_data': chart_data,
            'chart_options': {'showGrid': True},
            'layout': 'chart-full',
            '_auto_chart': True,   # marker so callers can identify auto-generated slides
        }
        # Carry over notes and bg if set
        if slide.get('notes'):
            chart_slide['notes'] = slide['notes']
        if slide.get('bg'):
            chart_slide['bg'] = slide['bg']

        result.append(chart_slide)

    return result


if __name__ == '__main__':
    main()
