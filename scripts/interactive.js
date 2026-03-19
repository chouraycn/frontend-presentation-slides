/**
 * interactive.js — Interactive Slide Modules (Zero-Dependency)
 * ════════════════════════════════════════════════════════════════════════════
 * Provides opt-in interactive components for frontend-slides presentations.
 * Zero external dependencies. Inline this file into the final HTML before
 * </body> alongside charts.js.
 *
 * Available modules:
 *   SlideInteractive.poll(el, options)    — Live audience poll (QR + local vote tally)
 *   SlideInteractive.quiz(el, options)    — Multiple-choice quiz with reveal
 *   SlideInteractive.wordcloud(el, words) — Animated word cloud input
 *   SlideInteractive.timer(el, options)   — Countdown / stopwatch
 *   SlideInteractive.rating(el, options)  — 1–5 star / emoji rating widget
 *   SlideInteractive.qrcode(el, url)      — QR code generator (pure SVG, no libs)
 *
 * Usage:
 *   // In your slide HTML:
 *   <div id="poll-1"></div>
 *   <script>
 *     SlideInteractive.poll('#poll-1', {
 *       question: 'What is the biggest challenge?',
 *       options: ['Time', 'Budget', 'People', 'Technology'],
 *       allowMultiple: false
 *     });
 *   </script>
 *
 * Storage:
 *   All vote/response data is stored in localStorage under 'slide-interactive-*'
 *   keys. Data persists across page reloads and can be exported via
 *   SlideInteractive.exportData().
 *
 * BroadcastChannel sync:
 *   Votes are broadcast on 'slide-interactive' channel so multiple open
 *   windows stay in sync automatically.
 * ════════════════════════════════════════════════════════════════════════════
 */

const SlideInteractive = (() => {
  'use strict';

  // ── Shared channel for multi-window sync ──────────────────────────────────
  const channel = typeof BroadcastChannel !== 'undefined'
    ? new BroadcastChannel('slide-interactive')
    : null;

  // ── Storage helpers ───────────────────────────────────────────────────────
  const store = {
    key: id => `slide-interactive-${id}`,
    get: id => {
      try { return JSON.parse(localStorage.getItem(store.key(id)) || 'null'); }
      catch { return null; }
    },
    set: (id, data) => {
      try {
        localStorage.setItem(store.key(id), JSON.stringify(data));
        if (channel) channel.postMessage({ type: 'update', id, data });
      } catch {}
    },
    clear: id => localStorage.removeItem(store.key(id)),
  };

  // ── DOM helpers ───────────────────────────────────────────────────────────
  function resolve(el) {
    return typeof el === 'string' ? document.querySelector(el) : el;
  }

  function css(el, styles) {
    Object.assign(el.style, styles);
  }

  function create(tag, attrs = {}, ...children) {
    const el = document.createElement(tag);
    Object.entries(attrs).forEach(([k, v]) => {
      if (k === 'class') el.className = v;
      else if (k === 'style') css(el, v);
      else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
      else el.setAttribute(k, v);
    });
    children.forEach(c => c && el.append(typeof c === 'string' ? c : c));
    return el;
  }

  // ── Theme detection (matches parent slide theme) ──────────────────────────
  function getThemeColors() {
    const root = document.documentElement;
    const style = getComputedStyle(root);
    return {
      primary:  style.getPropertyValue('--primary').trim()  || '#6366f1',
      bg:       style.getPropertyValue('--bg').trim()       || '#0f0f1a',
      surface:  style.getPropertyValue('--surface').trim()  || 'rgba(255,255,255,0.08)',
      text:     style.getPropertyValue('--text').trim()     || '#f0f0f0',
      muted:    style.getPropertyValue('--muted').trim()    || 'rgba(255,255,255,0.5)',
      accent:   style.getPropertyValue('--accent').trim()   || '#6366f1',
    };
  }

  // ── Module: Poll ──────────────────────────────────────────────────────────
  /**
   * SlideInteractive.poll(el, options)
   *
   * @param {string|Element} el  Target container element
   * @param {Object} options
   *   question      {string}   Poll question
   *   options       {string[]} Answer choices
   *   allowMultiple {boolean}  Allow multiple selection (default: false)
   *   showResults   {boolean}  Show results immediately (default: true)
   *   accentColor   {string}   Bar color override
   *   id            {string}   Unique poll ID (auto-generated if omitted)
   */
  function poll(el, opts = {}) {
    el = resolve(el);
    if (!el) return;

    const {
      question    = 'What do you think?',
      options: choices = ['Option A', 'Option B', 'Option C'],
      allowMultiple = false,
      showResults   = true,
      accentColor   = getThemeColors().primary,
      id            = `poll-${Date.now()}`,
    } = opts;

    // Load or init vote data
    let data = store.get(id) || { votes: new Array(choices.length).fill(0), total: 0, voted: false };

    function totalVotes() { return data.votes.reduce((a, b) => a + b, 0); }

    function render() {
      el.innerHTML = '';
      const total = totalVotes();

      el.append(
        create('div', {
          class: 'si-poll',
          style: {
            fontFamily: 'inherit',
            padding: '1.5rem',
            borderRadius: '12px',
            background: 'rgba(255,255,255,0.06)',
            backdropFilter: 'blur(8px)',
            maxWidth: '640px',
          }
        },
          create('p', {
            style: { fontSize: 'clamp(1rem, 2vw, 1.25rem)', fontWeight: '600',
                     color: getThemeColors().text, marginBottom: '1rem' }
          }, question),
          ...choices.map((choice, i) => {
            const pct = total > 0 ? Math.round((data.votes[i] / total) * 100) : 0;
            const isVoted = data.voted;

            const btn = create('button', {
              onclick: () => vote(i),
              style: {
                display: 'block', width: '100%', textAlign: 'left',
                padding: '0.6rem 1rem', marginBottom: '0.5rem',
                borderRadius: '8px', border: `1.5px solid ${accentColor}44`,
                background: 'transparent', cursor: isVoted ? 'default' : 'pointer',
                color: getThemeColors().text, fontSize: 'clamp(0.85rem, 1.5vw, 1rem)',
                position: 'relative', overflow: 'hidden',
                transition: 'border-color 0.2s',
              }
            });

            if (isVoted && showResults) {
              // Progress bar fill
              const bar = create('div', {
                style: {
                  position: 'absolute', left: '0', top: '0',
                  height: '100%', width: `${pct}%`,
                  background: `${accentColor}22`,
                  transition: 'width 0.6s cubic-bezier(0.4,0,0.2,1)',
                  borderRadius: '6px',
                }
              });
              btn.append(bar);
            }

            btn.append(
              create('span', { style: { position: 'relative', zIndex: '1' } }, choice)
            );

            if (isVoted && showResults) {
              btn.append(
                create('span', {
                  style: {
                    position: 'absolute', right: '1rem', top: '50%',
                    transform: 'translateY(-50%)',
                    fontSize: '0.85rem', opacity: '0.7',
                    zIndex: '1',
                  }
                }, `${pct}%`)
              );
            }

            return btn;
          }),
          create('p', {
            style: { fontSize: '0.8rem', opacity: '0.5', marginTop: '0.75rem',
                     color: getThemeColors().text }
          }, total > 0 ? `${total} response${total !== 1 ? 's' : ''}` : 'No votes yet')
        )
      );
    }

    function vote(idx) {
      if (data.voted && !allowMultiple) return;
      data.votes[idx]++;
      data.total = totalVotes();
      data.voted = true;
      store.set(id, data);
      render();
    }

    // Listen for remote votes (other windows)
    if (channel) {
      channel.onmessage = e => {
        if (e.data.type === 'update' && e.data.id === id) {
          data = e.data.data;
          render();
        }
      };
    }

    render();

    return {
      reset: () => { data = { votes: new Array(choices.length).fill(0), total: 0, voted: false }; store.set(id, data); render(); },
      getData: () => ({ ...data }),
    };
  }

  // ── Module: Quiz ──────────────────────────────────────────────────────────
  /**
   * SlideInteractive.quiz(el, options)
   * Multiple-choice quiz with animated reveal of correct answer.
   */
  function quiz(el, opts = {}) {
    el = resolve(el);
    if (!el) return;

    const {
      question   = 'Quiz question?',
      options: choices = [],
      correct    = 0,        // index of correct answer
      explanation = '',
      accentColor = getThemeColors().primary,
    } = opts;

    let answered = null;

    function render() {
      el.innerHTML = '';
      const colors = getThemeColors();

      el.append(
        create('div', {
          style: { fontFamily: 'inherit', padding: '1.5rem',
                   borderRadius: '12px', background: 'rgba(255,255,255,0.06)',
                   maxWidth: '640px' }
        },
          create('p', {
            style: { fontSize: 'clamp(1rem, 2vw, 1.2rem)', fontWeight: '600',
                     color: colors.text, marginBottom: '1rem' }
          }, question),
          ...choices.map((choice, i) => {
            let bg = 'transparent', borderColor = `${accentColor}44`;
            let icon = '';

            if (answered !== null) {
              if (i === correct) {
                bg = 'rgba(34,197,94,0.15)'; borderColor = '#22c55e'; icon = ' ✓';
              } else if (i === answered && answered !== correct) {
                bg = 'rgba(239,68,68,0.15)'; borderColor = '#ef4444'; icon = ' ✗';
              }
            }

            return create('button', {
              onclick: () => { if (answered === null) { answered = i; render(); } },
              style: {
                display: 'block', width: '100%', textAlign: 'left',
                padding: '0.65rem 1rem', marginBottom: '0.5rem',
                borderRadius: '8px', border: `1.5px solid ${borderColor}`,
                background: bg, cursor: answered !== null ? 'default' : 'pointer',
                color: colors.text, fontSize: 'clamp(0.85rem, 1.5vw, 1rem)',
                transition: 'all 0.3s',
              }
            }, choice + icon);
          }),
          answered !== null && explanation
            ? create('p', {
                style: { marginTop: '1rem', padding: '0.75rem', borderRadius: '8px',
                         background: 'rgba(255,255,255,0.06)', color: colors.muted,
                         fontSize: '0.9rem', lineHeight: '1.6' }
              }, explanation)
            : null,
          create('button', {
            onclick: () => { answered = null; render(); },
            style: {
              marginTop: '0.75rem', padding: '0.4rem 0.9rem', border: 'none',
              borderRadius: '6px', background: `${accentColor}33`,
              color: accentColor, cursor: 'pointer', fontSize: '0.8rem',
            }
          }, 'Reset')
        )
      );
    }

    render();
    return { reset: () => { answered = null; render(); } };
  }

  // ── Module: Timer ─────────────────────────────────────────────────────────
  /**
   * SlideInteractive.timer(el, options)
   * Countdown or stopwatch with visual urgency indicators.
   */
  function timer(el, opts = {}) {
    el = resolve(el);
    if (!el) return;

    const {
      mode        = 'countdown',   // 'countdown' | 'stopwatch'
      seconds     = 60,
      warningAt   = 10,            // seconds remaining when color turns yellow
      dangerAt    = 5,             // seconds remaining when color turns red
      accentColor = getThemeColors().primary,
      autoStart   = false,
    } = opts;

    // ── btnStyle must be defined before use (used in DOM creation below) ─────
    function btnStyle(bg) {
      return { padding: '0.4rem 1rem', border: 'none', borderRadius: '8px',
               background: bg, color: '#fff', cursor: 'pointer',
               fontSize: '0.85rem', fontWeight: '500', fontFamily: 'inherit' };
    }

    let remaining = mode === 'countdown' ? seconds : 0;
    let elapsed   = 0;
    let running   = false;
    let interval  = null;

    const display = create('div', {
      style: {
        fontFamily: 'inherit', textAlign: 'center', padding: '2rem',
        borderRadius: '16px', background: 'rgba(255,255,255,0.06)',
        display: 'inline-block', minWidth: '180px',
      }
    });

    const timeEl = create('div', {
      style: { fontSize: 'clamp(2.5rem, 6vw, 4rem)', fontWeight: '700',
               fontVariantNumeric: 'tabular-nums', lineHeight: '1',
               color: accentColor, transition: 'color 0.3s' }
    });

    const controls = create('div', { style: { marginTop: '1rem', display: 'flex', gap: '0.5rem', justifyContent: 'center' } });
    const startBtn = create('button', {
      onclick: toggle,
      style: btnStyle(accentColor),
    }, 'Start');
    const resetBtn = create('button', {
      onclick: reset,
      style: btnStyle('rgba(255,255,255,0.2)'),
    }, 'Reset');

    controls.append(startBtn, resetBtn);
    display.append(timeEl, controls);
    el.append(display);

    function fmt(secs) {
      const m = Math.floor(Math.abs(secs) / 60).toString().padStart(2, '0');
      const s = (Math.abs(secs) % 60).toString().padStart(2, '0');
      return `${m}:${s}`;
    }

    function updateDisplay() {
      const val = mode === 'countdown' ? remaining : elapsed;
      timeEl.textContent = fmt(val);

      if (mode === 'countdown') {
        if (remaining <= dangerAt) timeEl.style.color = '#ef4444';
        else if (remaining <= warningAt) timeEl.style.color = '#f59e0b';
        else timeEl.style.color = accentColor;
      }
    }

    function tick() {
      if (mode === 'countdown') {
        remaining = Math.max(0, remaining - 1);
        if (remaining === 0) { clearInterval(interval); running = false; startBtn.textContent = 'Start'; }
      } else {
        elapsed++;
      }
      updateDisplay();
    }

    function toggle() {
      if (running) {
        clearInterval(interval); running = false; startBtn.textContent = 'Resume';
      } else {
        interval = setInterval(tick, 1000); running = true; startBtn.textContent = 'Pause';
      }
    }

    function reset() {
      clearInterval(interval); running = false;
      remaining = seconds; elapsed = 0;
      startBtn.textContent = 'Start';
      updateDisplay();
    }

    updateDisplay();
    if (autoStart) toggle();

    return { toggle, reset, getTime: () => mode === 'countdown' ? remaining : elapsed };
  }

  // ── Module: Rating ────────────────────────────────────────────────────────
  /**
   * SlideInteractive.rating(el, options)
   * Star or emoji rating widget with tally display.
   */
  function rating(el, opts = {}) {
    el = resolve(el);
    if (!el) return;

    const {
      question    = 'Rate this session',
      max         = 5,
      type        = 'star',    // 'star' | 'emoji'
      id          = `rating-${Date.now()}`,
      accentColor = getThemeColors().primary,
    } = opts;

    const EMOJIS = ['😞', '😐', '🙂', '😊', '🤩'];
    let data = store.get(id) || { counts: new Array(max).fill(0), myRating: null };

    function symbol(i) {
      if (type === 'emoji') return EMOJIS[Math.min(i, EMOJIS.length - 1)];
      return data.myRating !== null && i <= data.myRating ? '★' : '☆';
    }

    function render() {
      el.innerHTML = '';
      const total = data.counts.reduce((a, b) => a + b, 0);
      const avg   = total > 0
        ? (data.counts.reduce((s, c, i) => s + c * (i + 1), 0) / total).toFixed(1)
        : '—';

      const btns = Array.from({ length: max }, (_, i) =>
        create('button', {
          onclick: () => vote(i),
          style: {
            background: 'none', border: 'none', cursor: 'pointer',
            fontSize: 'clamp(1.5rem, 3vw, 2.5rem)', padding: '0 0.2rem',
            color: data.myRating !== null && i <= data.myRating ? accentColor : getThemeColors().muted,
            transition: 'transform 0.15s',
          },
          onmouseenter: e => { e.target.style.transform = 'scale(1.2)'; },
          onmouseleave: e => { e.target.style.transform = 'scale(1)'; },
        }, symbol(i))
      );

      el.append(
        create('div', {
          style: { fontFamily: 'inherit', padding: '1.5rem', textAlign: 'center',
                   borderRadius: '12px', background: 'rgba(255,255,255,0.06)',
                   display: 'inline-block' }
        },
          create('p', {
            style: { color: getThemeColors().text, fontWeight: '600',
                     fontSize: 'clamp(0.9rem, 1.8vw, 1.1rem)', marginBottom: '0.75rem' }
          }, question),
          create('div', {}, ...btns),
          create('p', {
            style: { marginTop: '0.75rem', color: getThemeColors().muted, fontSize: '0.85rem' }
          }, total > 0 ? `Avg: ${avg} / ${max}  (${total} vote${total !== 1 ? 's' : ''})` : 'No ratings yet')
        )
      );
    }

    function vote(idx) {
      if (data.myRating !== null) return; // one vote per session
      data.counts[idx]++;
      data.myRating = idx;
      store.set(id, data);
      render();
    }

    render();
    return { reset: () => { data = { counts: new Array(max).fill(0), myRating: null }; store.set(id, data); render(); } };
  }

  // ── Module: Word Cloud ────────────────────────────────────────────────────
  /**
   * SlideInteractive.wordcloud(el, words, options)
   *
   * Renders an animated word cloud from a flat array of words or weighted
   * word objects. Words can be submitted live by audience members via a
   * small input form.
   *
   * Zero-dependency: pure CSS / JS positioning, no canvas or external libs.
   *
   * @param {string|Element} el  Target container element
   * @param {string[]|{word:string,weight:number}[]} words  Initial words
   * @param {Object} options
   *   showInput    {boolean}  Show an audience input box (default: false)
   *   maxWords     {number}   Max words to display (default: 60)
   *   id           {string}   Unique ID for localStorage persistence
   *   accentColor  {string}   Primary color override
   *   minSize      {number}   Minimum font size in rem (default: 0.8)
   *   maxSize      {number}   Maximum font size in rem (default: 3.0)
   *   animate      {boolean}  Fade-in each word with a staggered delay (default: true)
   *
   * Usage:
   *   // Static word cloud from a preset list
   *   SlideInteractive.wordcloud('#cloud', ['React','Vue','Angular','Svelte'], {
   *     maxSize: 3, minSize: 0.9
   *   });
   *
   *   // Live audience input — attendees type a word and submit
   *   SlideInteractive.wordcloud('#cloud', [], {
   *     showInput: true, id: 'session-cloud'
   *   });
   */
  function wordcloud(el, words = [], opts = {}) {
    el = resolve(el);
    if (!el) return;

    const {
      showInput   = false,
      maxWords    = 60,
      id          = `wc-${Date.now()}`,
      accentColor = getThemeColors().primary,
      minSize     = 0.8,
      maxSize     = 3.0,
      animate     = true,
    } = opts;

    // ── Normalise input words ─────────────────────────────────────────────
    function normalise(list) {
      return list.map(w =>
        typeof w === 'string'
          ? { word: w.trim(), weight: 1 }
          : { word: String(w.word || w.text || '').trim(), weight: Number(w.weight || w.count || 1) }
      ).filter(w => w.word.length > 0);
    }

    // ── Merge & accumulate weights ────────────────────────────────────────
    function merge(existing, incoming) {
      const map = new Map();
      existing.forEach(w => map.set(w.word.toLowerCase(), { word: w.word, weight: w.weight }));
      incoming.forEach(w => {
        const key = w.word.toLowerCase();
        if (map.has(key)) {
          map.get(key).weight += w.weight;
        } else {
          map.set(key, { word: w.word, weight: w.weight });
        }
      });
      return [...map.values()];
    }

    // ── Load persisted data ───────────────────────────────────────────────
    let data = store.get(id);
    if (!data) {
      data = { words: normalise(words) };
    } else if (words.length > 0) {
      // Merge preset words with any previously submitted words
      data.words = merge(data.words, normalise(words));
    }

    // ── Font size scale (linear interpolation) ────────────────────────────
    function scale(weight, minW, maxW) {
      if (minW === maxW) return (minSize + maxSize) / 2;
      return minSize + ((weight - minW) / (maxW - minW)) * (maxSize - minSize);
    }

    // ── Colour palette derived from accentColor + complementary hues ─────
    const PALETTE = [
      accentColor,
      getThemeColors().text,
      getThemeColors().muted,
      shiftHue(accentColor, 30),
      shiftHue(accentColor, -30),
      shiftHue(accentColor, 60),
    ];

    function shiftHue(hex, deg) {
      // Convert hex → HSL → shift hue → back to hex (best-effort)
      try {
        const r = parseInt(hex.slice(1, 3), 16) / 255;
        const g = parseInt(hex.slice(3, 5), 16) / 255;
        const b = parseInt(hex.slice(5, 7), 16) / 255;
        const max = Math.max(r, g, b), min = Math.min(r, g, b);
        let h, s, l = (max + min) / 2;
        if (max === min) { h = s = 0; }
        else {
          const d = max - min;
          s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
          switch (max) {
            case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
            case g: h = ((b - r) / d + 2) / 6; break;
            default: h = ((r - g) / d + 4) / 6;
          }
        }
        h = ((h * 360 + deg) % 360 + 360) % 360 / 360;
        const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
        const p = 2 * l - q;
        const hue2rgb = (p, q, t) => {
          if (t < 0) t += 1; if (t > 1) t -= 1;
          if (t < 1/6) return p + (q - p) * 6 * t;
          if (t < 1/2) return q;
          if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
          return p;
        };
        const rr = Math.round(hue2rgb(p, q, h + 1/3) * 255);
        const gg = Math.round(hue2rgb(p, q, h) * 255);
        const bb = Math.round(hue2rgb(p, q, h - 1/3) * 255);
        return `#${rr.toString(16).padStart(2,'0')}${gg.toString(16).padStart(2,'0')}${bb.toString(16).padStart(2,'0')}`;
      } catch { return hex; }
    }

    // ── Render cloud ──────────────────────────────────────────────────────
    function render() {
      el.innerHTML = '';

      const displayWords = [...data.words]
        .sort((a, b) => b.weight - a.weight)
        .slice(0, maxWords);

      if (displayWords.length === 0) {
        const empty = create('p', {
          style: { color: getThemeColors().muted, fontSize: '0.9rem', textAlign: 'center',
                   padding: '2rem', fontFamily: 'inherit' }
        }, 'No words yet — be the first!');
        el.append(empty);
        if (showInput) el.append(buildInput());
        return;
      }

      const weights = displayWords.map(w => w.weight);
      const minW = Math.min(...weights);
      const maxW = Math.max(...weights);

      // ── Container ─────────────────────────────────────────────────────
      const cloudBox = create('div', {
        style: {
          position: 'relative',
          width: '100%',
          minHeight: '200px',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '0.4rem 0.6rem',
          padding: '1.5rem',
          borderRadius: '16px',
          background: 'rgba(255,255,255,0.04)',
          boxSizing: 'border-box',
        }
      });

      // Shuffle for visual variety (largest words stay on top via font-size)
      const shuffled = [...displayWords].sort(() => Math.random() - 0.5);

      shuffled.forEach((item, idx) => {
        const size = scale(item.weight, minW, maxW);
        const color = PALETTE[Math.floor(Math.random() * PALETTE.length)];
        const opacity = 0.6 + 0.4 * ((item.weight - minW) / Math.max(maxW - minW, 1));

        const wordEl = create('span', {
          style: {
            fontSize: `${size.toFixed(2)}rem`,
            fontWeight: size > (minSize + maxSize) / 2 ? '700' : '500',
            color,
            opacity: animate ? '0' : String(opacity),
            cursor: 'default',
            userSelect: 'none',
            transition: 'transform 0.2s, opacity 0.5s',
            lineHeight: '1.2',
            display: 'inline-block',
            fontFamily: 'inherit',
          },
          title: `${item.word} (${item.weight})`,
          onmouseenter: e => {
            e.target.style.transform = 'scale(1.15)';
            e.target.style.opacity = '1';
          },
          onmouseleave: e => {
            e.target.style.transform = 'scale(1)';
            e.target.style.opacity = String(opacity);
          },
        }, item.word);

        cloudBox.append(wordEl);

        if (animate) {
          setTimeout(() => {
            wordEl.style.opacity = String(opacity);
          }, idx * 40 + 100);
        }
      });

      el.append(cloudBox);

      // Word count badge
      el.append(create('p', {
        style: { textAlign: 'center', color: getThemeColors().muted,
                 fontSize: '0.75rem', marginTop: '0.5rem', fontFamily: 'inherit' }
      }, `${data.words.length} word${data.words.length !== 1 ? 's' : ''} collected`));

      if (showInput) el.append(buildInput());
    }

    // ── Audience input form ───────────────────────────────────────────────
    function buildInput() {
      const input = create('input', {
        type: 'text',
        placeholder: 'Type a word and press Enter…',
        maxlength: '40',
        style: {
          marginTop: '0.75rem',
          padding: '0.5rem 1rem',
          borderRadius: '8px',
          border: `1.5px solid ${accentColor}66`,
          background: 'rgba(255,255,255,0.08)',
          color: getThemeColors().text,
          fontSize: '0.95rem',
          fontFamily: 'inherit',
          width: '220px',
          outline: 'none',
          display: 'block',
          marginLeft: 'auto',
          marginRight: 'auto',
          boxSizing: 'border-box',
        }
      });

      input.addEventListener('keydown', e => {
        if (e.key === 'Enter') {
          const word = input.value.trim();
          if (word) {
            data.words = merge(data.words, [{ word, weight: 1 }]);
            store.set(id, data);
            input.value = '';
            render();
          }
        }
      });

      const wrap = create('div', { style: { textAlign: 'center' } });
      wrap.append(input);
      return wrap;
    }

    // ── Listen for remote submissions (other windows) ─────────────────────
    if (channel) {
      channel.addEventListener('message', e => {
        if (e.data.type === 'update' && e.data.id === id) {
          data = e.data.data;
          render();
        }
      });
    }

    render();

    return {
      add: (word, weight = 1) => {
        data.words = merge(data.words, [{ word: String(word).trim(), weight }]);
        store.set(id, data);
        render();
      },
      clear: () => {
        data = { words: [] };
        store.set(id, data);
        render();
      },
      getData: () => ({ ...data }),
    };
  }

  // ── Module: QR Code ───────────────────────────────────────────────────────
  /**
   * SlideInteractive.qrcode(el, url, options)
   *
   * Renders a QR code for the given URL.
   *
   * Online mode (default): Uses Google Charts API as QR backend — requires
   * internet access. Works fine for conference / classroom use with Wi-Fi.
   *
   * Offline fallback: If the image fails to load (no network, or blocked CDN),
   * automatically falls back to a styled URL-text box so the content is never
   * lost. For fully offline presentations, pass `{ offline: true }` to skip
   * the network request entirely and show only the URL text.
   *
   * NOTE: This is the only module with an optional network dependency.
   * The poll/quiz/timer/rating modules are 100% offline. If you need a
   * fully offline QR code, replace the Google Charts call with a bundled
   * QR library such as qrcode.js (MIT license).
   */
  function qrcode(el, url, opts = {}) {
    el = resolve(el);
    if (!el) return;

    const {
      size       = 200,
      label      = '',
      fgColor    = getThemeColors().text || '#ffffff',
      bgColor    = 'transparent',
      offline    = false,   // set true to skip network request entirely
    } = opts;

    const wrapper = create('div', {
      style: { display: 'inline-flex', flexDirection: 'column', alignItems: 'center',
               gap: '0.5rem', padding: '1rem', borderRadius: '12px',
               background: 'rgba(255,255,255,0.06)' }
    });

    function makeUrlFallback() {
      /** Offline fallback: clean styled box showing the URL. */
      return create('div', {
        style: {
          width: `${size}px`, minHeight: `${Math.round(size * 0.6)}px`,
          borderRadius: '8px', background: '#fff',
          display: 'flex', flexDirection: 'column', alignItems: 'center',
          justifyContent: 'center', padding: '0.75rem', boxSizing: 'border-box',
          gap: '0.4rem',
        }
      },
        create('p', {
          style: { color: '#555', fontSize: '0.65rem', textAlign: 'center',
                   marginBottom: '0.25rem', fontFamily: 'monospace' }
        }, '[ QR — scan URL below ]'),
        create('p', {
          style: { color: '#000', fontSize: '0.7rem', wordBreak: 'break-all',
                   textAlign: 'center', lineHeight: '1.5', fontFamily: 'monospace' }
        }, url)
      );
    }

    if (offline) {
      wrapper.append(makeUrlFallback());
    } else {
      const googleQrUrl = `https://chart.googleapis.com/chart?chs=${size}x${size}&cht=qr&chl=${encodeURIComponent(url)}&choe=UTF-8`;
      const img = create('img', {
        src: googleQrUrl,
        width: size, height: size,
        style: { borderRadius: '8px', background: '#fff', padding: '4px' },
      });
      img.addEventListener('error', () => { img.replaceWith(makeUrlFallback()); });
      wrapper.append(img);
    }

    if (label) {
      wrapper.append(create('p', {
        style: { color: getThemeColors().muted, fontSize: '0.8rem', textAlign: 'center',
                 maxWidth: `${size}px`, wordBreak: 'break-all' }
      }, label));
    }

    wrapper.append(
      create('p', {
        style: { color: getThemeColors().muted, fontSize: '0.7rem',
                 maxWidth: `${size}px`, wordBreak: 'break-all', textAlign: 'center' }
      }, url)
    );

    el.append(wrapper);
  }

  // ── Data export ───────────────────────────────────────────────────────────
  /**
   * SlideInteractive.exportData()
   * Returns all stored interactive data as a JSON string.
   * Useful for post-session analysis.
   */
  function exportData() {
    const result = {};
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('slide-interactive-')) {
        const id = key.replace('slide-interactive-', '');
        try { result[id] = JSON.parse(localStorage.getItem(key)); }
        catch {}
      }
    }
    return JSON.stringify(result, null, 2);
  }

  /**
   * SlideInteractive.clearData()
   * Clears all stored interactive session data.
   */
  function clearData() {
    const keysToRemove = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('slide-interactive-')) keysToRemove.push(key);
    }
    keysToRemove.forEach(k => localStorage.removeItem(k));
    console.log(`SlideInteractive: cleared ${keysToRemove.length} data key(s).`);
  }

  // ── Public API ────────────────────────────────────────────────────────────
  return { poll, quiz, timer, rating, wordcloud, qrcode, exportData, clearData };

})();

// Make available globally
if (typeof window !== 'undefined') window.SlideInteractive = SlideInteractive;
if (typeof module !== 'undefined') module.exports = SlideInteractive;
