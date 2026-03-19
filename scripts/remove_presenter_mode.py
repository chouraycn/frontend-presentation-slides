#!/usr/bin/env python3
"""
remove_presenter_mode.py — Remove all Presenter Mode code from all 8 HTML templates.
Run: python3 scripts/remove_presenter_mode.py
"""

import re
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent.parent / "assets" / "templates"


def remove_presenter_from_simple(content: str) -> str:
    """Remove Presenter Mode from 'simple' templates (pitch-deck, tech-talk, product-launch, quarterly-report, claude-warmth)."""
    lines = content.split('\n')
    result = []
    skip_patterns_active = False

    # Strategy: line-by-line filtering with block detection
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 1. Remove HTML comment references to presenter mode
        if 'press [P] for presenter mode' in stripped.lower() or 'press [P] for presenter mode' in stripped:
            i += 1
            continue

        # 2. Skip CSS: #presenterBtn { ... } (may span multiple lines)
        if stripped.startswith('#presenterBtn {') or stripped.startswith('#presenterBtn{'):
            # Skip until closing brace
            while i < len(lines) and '}' not in lines[i]:
                i += 1
            i += 1  # skip the closing brace line
            continue

        # 3. Skip standalone #presenterBtn:hover line
        if stripped.startswith('#presenterBtn:hover'):
            i += 1
            continue

        # 4. Remove #presenterBtn from print media queries
        if '#presenterBtn' in stripped and 'display: none' in stripped:
            # Remove #presenterBtn from the selector list
            result.append(line.replace(', #presenterBtn', '').replace('#presenterBtn, ', ''))
            i += 1
            continue

        # 5. Remove HTML presenter button
        if '<button id="presenterBtn"' in stripped or '<button id=\'presenterBtn\'' in stripped:
            i += 1
            continue

        # 6. Remove <!-- Presenter mode button --> comment
        if stripped == '<!-- Presenter mode button -->':
            i += 1
            continue

        # 7. Remove JavaScript: CHANNEL, presenterWin, bc, BroadcastChannel initialization
        if re.match(r"const\s+CHANNEL\s*=\s*['\"]slides-presenter-sync['\"]", stripped):
            i += 1
            continue
        if re.match(r"let\s+presenterWin\s*=", stripped):
            i += 1
            continue
        if re.match(r"let\s+bc\s*=\s*null", stripped):
            i += 1
            continue
        if 'try{bc=new BroadcastChannel(CHANNEL);}catch(e){}' in stripped:
            i += 1
            continue
        if "try{bc=new BroadcastChannel(CHANNEL);}catch(e){" in stripped:
            i += 1
            continue

        # 8. Remove keyboard handler for 'p' key in keydown
        if re.search(r"else\s+if\s*\(\s*e\.key\.toLowerCase\(\)\s*===\s*['\"]p['\"]\s*\)\s*openPresenter\s*\(\s*\)", stripped):
            i += 1
            continue
        if re.search(r"else\s+if\s*\(\s*e\.key\s*===\s*['\"]p['\"]\s*\|\|\s*e\.key\s*===\s*['\"]P['\"]\s*\)\s*\{?\s*openPresenterView\s*\(\s*\)", stripped):
            i += 1
            continue
        if re.search(r"else\s+if\s*\(\s*e\.key\s*===\s*['\"]p['\"]\s*\|\|\s*e\.key\s*===\s*['\"]P['\"]\s*\)\s*\{?\s*openPresenterView", stripped):
            i += 1
            continue

        # 9. Remove function openPresenter() / openPresenterView() definitions (multi-line)
        if re.match(r'function\s+openPresenter\s*\(\s*\)\s*\{', stripped):
            brace_count = stripped.count('{') - stripped.count('}')
            i += 1
            while i < len(lines) and brace_count > 0:
                brace_count += lines[i].count('{') - lines[i].count('}')
                i += 1
            continue

        if re.match(r'function\s+openPresenterView\s*\(\s*\)\s*\{', stripped):
            brace_count = stripped.count('{') - stripped.count('}')
            i += 1
            while i < len(lines) and brace_count > 0:
                brace_count += lines[i].count('{') - lines[i].count('}')
                i += 1
            continue

        # 10. Remove presenterBtn addEventListener
        if "document.getElementById('presenterBtn').addEventListener" in stripped:
            i += 1
            continue
        if "getElementById('presenterBtn')" in stripped and 'addEventListener' in stripped:
            i += 1
            continue

        # 11. Remove if(bc)bc.addEventListener('message' block
        if re.match(r"if\s*\(bc\)\s*bc\.addEventListener\s*\(\s*'message'", stripped):
            brace_count = stripped.count('{') - stripped.count('}')
            i += 1
            while i < len(lines) and brace_count > 0:
                brace_count += lines[i].count('{') - lines[i].count('}')
                i += 1
            continue

        # 12. Remove relayPointer function
        if re.match(r'function\s+relayPointer\s*\(', stripped):
            brace_count = stripped.count('{') - stripped.count('}')
            i += 1
            while i < len(lines) and brace_count > 0:
                brace_count += lines[i].count('{') - lines[i].count('}')
                i += 1
            continue

        # 13. Remove toggleBlackout function
        if re.match(r'function\s+toggleBlackout\s*\(', stripped):
            brace_count = stripped.count('{') - stripped.count('}')
            i += 1
            while i < len(lines) and brace_count > 0:
                brace_count += lines[i].count('{') - lines[i].count('}')
                i += 1
            continue

        # 14. Remove showLaser function
        if re.match(r'function\s+showLaser\s*\(', stripped):
            brace_count = stripped.count('{') - stripped.count('}')
            i += 1
            while i < len(lines) and brace_count > 0:
                brace_count += lines[i].count('{') - lines[i].count('}')
                i += 1
            continue

        # 15. Remove Laser pointer relay comment block
        if stripped.startswith('// ── Laser pointer relay'):
            i += 1
            continue

        # 16. Remove Blackout relay comment block
        if stripped.startswith('// ── Blackout relay'):
            i += 1
            continue

        # 17. Remove let laserDot = null; declaration
        if stripped == 'let laserDot=null;' or stripped == 'let laserDot = null;':
            i += 1
            continue

        # 18. Remove let blackoutEl = null; declaration
        if stripped == 'let blackoutEl=null;' or stripped == 'let blackoutEl = null;':
            i += 1
            continue

        # 19. Remove postMessage bridge block
        if '// postMessage bridge' in stripped and 'presenter' in stripped.lower():
            # Skip the comment and the next few lines (window.addEventListener block)
            i += 1
            while i < len(lines):
                if 'window.addEventListener' in lines[i] and "'message'" in lines[i]:
                    # Skip until closing of this block
                    brace_count = lines[i].count('{') - lines[i].count('}')
                    i += 1
                    while i < len(lines) and brace_count > 0:
                        brace_count += lines[i].count('{') - lines[i].count('}')
                        i += 1
                    break
                elif lines[i].strip() == '':
                    i += 1
                    break
                else:
                    i += 1
                    break
            continue

        # 20. Remove inline Presenter View Template comment + script block
        if re.match(r'<!--\s*═+\s*Inline\s+Presenter\s+View', stripped) or \
           re.match(r'<!--\s*═+\s*PRESENTER\s+VIEW', stripped) or \
           stripped == '<!-- ══ Inline Presenter View Template ══ -->':
            # Skip everything until matching </script>
            i += 1
            script_depth = 0
            while i < len(lines):
                if '<script' in lines[i]:
                    script_depth += 1
                if '</script>' in lines[i]:
                    script_depth -= 1
                    if script_depth <= 0:
                        i += 1
                        break
                i += 1
            continue

        # 21. Remove "Slide counter + Presenter button" CSS comment
        if 'Presenter button' in stripped and '/*' in stripped:
            i += 1
            continue

        # 22. Remove // Presenter button JS comment
        if stripped.strip() == '// Presenter button':
            i += 1
            continue

        result.append(line)
        i += 1

    # Clean up excessive blank lines
    text = '\n'.join(result)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text


def remove_presenter_from_forai_white(content: str) -> str:
    """Remove Presenter Mode from template-forai-white.html (class-based architecture)."""
    # This template uses a class-based approach with different code patterns

    # 1. Remove HTML comment
    content = re.sub(r'    3\. Press \[P\] for presenter mode\n', '', content)

    # 2. Remove CSS comment about Presenter button
    content = re.sub(r'    /\* ── Slide counter \+ Presenter button ─+ \*/\n', '    /* ── Slide counter ───────────────────────── */\n', content)

    # 3. Remove #presenterBtn CSS rules
    content = re.sub(r'    #presenterBtn \{[^}]*\}\n', '', content)
    content = re.sub(r'    #presenterBtn:hover \{[^}]*\}\n', '', content)

    # 4. Remove #presenterBtn from print queries
    content = content.replace(', #presenterBtn { display: none; }', ' { display: none; }')
    content = content.replace(', #presenterBtn { display: none !important; }', ' { display: none !important; }')

    # 5. Remove HTML button and comment
    content = re.sub(r'<!-- Presenter mode button -->\n<button id="presenterBtn"[^>]*>[^<]*</button>\n', '', content)

    # 6. Remove Presenter button JS comment and event listener
    content = re.sub(r"    // Presenter button\n    const presenterBtn = document\.getElementById\('presenterBtn'\);\n    if \(presenterBtn\) presenterBtn\.addEventListener\('click', \(\) => this\._openPresenterView\(\)\);\n", '', content)

    # 7. Remove case 'p': case 'P' from keyboard handler
    content = re.sub(r"        case 'p': case 'P': this\._openPresenterView\(\); break;\n", '', content)

    # 8. Remove postMessage bridge (presenter-related)
    content = re.sub(r"    // postMessage bridge — allows Presenter iframe to drive this page\n    window\.addEventListener\('message', e => \{\n      if \(e\.data && e\.data\.type === 'goto-slide'\) this\.goTo\(e\.data\.index, true\);\n    \}\);\n", '', content)

    # 9. Remove BroadcastChannel init and handler
    content = re.sub(
        r"    // BroadcastChannel \(Presenter Mode\)\n    this\._channel = new BroadcastChannel\('slides-presenter-sync'\);\n    this\._channel\.onmessage = e => \{[^}]*\};\n",
        '', content)

    # 10. Remove _showLaser method
    content = re.sub(
        r"  _showLaser\(x, y\) \{[^}]*\n    \}\n",
        '', content)

    # 11. Remove _setBlackout method
    content = re.sub(
        r"  _setBlackout\(active\) \{[^}]*\n    \}\n",
        '', content)

    # 12. Remove _broadcastState method
    content = re.sub(
        r"  _broadcastState\(\) \{[^}]*\n      \}\n    \}\n",
        '', content)

    # 13. Remove _openPresenterView method and _presenterViewHTML method
    # These are more complex, need to match multi-line methods
    # _openPresenterView
    content = re.sub(
        r"  /\* ── Presenter Mode v2 ─+ \*/\n  _openPresenterView\(\) \{.*?\n  \}\n\n",
        '', content, flags=re.DOTALL)

    # _presenterViewHTML - this is a template literal method, very long
    # Find the method and remove it
    pattern = r"  _presenterViewHTML\(\) \{\s*return `<!DOCTYPE html>.*?</script></body></html>`;\s*\}"
    content = re.sub(pattern, '', content, flags=re.DOTALL)

    # Also handle the variant with escaped script tag
    pattern2 = r"  _presenterViewHTML\(\) \{.*?<\\/script></body></html>`;\s*\}"
    content = re.sub(pattern2, '', content, flags=re.DOTALL)

    # Clean up excessive blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)

    return content


def remove_presenter_from_hhart_red(content: str) -> str:
    """Remove Presenter Mode from template-hhart-red.html (class-based architecture)."""

    # 1. Remove HTML comment
    content = re.sub(r'    4\. Press \[P\] for presenter mode\n', '', content)

    # 2. Remove #presenterBtn CSS rules
    content = re.sub(r'    #presenterBtn \{[^}]*\}\n', '', content)
    content = re.sub(r'    #presenterBtn:hover \{[^}]*\}\n', '', content)

    # 3. Remove #presenterBtn from print queries
    content = content.replace(', #presenterBtn { display: none; }', ' { display: none; }')

    # 4. Remove HTML button
    content = re.sub(r'  <button id="presenterBtn"[^>]*>[^<]*</button>\n', '', content)

    # 5. Remove this.channel = new BroadcastChannel
    content = re.sub(r"        this\.channel\s*=\s*new BroadcastChannel\('slide-sync'\);\n", '', content)

    # 6. Remove this._bindChannel() call
    content = re.sub(r"        this\._bindChannel\(\);\n", '', content)

    # 7. Remove presenterBtn addEventListener
    content = re.sub(r"        document\.getElementById\('presenterBtn'\)\.addEventListener\('click', \(\) => this\._openPresenter\(\)\);\n", '', content)

    # 8. Remove 'p': and 'P': from keyboard map
    content = re.sub(r"            'p': \(\) => this\._openPresenter\(\), 'P': \(\) => this\._openPresenter\(\)\n", '', content)

    # 9. Remove _bindChannel method
    content = re.sub(
        r"      _bindChannel\(\) \{.*?\n      \}\n",
        '', content, flags=re.DOTALL)

    # 10. Remove _openPresenter method
    content = re.sub(
        r"      _openPresenter\(\) \{.*?\n      \}\n",
        '', content, flags=re.DOTALL)

    # 11. Remove inline Presenter View Template
    content = re.sub(
        r"  <!-- ── PRESENTER VIEW TEMPLATE ─+ -->\n  <script id=\"presenter-view-html\" type=\"text/plain\">.*?</script>\n",
        '', content, flags=re.DOTALL)

    # Clean up
    content = re.sub(r'\n{3,}', '\n\n', content)

    return content


def remove_presenter_from_pash_orange(content: str) -> str:
    """Remove Presenter Mode from template-pash-orange.html (IIFE + named function style)."""

    # 1. Remove HTML comment
    content = re.sub(r'    4\. Press \[P\] for presenter mode\n', '', content)

    # 2. Remove #presenterBtn CSS rules (multi-line)
    content = re.sub(
        r'    #presenterBtn \{\s*position: fixed;[^}]*\}\n',
        '', content, flags=re.DOTALL)
    content = re.sub(r'    #presenterBtn:hover \{[^}]*\}\n', '', content)

    # 3. Remove #presenterBtn from print queries
    content = content.replace(', #presenterBtn { display: none !important; }', ' { display: none !important; }')

    # 4. Remove HTML button
    content = re.sub(r'<button id="presenterBtn">[^<]*</button>\n', '', content)

    # 5. Remove BroadcastChannel for Presenter Mode comment and try block in goTo
    content = re.sub(
        r"    /\* BroadcastChannel for Presenter Mode \*/\n    try \{[^}]*\} catch \(e\) \{\}\n",
        '', content)

    # 6. Remove 'p' || 'P' key handler
    content = re.sub(r"    else if \(e\.key === 'p' \|\| e\.key === 'P'\) \{ openPresenterView\(\); \}\n", '', content)

    # 7. Remove BROADCASTER block
    content = re.sub(
        r"  /\* =+\n     BROADCASTER — for Presenter Mode\n[^*]*\*+ \*/\n  const presenterChannel = new BroadcastChannel\('slides-presenter-sync'\);\n",
        '', content, flags=re.DOTALL)

    # 8. Remove presenterChannel.onmessage block
    content = re.sub(
        r"  presenterChannel\.onmessage = \(e\) => \{.*?\n  \};\n",
        '', content, flags=re.DOTALL)

    # 9. Remove window.addEventListener('load') presenter init block
    content = re.sub(
        r"  window\.addEventListener\('load', \(\) => \{\n    presenterChannel\.postMessage.*?\n  \}\);\n",
        '', content, flags=re.DOTALL)

    # 10. Remove Laser pointer overlay block
    content = re.sub(
        r"  /\* ── Laser pointer overlay ── \*/\n  const laserDot = document\.createElement.*?document\.body\.appendChild\(laserDot\);\n\n  function showLaser.*?\n  \}\n",
        '', content, flags=re.DOTALL)

    # 11. Remove Blackout block
    content = re.sub(
        r"  /\* ── Blackout ── \*/\n  const blackoutOverlay.*?document\.addEventListener\('keydown', e => \{\n    if \(e\.key === 'b' \|\| e\.key === 'B'\) toggleBlackout\(\);\n  \}\);\n",
        '', content, flags=re.DOTALL)

    # 12. Remove PRESENTER VIEW section
    content = re.sub(
        r"  /\* =+\n     PRESENTER VIEW\n[^*]*\*+ \*/\n  document\.getElementById\('presenterBtn'\)\.addEventListener.*?\n  \}\);\n",
        '', content, flags=re.DOTALL)

    # 13. Remove postMessage bridge
    content = re.sub(
        r"  // postMessage bridge — Presenter iframe drives this page via postMessage\n  window\.addEventListener\('message', e => \{\n    if \(e\.data && e\.data\.type === 'goto-slide'\) goTo\(e\.data\.index\);\n  \}\);\n",
        '', content)

    # 14. Remove inline Presenter View Template
    content = re.sub(
        r"<!-- =+\n     PRESENTER VIEW TEMPLATE \(inline, not rendered\)\n     =+ -->\n<script id=\"presenter-view-html\" type=\"text/plain\">.*?</script>\n\n",
        '', content, flags=re.DOTALL)

    # Also handle the closing </body></html> after the template
    content = re.sub(r'\n</body>\n</html>\n$', '\n', content)

    # Clean up
    content = re.sub(r'\n{3,}', '\n\n', content)

    return content


def finalize_html(content: str) -> str:
    """Ensure the file ends with </body></html>"""
    content = content.rstrip()
    if not content.endswith('</html>'):
        content = content.rstrip() + '\n</html>\n'
    return content + '\n'


# Template-specific handlers
HANDLERS = {
    'template-pitch-deck.html': remove_presenter_from_simple,
    'template-tech-talk.html': remove_presenter_from_simple,
    'template-product-launch.html': remove_presenter_from_simple,
    'template-quarterly-report.html': remove_presenter_from_simple,
    'template-claude-warmth.html': remove_presenter_from_simple,
    'template-forai-white.html': remove_presenter_from_forai_white,
    'template-hhart-red.html': remove_presenter_from_hhart_red,
    'template-pash-orange.html': remove_presenter_from_pash_orange,
}


def main():
    count = 0
    for f in sorted(TEMPLATES_DIR.glob("template-*.html")):
        handler = HANDLERS.get(f.name)
        if not handler:
            print(f"  SKIP (no handler): {f.name}")
            continue

        original = f.read_text(encoding="utf-8")

        # Check if presenter mode code exists
        if 'presenter' not in original.lower():
            print(f"  SKIP (already clean): {f.name}")
            continue

        cleaned = handler(original)
        cleaned = finalize_html(cleaned)

        # Verify presenter code is removed
        remaining = [line for line in cleaned.split('\n') if 'presenter' in line.lower() and 'data-notes' not in line.lower()]
        # Allow some benign references
        benign_remaining = [line for line in remaining
                           if 'presenter' in line.lower()
                           and not any(kw in line.lower() for kw in [
                               'data-notes', 'slide-label', 'subtitle', 'presenter info',
                               'presenter / event', 'company, presenter', 'subtitle, presenter'
                           ])]

        if benign_remaining:
            print(f"  WARNING - {f.name}: {len(benign_remaining)} lines still contain 'presenter':")
            for line in benign_remaining[:5]:
                print(f"    {line.strip()[:100]}")

        f.write_text(cleaned, encoding="utf-8")
        size_before = len(original)
        size_after = len(cleaned)
        reduction = (1 - size_after / size_before) * 100
        print(f"  CLEANED: {f.name} ({size_before} → {size_after} chars, -{reduction:.1f}%)")
        count += 1

    print(f"\nDone. {count} templates cleaned.")


if __name__ == '__main__':
    main()
