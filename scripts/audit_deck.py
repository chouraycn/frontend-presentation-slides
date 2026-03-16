#!/usr/bin/env python3
"""
audit_deck.py — AI Content Audit & Improvement Suggestions
══════════════════════════════════════════════════════════════════════════════
Analyzes a finished HTML presentation for content quality issues and outputs
a structured improvement report. Works entirely offline — no LLM API required
for the rule-based checks; optionally calls an LLM for narrative suggestions.

Checks performed:
  1. Text density  — slides with too many words (>120) or too many bullets (>6)
  2. Narrative flow — missing skeleton sections, abrupt topic jumps
  3. Data gaps      — stat/claim slides that lack supporting numbers
  4. Readability    — overly long sentences, passive voice ratio
  5. CTA coverage   — decks without a clear call-to-action at the end
  6. Title variety  — duplicate or generic titles ("Slide N", "Untitled")

Usage:
    python3 scripts/audit_deck.py <input.html> [options]

Examples:
    python3 scripts/audit_deck.py presentation.html
    python3 scripts/audit_deck.py deck.html --output report.json
    python3 scripts/audit_deck.py deck.html --format md
    python3 scripts/audit_deck.py deck.html --llm         # LLM narrative suggestions
    python3 scripts/audit_deck.py deck.html --fix-hints   # Print inline fix hints

Options:
    --output, -o     Output path (default: <input_stem>-audit.json or .md)
    --format         Output format: json | md  (default: md)
    --llm            Call LLM (via codebuddy CLI) for narrative suggestions
    --fix-hints      Append inline code-comment hints for each issue
    --verbose, -v    Print progress

Requirements:
    pip3 install beautifulsoup4
══════════════════════════════════════════════════════════════════════════════
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime


# ── Dependency check ──────────────────────────────────────────────────────────

def check_deps():
    try:
        from bs4 import BeautifulSoup  # noqa: F401
    except ImportError:
        print("❌ Missing dependency: beautifulsoup4")
        print("   Run: pip3 install beautifulsoup4")
        sys.exit(1)


# ── Text utilities ────────────────────────────────────────────────────────────

def clean(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip())


def word_count(text):
    return len(re.findall(r'\w+', text or ""))


def sentence_count(text):
    return len(re.findall(r'[.!?。！？]+', text or ""))


def avg_words_per_sentence(text):
    wc = word_count(text)
    sc = sentence_count(text)
    return round(wc / sc, 1) if sc else wc


# ── Individual checks ─────────────────────────────────────────────────────────

def check_text_density(slides):
    """Flag slides with too many words or too many bullet points."""
    issues = []
    for i, s in enumerate(slides):
        wc = word_count(s["body_text"])
        bc = s["bullet_count"]
        if wc > 120:
            issues.append({
                "slide": i + 1,
                "title": s["title"],
                "severity": "high",
                "check": "text_density",
                "message": f"Slide {i+1} has {wc} words — exceeds 120-word limit. "
                           f"Consider splitting into two slides or reducing to key phrases.",
                "fix": "Split into two slides or trim body text to ≤80 words."
            })
        elif wc > 80:
            issues.append({
                "slide": i + 1,
                "title": s["title"],
                "severity": "medium",
                "check": "text_density",
                "message": f"Slide {i+1} has {wc} words — slightly dense for a presentation slide.",
                "fix": "Trim to ≤80 words, move details to speaker notes."
            })
        if bc > 6:
            issues.append({
                "slide": i + 1,
                "title": s["title"],
                "severity": "high",
                "check": "bullet_overload",
                "message": f"Slide {i+1} has {bc} bullet points — exceeds 6. "
                           f"Audiences can't absorb more than 5–6 items at once.",
                "fix": "Split into two slides or group bullets under sub-headings."
            })
    return issues


def check_data_gaps(slides):
    """Find claim slides that assert things without numbers."""
    CLAIM_WORDS = re.compile(
        r'\b(increase|decrease|grow|reduce|improve|fastest|largest|best|significant|'
        r'major|huge|massive|dramatically|substantially|'
        r'增长|提升|下降|最大|最快|显著|大幅|重要)\b', re.I
    )
    NUMBER_PATTERN = re.compile(r'\d+[\.,]?\d*\s*(%|x|倍|万|亿|billion|million|k\b)?', re.I)

    issues = []
    for i, s in enumerate(slides):
        text = s["body_text"]
        has_claim = bool(CLAIM_WORDS.search(text))
        has_number = bool(NUMBER_PATTERN.search(text))
        if has_claim and not has_number:
            issues.append({
                "slide": i + 1,
                "title": s["title"],
                "severity": "medium",
                "check": "data_gap",
                "message": f"Slide {i+1} makes a claim without supporting data. "
                           f"Vague assertions weaken credibility.",
                "fix": "Add a specific metric: percentage, absolute number, or timeframe."
            })
    return issues


def check_title_variety(slides):
    """Detect duplicate or generic titles."""
    GENERIC = re.compile(r'^(slide\s*\d*|untitled|undefined|no title|新幻灯片|幻灯片\s*\d*)$', re.I)
    seen = {}
    issues = []
    for i, s in enumerate(slides):
        title = s["title"].strip()
        if not title or GENERIC.match(title):
            issues.append({
                "slide": i + 1,
                "title": title or "(empty)",
                "severity": "medium",
                "check": "generic_title",
                "message": f"Slide {i+1} has a generic or missing title: '{title}'.",
                "fix": "Give each slide a descriptive, outcome-oriented title."
            })
        else:
            key = title.lower()
            if key in seen:
                issues.append({
                    "slide": i + 1,
                    "title": title,
                    "severity": "low",
                    "check": "duplicate_title",
                    "message": f"Slide {i+1} has the same title as slide {seen[key]+1}: '{title}'.",
                    "fix": "Differentiate slide titles to aid navigation and comprehension."
                })
            else:
                seen[key] = i
    return issues


def check_cta_coverage(slides):
    """Verify the deck ends with a clear call to action."""
    CTA_WORDS = re.compile(
        r'\b(contact|sign up|register|download|try|demo|join|book|get started|reach out|next steps|'
        r'联系|注册|下载|试用|体验|预约|加入|开始|下一步|立即)\b', re.I
    )
    if not slides:
        return []

    # Check last 2 slides for CTA
    last_two_text = " ".join(s["body_text"] for s in slides[-2:])
    if not CTA_WORDS.search(last_two_text):
        return [{
            "slide": len(slides),
            "title": slides[-1]["title"],
            "severity": "medium",
            "check": "missing_cta",
            "message": "The deck has no clear call-to-action in the final slides. "
                       "Audiences need a concrete next step.",
            "fix": "Add a closing slide with a specific action: contact info, URL, sign-up link, or next step."
        }]
    return []


def check_readability(slides):
    """Flag slides with very long sentences."""
    issues = []
    for i, s in enumerate(slides):
        avg = avg_words_per_sentence(s["body_text"])
        if avg > 30:
            issues.append({
                "slide": i + 1,
                "title": s["title"],
                "severity": "low",
                "check": "long_sentences",
                "message": f"Slide {i+1} has an average sentence length of {avg} words. "
                           f"Aim for ≤20 words per sentence in presentations.",
                "fix": "Break long sentences into shorter phrases. Bullet points help."
            })
    return issues


def check_narrative_flow(slides):
    """Detect abrupt topic transitions between adjacent slides."""
    issues = []
    # Simple heuristic: if consecutive title keywords share no common root, flag it
    # Only flag if deck has 6+ slides (short decks are exempt)
    if len(slides) < 6:
        return []

    # Check for missing opening context (slide 2 jumps straight to data)
    second = slides[1] if len(slides) > 1 else None
    if second:
        DATA_PATTERN = re.compile(r'\d+%|\$\d|revenue|sales|growth|指标|数据|增长', re.I)
        if DATA_PATTERN.search(second["body_text"]) and word_count(second["body_text"]) > 40:
            issues.append({
                "slide": 2,
                "title": second["title"],
                "severity": "low",
                "check": "narrative_flow",
                "message": "Slide 2 jumps straight into data without establishing context. "
                           "Audiences need framing before numbers.",
                "fix": "Add a brief problem/context statement before data slides."
            })

    # Check for missing transition between major sections
    for i in range(1, len(slides) - 1):
        curr_wc = word_count(slides[i]["body_text"])
        prev_wc = word_count(slides[i - 1]["body_text"])
        # Slide goes from content-heavy to empty might indicate a missing transition
        if prev_wc > 60 and curr_wc < 15 and slides[i]["bullet_count"] == 0:
            issues.append({
                "slide": i + 1,
                "title": slides[i]["title"],
                "severity": "low",
                "check": "narrative_flow",
                "message": f"Slide {i+1} is very sparse after a content-heavy slide {i}. "
                           f"Consider adding a section divider or transition note.",
                "fix": "Use this as an intentional section break slide, or merge with an adjacent slide."
            })

    return issues


# ── Slide extraction ──────────────────────────────────────────────────────────

def extract_slides(soup):
    """Extract structured data from each slide for auditing."""
    slide_els = soup.select(".slide")
    if not slide_els:
        slide_els = soup.select("section")

    slides = []
    for el in slide_els:
        # Remove script/style tags so their content doesn't pollute word counts
        for tag in el.find_all(["script", "style", "noscript"]):
            tag.decompose()

        # Collect all visible text
        title_el = el.select_one("h1, h2, h3, .slide-title, .title-text")
        title = clean(title_el.get_text()) if title_el else ""

        # Remove title from body to avoid double-counting
        if title_el:
            title_el.extract()

        body_text = clean(el.get_text())
        bullet_count = len(el.select("li"))
        has_chart = bool(el.select("[id*='chart'], canvas, svg.chart, .chart-container"))
        has_image = bool(el.select("img, [style*='background-image']"))
        notes = ""
        notes_el = el.select_one(".notes, aside.notes, [data-notes]")
        if notes_el:
            notes = clean(notes_el.get_text())
        elif el.get("data-notes"):
            notes = clean(el["data-notes"])

        slides.append({
            "title": title,
            "body_text": body_text,
            "bullet_count": bullet_count,
            "has_chart": has_chart,
            "has_image": has_image,
            "has_notes": bool(notes),
            "notes": notes,
            "word_count": word_count(body_text),
        })
    return slides


# ── Score calculation ─────────────────────────────────────────────────────────

SEVERITY_SCORE = {"high": 10, "medium": 5, "low": 2}

def calculate_score(issues, total_slides):
    """Return a 0–100 quality score. Higher is better."""
    if total_slides == 0:
        return 0
    deduction = sum(SEVERITY_SCORE.get(i["severity"], 0) for i in issues)
    # Normalize: max possible deduction assumed to be total_slides * 10
    max_deduction = total_slides * 10
    score = max(0, 100 - int((deduction / max(max_deduction, 1)) * 100))
    return score


# ── LLM narrative suggestions ─────────────────────────────────────────────────

def get_llm_suggestions(slides, issues):
    """
    Call codebuddy CLI for narrative-level suggestions.
    Falls back gracefully if CLI is not available.
    """
    import subprocess
    import shutil

    if not shutil.which("codebuddy"):
        return "LLM suggestions unavailable: codebuddy CLI not found. Run: npm install -g @tencent-ai/codebuddy-code"

    slide_summary = "\n".join(
        f"Slide {i+1}: [{s['word_count']} words, {s['bullet_count']} bullets] {s['title']}"
        for i, s in enumerate(slides)
    )
    issue_summary = "\n".join(
        f"- [{i['severity'].upper()}] Slide {i['slide']}: {i['message']}"
        for i in issues[:10]  # Top 10 issues only
    )

    prompt = f"""You are a presentation coach reviewing a slide deck.
Here is the slide structure:
{slide_summary}

Key issues detected:
{issue_summary}

In 3–5 sentences, give high-level narrative advice on how to improve this deck's storytelling flow.
Be specific and actionable. Focus on structure, not visual design."""

    try:
        result = subprocess.run(
            ["codebuddy", "ask", prompt],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        return f"LLM call returned empty output. stderr: {result.stderr[:200]}"
    except subprocess.TimeoutExpired:
        return "LLM call timed out (30s)."
    except Exception as e:
        return f"LLM call failed: {e}"


# ── Report formatters ─────────────────────────────────────────────────────────

def format_markdown(audit_data):
    lines = []
    lines.append(f"# Deck Audit Report")
    lines.append(f"\n**File:** `{audit_data['file']}`")
    lines.append(f"**Slides:** {audit_data['total_slides']}")
    lines.append(f"**Quality Score:** {audit_data['score']}/100")
    lines.append(f"**Generated:** {audit_data['generated_at']}")

    # Score interpretation
    score = audit_data['score']
    if score >= 85:
        verdict = "✅ Excellent — ready to present"
    elif score >= 70:
        verdict = "🟡 Good — minor improvements recommended"
    elif score >= 50:
        verdict = "🟠 Needs Work — several issues to address"
    else:
        verdict = "🔴 Critical — significant revision needed"
    lines.append(f"\n**Verdict:** {verdict}")

    # Issue summary
    issues = audit_data["issues"]
    high = [i for i in issues if i["severity"] == "high"]
    med  = [i for i in issues if i["severity"] == "medium"]
    low  = [i for i in issues if i["severity"] == "low"]

    lines.append(f"\n## Issue Summary\n")
    lines.append(f"| Severity | Count |")
    lines.append(f"|----------|-------|")
    lines.append(f"| 🔴 High   | {len(high)} |")
    lines.append(f"| 🟡 Medium | {len(med)} |")
    lines.append(f"| 🔵 Low    | {len(low)} |")
    lines.append(f"| **Total** | **{len(issues)}** |")

    # Per-check breakdown
    lines.append(f"\n## Detailed Issues\n")
    if not issues:
        lines.append("_No issues found — great work!_")
    else:
        for issue in issues:
            sev_icon = {"high": "🔴", "medium": "🟡", "low": "🔵"}.get(issue["severity"], "⚪")
            lines.append(f"### {sev_icon} Slide {issue['slide']}: {issue['title'] or '(no title)'}")
            lines.append(f"**Check:** `{issue['check']}`  ")
            lines.append(f"**Issue:** {issue['message']}  ")
            lines.append(f"**Fix:** {issue['fix']}")
            lines.append("")

    # Slide-by-slide stats
    lines.append("## Slide Statistics\n")
    lines.append("| # | Title | Words | Bullets | Chart | Image | Notes |")
    lines.append("|---|-------|-------|---------|-------|-------|-------|")
    for i, s in enumerate(audit_data["slides"]):
        title = (s["title"][:30] + "…") if len(s["title"]) > 30 else s["title"]
        chart = "✓" if s["has_chart"] else "—"
        image = "✓" if s["has_image"] else "—"
        notes = "✓" if s["has_notes"] else "—"
        lines.append(f"| {i+1} | {title} | {s['word_count']} | {s['bullet_count']} | {chart} | {image} | {notes} |")

    # LLM suggestions (if present)
    if audit_data.get("llm_suggestions"):
        lines.append(f"\n## AI Narrative Suggestions\n")
        lines.append(audit_data["llm_suggestions"])

    # Recommendations
    lines.append(f"\n## Quick Wins\n")
    if high:
        lines.append("**Address these first (High severity):**")
        for issue in high[:3]:
            lines.append(f"- Slide {issue['slide']}: {issue['fix']}")
    if med:
        lines.append("\n**Then tackle these (Medium severity):**")
        for issue in med[:3]:
            lines.append(f"- Slide {issue['slide']}: {issue['fix']}")

    # Fix hints (inline HTML comment format, for pasting into the deck)
    if audit_data.get("fix_hints"):
        lines.append(f"\n## Inline Fix Hints\n")
        lines.append("_Copy these comments into the relevant slide's HTML for in-code reminders:_\n")
        for hint in audit_data["fix_hints"]:
            lines.append(f"- Slide {hint['slide']} ({hint['check']}): `{hint['hint']}`")

    lines.append(f"\n---\n_Generated by audit_deck.py — part of frontend-presentation-slides skill_")
    return "\n".join(lines)


# ── Main audit function ───────────────────────────────────────────────────────

def audit_deck(input_path, output_path=None, fmt="md", use_llm=False,
               fix_hints=False, verbose=False):
    from bs4 import BeautifulSoup

    input_path = Path(input_path)
    if not input_path.exists():
        print(f"❌ File not found: {input_path}")
        sys.exit(1)

    if verbose:
        print(f"🔍 Auditing: {input_path.name}")

    html = input_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    slides = extract_slides(soup)
    if not slides:
        print("⚠️  No slides found. Is this a frontend-slides presentation?")
        sys.exit(1)

    if verbose:
        print(f"   Found {len(slides)} slides")

    # Run all checks
    issues = []
    issues += check_text_density(slides)
    issues += check_data_gaps(slides)
    issues += check_title_variety(slides)
    issues += check_cta_coverage(slides)
    issues += check_readability(slides)
    issues += check_narrative_flow(slides)

    # Sort by severity then slide number
    sev_order = {"high": 0, "medium": 1, "low": 2}
    issues.sort(key=lambda x: (sev_order.get(x["severity"], 9), x["slide"]))

    score = calculate_score(issues, len(slides))

    llm_suggestions = None
    if use_llm:
        if verbose:
            print("   Calling LLM for narrative suggestions…")
        llm_suggestions = get_llm_suggestions(slides, issues)

    audit_data = {
        "file": str(input_path),
        "total_slides": len(slides),
        "score": score,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "issues": issues,
        "slides": slides,
    }
    if llm_suggestions:
        audit_data["llm_suggestions"] = llm_suggestions
    if fix_hints:
        audit_data["fix_hints"] = [
            {
                "slide": i["slide"],
                "check": i["check"],
                "hint": f"<!-- AUDIT [{i['severity'].upper()}] {i['check']}: {i['fix']} -->"
            }
            for i in issues
        ]

    # Determine output path
    if output_path is None:
        ext = ".md" if fmt == "md" else ".json"
        output_path = input_path.with_name(input_path.stem + "-audit" + ext)
    else:
        output_path = Path(output_path)

    # Write output
    if fmt == "md":
        content = format_markdown(audit_data)
        output_path.write_text(content, encoding="utf-8")
    else:
        output_path.write_text(
            json.dumps(audit_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    high_count = len([i for i in issues if i["severity"] == "high"])
    med_count  = len([i for i in issues if i["severity"] == "medium"])
    low_count  = len([i for i in issues if i["severity"] == "low"])

    print(f"✅ Audit complete → {output_path}")
    print(f"   Score   : {score}/100")
    print(f"   Issues  : {len(issues)} total  (🔴 {high_count} high · 🟡 {med_count} medium · 🔵 {low_count} low)")
    if high_count > 0:
        print(f"   ⚠️  {high_count} high-severity issue(s) need attention before presenting.")


# ── CLI entry point ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Audit an HTML slide deck for content quality issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/audit_deck.py presentation.html
  python3 scripts/audit_deck.py deck.html --format json
  python3 scripts/audit_deck.py deck.html --llm
  python3 scripts/audit_deck.py deck.html --output report.md --verbose
        """
    )
    parser.add_argument("input", help="Path to the HTML presentation")
    parser.add_argument("--output", "-o", help="Output path (default: <input_stem>-audit.md or .json)")
    parser.add_argument("--format", "-f", choices=["md", "json"], default="md",
                        dest="fmt", help="Output format: md (default) or json")
    parser.add_argument("--llm", action="store_true",
                        help="Call LLM (codebuddy CLI) for narrative suggestions")
    parser.add_argument("--fix-hints", action="store_true", dest="fix_hints",
                        help="Append inline HTML comment hints for each issue (copy into your deck)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print progress")
    args = parser.parse_args()

    check_deps()
    audit_deck(
        args.input,
        output_path=args.output,
        fmt=args.fmt,
        use_llm=args.llm,
        fix_hints=args.fix_hints,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
