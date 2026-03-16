#!/usr/bin/env python3
"""
apply_comments.py — Apply Reviewer Comments to an HTML Slide Deck
══════════════════════════════════════════════════════════════════════════════
Reads a JSON comments file (from a reviewer) and applies the suggested text
changes to an HTML presentation. Supports five action types:

  replace    — Replace the specified text with new text
  insert     — Insert text before/after an existing anchor text
  delete     — Remove the specified text from a slide
  highlight  — Wrap the specified text in a <mark> tag for visual review
               (does NOT change the text content; creates a backup automatically)
  note       — Print the comment (no file change; for awareness only)

Comments file format (comments.json):
  {
    "deck": "presentation.html",
    "reviewer": "Alice Chen",
    "date": "2025-03-15",
    "comments": [
      {
        "id": "c1",
        "slide": 3,
        "action": "replace",
        "find": "Our product increases efficiency.",
        "replace": "Our product increases team efficiency by 40% (Q3 pilot).",
        "note": "Add the actual metric from the pilot report."
      },
      {
        "id": "c2",
        "slide": 5,
        "action": "insert",
        "position": "after",
        "anchor": "Key Milestones",
        "text": "(as of Q4 2025)",
        "note": "Clarify that this is Q4 data."
      },
      {
        "id": "c3",
        "slide": 7,
        "action": "delete",
        "find": "See appendix for details.",
        "note": "Appendix was removed — this reference is now broken."
      },
      {
        "id": "c4",
        "slide": 2,
        "action": "note",
        "note": "The market size stat here needs a citation. Ask David for the source."
      },
      {
        "id": "c5",
        "slide": 4,
        "action": "highlight",
        "find": "Text to visually flag for review",
        "color": "#ffdd57",
        "note": "This claim needs a source — highlighted for discussion."
      }
    ]
  }

Usage:
    python3 scripts/apply_comments.py <comments.json> [options]

Examples:
    python3 scripts/apply_comments.py review.json
    python3 scripts/apply_comments.py review.json --dry-run
    python3 scripts/apply_comments.py review.json --output revised.html
    python3 scripts/apply_comments.py review.json --verbose

Options:
    --output, -o     Output HTML path (default: overwrites input deck with backup)
    --dry-run        Show what would change without writing any files
    --backup         Always create a .bak backup before writing (default: on)
    --no-backup      Skip backup creation
    --verbose, -v    Print each applied change

Requirements:
    pip3 install beautifulsoup4
══════════════════════════════════════════════════════════════════════════════
"""

import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


# ── Dependency check ──────────────────────────────────────────────────────────

def check_deps():
    try:
        from bs4 import BeautifulSoup  # noqa: F401
    except ImportError:
        print("❌ Missing dependency: beautifulsoup4")
        print("   Run: pip3 install beautifulsoup4")
        sys.exit(1)


# ── Helpers ───────────────────────────────────────────────────────────────────

def clean(text):
    return re.sub(r'\s+', ' ', (text or "").strip())


# ── Comment applicators ───────────────────────────────────────────────────────

def apply_replace(html, comment, verbose):
    find    = comment.get("find", "")
    replace = comment.get("replace", "")
    if not find:
        return html, False, "Missing 'find' field"

    if find not in html:
        # Try case-insensitive / whitespace-collapsed match
        pattern = re.compile(re.escape(find), re.IGNORECASE)
        if not pattern.search(html):
            return html, False, f"Text not found: '{find[:60]}'"
        new_html = pattern.sub(replace, html, count=1)
    else:
        new_html = html.replace(find, replace, 1)

    if verbose:
        print(f"   ✏️  Replace: '{find[:50]}' → '{replace[:50]}'")
    return new_html, True, None


def apply_insert(html, comment, verbose):
    anchor   = comment.get("anchor", "")
    text     = comment.get("text", "")
    position = comment.get("position", "after").lower()  # before | after

    if not anchor:
        return html, False, "Missing 'anchor' field"
    if anchor not in html:
        return html, False, f"Anchor not found: '{anchor[:60]}'"

    if position == "before":
        new_html = html.replace(anchor, text + anchor, 1)
    else:
        new_html = html.replace(anchor, anchor + text, 1)

    if verbose:
        print(f"   ➕ Insert {position} '{anchor[:40]}': '{text[:50]}'")
    return new_html, True, None


def apply_delete(html, comment, verbose):
    find = comment.get("find", "")
    if not find:
        return html, False, "Missing 'find' field"

    if find not in html:
        pattern = re.compile(re.escape(find), re.IGNORECASE)
        if not pattern.search(html):
            return html, False, f"Text not found: '{find[:60]}'"
        new_html = pattern.sub("", html, count=1)
    else:
        new_html = html.replace(find, "", 1)

    if verbose:
        print(f"   🗑️  Delete: '{find[:60]}'")
    return new_html, True, None


def apply_note(html, comment, verbose):
    """Notes are informational only — no file changes."""
    if verbose:
        print(f"   📌 Note: {comment.get('note', '')}")
    return html, True, None


def apply_highlight(html, comment, verbose):
    """
    Wrap the target text in a <mark> element for visual review.
    Does NOT change the text content — purely a visual annotation layer.
    The <mark> carries a data-comment-id and data-note for traceability.
    """
    find  = comment.get("find", "")
    color = comment.get("color", "#ffdd57")   # default: bright yellow
    cid   = comment.get("id", "?")
    note  = comment.get("note", "")

    if not find:
        return html, False, "Missing 'find' field"

    # Build replacement: <mark> wrapper with inline style
    style = (
        f"background:{color}; color:#000; border-radius:3px; "
        f"padding:0 2px; outline:2px dashed {color};"
    )
    mark_open  = (
        f'<mark data-comment-id="{cid}" data-note="{note.replace(chr(34), chr(39))}" '
        f'title="[{cid}] {note.replace(chr(34), chr(39))}" style="{style}">'
    )
    mark_close = "</mark>"

    if find not in html:
        pattern = re.compile(re.escape(find), re.IGNORECASE)
        if not pattern.search(html):
            return html, False, f"Text not found: '{find[:60]}'"
        new_html = pattern.sub(mark_open + find + mark_close, html, count=1)
    else:
        new_html = html.replace(find, mark_open + find + mark_close, 1)

    if verbose:
        print(f"   🖊️  Highlight [{cid}]: '{find[:50]}'")
    return new_html, True, None


APPLICATORS = {
    "replace":   apply_replace,
    "insert":    apply_insert,
    "delete":    apply_delete,
    "highlight": apply_highlight,
    "note":      apply_note,
}


# ── Main function ─────────────────────────────────────────────────────────────

def apply_comments(comments_path, output_path=None, dry_run=False,
                   backup=True, verbose=False):
    comments_path = Path(comments_path)
    if not comments_path.exists():
        print(f"❌ Comments file not found: {comments_path}")
        sys.exit(1)

    # Load comments
    try:
        review = json.loads(comments_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {comments_path}: {e}")
        sys.exit(1)

    # Resolve deck path
    deck_name = review.get("deck", "")
    if not deck_name:
        print("❌ 'deck' field missing in comments JSON. Add the HTML filename.")
        sys.exit(1)

    deck_path = Path(deck_name)
    if not deck_path.is_absolute():
        deck_path = comments_path.parent / deck_name

    if not deck_path.exists():
        print(f"❌ Deck file not found: {deck_path}")
        sys.exit(1)

    html = deck_path.read_text(encoding="utf-8")
    original_html = html

    comments = review.get("comments", [])
    if not comments:
        print("⚠️  No comments found in the review file.")
        return

    reviewer = review.get("reviewer", "Anonymous")
    date_str = review.get("date", "")
    print(f"📋 Applying comments from: {reviewer}{' · ' + date_str if date_str else ''}")
    print(f"   Deck : {deck_path.name}")
    print(f"   Total: {len(comments)} comment(s)")
    print()

    # Process each comment
    results = []
    for comment in comments:
        cid    = comment.get("id", "?")
        slide  = comment.get("slide", "?")
        action = comment.get("action", "note").lower()
        note   = comment.get("note", "")

        applicator = APPLICATORS.get(action)
        if not applicator:
            results.append((cid, slide, action, False, f"Unknown action: '{action}'"))
            continue

        if not dry_run:
            new_html, ok, err = applicator(html, comment, verbose)
            if ok:
                html = new_html
        else:
            # Dry-run: validate but don't apply
            _, ok, err = applicator(original_html, comment, False)

        status = "✅" if ok else "⚠️ "
        detail = note[:60] if note else (err or "")
        results.append((cid, slide, action, ok, detail))
        if not verbose:
            print(f"  {status} [{cid}] Slide {slide} · {action.upper():8s} {detail}")

    # Summary
    applied = sum(1 for _, _, _, ok, _ in results if ok)
    skipped = len(results) - applied
    print()
    print(f"{'[DRY RUN] ' if dry_run else ''}Results: {applied} applied, {skipped} skipped")

    if dry_run:
        print("   No files were written (--dry-run mode).")
        return

    if html == original_html:
        print("   No changes detected — deck not modified.")
        return

    # Determine output
    if output_path is None:
        output_path = deck_path
    else:
        output_path = Path(output_path)

    # Backup
    if backup:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        bak = output_path.with_name(output_path.stem + f"-bak-{ts}.html")
        shutil.copy2(deck_path, bak)
        print(f"   Backup : {bak.name}")

    output_path.write_text(html, encoding="utf-8")
    print(f"   Saved  : {output_path}")

    # Append a comment summary block to the HTML (hidden, for traceability)
    summary = {
        "applied_by": "apply_comments.py",
        "reviewer": reviewer,
        "date": date_str,
        "applied_at": datetime.now().isoformat(),
        "changes": applied,
    }
    comment_block = f"\n<!-- review-applied: {json.dumps(summary)} -->"
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(comment_block)

    print(f"\n✅ Done — {applied} change(s) applied to {output_path.name}")


# ── Init: create a blank comments template ────────────────────────────────────

def init_template(deck_path, output_path=None):
    """Generate a blank comments.json template for a reviewer to fill in."""
    deck = Path(deck_path)
    template = {
        "deck": deck.name,
        "reviewer": "Your Name",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "comments": [
            {
                "id": "c1",
                "slide": 1,
                "action": "note",
                "note": "Example: Add a clearer tagline to the cover slide."
            },
            {
                "id": "c2",
                "slide": 3,
                "action": "replace",
                "find": "Original text to find (exact match)",
                "replace": "New text to replace it with",
                "note": "Reason for change"
            },
            {
                "id": "c3",
                "slide": 5,
                "action": "insert",
                "position": "after",
                "anchor": "Text to insert after (exact match)",
                "text": " [NEW TEXT]",
                "note": "What you're adding and why"
            },
            {
                "id": "c4",
                "slide": 7,
                "action": "delete",
                "find": "Text to remove completely",
                "note": "Why this should be removed"
            },
            {
                "id": "c5",
                "slide": 2,
                "action": "highlight",
                "find": "Claim or stat that needs verification",
                "color": "#ffdd57",
                "note": "Needs a source — flag for discussion without changing text"
            }
        ]
    }

    out = output_path or deck.with_name(deck.stem + "-comments.json")
    Path(out).write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Template created: {out}")
    print("   Fill in the 'comments' array and run:")
    print(f"   python3 scripts/apply_comments.py {Path(out).name}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Apply reviewer comments (JSON) to an HTML slide deck",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Actions supported in comments.json:
  replace    — Replace exact text with new text
  insert     — Insert text before/after an anchor string
  delete     — Remove a text string
  highlight  — Wrap text in <mark> for visual review (no content change)
  note       — Informational only, no file change

Examples:
  python3 scripts/apply_comments.py review.json
  python3 scripts/apply_comments.py review.json --dry-run
  python3 scripts/apply_comments.py review.json --output revised.html
  python3 scripts/apply_comments.py --init presentation.html   # Create blank template
        """
    )
    parser.add_argument("comments", nargs="?",
                        help="Path to the JSON comments file")
    parser.add_argument("--output", "-o",
                        help="Output HTML path (default: overwrite with backup)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without writing any files")
    parser.add_argument("--backup", action="store_true", default=True,
                        help="Create timestamped .html backup before writing (default: on)")
    parser.add_argument("--no-backup", action="store_false", dest="backup",
                        help="Skip backup")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print each change as it's applied")
    parser.add_argument("--init", metavar="DECK_HTML",
                        help="Generate a blank comments.json template for the given deck")
    args = parser.parse_args()

    if args.init:
        init_template(args.init, args.output)
        return

    if not args.comments:
        parser.print_help()
        sys.exit(1)

    check_deps()
    apply_comments(
        args.comments,
        output_path=args.output,
        dry_run=args.dry_run,
        backup=args.backup,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
