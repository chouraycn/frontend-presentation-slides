#!/usr/bin/env python3
"""
parse_html.py — Reverse-parse a slide HTML back to a structured JSON outline.
═══════════════════════════════════════════════════════════════════════════════
Takes a frontend-slides HTML presentation and extracts all slides into the
same JSON format that generate_slides.py consumes. This enables a two-way
editing workflow:

  HTML  →  parse_html.py  →  outline.json
                                  ↓  (edit in any text editor)
  HTML  ←  generate_slides.py  ←  outline.json

Usage:
    python3 scripts/parse_html.py <input.html> [options]

Examples:
    python3 scripts/parse_html.py out.html                     # → out.json
    python3 scripts/parse_html.py presentation.html -o edit.json
    python3 scripts/parse_html.py deck.html --pretty           # pretty-print JSON
    python3 scripts/parse_html.py deck.html --stats            # summary only, no file

Options:
    --output, -o   Output JSON path (default: <input_stem>.json)
    --pretty       Pretty-print JSON with indent=2 (default: compact)
    --stats        Print slide count summary only, do not write file
    --verbose, -v  Print each extracted slide as it is parsed

Requirements:
    pip3 install beautifulsoup4
"""

import argparse
import json
import re
import sys
from pathlib import Path


# ── Dependency check ──────────────────────────────────────────────────────────

def check_deps():
    try:
        from bs4 import BeautifulSoup  # noqa: F401
    except ImportError:
        print("❌ Missing dependency: beautifulsoup4")
        print("   Run: pip3 install beautifulsoup4")
        sys.exit(1)


# ── Helper utilities ──────────────────────────────────────────────────────────

def clean(text):
    """Strip whitespace and collapse internal newlines."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip())


def elem_text(el, selector, default=""):
    """Find first matching element and return its clean text."""
    found = el.select_one(selector)
    return clean(found.get_text()) if found else default


def detect_template(soup):
    """Guess the template name from CSS class on <body> or <html>."""
    # Check <body> class
    body = soup.find("body")
    if body:
        classes = " ".join(body.get("class", []))
        # Map known body classes to template names
        mapping = {
            "theme-claude-warmth":    "claude-warmth",
            "theme-pitch-deck":       "pitch-deck",
            "theme-product-launch":   "product-launch",
            "theme-quarterly-report": "quarterly-report",
            "theme-tech-talk":        "tech-talk",
            "theme-forai-white":      "forai-white",
            "theme-pash-orange":      "pash-orange",
            "theme-hhart-red":        "hhart-red",
            "theme-dark-elegance":    "dark-elegance",
            "theme-vibrant-energy":   "vibrant-energy",
            "theme-clean-minimal":    "clean-minimal",
        }
        for cls, name in mapping.items():
            if cls in classes:
                return name

    # Fallback: check <title> or meta description
    title_el = soup.find("title")
    if title_el:
        title_text = title_el.get_text().lower()
        for key in ["warmth", "pitch", "product", "quarterly", "tech", "white", "orange", "red",
                    "elegance", "vibrant", "minimal"]:
            if key in title_text:
                return key

    return "claude-warmth"  # safe default


def detect_lang(soup):
    html_el = soup.find("html")
    if html_el and html_el.get("lang"):
        return html_el.get("lang")
    return "zh-CN"


# ── Slide type detectors ──────────────────────────────────────────────────────

def parse_title_slide(slide_el):
    """Slide with big title + subtitle, typically the first slide."""
    data = {"type": "title"}
    eyebrow = slide_el.select_one(".eyebrow, .kicker, .category")
    if eyebrow:
        data["eyebrow"] = clean(eyebrow.get_text())

    h1 = slide_el.select_one("h1, .title-text, .slide-title")
    if h1:
        data["title"] = clean(h1.get_text())

    sub = slide_el.select_one(".subtitle, h2, .slide-subtitle")
    if sub:
        data["subtitle"] = clean(sub.get_text())

    attr = slide_el.select_one(".attr, .author, .byline")
    if attr:
        data["author"] = clean(attr.get_text())

    return data


def parse_bullets_slide(slide_el):
    """Slide containing a <ul>/<ol> list."""
    data = {"type": "bullets"}
    h = slide_el.select_one("h2, h3, .slide-title")
    if h:
        data["title"] = clean(h.get_text())

    sub = slide_el.select_one(".subtitle, .slide-subtitle")
    if sub:
        data["subtitle"] = clean(sub.get_text())

    items = []
    for li in slide_el.select("li"):
        text = clean(li.get_text())
        if text:
            items.append(text)
    if items:
        data["items"] = items

    return data


def parse_stats_slide(slide_el):
    """Slide with big number/label stat cards."""
    data = {"type": "stats"}
    h = slide_el.select_one("h2, h3, .slide-title")
    if h:
        data["title"] = clean(h.get_text())

    stats = []
    # Typical stat block: .stat-card, .stat-item, .metric
    for card in slide_el.select(".stat-card, .stat-item, .metric, .kpi"):
        value_el = card.select_one(".stat-value, .value, .number, strong")
        label_el = card.select_one(".stat-label, .label, span:last-child")
        if value_el:
            stat = {"value": clean(value_el.get_text())}
            if label_el and label_el != value_el:
                stat["label"] = clean(label_el.get_text())
            stats.append(stat)

    if stats:
        data["stats"] = stats

    return data


def parse_two_col_slide(slide_el):
    """Slide split into two columns."""
    data = {"type": "two-col"}
    h = slide_el.select_one("h2, h3, .slide-title")
    if h:
        data["title"] = clean(h.get_text())

    cols = slide_el.select(".col, .column, .left, .right, [class*='col-']")
    if len(cols) >= 2:
        left_el = cols[0]
        right_el = cols[1]

        left_title = left_el.select_one("h3, h4, strong, .col-title")
        left_body_el = left_el.select_one("p, .col-body")
        data["left"] = {
            "title": clean(left_title.get_text()) if left_title else "",
            "body": clean(left_body_el.get_text()) if left_body_el else clean(left_el.get_text()),
        }

        right_title = right_el.select_one("h3, h4, strong, .col-title")
        right_body_el = right_el.select_one("p, .col-body")
        data["right"] = {
            "title": clean(right_title.get_text()) if right_title else "",
            "body": clean(right_body_el.get_text()) if right_body_el else clean(right_el.get_text()),
        }

    return data


def parse_quote_slide(slide_el):
    """Slide with a big blockquote."""
    data = {"type": "quote"}
    q = slide_el.select_one("blockquote, .quote-text, .pullquote")
    if q:
        data["quote"] = clean(q.get_text())

    attr = slide_el.select_one(".attr, .quote-attr, cite, .attribution")
    if attr:
        data["author"] = clean(attr.get_text())

    return data


def parse_features_slide(slide_el):
    """Slide with icon+title+desc feature cards."""
    data = {"type": "features"}
    h = slide_el.select_one("h2, h3, .slide-title")
    if h:
        data["title"] = clean(h.get_text())

    sub = slide_el.select_one(".subtitle, .slide-subtitle")
    if sub:
        data["subtitle"] = clean(sub.get_text())

    items = []
    for card in slide_el.select(".feature-card, .feature-item, .card"):
        icon_el = card.select_one(".icon, .feature-icon, [class*='icon']")
        title_el = card.select_one("h3, h4, strong, .feature-title")
        desc_el = card.select_one("p, .desc, .feature-desc")
        item = {}
        if icon_el:
            item["icon"] = clean(icon_el.get_text()) or "✦"
        if title_el:
            item["title"] = clean(title_el.get_text())
        if desc_el:
            item["desc"] = clean(desc_el.get_text())
        if item.get("title"):
            items.append(item)

    if items:
        data["items"] = items

    return data


def parse_text_slide(slide_el):
    """Generic text/section slide."""
    data = {"type": "text"}
    h = slide_el.select_one("h2, h3, .slide-title")
    if h:
        data["title"] = clean(h.get_text())

    sub = slide_el.select_one(".subtitle, .slide-subtitle")
    if sub:
        data["subtitle"] = clean(sub.get_text())

    body_el = slide_el.select_one("p, .body, .content p")
    if body_el:
        data["body"] = clean(body_el.get_text())

    return data


def parse_end_slide(slide_el):
    """Thank-you / closing slide."""
    data = {"type": "end"}
    h = slide_el.select_one("h2, h3, .slide-title, .end-title")
    if h:
        data["title"] = clean(h.get_text())

    sub = slide_el.select_one(".subtitle, .slide-subtitle")
    if sub:
        data["subtitle"] = clean(sub.get_text())

    cta = slide_el.select_one(".cta, .button, a.btn")
    if cta:
        data["cta"] = clean(cta.get_text())

    return data


# ── Slide type classifier ─────────────────────────────────────────────────────

def classify_and_parse(slide_el, index):
    """Detect what kind of slide this is and delegate to the right parser."""
    classes = " ".join(slide_el.get("class", []))
    has_list = bool(slide_el.find("ul") or slide_el.find("ol"))
    has_blockquote = bool(slide_el.find("blockquote") or slide_el.select_one(".quote-text, .pullquote"))
    has_stats = bool(slide_el.select(".stat-card, .stat-item, .metric, .kpi"))
    has_features = bool(slide_el.select(".feature-card, .feature-item"))
    two_col = bool(slide_el.select(".col, .column, .two-col, [class*='col-']"))
    is_title = index == 0 or "slide-title-hero" in classes or bool(slide_el.find("h1"))
    is_end = "slide-end" in classes or "slide-thanks" in classes

    if is_end:
        return parse_end_slide(slide_el)
    if is_title:
        return parse_title_slide(slide_el)
    if has_blockquote:
        return parse_quote_slide(slide_el)
    if has_stats:
        return parse_stats_slide(slide_el)
    if has_features:
        return parse_features_slide(slide_el)
    if has_list:
        return parse_bullets_slide(slide_el)
    if two_col:
        return parse_two_col_slide(slide_el)
    return parse_text_slide(slide_el)


# ── Speaker notes ─────────────────────────────────────────────────────────────

def extract_notes(slide_el):
    """Extract any speaker notes hidden in the slide markup."""
    # Convention: <div class="notes"> or <aside class="notes">
    notes_el = slide_el.select_one(".notes, aside.notes, [data-notes]")
    if notes_el:
        return clean(notes_el.get_text())
    # Also check data attribute
    if slide_el.get("data-notes"):
        return clean(slide_el["data-notes"])
    return None


# ── Main parser ───────────────────────────────────────────────────────────────

def parse_html(input_path, output_path=None, pretty=False, stats_only=False, verbose=False):
    from bs4 import BeautifulSoup

    input_path = Path(input_path)
    if not input_path.exists():
        print(f"❌ File not found: {input_path}")
        sys.exit(1)

    html = input_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # ── Meta ──────────────────────────────────────────────────────────────────
    template = detect_template(soup)
    lang = detect_lang(soup)

    # Try to extract deck-level title/subtitle from first slide
    title_tag = soup.find("title")
    deck_title = clean(title_tag.get_text()) if title_tag else ""
    deck_subtitle = ""
    deck_author = ""
    deck_date = ""

    # Grab meta author/date if present
    meta_author = soup.find("meta", {"name": re.compile(r"author", re.I)})
    if meta_author and meta_author.get("content"):
        deck_author = meta_author["content"]

    meta_date = soup.find("meta", {"name": re.compile(r"date|created", re.I)})
    if meta_date and meta_date.get("content"):
        deck_date = meta_date["content"]

    # ── Find slides ───────────────────────────────────────────────────────────
    # Support multiple common selectors used by this skill's templates
    slide_els = soup.select(".slide")
    if not slide_els:
        slide_els = soup.select("[class*='slide']")
    if not slide_els:
        slide_els = soup.select("section")

    if not slide_els:
        print("⚠️  No slides found in the HTML. Are you sure this is a frontend-slides presentation?")
        sys.exit(1)

    if stats_only:
        print(f"📊 Slide stats for: {input_path.name}")
        print(f"   Total slides  : {len(slide_els)}")
        print(f"   Detected template: {template}")
        print(f"   Language: {lang}")
        return

    # ── Parse each slide ──────────────────────────────────────────────────────
    slides = []
    for i, slide_el in enumerate(slide_els):
        parsed = classify_and_parse(slide_el, i)

        notes = extract_notes(slide_el)
        if notes:
            parsed["notes"] = notes

        # Grab deck-level metadata from slide 0 if not already found
        if i == 0:
            if not deck_title and parsed.get("title"):
                deck_title = parsed["title"]
            if not deck_subtitle and parsed.get("subtitle"):
                deck_subtitle = parsed["subtitle"]
            if not deck_author and parsed.get("author"):
                deck_author = parsed["author"]

        if verbose:
            type_str = parsed.get("type", "unknown")
            title_str = parsed.get("title", "(no title)")[:50]
            print(f"  Slide {i+1:02d}: [{type_str:12s}] {title_str}")

        slides.append(parsed)

    # ── Build output JSON ─────────────────────────────────────────────────────
    outline = {
        "title": deck_title,
        "template": template,
        "lang": lang,
    }
    if deck_subtitle:
        outline["subtitle"] = deck_subtitle
    if deck_author:
        outline["author"] = deck_author
    if deck_date:
        outline["date"] = deck_date
    outline["slides"] = slides

    # ── Write output ──────────────────────────────────────────────────────────
    if output_path is None:
        output_path = input_path.with_suffix(".json")
    else:
        output_path = Path(output_path)

    json_str = json.dumps(outline, ensure_ascii=False, indent=2 if pretty else None)
    output_path.write_text(json_str, encoding="utf-8")

    print(f"✅ Parsed {len(slides)} slides → {output_path}")
    print(f"   Template : {template}")
    print(f"   Language : {lang}")
    if verbose:
        type_counts = {}
        for s in slides:
            t = s.get("type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1
        print(f"   Slide types: {dict(sorted(type_counts.items(), key=lambda x: -x[1]))}")
    print(f"\n   Edit {output_path.name} and run:")
    print(f"   python3 scripts/generate_slides.py {output_path.name} -t {template} -o {input_path.name}")


# ── CLI entry point ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Reverse-parse a slide HTML presentation back to a JSON outline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/parse_html.py out.html
  python3 scripts/parse_html.py deck.html -o editable.json --pretty
  python3 scripts/parse_html.py deck.html --stats
        """
    )
    parser.add_argument("input", help="Path to the HTML presentation file")
    parser.add_argument("--output", "-o", help="Output JSON path (default: <input_stem>.json)")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON (indent=2)")
    parser.add_argument("--stats", action="store_true", dest="stats_only",
                        help="Print slide count/type summary only, don't write file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print each slide as it's parsed")
    args = parser.parse_args()

    check_deps()
    parse_html(
        args.input,
        output_path=args.output,
        pretty=args.pretty,
        stats_only=args.stats_only,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
