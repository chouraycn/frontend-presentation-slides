/**
 * charts.js — Zero-dependency SVG chart engine for frontend-slides skill
 * v2.0 — Dynamic update support with smooth transition animations
 *
 * Usage: Include this script inline in your presentation HTML (copy-paste the
 * whole file into a <script> block), then call the chart functions to inject
 * charts into container elements.
 *
 * Chart types:
 *   SlideCharts.bar(container, data, options)         → ChartInstance
 *   SlideCharts.line(container, data, options)        → ChartInstance
 *   SlideCharts.donut(container, data, options)       → ChartInstance
 *   SlideCharts.horizontalBar(container, data, options) → ChartInstance
 *   SlideCharts.progress(container, data, options)   → ChartInstance
 *   SlideCharts.area(container, data, options)        → ChartInstance
 *   SlideCharts.radar(container, data, options)       → ChartInstance
 *   SlideCharts.sankey(container, data, options)      → ChartInstance
 *   SlideCharts.treemap(container, data, options)     → ChartInstance
 *   SlideCharts.waterfall(container, data, options)   → ChartInstance
 *   SlideCharts.bullet(container, data, options)      → ChartInstance
 *   SlideCharts.scatter(container, data, options)     → ChartInstance
 *   SlideCharts.gauge(container, data, options)       → ChartInstance
 *
 * ── v2.0 Dynamic Update API ───────────────────────────────────────────────
 *
 *   const chart = SlideCharts.bar('#myChart', data, options);
 *
 *   // Update with new data (smooth animated transition):
 *   chart.update(newData);
 *
 *   // Update options (re-renders with new style):
 *   chart.setOptions(newOptions);
 *
 *   // Trigger re-render (e.g. after container resize):
 *   chart.render();
 *
 *   // Load data from URL or postMessage:
 *   chart.loadURL('https://example.com/data.json', transformer?);
 *
 *   // Listen for external data via postMessage:
 *   //   window.postMessage({ type: 'chart:data', id: 'myChart', data: {...} }, '*')
 *   chart.listenPostMessage();
 *
 * ── Theme Integration ────────────────────────────────────────────────────
 *
 *   This library integrates seamlessly with charts-theme-adapter.js for
 *   automatic theme color detection and palette generation:
 *
 *   <script src="charts.js"></script>
 *   <script src="charts-theme-adapter.js"></script>
 *
 *   // Auto-detect template theme and apply colors:
 *   SlideChartsTheme.applyToCharts();
 *
 *   // Or manually specify theme and style:
 *   const palette = SlideChartsTheme.getPalette({
 *     theme: 'pash-orange',
 *     style: 'monochrome',
 *     count: 6
 *   });
 *   SlideChartsTheme.updateChartsPalette(palette);
 *
 * ── All charts ────────────────────────────────────────────────────────────
 *   - Are pure SVG + CSS — zero dependencies
 *   - Animate on first render (respects prefers-reduced-motion)
 *   - Use CSS custom properties for theming (inherit from :root)
 *   - Are fully responsive via viewBox
 *   - Emit a 'chart:ready' CustomEvent on the container when done
 *   - Emit a 'chart:updated' CustomEvent when update() is called
 *
 * ─── Quick Example ────────────────────────────────────────────────────────
 *
 * <div id="myChart" class="chart-container"></div>
 * <script>
 *   const chart = SlideCharts.bar('#myChart', {
 *     labels: ['Q1', 'Q2', 'Q3', 'Q4'],
 *     datasets: [{ label: 'Revenue', values: [42, 68, 55, 91], color: 'var(--accent)' }]
 *   });
 *
 *   // Later — animated update:
 *   chart.update({
 *     labels: ['Q1', 'Q2', 'Q3', 'Q4'],
 *     datasets: [{ label: 'Revenue', values: [58, 74, 69, 103], color: 'var(--accent)' }]
 *   });
 * </script>
 *
 * ─────────────────────────────────────────────────────────────────────────
 */

const SlideCharts = (() => {
  'use strict';

  // ── Utility helpers ──────────────────────────────────────────────────────

  const svgNS = 'http://www.w3.org/2000/svg';

  /** Create an SVG element with attributes */
  function svgEl(tag, attrs = {}) {
    const el = document.createElementNS(svgNS, tag);
    for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
    return el;
  }

  /** Resolve a selector or element reference to a DOM node */
  function resolve(container) {
    return typeof container === 'string'
      ? document.querySelector(container)
      : container;
  }

  /** Check user motion preference */
  function prefersReducedMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  /** Lerp between two values */
  function lerp(a, b, t) { return a + (b - a) * t; }

  /** Ease-out cubic */
  function easeOut(t) { return 1 - Math.pow(1 - t, 3); }

  /** Format numbers compactly: 1200 → "1.2k", 1500000 → "1.5M" */
  function fmt(n) {
    if (Math.abs(n) >= 1e6) return (n / 1e6).toFixed(1).replace(/\.0$/, '') + 'M';
    if (Math.abs(n) >= 1e3) return (n / 1e3).toFixed(1).replace(/\.0$/, '') + 'k';
    return String(n);
  }

  /** Generate a unique ID for clip paths / gradients */
  let _uid = 0;
  function uid(prefix = 'sc') { return `${prefix}-${++_uid}`; }

  /** Inject shared CSS once */
  let _cssInjected = false;
  function injectCSS() {
    if (_cssInjected) return;
    _cssInjected = true;
    const style = document.createElement('style');
    style.textContent = `
      /* ── SlideCharts shared styles ── */
      .sc-wrap { width: 100%; height: 100%; }
      .sc-svg   { overflow: visible; display: block; }
      .sc-label { font-family: var(--font-body, system-ui, sans-serif); }
      .sc-title { font-family: var(--font-heading, system-ui, sans-serif); font-weight: 700; }
      .sc-legend { display: flex; gap: 16px; flex-wrap: wrap; justify-content: center;
                   margin-top: 12px; font-family: var(--font-body, system-ui, sans-serif); }
      .sc-legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px;
                        color: var(--text-secondary, #888); }
      .sc-legend-dot  { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

      /* Bar animation */
      @keyframes sc-growY {
        from { transform: scaleY(0); }
        to   { transform: scaleY(1); }
      }
      @keyframes sc-growX {
        from { transform: scaleX(0); }
        to   { transform: scaleX(1); }
      }
      @keyframes sc-fadeIn {
        from { opacity: 0; }
        to   { opacity: 1; }
      }
      @keyframes sc-drawLine {
        from { stroke-dashoffset: var(--sc-len, 1000); }
        to   { stroke-dashoffset: 0; }
      }
      @keyframes sc-donutSpin {
        from { stroke-dashoffset: var(--sc-circumference, 314); }
        to   { stroke-dashoffset: var(--sc-target, 0); }
      }
      @keyframes sc-progressFill {
        from { width: 0%; }
        to   { width: var(--sc-pct, 0%); }
      }

      /* Update flash pulse — signals a live data change */
      @keyframes sc-updatePulse {
        0%   { opacity: 1; }
        30%  { opacity: 0.35; }
        100% { opacity: 1; }
      }
      .sc-updating { animation: sc-updatePulse 0.4s ease; }

      /* ── Tooltip ── */
      .sc-tooltip {
        position: fixed; z-index: 9999; pointer-events: none;
        background: var(--sc-tooltip-bg, rgba(20,20,30,0.93));
        color: var(--sc-tooltip-color, #f0f0f0);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 7px;
        padding: 7px 11px;
        font-family: var(--font-body, system-ui, sans-serif);
        font-size: 12px;
        line-height: 1.55;
        box-shadow: 0 6px 24px rgba(0,0,0,0.35);
        backdrop-filter: blur(4px);
        white-space: nowrap;
        opacity: 0;
        transform: translateY(4px) scale(0.97);
        transition: opacity 0.15s ease, transform 0.15s ease;
        max-width: 200px;
        white-space: normal;
      }
      .sc-tooltip.visible {
        opacity: 1;
        transform: translateY(0) scale(1);
      }
      .sc-tooltip-label {
        font-weight: 600;
        margin-bottom: 2px;
      }
      .sc-tooltip-value {
        color: var(--accent, #6366f1);
        font-weight: 700;
      }

      /* ── Legend interactive filter ── */
      .sc-legend-item {
        cursor: pointer;
        transition: opacity 0.2s ease;
        user-select: none;
      }
      .sc-legend-item:hover  { opacity: 0.75; }
      .sc-legend-item.hidden { opacity: 0.3; text-decoration: line-through; }

      @media (prefers-reduced-motion: reduce) {
        .sc-bar-rect, .sc-line-path, .sc-donut-arc, .sc-progress-fill,
        .sc-hbar-rect { animation: none !important; transition: none !important; }
      }
    `;
    document.head.appendChild(style);
  }

  // ── Default palette (falls back to CSS vars, then hardcoded) ─────────────
  const PALETTE = [
    'var(--accent,  #6366f1)',
    'var(--accent2, #ec4899)',
    'var(--chart3,  #10b981)',
    'var(--chart4,  #f59e0b)',
    'var(--chart5,  #3b82f6)',
    'var(--chart6,  #ef4444)',
  ];

  // ── Tooltip singleton ─────────────────────────────────────────────────────

  let _tooltipEl = null;
  let _tooltipHideTimer = null;

  function getTooltip() {
    if (!_tooltipEl) {
      _tooltipEl = document.createElement('div');
      _tooltipEl.className = 'sc-tooltip';
      document.body.appendChild(_tooltipEl);
    }
    return _tooltipEl;
  }

  /**
   * Show the shared tooltip near the cursor.
   * @param {MouseEvent} event
   * @param {string}     label   — e.g. "Q3"
   * @param {string}     value   — e.g. "91K"
   * @param {string}     [color] — swatch color
   */
  function showTooltip(event, label, value, color) {
    clearTimeout(_tooltipHideTimer);
    const tip = getTooltip();
    const swatch = color ? `<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${color};margin-right:5px;flex-shrink:0;"></span>` : '';
    tip.innerHTML = `
      <div class="sc-tooltip-label">${swatch}${label}</div>
      <div class="sc-tooltip-value">${value}</div>
    `;
    positionTooltip(event);
    tip.classList.add('visible');
  }

  function positionTooltip(event) {
    const tip = getTooltip();
    const W = window.innerWidth, H = window.innerHeight;
    const tw = tip.offsetWidth || 140, th = tip.offsetHeight || 50;
    let left = event.clientX + 14;
    let top  = event.clientY - th / 2;
    if (left + tw > W - 8) left = event.clientX - tw - 14;
    if (top < 8) top = 8;
    if (top + th > H - 8) top = H - th - 8;
    tip.style.left = left + 'px';
    tip.style.top  = top  + 'px';
  }

  function hideTooltip() {
    clearTimeout(_tooltipHideTimer);
    _tooltipHideTimer = setTimeout(() => {
      const tip = getTooltip();
      tip.classList.remove('visible');
    }, 80);
  }

  /**
   * Attach hover tooltip to an SVG element.
   * @param {SVGElement} el
   * @param {string}     label
   * @param {string|number} value
   * @param {string}     [color]
   */
  function attachTooltip(el, label, value, color) {
    el.style.cursor = 'default';
    el.addEventListener('mouseenter', (e) => showTooltip(e, label, String(value), color));
    el.addEventListener('mousemove',  (e) => positionTooltip(e));
    el.addEventListener('mouseleave', hideTooltip);
  }

  // ── Legend filter helper ──────────────────────────────────────────────────

  /**
   * Make a legend interactive: clicking a legend item hides/shows
   * the corresponding SVG elements with class `sc-legend-target-{index}`.
   *
   * @param {HTMLElement} legendEl  — .sc-legend wrapper
   * @param {SVGElement}  svgEl     — the chart SVG
   * @param {function}    [onToggle] — optional callback(index, isHidden)
   */
  function makeLegendFilterable(legendEl, chartSvg, onToggle) {
    const items = Array.from(legendEl.querySelectorAll('.sc-legend-item'));
    items.forEach((item, idx) => {
      item.addEventListener('click', () => {
        const isHidden = item.classList.toggle('hidden');
        // Toggle visibility of matching elements in the SVG
        if (chartSvg) {
          const targets = chartSvg.querySelectorAll(`.sc-series-${idx}`);
          targets.forEach(t => {
            t.style.transition = 'opacity 0.25s ease';
            t.style.opacity = isHidden ? '0.05' : '';
            t.style.pointerEvents = isHidden ? 'none' : '';
          });
        }
        if (onToggle) onToggle(idx, isHidden);
      });
    });
  }

  // ── Poll ↔ Chart binding ──────────────────────────────────────────────────

  /**
   * Bind a SlideCharts instance to a live poll data source.
   *
   * Usage:
   *   const chart = SlideCharts.bar('#myChart', initialData);
   *   SlideCharts.pollBind(chart, '#voteEl', {
   *     options: ['Option A', 'Option B', 'Option C'],
   *     color: 'var(--accent)',
   *   });
   *
   * Whenever the vote tallies update (via CustomEvent 'poll:update' on voteEl,
   * or via postMessage { type: 'poll:votes', options: [...], votes: [...] }),
   * the chart is updated with a smooth animation.
   *
   * @param {ChartInstance} chartInstance
   * @param {string|Element} pollContainer  — element that emits 'poll:update' events
   * @param {Object} config
   *   @param {string[]} config.options  — option labels
   *   @param {string}   [config.color]  — bar/segment color
   *   @param {string}   [config.chartType='bar']  — 'bar' | 'donut' | 'horizontalBar'
   */
  function pollBind(chartInstance, pollContainer, config = {}) {
    const { options = [], color, chartType = 'bar' } = config;
    const pollEl = resolve(pollContainer);

    function applyVotes(votes) {
      if (chartType === 'donut') {
        chartInstance.update({
          segments: options.map((opt, i) => ({
            label: opt,
            value: votes[i] || 0,
            color: color || undefined,
          })),
        });
      } else if (chartType === 'horizontalBar') {
        chartInstance.update({
          items: options.map((opt, i) => ({
            label: opt,
            value: votes[i] || 0,
            color: color || undefined,
          })),
        });
      } else {
        // bar (default)
        chartInstance.update({
          labels: options,
          datasets: [{
            label: 'Votes',
            values: options.map((_, i) => votes[i] || 0),
            color: color || undefined,
          }],
        });
      }
    }

    // Listen for CustomEvent 'poll:update' on the poll element
    if (pollEl) {
      pollEl.addEventListener('poll:update', (e) => {
        const votes = e.detail?.votes || [];
        applyVotes(votes);
      });
    }

    // Listen for window.postMessage { type: 'poll:votes', options, votes }
    window.addEventListener('message', (e) => {
      if (!e.data || e.data.type !== 'poll:votes') return;
      const votes = e.data.votes || [];
      applyVotes(votes);
    });

    return { applyVotes };
  }

  function getColor(index, override) {
    return override || PALETTE[index % PALETTE.length];
  }

  // ── Shared axis / grid helpers ────────────────────────────────────────────

  /**
   * Compute nice axis ticks for a value range.
   * Returns { min, max, step, ticks[] }
   */
  function niceScale(dataMin, dataMax, tickCount = 5) {
    const range = dataMax - dataMin || 1;
    const roughStep = range / (tickCount - 1);
    const magnitude = Math.pow(10, Math.floor(Math.log10(roughStep)));
    const niceStep = [1, 2, 2.5, 5, 10].map(f => f * magnitude)
      .find(s => s >= roughStep) || magnitude * 10;
    const min = Math.floor(dataMin / niceStep) * niceStep;
    const max = Math.ceil(dataMax / niceStep) * niceStep;
    const ticks = [];
    for (let t = min; t <= max + niceStep * 0.01; t += niceStep) {
      ticks.push(parseFloat(t.toPrecision(10)));
    }
    return { min, max, step: niceStep, ticks };
  }

  // ── ChartInstance factory ─────────────────────────────────────────────────
  /**
   * Wraps a chart render function into an instance with update/setOptions/render/loadURL/listenPostMessage.
   * @param {Element} el            — the container DOM element
   * @param {Function} renderFn     — (el, data, options) => void
   * @param {Object}  initialData
   * @param {Object}  initialOpts
   * @param {number}  updateDuration — transition duration in ms
   */
  function makeInstance(el, renderFn, initialData, initialOpts, updateDuration = 500) {
    let _data = JSON.parse(JSON.stringify(initialData));
    let _opts  = Object.assign({}, initialOpts);
    let _messageUnlisten = null;

    const instance = {
      /** Get current data snapshot */
      getData() { return JSON.parse(JSON.stringify(_data)); },
      /** Get current options snapshot */
      getOptions() { return Object.assign({}, _opts); },

      /** Re-render in place (e.g. after resize) */
      render() {
        renderFn(el, _data, _opts);
        return instance;
      },

      /** Update options and re-render */
      setOptions(newOpts) {
        Object.assign(_opts, newOpts);
        renderFn(el, _data, _opts);
        el.dispatchEvent(new CustomEvent('chart:updated', { bubbles: true, detail: { data: _data, options: _opts } }));
        return instance;
      },

      /**
       * Animated update to new data.
       * For bar/horizontalBar/progress → interpolates numeric values via rAF.
       * For line/area/donut/radar → cross-fades (fade out old, render new, fade in).
       * Falls back to immediate re-render when prefers-reduced-motion.
       */
      update(newData) {
        _data = JSON.parse(JSON.stringify(newData));

        if (prefersReducedMotion()) {
          renderFn(el, _data, _opts);
          el.dispatchEvent(new CustomEvent('chart:updated', { bubbles: true, detail: { data: _data, options: _opts } }));
          return instance;
        }

        // Cross-fade: pulse the wrapper, then re-render
        const wrap = el.firstElementChild;
        if (wrap) {
          wrap.classList.remove('sc-updating');
          // Force reflow
          void wrap.offsetWidth;
          wrap.classList.add('sc-updating');
        }

        setTimeout(() => {
          renderFn(el, _data, Object.assign({}, _opts, { animDuration: updateDuration }));
          el.dispatchEvent(new CustomEvent('chart:updated', { bubbles: true, detail: { data: _data, options: _opts } }));
        }, 150); // halfway through the pulse

        return instance;
      },

      /**
       * Fetch JSON from a URL and update the chart.
       * @param {string}   url         — endpoint returning chart-compatible JSON
       * @param {Function} [transform] — optional (rawJson) => chartData transformer
       */
      async loadURL(url, transform) {
        try {
          const resp = await fetch(url);
          if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
          const raw = await resp.json();
          instance.update(transform ? transform(raw) : raw);
        } catch (err) {
          console.warn('[SlideCharts] loadURL failed:', err);
        }
        return instance;
      },

      /**
       * Listen for window.postMessage events of the form:
       *   { type: 'chart:data', id: '<containerId>', data: { ... } }
       * Calls update() automatically when a matching message arrives.
       */
      listenPostMessage() {
        if (_messageUnlisten) return instance; // already listening
        const handler = (e) => {
          if (!e.data || e.data.type !== 'chart:data') return;
          const containerId = el.id || el.dataset.chartId;
          if (containerId && e.data.id !== containerId) return;
          instance.update(e.data.data);
        };
        window.addEventListener('message', handler);
        _messageUnlisten = () => window.removeEventListener('message', handler);
        return instance;
      },

      /** Remove the postMessage listener */
      unlistenPostMessage() {
        if (_messageUnlisten) { _messageUnlisten(); _messageUnlisten = null; }
        return instance;
      },
    };

    return instance;
  }

  // ── No-op ChartInstance (returned when container cannot be resolved) ─────
  const _noopInstance = Object.freeze({
    getData()          { return {}; },
    getOptions()       { return {}; },
    render()           { return _noopInstance; },
    setOptions()       { return _noopInstance; },
    update()           { return _noopInstance; },
    async loadURL()    { return _noopInstance; },
    listenPostMessage(){ return _noopInstance; },
    unlistenPostMessage(){ return _noopInstance; },
  });

  // ─────────────────────────────────────────────────────────────────────────
  // BAR CHART
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Renders a vertical bar chart.
   *
   * @param {string|Element} container
   * @param {Object} data
   *   @param {string[]} data.labels
   *   @param {Array<{label:string, values:number[], color?:string}>} data.datasets
   * @param {Object} [options]
   *   @param {number}  [options.width=600]
   *   @param {number}  [options.height=340]
   *   @param {boolean} [options.showGrid=true]
   *   @param {boolean} [options.showValues=true]
   *   @param {boolean} [options.showLegend=true]
   *   @param {number}  [options.barRadius=4]
   *   @param {number}  [options.animDuration=700]  ms
   *   @param {string}  [options.title]
   * @returns {ChartInstance}
   */
  function bar(container, data, options = {}) {
    injectCSS();
    const el = resolve(container);
    if (!el) { console.warn(`[SlideCharts] bar: container not found — "${container}"`); return _noopInstance; }
    _renderBar(el, data, options);
    return makeInstance(el, _renderBar, data, options);
  }

  function _renderBar(el, data, options = {}) {
    const {
      width = 600, height = 340,
      showGrid = true, showValues = true, showLegend = true,
      barRadius = 4, animDuration = 700, title,
    } = options;

    const margin = { top: title ? 48 : 20, right: 20, bottom: 52, left: 48 };
    const W = width - margin.left - margin.right;
    const H = height - margin.top - margin.bottom;

    const allValues = data.datasets.flatMap(d => d.values);
    const scale = niceScale(Math.min(0, ...allValues), Math.max(...allValues));
    const yRange = scale.max - scale.min;

    const svg = svgEl('svg', {
      viewBox: `0 0 ${width} ${height}`,
      class: 'sc-svg',
      role: 'img',
      'aria-label': title || 'Bar chart',
    });

    const defs = svgEl('defs');
    svg.appendChild(defs);

    const gradIds = data.datasets.map((ds, i) => {
      const gid = uid('barg');
      const color = getColor(i, ds.color);
      const grad = svgEl('linearGradient', { id: gid, x1: '0', y1: '0', x2: '0', y2: '1' });
      const s1 = svgEl('stop', { offset: '0%', 'stop-color': color, 'stop-opacity': '1' });
      const s2 = svgEl('stop', { offset: '100%', 'stop-color': color, 'stop-opacity': '0.6' });
      grad.appendChild(s1); grad.appendChild(s2);
      defs.appendChild(grad);
      return gid;
    });

    const g = svgEl('g', { transform: `translate(${margin.left},${margin.top})` });
    svg.appendChild(g);

    if (title) {
      const t = svgEl('text', { x: width / 2, y: -margin.top / 2 + 10, 'text-anchor': 'middle', class: 'sc-title', fill: 'var(--text-primary, #fff)', 'font-size': '14' });
      t.textContent = title;
      g.appendChild(t);
    }

    scale.ticks.forEach(tick => {
      const y = H - ((tick - scale.min) / yRange) * H;
      if (showGrid) {
        g.appendChild(svgEl('line', { x1: 0, y1: y, x2: W, y2: y, stroke: 'var(--text-secondary, #555)', 'stroke-opacity': '0.2', 'stroke-width': '1', 'stroke-dasharray': tick === 0 ? 'none' : '4 4' }));
      }
      const label = svgEl('text', { x: -8, y: y + 4, 'text-anchor': 'end', class: 'sc-label', fill: 'var(--text-secondary, #888)', 'font-size': '11' });
      label.textContent = fmt(tick);
      g.appendChild(label);
    });

    const nGroups = data.labels.length;
    const nSets = data.datasets.length;
    const groupW = W / nGroups;
    const barPad = groupW * 0.15;
    const barW = (groupW - barPad * 2) / nSets;
    const delay = prefersReducedMotion() ? 0 : animDuration / nGroups;

    data.labels.forEach((label, gi) => {
      const groupX = gi * groupW + barPad;
      data.datasets.forEach((ds, di) => {
        const value = ds.values[gi] ?? 0;
        const barH = Math.abs(((value - scale.min) / yRange) * H - ((0 - scale.min) / yRange) * H);
        const barX = groupX + di * barW;
        const barY = H - ((Math.max(value, 0) - scale.min) / yRange) * H;
        const rect = svgEl('rect', { x: barX, y: barY, width: barW * 0.85, height: Math.max(barH, 1), rx: barRadius, ry: barRadius, fill: `url(#${gradIds[di]})`, class: `sc-bar-rect sc-series-${di}`, 'transform-origin': `${barX + barW * 0.4}px ${barY + barH}px` });
        if (!prefersReducedMotion()) rect.style.animation = `sc-growY ${animDuration}ms cubic-bezier(0.34,1.56,0.64,1) ${gi * (delay * 0.5)}ms both`;
        attachTooltip(rect, `${label} — ${ds.label || ''}`, fmt(value), getColor(di, ds.color));
        g.appendChild(rect);
        if (showValues && barH > 12) {
          const vLabel = svgEl('text', { x: barX + barW * 0.4, y: barY - 5, 'text-anchor': 'middle', class: 'sc-label', fill: 'var(--text-secondary, #aaa)', 'font-size': '10', opacity: '0' });
          vLabel.textContent = fmt(value);
          if (!prefersReducedMotion()) vLabel.style.animation = `sc-fadeIn 0.4s ease ${gi * (delay * 0.5) + animDuration * 0.7}ms forwards`;
          else vLabel.setAttribute('opacity', '1');
          g.appendChild(vLabel);
        }
      });
      const xLabel = svgEl('text', { x: gi * groupW + groupW / 2, y: H + 20, 'text-anchor': 'middle', class: 'sc-label', fill: 'var(--text-secondary, #888)', 'font-size': '11' });
      xLabel.textContent = label;
      g.appendChild(xLabel);
    });

    const zeroY = H - ((0 - scale.min) / yRange) * H;
    g.appendChild(svgEl('line', { x1: 0, y1: zeroY, x2: W, y2: zeroY, stroke: 'var(--text-secondary, #555)', 'stroke-width': '1.5' }));

    const wrap = document.createElement('div');
    wrap.className = 'sc-wrap';
    wrap.appendChild(svg);
    if (showLegend && data.datasets.length > 1) {
      const legend = document.createElement('div');
      legend.className = 'sc-legend';
      data.datasets.forEach((ds, i) => {
        const item = document.createElement('div'); item.className = 'sc-legend-item';
        const dot = document.createElement('span'); dot.className = 'sc-legend-dot'; dot.style.background = getColor(i, ds.color);
        item.appendChild(dot); item.appendChild(document.createTextNode(ds.label)); legend.appendChild(item);
      });
      wrap.appendChild(legend);
      makeLegendFilterable(legend, svg);
    }
    el.innerHTML = '';
    el.appendChild(wrap);
    el.dispatchEvent(new CustomEvent('chart:ready', { bubbles: true }));
  }

  // ─────────────────────────────────────────────────────────────────────────
  // LINE / AREA CHART
  // ─────────────────────────────────────────────────────────────────────────

  function line(container, data, options = {}) {
    injectCSS();
    const el = resolve(container);
    if (!el) { console.warn(`[SlideCharts] line: container not found — "${container}"`); return _noopInstance; }
    _renderLine(el, data, { ...options, filled: false });
    return makeInstance(el, (e, d, o) => _renderLine(e, d, { ...o, filled: false }), data, options);
  }

  function area(container, data, options = {}) {
    injectCSS();
    const el = resolve(container);
    if (!el) { console.warn(`[SlideCharts] area: container not found — "${container}"`); return _noopInstance; }
    _renderLine(el, data, { ...options, filled: true });
    return makeInstance(el, (e, d, o) => _renderLine(e, d, { ...o, filled: true }), data, options);
  }

  function _renderLine(el, data, options = {}) {
    const {
      width = 600, height = 320,
      filled = false, smooth = true, dots = true,
      strokeWidth = 2.5, animDuration = 900,
      showGrid = true, showValues = false, showLegend = true, title,
    } = options;

    const margin = { top: title ? 48 : 20, right: 24, bottom: 52, left: 48 };
    const W = width - margin.left - margin.right;
    const H = height - margin.top - margin.bottom;

    const allValues = data.datasets.flatMap(d => d.values);
    const scale = niceScale(Math.min(0, ...allValues), Math.max(...allValues));
    const yRange = scale.max - scale.min;
    const nPoints = data.labels.length;
    // xStep: when only 1 point, center it horizontally instead of NaN
    const xStep = nPoints > 1 ? W / (nPoints - 1) : W / 2;

    const svg = svgEl('svg', { viewBox: `0 0 ${width} ${height}`, class: 'sc-svg', role: 'img', 'aria-label': title || 'Line chart' });
    const defs = svgEl('defs'); svg.appendChild(defs);
    const g = svgEl('g', { transform: `translate(${margin.left},${margin.top})` }); svg.appendChild(g);

    if (title) {
      const t = svgEl('text', { x: width / 2, y: -margin.top / 2 + 10, 'text-anchor': 'middle', class: 'sc-title', fill: 'var(--text-primary, #fff)', 'font-size': '14' });
      t.textContent = title; g.appendChild(t);
    }

    scale.ticks.forEach(tick => {
      const y = H - ((tick - scale.min) / yRange) * H;
      if (showGrid) g.appendChild(svgEl('line', { x1: 0, y1: y, x2: W, y2: y, stroke: 'var(--text-secondary, #555)', 'stroke-opacity': '0.2', 'stroke-width': '1', 'stroke-dasharray': tick === 0 ? 'none' : '4 4' }));
      const label = svgEl('text', { x: -8, y: y + 4, 'text-anchor': 'end', class: 'sc-label', fill: 'var(--text-secondary, #888)', 'font-size': '11' });
      label.textContent = fmt(tick); g.appendChild(label);
    });

    data.labels.forEach((label, i) => {
      const x = nPoints > 1 ? (i / (nPoints - 1)) * W : W / 2;
      const t = svgEl('text', { x, y: H + 20, 'text-anchor': 'middle', class: 'sc-label', fill: 'var(--text-secondary, #888)', 'font-size': '11' });
      t.textContent = label; g.appendChild(t);
    });

    data.datasets.forEach((ds, di) => {
      const color = getColor(di, ds.color);
      const points = ds.values.map((v, i) => ({ x: nPoints > 1 ? (i / (nPoints - 1)) * W : W / 2, y: H - ((v - scale.min) / yRange) * H }));

      function buildPath(pts, close = false) {
        if (pts.length === 0) return '';
        let d = `M ${pts[0].x} ${pts[0].y}`;
        if (smooth && pts.length > 2) {
          for (let i = 1; i < pts.length; i++) {
            const prev = pts[i - 1], curr = pts[i], cpX = (prev.x + curr.x) / 2;
            d += ` C ${cpX} ${prev.y} ${cpX} ${curr.y} ${curr.x} ${curr.y}`;
          }
        } else pts.slice(1).forEach(p => { d += ` L ${p.x} ${p.y}`; });
        if (close) d += ` L ${pts[pts.length - 1].x} ${H} L ${pts[0].x} ${H} Z`;
        return d;
      }

      if (filled) {
        const areaId = uid('areag');
        const aGrad = svgEl('linearGradient', { id: areaId, x1: '0', y1: '0', x2: '0', y2: '1' });
        aGrad.appendChild(svgEl('stop', { offset: '0%', 'stop-color': color, 'stop-opacity': '0.35' }));
        aGrad.appendChild(svgEl('stop', { offset: '100%', 'stop-color': color, 'stop-opacity': '0.02' }));
        defs.appendChild(aGrad);
        const areaPath = svgEl('path', { d: buildPath(points, true), fill: `url(#${areaId})`, class: 'sc-area-fill' });
        if (!prefersReducedMotion()) areaPath.style.animation = `sc-fadeIn ${animDuration}ms ease ${di * 120}ms both`;
        g.appendChild(areaPath);
      }

      const pathEl = svgEl('path', { d: buildPath(points), fill: 'none', stroke: color, 'stroke-width': strokeWidth, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', class: 'sc-line-path' });
      if (!prefersReducedMotion()) {
        const pathLen = W * 1.5;
        pathEl.style.setProperty('--sc-len', pathLen);
        pathEl.style.strokeDasharray = pathLen;
        pathEl.style.strokeDashoffset = pathLen;
        pathEl.style.animation = `sc-drawLine ${animDuration}ms cubic-bezier(0.4,0,0.2,1) ${di * 150}ms forwards`;
      }
      g.appendChild(pathEl);

      requestAnimationFrame(() => {
        const len = pathEl.getTotalLength?.() || W * 1.5;
        pathEl.style.setProperty('--sc-len', len);
        pathEl.style.strokeDasharray = len;
        if (prefersReducedMotion()) pathEl.style.strokeDashoffset = 0;
        else pathEl.style.strokeDashoffset = len;
      });

      if (dots) {
        points.forEach((p, i) => {
          const circle = svgEl('circle', { cx: p.x, cy: p.y, r: 4, fill: 'var(--bg, #0d0d1a)', stroke: color, 'stroke-width': '2', class: `sc-dot sc-series-${di}` });
          if (!prefersReducedMotion()) circle.style.animation = `sc-fadeIn 0.3s ease ${di * 150 + animDuration * 0.6 + i * 40}ms both`;
          attachTooltip(circle, `${data.labels[i]} — ${ds.label || ''}`, fmt(ds.values[i]), color);
          g.appendChild(circle);
          if (showValues) {
            const vt = svgEl('text', { x: p.x, y: p.y - 10, 'text-anchor': 'middle', class: 'sc-label', fill: 'var(--text-secondary, #aaa)', 'font-size': '10' });
            vt.textContent = fmt(ds.values[i]);
            if (!prefersReducedMotion()) vt.style.animation = `sc-fadeIn 0.3s ease ${di * 150 + animDuration * 0.8 + i * 40}ms both`;
            g.appendChild(vt);
          }
        });
      }

      // Also make the line path itself hoverable for the series
      pathEl.classList.add(`sc-series-${di}`);
    });

    const wrap = document.createElement('div');
    wrap.className = 'sc-wrap';
    wrap.appendChild(svg);
    if (showLegend && data.datasets.length > 1) {
      const legend = document.createElement('div'); legend.className = 'sc-legend';
      data.datasets.forEach((ds, i) => {
        const item = document.createElement('div'); item.className = 'sc-legend-item';
        const dot = document.createElement('span'); dot.className = 'sc-legend-dot'; dot.style.background = getColor(i, ds.color);
        item.appendChild(dot); item.appendChild(document.createTextNode(ds.label)); legend.appendChild(item);
      });
      wrap.appendChild(legend);
      makeLegendFilterable(legend, svg);
    }
    el.innerHTML = '';
    el.appendChild(wrap);
    el.dispatchEvent(new CustomEvent('chart:ready', { bubbles: true }));
  }

  // ─────────────────────────────────────────────────────────────────────────
  // DONUT / PIE CHART
  // ─────────────────────────────────────────────────────────────────────────

  function donut(container, data, options = {}) {
    injectCSS();
    const el = resolve(container);
    if (!el) { console.warn(`[SlideCharts] donut: container not found — "${container}"`); return _noopInstance; }
    _renderDonut(el, data, options);
    return makeInstance(el, _renderDonut, data, options);
  }

  function _renderDonut(el, data, options = {}) {
    const {
      width = 360, height = 360, pie = false,
      innerRadius = pie ? 0 : 0.55,
      centerLabel, centerValue,
      showLegend = true, showPercentages = true,
      animDuration = 800, title,
    } = options;

    const cx = width / 2, cy = height / 2;
    const R = Math.min(width, height) / 2 - 16;
    const r = R * innerRadius;
    const total = data.segments.reduce((s, d) => s + d.value, 0);

    const svg = svgEl('svg', { viewBox: `0 0 ${width} ${height}`, class: 'sc-svg', role: 'img', 'aria-label': title || 'Donut chart' });
    const defs = svgEl('defs'); svg.appendChild(defs);
    const g = svgEl('g'); svg.appendChild(g);

    if (title) {
      const t = svgEl('text', { x: width / 2, y: 18, 'text-anchor': 'middle', class: 'sc-title', fill: 'var(--text-primary, #fff)', 'font-size': '14' });
      t.textContent = title; g.appendChild(t);
    }

    let cumulativeAngle = -90;
    data.segments.forEach((seg, i) => {
      const color = getColor(i, seg.color);
      const pct = seg.value / total, angle = pct * 360;
      const startRad = (cumulativeAngle * Math.PI) / 180;
      const endRad = ((cumulativeAngle + angle) * Math.PI) / 180;
      const x1 = cx + R * Math.cos(startRad), y1 = cy + R * Math.sin(startRad);
      const x2 = cx + R * Math.cos(endRad), y2 = cy + R * Math.sin(endRad);
      const xi1 = cx + r * Math.cos(endRad), yi1 = cy + r * Math.sin(endRad);
      const xi2 = cx + r * Math.cos(startRad), yi2 = cy + r * Math.sin(startRad);
      const largeArc = angle > 180 ? 1 : 0;
      let d;
      if (pie || innerRadius === 0) d = `M ${cx} ${cy} L ${x1} ${y1} A ${R} ${R} 0 ${largeArc} 1 ${x2} ${y2} Z`;
      else d = `M ${x1} ${y1} A ${R} ${R} 0 ${largeArc} 1 ${x2} ${y2} L ${xi1} ${yi1} A ${r} ${r} 0 ${largeArc} 0 ${xi2} ${yi2} Z`;
      const path = svgEl('path', { d, fill: color, class: `sc-donut-arc sc-series-${i}`, 'aria-label': `${seg.label}: ${fmt(seg.value)} (${(pct * 100).toFixed(1)}%)` });
      if (!prefersReducedMotion()) {
        path.style.opacity = '0'; path.style.transform = 'scale(0.8)'; path.style.transformOrigin = `${cx}px ${cy}px`;
        path.style.transition = `opacity 0.4s ease ${i * (animDuration / data.segments.length)}ms, transform 0.4s cubic-bezier(0.34,1.56,0.64,1) ${i * (animDuration / data.segments.length)}ms`;
        requestAnimationFrame(() => requestAnimationFrame(() => { path.style.opacity = '1'; path.style.transform = 'scale(1)'; }));
      }
      attachTooltip(path, seg.label, `${fmt(seg.value)} (${(pct * 100).toFixed(1)}%)`, color);
      g.appendChild(path);
      if (showPercentages && pct > 0.05) {
        const midAngle = cumulativeAngle + angle / 2, midRad = (midAngle * Math.PI) / 180;
        const labelR = pie ? R * 0.65 : (R + r) / 2;
        const lx = cx + labelR * Math.cos(midRad), ly = cy + labelR * Math.sin(midRad);
        const lt = svgEl('text', { x: lx, y: ly + 4, 'text-anchor': 'middle', class: 'sc-label', fill: '#fff', 'font-size': '11', 'font-weight': '600' });
        lt.textContent = `${Math.round(pct * 100)}%`;
        if (!prefersReducedMotion()) lt.style.animation = `sc-fadeIn 0.4s ease ${i * (animDuration / data.segments.length) + 300}ms both`;
        g.appendChild(lt);
      }
      cumulativeAngle += angle;
    });

    if (!pie && (centerValue || centerLabel)) {
      if (centerValue) { const cv = svgEl('text', { x: cx, y: cy + 6, 'text-anchor': 'middle', class: 'sc-title', fill: 'var(--text-primary, #fff)', 'font-size': '28' }); cv.textContent = centerValue; g.appendChild(cv); }
      if (centerLabel) { const cl = svgEl('text', { x: cx, y: cy + (centerValue ? 22 : 6), 'text-anchor': 'middle', class: 'sc-label', fill: 'var(--text-secondary, #aaa)', 'font-size': '12' }); cl.textContent = centerLabel; g.appendChild(cl); }
    }

    const wrap = document.createElement('div'); wrap.className = 'sc-wrap'; wrap.style.cssText = 'display:flex;flex-direction:column;align-items:center;'; wrap.appendChild(svg);
    if (showLegend) {
      const legend = document.createElement('div'); legend.className = 'sc-legend';
      data.segments.forEach((seg, i) => {
        const item = document.createElement('div'); item.className = 'sc-legend-item';
        const dot = document.createElement('span'); dot.className = 'sc-legend-dot'; dot.style.background = getColor(i, seg.color);
        item.appendChild(dot); item.appendChild(document.createTextNode(seg.label)); legend.appendChild(item);
      });
      wrap.appendChild(legend);
      makeLegendFilterable(legend, svg);
    }
    el.innerHTML = ''; el.appendChild(wrap);
    el.dispatchEvent(new CustomEvent('chart:ready', { bubbles: true }));
  }

  // ─────────────────────────────────────────────────────────────────────────
  // HORIZONTAL BAR CHART
  // ─────────────────────────────────────────────────────────────────────────

  function horizontalBar(container, data, options = {}) {
    injectCSS();
    const el = resolve(container);
    if (!el) { console.warn(`[SlideCharts] horizontalBar: container not found — "${container}"`); return _noopInstance; }
    _renderHBar(el, data, options);
    return makeInstance(el, _renderHBar, data, options);
  }

  function _renderHBar(el, data, options = {}) {
    const {
      width = 560, height,
      showValues = true, showRank = false,
      barHeight = 28, barRadius = 4,
      animDuration = 600, title,
    } = options;

    const items = data.items;
    const maxVal = data.max || Math.max(...items.map(d => d.value));
    const labelW = 100, valueW = showValues ? 48 : 0, rankW = showRank ? 28 : 0, gap = 10;
    const barW = width - labelW - valueW - rankW - gap * 3;
    const rowH = barHeight + 16, marginTop = title ? 44 : 16;
    const computedH = height || marginTop + items.length * rowH + 16;

    const svg = svgEl('svg', { viewBox: `0 0 ${width} ${computedH}`, class: 'sc-svg', role: 'img', 'aria-label': title || 'Horizontal bar chart' });
    const defs = svgEl('defs'); svg.appendChild(defs);

    if (title) {
      const t = svgEl('text', { x: width / 2, y: 22, 'text-anchor': 'middle', class: 'sc-title', fill: 'var(--text-primary, #fff)', 'font-size': '14' });
      t.textContent = title; svg.appendChild(t);
    }

    items.forEach((item, i) => {
      const y = marginTop + i * rowH, color = getColor(i, item.color);
      const pct = item.value / maxVal, fillW = pct * barW;
      if (showRank) {
        const rankT = svgEl('text', { x: rankW / 2, y: y + barHeight / 2 + 4, 'text-anchor': 'middle', class: 'sc-label', fill: 'var(--text-secondary, #888)', 'font-size': '11', 'font-weight': '600' });
        rankT.textContent = `#${i + 1}`; svg.appendChild(rankT);
      }
      const labelT = svgEl('text', { x: rankW + gap, y: y + barHeight / 2 + 4, 'text-anchor': 'start', class: 'sc-label', fill: 'var(--text-primary, #eee)', 'font-size': '12' });
      labelT.textContent = item.label.length > 14 ? item.label.slice(0, 13) + '…' : item.label; svg.appendChild(labelT);
      svg.appendChild(svgEl('rect', { x: rankW + labelW + gap, y, width: barW, height: barHeight, rx: barRadius, fill: 'var(--surface, #222)', opacity: '0.5' }));
      const gradId = uid('hbarg');
      const grad = svgEl('linearGradient', { id: gradId, x1: '0', y1: '0', x2: '1', y2: '0' });
      grad.appendChild(svgEl('stop', { offset: '0%', 'stop-color': color, 'stop-opacity': '0.8' }));
      grad.appendChild(svgEl('stop', { offset: '100%', 'stop-color': color, 'stop-opacity': '1' }));
      defs.appendChild(grad);
      const barX = rankW + labelW + gap;
      const fillRect = svgEl('rect', { x: barX, y, width: fillW, height: barHeight, rx: barRadius, fill: `url(#${gradId})`, class: `sc-hbar-rect sc-series-${i}`, 'transform-origin': `${barX}px ${y}px` });
      if (!prefersReducedMotion()) fillRect.style.animation = `sc-growX ${animDuration}ms cubic-bezier(0.4,0,0.2,1) ${i * 80}ms both`;
      attachTooltip(fillRect, item.label, fmt(item.value), color);
      svg.appendChild(fillRect);
      if (showValues) {
        const vt = svgEl('text', { x: rankW + labelW + gap + barW + gap, y: y + barHeight / 2 + 4, 'text-anchor': 'start', class: 'sc-label', fill: 'var(--text-secondary, #aaa)', 'font-size': '11' });
        vt.textContent = fmt(item.value);
        if (!prefersReducedMotion()) vt.style.animation = `sc-fadeIn 0.4s ease ${i * 80 + animDuration * 0.6}ms both`;
        svg.appendChild(vt);
      }
    });

    el.innerHTML = ''; el.appendChild(svg);
    el.dispatchEvent(new CustomEvent('chart:ready', { bubbles: true }));
  }

  // ─────────────────────────────────────────────────────────────────────────
  // PROGRESS BARS
  // ─────────────────────────────────────────────────────────────────────────

  function progress(container, data, options = {}) {
    injectCSS();
    const el = resolve(container);
    if (!el) { console.warn(`[SlideCharts] progress: container not found — "${container}"`); return _noopInstance; }
    _renderProgress(el, data, options);
    return makeInstance(el, _renderProgress, data, options);
  }

  function _renderProgress(el, data, options = {}) {
    const { barHeight = 12, barRadius = 6, showPercentage = true, animDuration = 700, title, gap = 20 } = options;
    const wrap = document.createElement('div');
    wrap.className = 'sc-wrap';
    wrap.style.cssText = 'display:flex;flex-direction:column;justify-content:center;gap:' + gap + 'px;width:100%;padding:8px 0;';

    if (title) {
      const h = document.createElement('p'); h.className = 'sc-title';
      h.style.cssText = 'color:var(--text-primary,#fff);font-size:14px;margin-bottom:4px;';
      h.textContent = title; wrap.appendChild(h);
    }

    data.items.forEach((item, i) => {
      const max = item.max || 100, pct = Math.min(100, Math.max(0, (item.value / max) * 100));
      const color = getColor(i, item.color);
      const row = document.createElement('div'); row.style.cssText = 'display:flex;flex-direction:column;gap:5px;width:100%;';
      const header = document.createElement('div'); header.style.cssText = 'display:flex;justify-content:space-between;align-items:baseline;';
      const lbl = document.createElement('span'); lbl.style.cssText = 'color:var(--text-primary,#eee);font-size:13px;font-family:var(--font-body,sans-serif);'; lbl.textContent = item.label;
      const pctEl = document.createElement('span'); pctEl.style.cssText = 'color:var(--text-secondary,#aaa);font-size:11px;font-family:var(--font-body,sans-serif);'; pctEl.textContent = showPercentage ? `${Math.round(pct)}%` : fmt(item.value);
      header.appendChild(lbl); if (showPercentage || item.sublabel) header.appendChild(pctEl); row.appendChild(header);
      const track = document.createElement('div'); track.style.cssText = `width:100%;height:${barHeight}px;border-radius:${barRadius}px;background:var(--surface,#1a1a2e);overflow:hidden;`;
      const fill = document.createElement('div'); fill.className = 'sc-progress-fill';
      fill.style.cssText = `height:100%;border-radius:${barRadius}px;background:linear-gradient(90deg,${color}99,${color});--sc-pct:${pct}%;width:0%;`;
      if (!prefersReducedMotion()) fill.style.animation = `sc-progressFill ${animDuration}ms cubic-bezier(0.4,0,0.2,1) ${i * 100}ms forwards`;
      else fill.style.width = `${pct}%`;
      track.appendChild(fill); row.appendChild(track);
      if (item.sublabel) { const sub = document.createElement('span'); sub.style.cssText = 'color:var(--text-secondary,#888);font-size:11px;font-family:var(--font-body,sans-serif);'; sub.textContent = item.sublabel; row.appendChild(sub); }
      wrap.appendChild(row);
    });

    el.innerHTML = ''; el.appendChild(wrap);
    el.dispatchEvent(new CustomEvent('chart:ready', { bubbles: true }));
  }

  // ─────────────────────────────────────────────────────────────────────────
  // RADAR / SPIDER CHART
  // ─────────────────────────────────────────────────────────────────────────

  function radar(container, data, options = {}) {
    injectCSS();
    const el = resolve(container);
    if (!el) { console.warn(`[SlideCharts] radar: container not found — "${container}"`); return _noopInstance; }
    _renderRadar(el, data, options);
    return makeInstance(el, _renderRadar, data, options);
  }

  function _renderRadar(el, data, options = {}) {
    const { width = 380, height = 380, levels = 5, showDots = true, filled = true, showLegend = true, animDuration = 700, title } = options;
    const axes = data.axes, N = axes.length;
    if (N < 3) { console.warn('SlideCharts.radar: need at least 3 axes'); return; }
    const allVals = data.datasets.flatMap(d => d.values);
    const dataMax = data.max || Math.max(...allVals) || 100;
    const cx = width / 2, cy = height / 2 + (title ? 12 : 0);
    const titleH = title ? 28 : 0, R = Math.min(width, height - titleH) / 2 - 40;

    function angleOf(i) { return (2 * Math.PI * i / N) - Math.PI / 2; }
    function polarToXY(angle, r) { return { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) }; }
    function valToR(v) { return (Math.max(0, Math.min(v, dataMax)) / dataMax) * R; }

    const svg = svgEl('svg', { viewBox: `0 0 ${width} ${height + titleH}`, class: 'sc-svg', role: 'img', 'aria-label': title || 'Radar chart' });
    const defs = svgEl('defs'); svg.appendChild(defs);
    const g = svgEl('g'); svg.appendChild(g);

    if (title) {
      const t = svgEl('text', { x: cx, y: 18, 'text-anchor': 'middle', class: 'sc-title', fill: 'var(--text-primary, #fff)', 'font-size': '14' });
      t.textContent = title; g.appendChild(t);
    }

    for (let l = 1; l <= levels; l++) {
      const rr = (l / levels) * R, pts = axes.map((_, i) => polarToXY(angleOf(i), rr));
      const d = pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ') + ' Z';
      g.appendChild(svgEl('path', { d, fill: 'none', stroke: 'var(--text-secondary, #555)', 'stroke-opacity': '0.2', 'stroke-width': '1', 'stroke-dasharray': l < levels ? '4 4' : 'none' }));
      const labelPt = polarToXY(angleOf(0), rr);
      const lbl = svgEl('text', { x: labelPt.x + 4, y: labelPt.y - 3, class: 'sc-label', fill: 'var(--text-secondary, #888)', 'font-size': '9' });
      lbl.textContent = fmt((l / levels) * dataMax); g.appendChild(lbl);
    }

    axes.forEach((axis, i) => {
      const angle = angleOf(i), tip = polarToXY(angle, R);
      g.appendChild(svgEl('line', { x1: cx, y1: cy, x2: tip.x, y2: tip.y, stroke: 'var(--text-secondary, #555)', 'stroke-opacity': '0.25', 'stroke-width': '1' }));
      const labelR = R + 22, lp = polarToXY(angle, labelR);
      const anchor = Math.abs(lp.x - cx) < 5 ? 'middle' : lp.x < cx ? 'end' : 'start';
      const axisLabel = svgEl('text', { x: lp.x, y: lp.y + 4, 'text-anchor': anchor, class: 'sc-label', fill: 'var(--text-primary, #ddd)', 'font-size': '11', 'font-weight': '500' });
      axisLabel.textContent = axis; g.appendChild(axisLabel);
    });

    data.datasets.forEach((ds, di) => {
      const color = getColor(di, ds.color);
      const points = ds.values.map((v, i) => polarToXY(angleOf(i), valToR(v)));
      const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ') + ' Z';
      if (filled) {
        const fillId = uid('radarf');
        const rGrad = svgEl('radialGradient', { id: fillId, cx: '50%', cy: '50%', r: '50%' });
        rGrad.appendChild(svgEl('stop', { offset: '0%', 'stop-color': color, 'stop-opacity': '0.35' }));
        rGrad.appendChild(svgEl('stop', { offset: '100%', 'stop-color': color, 'stop-opacity': '0.08' }));
        defs.appendChild(rGrad);
        const fillPath = svgEl('path', { d: pathD, fill: `url(#${fillId})`, class: 'sc-radar-fill' });
        if (!prefersReducedMotion()) fillPath.style.animation = `sc-fadeIn ${animDuration}ms ease ${di * 150}ms both`;
        g.appendChild(fillPath);
      }
      const strokePath = svgEl('path', { d: pathD, fill: 'none', stroke: color, 'stroke-width': '2', 'stroke-linejoin': 'round', class: `sc-radar-stroke sc-series-${di}` });
      if (!prefersReducedMotion()) strokePath.style.animation = `sc-fadeIn ${animDuration * 0.8}ms ease ${di * 150}ms both`;
      g.appendChild(strokePath);
      if (showDots) {
        points.forEach((p, pi) => {
          const dot = svgEl('circle', { cx: p.x, cy: p.y, r: 4, fill: 'var(--bg, #0d0d1a)', stroke: color, 'stroke-width': '2', class: `sc-radar-dot sc-series-${di}` });
          if (!prefersReducedMotion()) dot.style.animation = `sc-fadeIn 0.3s ease ${di * 150 + animDuration * 0.6 + pi * 40}ms both`;
          attachTooltip(dot, `${axes[pi]} — ${ds.label || ''}`, fmt(ds.values[pi]), color);
          g.appendChild(dot);
        });
      }
    });

    const wrap = document.createElement('div'); wrap.className = 'sc-wrap'; wrap.style.cssText = 'display:flex;flex-direction:column;align-items:center;'; wrap.appendChild(svg);
    if (showLegend && data.datasets.length > 1) {
      const legend = document.createElement('div'); legend.className = 'sc-legend';
      data.datasets.forEach((ds, i) => {
        const item = document.createElement('div'); item.className = 'sc-legend-item';
        const dot = document.createElement('span'); dot.className = 'sc-legend-dot'; dot.style.background = getColor(i, ds.color);
        item.appendChild(dot); item.appendChild(document.createTextNode(ds.label)); legend.appendChild(item);
      });
      wrap.appendChild(legend);
      makeLegendFilterable(legend, svg);
    }
    el.innerHTML = ''; el.appendChild(wrap);
    el.dispatchEvent(new CustomEvent('chart:ready', { bubbles: true }));
  }

  // ─────────────────────────────────────────────────────────────────────────
  // SANKEY / FLOW CHART
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Renders a Sankey (flow/alluvial) diagram.
   *
   * @param {string|Element} container
   * @param {Object} data
   *   @param {Array<string>}                    data.nodes   — node labels (order matters: left → right)
   *   @param {Array<{source:string, target:string, value:number, color?:string}>} data.links
   * @param {Object} [options]
   *   @param {number}  [options.width=640]
   *   @param {number}  [options.height=340]
   *   @param {number}  [options.nodeWidth=18]
   *   @param {number}  [options.nodePadding=14]  gap between nodes in the same column
   *   @param {boolean} [options.showValues=true]
   *   @param {boolean} [options.showLegend=false]
   *   @param {number}  [options.animDuration=900] ms
   *   @param {string}  [options.title]
   * @returns {ChartInstance}
   *
   * Data format example:
   *   {
   *     nodes: ['访问', '注册', '激活', '付费', '续费'],
   *     links: [
   *       { source: '访问',   target: '注册', value: 8500 },
   *       { source: '注册',   target: '激活', value: 4200 },
   *       { source: '激活',   target: '付费', value: 1800 },
   *       { source: '付费',   target: '续费', value:  950 },
   *     ]
   *   }
   */
  function sankey(container, data, options = {}) {
    injectCSS();
    const el = resolve(container);
    if (!el) { console.warn(`[SlideCharts] sankey: container not found — "${container}"`); return _noopInstance; }
    _renderSankey(el, data, options);
    return makeInstance(el, _renderSankey, data, options);
  }

  function _renderSankey(el, data, options = {}) {
    const {
      width = 640, height = 340,
      nodeWidth = 18, nodePadding = 14,
      showValues = true, showLegend = false,
      animDuration = 900, title,
    } = options;

    const titleH = title ? 36 : 0;
    const margin = { top: titleH + 12, right: 80, bottom: 20, left: 80 };
    const W = width  - margin.left - margin.right;
    const H = height - margin.top  - margin.bottom;

    // ── Build node / link index ──────────────────────────────────────────────
    const nodeIndex = {};
    data.nodes.forEach((n, i) => { nodeIndex[n] = i; });
    const N = data.nodes.length;

    // ── Compute columns (depth via longest-path BFS) ─────────────────────────
    const inLinks  = Array.from({ length: N }, () => []);
    const outLinks = Array.from({ length: N }, () => []);
    data.links.forEach((lk, li) => {
      const s = nodeIndex[lk.source], t = nodeIndex[lk.target];
      if (s == null || t == null) return;
      outLinks[s].push(li); inLinks[t].push(li);
    });

    const depth = new Array(N).fill(-1);
    // Seed: source nodes (no incoming links)
    data.nodes.forEach((_, i) => { if (inLinks[i].length === 0) depth[i] = 0; });
    // BFS to assign depths
    let changed = true;
    while (changed) {
      changed = false;
      data.links.forEach(lk => {
        const s = nodeIndex[lk.source], t = nodeIndex[lk.target];
        if (s == null || t == null) return;
        if (depth[s] >= 0 && depth[t] <= depth[s]) {
          depth[t] = depth[s] + 1; changed = true;
        }
      });
    }
    // Any still unassigned node → put at col 0
    depth.forEach((d, i) => { if (d < 0) depth[i] = 0; });

    const maxDepth = Math.max(...depth);
    const nCols = maxDepth + 1;
    const colX = (d) => (d / Math.max(nCols - 1, 1)) * (W - nodeWidth);

    // ── Compute node sizes (sum of max(in, out) flow) ────────────────────────
    const nodeValue = new Array(N).fill(0);
    data.links.forEach(lk => {
      const s = nodeIndex[lk.source], t = nodeIndex[lk.target];
      if (s == null || t == null) return;
      nodeValue[s] += lk.value;
      nodeValue[t] += lk.value;
    });
    // For nodes with both in and out, use max (avoid double-counting)
    data.nodes.forEach((_, i) => {
      const inVal  = inLinks[i].reduce((acc, li) => acc + data.links[li].value, 0);
      const outVal = outLinks[i].reduce((acc, li) => acc + data.links[li].value, 0);
      nodeValue[i] = Math.max(inVal, outVal) || nodeValue[i];
    });

    // ── Layout nodes within each column ─────────────────────────────────────
    const colNodes = Array.from({ length: nCols }, () => []);
    data.nodes.forEach((_, i) => colNodes[depth[i]].push(i));

    const nodeY = new Array(N).fill(0);
    const nodeH = new Array(N).fill(0);

    colNodes.forEach((col) => {
      const th = col.reduce((s, i) => s + nodeValue[i], 0) +
                 Math.max(0, col.length - 1) * nodePadding;
      const scale = Math.min(1, H / (th || 1));
      let y = (H - th * scale) / 2; // vertically center the column
      col.forEach(i => {
        const h = nodeValue[i] * scale;
        nodeY[i] = y;
        nodeH[i] = Math.max(h, 2);
        y += nodeH[i] + nodePadding * scale;
      });
    });

    // ── Flow offsets (to stagger multiple links at each node) ────────────────
    const srcOffset = new Array(N).fill(0);
    const tgtOffset = new Array(N).fill(0);

    // Sort links by target y for cleaner crossings
    const sortedLinks = [...data.links].sort((a, b) => {
      const tA = nodeIndex[a.target], tB = nodeIndex[b.target];
      return nodeY[tA] - nodeY[tB];
    });

    // ── SVG assembly ─────────────────────────────────────────────────────────
    const svg = svgEl('svg', {
      viewBox: `0 0 ${width} ${height}`,
      class: 'sc-svg',
      role: 'img',
      'aria-label': title || 'Sankey diagram',
    });
    const defs = svgEl('defs'); svg.appendChild(defs);
    const g = svgEl('g', { transform: `translate(${margin.left},${margin.top})` });
    svg.appendChild(g);

    if (title) {
      const t = svgEl('text', {
        x: width / 2, y: titleH / 2 + 4,
        'text-anchor': 'middle', class: 'sc-title',
        fill: 'var(--text-primary, #fff)', 'font-size': '14',
      });
      t.textContent = title; svg.appendChild(t);
    }

    // Draw links first (behind nodes)
    sortedLinks.forEach((lk, li) => {
      const s = nodeIndex[lk.source], t = nodeIndex[lk.target];
      if (s == null || t == null) return;

      const color = getColor(s, lk.color);
      const maxFlow = Math.max(...data.links.map(l => l.value)) || 1;
      const scale   = (nodeH[s] / (nodeValue[s] || 1));
      const lh      = Math.max(lk.value * scale, 1.5);

      const x0 = colX(depth[s]) + nodeWidth;
      const x1 = colX(depth[t]);
      const y0 = nodeY[s] + srcOffset[s];
      const y1 = nodeY[t] + tgtOffset[t];

      srcOffset[s] += lh;
      tgtOffset[t] += lh;

      const cpX = (x0 + x1) / 2;
      const pathD = `M ${x0} ${y0 + lh / 2} C ${cpX} ${y0 + lh / 2} ${cpX} ${y1 + lh / 2} ${x1} ${y1 + lh / 2}`;

      // Gradient for the link
      const gradId = uid('skg');
      const grad = svgEl('linearGradient', { id: gradId, x1: '0%', y1: '0%', x2: '100%', y2: '0%' });
      grad.appendChild(svgEl('stop', { offset: '0%',   'stop-color': color, 'stop-opacity': '0.5' }));
      grad.appendChild(svgEl('stop', { offset: '100%', 'stop-color': getColor(t, null), 'stop-opacity': '0.35' }));
      defs.appendChild(grad);

      const path = svgEl('path', {
        d: pathD,
        fill: 'none',
        stroke: `url(#${gradId})`,
        'stroke-width': lh,
        'stroke-linecap': 'butt',
        class: 'sc-sankey-link',
        'aria-label': `${lk.source} → ${lk.target}: ${fmt(lk.value)}`,
      });
      if (!prefersReducedMotion()) {
        path.style.opacity = '0';
        path.style.transition = `opacity ${animDuration * 0.6}ms ease ${li * 50}ms`;
        requestAnimationFrame(() => requestAnimationFrame(() => { path.style.opacity = '1'; }));
      }
      attachTooltip(path, `${lk.source} → ${lk.target}`, fmt(lk.value), color);
      g.appendChild(path);
    });

    // Draw nodes
    data.nodes.forEach((name, i) => {
      const x = colX(depth[i]);
      const y = nodeY[i];
      const h = nodeH[i];
      const color = getColor(i, null);

      const rect = svgEl('rect', {
        x, y, width: nodeWidth, height: Math.max(h, 2),
        rx: 3, ry: 3,
        fill: color,
        class: 'sc-sankey-node',
        'aria-label': `${name}: ${fmt(nodeValue[i])}`,
      });
      if (!prefersReducedMotion()) {
        rect.style.opacity = '0';
        rect.style.transform = `scaleY(0)`;
        rect.style.transformOrigin = `${x + nodeWidth / 2}px ${y}px`;
        rect.style.transition = `opacity 0.4s ease ${i * 60}ms, transform 0.4s cubic-bezier(0.34,1.56,0.64,1) ${i * 60}ms`;
        requestAnimationFrame(() => requestAnimationFrame(() => {
          rect.style.opacity = '1';
          rect.style.transform = 'scaleY(1)';
        }));
      }
      attachTooltip(rect, name, fmt(nodeValue[i]), color);
      g.appendChild(rect);

      // Node label — left of leftmost column, right of rightmost, else inline
      const isLeft  = depth[i] === 0;
      const isRight = depth[i] === maxDepth;
      const labelX  = isLeft ? x - 6 : isRight ? x + nodeWidth + 6 : x + nodeWidth / 2;
      const anchor  = isLeft ? 'end' : isRight ? 'start' : 'middle';
      const labelY  = y + h / 2 + 4;

      const label = svgEl('text', {
        x: labelX, y: labelY,
        'text-anchor': anchor,
        class: 'sc-label',
        fill: 'var(--text-primary, #eee)',
        'font-size': '11',
        'font-weight': '500',
      });
      label.textContent = name;
      if (!prefersReducedMotion()) label.style.animation = `sc-fadeIn 0.4s ease ${i * 60 + 300}ms both`;
      g.appendChild(label);

      // Value label
      if (showValues && nodeValue[i] > 0) {
        const vLabel = svgEl('text', {
          x: labelX,
          y: labelY + 13,
          'text-anchor': anchor,
          class: 'sc-label',
          fill: 'var(--text-secondary, #888)',
          'font-size': '9',
        });
        vLabel.textContent = fmt(nodeValue[i]);
        if (!prefersReducedMotion()) vLabel.style.animation = `sc-fadeIn 0.4s ease ${i * 60 + 400}ms both`;
        g.appendChild(vLabel);
      }
    });

    const wrap = document.createElement('div');
    wrap.className = 'sc-wrap';
    wrap.appendChild(svg);

    if (showLegend) {
      const legend = document.createElement('div'); legend.className = 'sc-legend';
      data.nodes.forEach((name, i) => {
        const item = document.createElement('div'); item.className = 'sc-legend-item';
        const dot  = document.createElement('span'); dot.className = 'sc-legend-dot';
        dot.style.background = getColor(i, null);
        item.appendChild(dot); item.appendChild(document.createTextNode(name));
        legend.appendChild(item);
      });
      wrap.appendChild(legend);
    }

    el.innerHTML = '';
    el.appendChild(wrap);
    el.dispatchEvent(new CustomEvent('chart:ready', { bubbles: true }));
  }

  // ─────────────────────────────────────────────────────────────────────────
  // TREEMAP
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Renders a squarified treemap.
   *
   * @param {string|Element} container
   * @param {Object} data
   *   @param {Array<{label:string, value:number, color?:string, children?:Array}>} data.items
   *     Each item may have nested `children` for a 2-level treemap.
   * @param {Object} [options]
   *   @param {number}  [options.width=600]
   *   @param {number}  [options.height=360]
   *   @param {number}  [options.padding=3]       gap between sibling tiles
   *   @param {number}  [options.outerPadding=0]  gap from outer bounds
   *   @param {boolean} [options.showValues=true]  show value labels
   *   @param {boolean} [options.showLegend=false]
   *   @param {number}  [options.animDuration=700] ms
   *   @param {number}  [options.minFontSize=9]
   *   @param {number}  [options.maxFontSize=18]
   *   @param {string}  [options.title]
   * @returns {ChartInstance}
   *
   * Data format example:
   *   {
   *     items: [
   *       { label: 'Product A', value: 420, color: 'var(--accent)' },
   *       { label: 'Product B', value: 300 },
   *       { label: 'Product C', value: 180,
   *         children: [
   *           { label: 'C1', value: 100 },
   *           { label: 'C2', value: 80  },
   *         ]
   *       },
   *     ]
   *   }
   */
  function treemap(container, data, options = {}) {
    injectCSS();
    const el = resolve(container);
    if (!el) { console.warn(`[SlideCharts] treemap: container not found — "${container}"`); return _noopInstance; }
    _renderTreemap(el, data, options);
    return makeInstance(el, _renderTreemap, data, options);
  }

  /**
   * Squarified treemap layout algorithm.
   * Distributes `nodes` (each with a `value`) into the rect [x, y, w, h].
   * Returns array of { node, x, y, w, h }.
   */
  function _squarify(nodes, x, y, w, h) {
    if (nodes.length === 0) return [];

    const total = nodes.reduce((s, n) => s + n.value, 0);
    if (total === 0) return [];

    const area = w * h;
    const result = [];

    let remaining = nodes.slice().sort((a, b) => b.value - a.value);

    function worstRatio(row, side) {
      const rowSum = row.reduce((s, n) => s + n.value, 0);
      const rowArea = (rowSum / total) * area;
      if (side === 0 || rowArea === 0) return Infinity;
      const rowSide = rowArea / side;
      return Math.max(
        ...row.map(n => {
          const tileArea = (n.value / total) * area;
          const tileSide = tileArea / rowSide;
          return Math.max(rowSide / tileSide, tileSide / rowSide);
        })
      );
    }

    function layout(row, side, rx, ry, rw, rh) {
      const rowSum = row.reduce((s, n) => s + n.value, 0);
      const rowArea = (rowSum / total) * area;
      const rowSide = rowArea / side;
      let offset = 0;
      row.forEach(n => {
        const tileArea = (n.value / total) * area;
        const tileSide = tileArea / rowSide;
        if (side === rw) {
          result.push({ node: n, x: rx + offset, y: ry, w: tileSide, h: rowSide });
        } else {
          result.push({ node: n, x: rx, y: ry + offset, w: rowSide, h: tileSide });
        }
        offset += tileSide;
      });
    }

    let rx = x, ry = y, rw = w, rh = h;

    while (remaining.length > 0) {
      const side = Math.min(rw, rh);
      let row = [remaining[0]];
      let i = 1;
      while (i < remaining.length) {
        const candidate = [...row, remaining[i]];
        if (worstRatio(candidate, side) <= worstRatio(row, side)) {
          row = candidate;
          i++;
        } else {
          break;
        }
      }
      layout(row, side, rx, ry, rw, rh);
      remaining = remaining.slice(row.length);
      const rowSum = row.reduce((s, n) => s + n.value, 0);
      const rowArea = (rowSum / total) * area;
      const rowSide = rowArea / side;
      if (side === rw) { ry += rowSide; rh -= rowSide; }
      else             { rx += rowSide; rw -= rowSide; }
    }

    return result;
  }

  function _renderTreemap(el, data, options = {}) {
    const {
      width = 600, height = 360,
      padding = 3, outerPadding = 0,
      showValues = true, showLegend = false,
      animDuration = 700,
      minFontSize = 9, maxFontSize = 18,
      title,
    } = options;

    const titleH = title ? 32 : 0;
    const chartY = titleH + outerPadding;
    const chartW = width  - outerPadding * 2;
    const chartH = height - chartY - outerPadding;

    const items = (data.items || []).filter(n => n.value > 0);
    if (items.length === 0) return;

    const svg = svgEl('svg', {
      viewBox: `0 0 ${width} ${height}`,
      class: 'sc-svg',
      role: 'img',
      'aria-label': title || 'Treemap',
    });

    if (title) {
      const t = svgEl('text', {
        x: width / 2, y: titleH / 2 + 6,
        'text-anchor': 'middle', class: 'sc-title',
        fill: 'var(--text-primary, #fff)', 'font-size': '14',
      });
      t.textContent = title;
      svg.appendChild(t);
    }

    const tiles = _squarify(items, outerPadding, chartY, chartW, chartH);
    const maxVal = Math.max(...items.map(n => n.value));

    tiles.forEach((tile, i) => {
      const { node, x, y, w, h } = tile;
      const color = getColor(i, node.color);
      const inner = { x: x + padding, y: y + padding, w: w - padding * 2, h: h - padding * 2 };
      if (inner.w <= 0 || inner.h <= 0) return;

      // Gradient fill
      const gradId = uid('tmg');
      const defs = svg.querySelector('defs') || (() => { const d = svgEl('defs'); svg.insertBefore(d, svg.firstChild); return d; })();
      const grad = svgEl('linearGradient', { id: gradId, x1: '0', y1: '0', x2: '0', y2: '1' });
      grad.appendChild(svgEl('stop', { offset: '0%',   'stop-color': color, 'stop-opacity': '1'   }));
      grad.appendChild(svgEl('stop', { offset: '100%', 'stop-color': color, 'stop-opacity': '0.65' }));
      defs.appendChild(grad);

      const rect = svgEl('rect', {
        x: inner.x, y: inner.y, width: inner.w, height: inner.h,
        rx: 4, ry: 4,
        fill: `url(#${gradId})`,
        class: 'sc-treemap-tile',
        'aria-label': `${node.label}: ${fmt(node.value)}`,
      });
      if (!prefersReducedMotion()) {
        rect.style.opacity = '0';
        rect.style.transform = 'scale(0.92)';
        rect.style.transformOrigin = `${inner.x + inner.w / 2}px ${inner.y + inner.h / 2}px`;
        rect.style.transition = [
          `opacity 0.4s ease ${i * (animDuration / tiles.length * 0.6)}ms`,
          `transform 0.4s cubic-bezier(0.34,1.56,0.64,1) ${i * (animDuration / tiles.length * 0.6)}ms`,
        ].join(', ');
        requestAnimationFrame(() => requestAnimationFrame(() => {
          rect.style.opacity = '1';
          rect.style.transform = 'scale(1)';
        }));
      }
      attachTooltip(rect, node.label, fmt(node.value), color);
      svg.appendChild(rect);

      // Children (level-2 tiles)
      if (node.children && node.children.length > 0) {
        const childPad = padding + 1;
        const childTiles = _squarify(
          node.children.filter(c => c.value > 0),
          inner.x + childPad, inner.y + childPad + 18,
          inner.w - childPad * 2, inner.h - childPad * 2 - 18,
        );
        childTiles.forEach((ct, ci) => {
          const cinner = { x: ct.x + 1, y: ct.y + 1, w: ct.w - 2, h: ct.h - 2 };
          if (cinner.w <= 0 || cinner.h <= 0) return;
          const childColor = getColor(i * 6 + ci + 1, ct.node.color);
          const cGradId = uid('tmcg');
          const cGrad = svgEl('linearGradient', { id: cGradId, x1: '0', y1: '0', x2: '0', y2: '1' });
          cGrad.appendChild(svgEl('stop', { offset: '0%',   'stop-color': childColor, 'stop-opacity': '0.9' }));
          cGrad.appendChild(svgEl('stop', { offset: '100%', 'stop-color': childColor, 'stop-opacity': '0.5' }));
          defs.appendChild(cGrad);
          const cRect = svgEl('rect', {
            x: cinner.x, y: cinner.y, width: cinner.w, height: cinner.h,
            rx: 3, ry: 3,
            fill: `url(#${cGradId})`,
            class: 'sc-treemap-child',
            'aria-label': `${ct.node.label}: ${fmt(ct.node.value)}`,
          });
          if (!prefersReducedMotion()) {
            cRect.style.opacity = '0';
            cRect.style.transition = `opacity 0.35s ease ${(i + ci + 2) * 50}ms`;
            requestAnimationFrame(() => requestAnimationFrame(() => { cRect.style.opacity = '1'; }));
          }
          svg.appendChild(cRect);
          // Child label
          if (cinner.w > 30 && cinner.h > 16) {
            const cfs = Math.min(maxFontSize, Math.max(minFontSize, Math.sqrt(cinner.w * cinner.h) * 0.12));
            const cLabel = svgEl('text', {
              x: cinner.x + cinner.w / 2,
              y: cinner.y + cinner.h / 2 + cfs * 0.35,
              'text-anchor': 'middle',
              class: 'sc-label',
              fill: '#fff',
              'font-size': cfs.toFixed(1),
              'font-weight': '600',
            });
            cLabel.textContent = ct.node.label;
            if (!prefersReducedMotion()) {
              cLabel.style.opacity = '0';
              cLabel.style.transition = `opacity 0.3s ease ${(i + ci + 3) * 50 + 200}ms`;
              requestAnimationFrame(() => requestAnimationFrame(() => { cLabel.style.opacity = '1'; }));
            }
            svg.appendChild(cLabel);
          }
        });
      }

      // Tile label + value
      if (inner.w > 40 && inner.h > 22) {
        const fs = Math.min(maxFontSize, Math.max(minFontSize, Math.sqrt(inner.w * inner.h) * 0.13));
        const labelY = inner.h > 48 ? inner.y + fs + 8 : inner.y + inner.h / 2 + (showValues ? -4 : fs * 0.35);

        const labelEl = svgEl('text', {
          x: inner.x + inner.w / 2,
          y: labelY,
          'text-anchor': 'middle',
          class: 'sc-label',
          fill: '#fff',
          'font-size': fs.toFixed(1),
          'font-weight': '700',
        });
        // Truncate label to fit tile width
        const maxChars = Math.max(3, Math.floor(inner.w / (fs * 0.62)));
        labelEl.textContent = node.label.length > maxChars
          ? node.label.slice(0, maxChars - 1) + '…'
          : node.label;
        if (!prefersReducedMotion()) {
          labelEl.style.opacity = '0';
          labelEl.style.transition = `opacity 0.3s ease ${i * (animDuration / tiles.length * 0.6) + 300}ms`;
          requestAnimationFrame(() => requestAnimationFrame(() => { labelEl.style.opacity = '1'; }));
        }
        svg.appendChild(labelEl);

        if (showValues && inner.h > 40) {
          const vfs = Math.max(minFontSize, fs * 0.78);
          const valEl = svgEl('text', {
            x: inner.x + inner.w / 2,
            y: labelY + fs * 1.2,
            'text-anchor': 'middle',
            class: 'sc-label',
            fill: 'rgba(255,255,255,0.75)',
            'font-size': vfs.toFixed(1),
          });
          valEl.textContent = fmt(node.value);
          if (!prefersReducedMotion()) {
            valEl.style.opacity = '0';
            valEl.style.transition = `opacity 0.3s ease ${i * (animDuration / tiles.length * 0.6) + 380}ms`;
            requestAnimationFrame(() => requestAnimationFrame(() => { valEl.style.opacity = '1'; }));
          }
          svg.appendChild(valEl);
        }
      }
    });

    const wrap = document.createElement('div');
    wrap.className = 'sc-wrap';
    wrap.appendChild(svg);

    if (showLegend) {
      const legend = document.createElement('div'); legend.className = 'sc-legend';
      items.forEach((item, i) => {
        const li = document.createElement('div'); li.className = 'sc-legend-item';
        const dot = document.createElement('span'); dot.className = 'sc-legend-dot';
        dot.style.background = getColor(i, item.color);
        li.appendChild(dot); li.appendChild(document.createTextNode(item.label));
        legend.appendChild(li);
      });
      wrap.appendChild(legend);
    }

    el.innerHTML = '';
    el.appendChild(wrap);
    el.dispatchEvent(new CustomEvent('chart:ready', { bubbles: true }));
  }

  // ─────────────────────────────────────────────────────────────────────────
  // WATERFALL CHART
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Renders a waterfall (bridge) chart showing incremental value changes.
   *
   * @param {string|Element} container
   * @param {Object} data
   *   @param {Array<{label:string, value:number, type?:'start'|'end'|'delta', color?:string}>} data.items
   *     - type 'start'  → absolute opening bar (e.g. "开始"/"Start")
   *     - type 'end'    → absolute closing bar  (e.g. "合计"/"Total")
   *     - type 'delta'  → incremental change (default, positive=up, negative=down)
   * @param {Object} [options]
   *   @param {number}  [options.width=640]
   *   @param {number}  [options.height=360]
   *   @param {boolean} [options.showValues=true]
   *   @param {boolean} [options.showConnectors=true]  draw floating dotted connector lines
   *   @param {string}  [options.colorPositive]  default var(--chart3, #10b981)
   *   @param {string}  [options.colorNegative]  default var(--chart6, #ef4444)
   *   @param {string}  [options.colorTotal]     default var(--accent, #6366f1)
   *   @param {number}  [options.animDuration=700]
   *   @param {string}  [options.title]
   * @returns {ChartInstance}
   *
   * Data format example:
   *   {
   *     items: [
   *       { label: '期初余额',  value: 5000, type: 'start' },
   *       { label: '销售收入',  value: 3200 },
   *       { label: '退款',      value: -480 },
   *       { label: '运营成本',  value: -1200 },
   *       { label: '净利润',    value: 820, type: 'end' },
   *     ]
   *   }
   */
  function waterfall(container, data, options = {}) {
    injectCSS();
    const el = resolve(container);
    if (!el) { console.warn(`[SlideCharts] waterfall: container not found — "${container}"`); return _noopInstance; }
    _renderWaterfall(el, data, options);
    return makeInstance(el, _renderWaterfall, data, options);
  }

  function _renderWaterfall(el, data, options = {}) {
    const {
      width = 640, height = 360,
      showValues = true, showConnectors = true,
      colorPositive = 'var(--chart3, #10b981)',
      colorNegative = 'var(--chart6, #ef4444)',
      colorTotal    = 'var(--accent, #6366f1)',
      animDuration = 700, title,
    } = options;

    const margin = { top: title ? 52 : 24, right: 24, bottom: 56, left: 56 };
    const W = width  - margin.left - margin.right;
    const H = height - margin.top  - margin.bottom;

    // ── Compute running totals ────────────────────────────────────────────────
    const items = data.items || [];
    const computed = []; // { label, value, base, type, color }
    let running = 0;

    items.forEach((item, i) => {
      const type = item.type || 'delta';
      let base, barValue;

      if (type === 'start') {
        base = 0;
        barValue = item.value;
        running = item.value;
      } else if (type === 'end') {
        base = 0;
        barValue = running;
      } else {
        // delta
        base = item.value >= 0 ? running : running + item.value;
        barValue = Math.abs(item.value);
        running += item.value;
      }

      const color = item.color || (
        type === 'start' || type === 'end' ? colorTotal :
        item.value >= 0 ? colorPositive : colorNegative
      );
      computed.push({ label: item.label, value: item.value, base, barValue, type, color });
    });

    // ── Y scale ───────────────────────────────────────────────────────────────
    const allPoints = computed.flatMap(c => [c.base, c.base + c.barValue]);
    const scale = niceScale(Math.min(0, ...allPoints), Math.max(...allPoints));
    const yRange = scale.max - scale.min;

    // ── SVG ───────────────────────────────────────────────────────────────────
    const svg = svgEl('svg', { viewBox: `0 0 ${width} ${height}`, class: 'sc-svg', role: 'img', 'aria-label': title || 'Waterfall chart' });
    const defs = svgEl('defs'); svg.appendChild(defs);
    const g = svgEl('g', { transform: `translate(${margin.left},${margin.top})` }); svg.appendChild(g);

    if (title) {
      const t = svgEl('text', { x: width / 2, y: -margin.top / 2 + 12, 'text-anchor': 'middle', class: 'sc-title', fill: 'var(--text-primary, #fff)', 'font-size': '14' });
      t.textContent = title; g.appendChild(t);
    }

    // Grid lines + Y axis labels
    scale.ticks.forEach(tick => {
      const y = H - ((tick - scale.min) / yRange) * H;
      g.appendChild(svgEl('line', { x1: 0, y1: y, x2: W, y2: y, stroke: 'var(--text-secondary, #555)', 'stroke-opacity': '0.2', 'stroke-width': '1', 'stroke-dasharray': tick === 0 ? 'none' : '4 4' }));
      const lbl = svgEl('text', { x: -8, y: y + 4, 'text-anchor': 'end', class: 'sc-label', fill: 'var(--text-secondary, #888)', 'font-size': '11' });
      lbl.textContent = fmt(tick); g.appendChild(lbl);
    });

    const n = computed.length;
    const groupW = W / n;
    const barPad = groupW * 0.18;
    const barW = groupW - barPad * 2;
    const delay = prefersReducedMotion() ? 0 : animDuration / n;

    computed.forEach((c, i) => {
      const barX = i * groupW + barPad;
      const baseY = H - ((c.base + c.barValue - scale.min) / yRange) * H;
      const barH  = Math.max((c.barValue / yRange) * H, 1);
      const topY  = baseY; // top of bar in SVG coords

      // Gradient
      const gradId = uid('wfg');
      const grad = svgEl('linearGradient', { id: gradId, x1: '0', y1: '0', x2: '0', y2: '1' });
      grad.appendChild(svgEl('stop', { offset: '0%',   'stop-color': c.color, 'stop-opacity': '1' }));
      grad.appendChild(svgEl('stop', { offset: '100%', 'stop-color': c.color, 'stop-opacity': '0.65' }));
      defs.appendChild(grad);

      const rect = svgEl('rect', { x: barX, y: topY, width: barW, height: barH, rx: 3, fill: `url(#${gradId})`, class: 'sc-wf-bar', 'transform-origin': `${barX + barW / 2}px ${topY + barH}px` });
      if (!prefersReducedMotion()) rect.style.animation = `sc-growY ${animDuration}ms cubic-bezier(0.34,1.56,0.64,1) ${i * delay * 0.5}ms both`;
      const sign = c.type === 'delta' && c.value < 0 ? '−' : (c.type === 'delta' && c.value > 0 ? '+' : '');
      attachTooltip(rect, c.label, sign + fmt(Math.abs(c.value)), c.color);
      g.appendChild(rect);

      // Connector line to next bar (dashed, at top of this bar)
      if (showConnectors && i < n - 1 && c.type !== 'start') {
        const nextBarX = (i + 1) * groupW + barPad;
        const connY = H - (((c.base + c.barValue) - scale.min) / yRange) * H;
        g.appendChild(svgEl('line', { x1: barX + barW, y1: connY, x2: nextBarX, y2: connY, stroke: c.color, 'stroke-width': '1', 'stroke-dasharray': '4 3', 'stroke-opacity': '0.5' }));
      }

      // Value label
      if (showValues) {
        const sign = c.type === 'delta' && c.value < 0 ? '−' : (c.type === 'delta' && c.value > 0 ? '+' : '');
        const vLbl = svgEl('text', { x: barX + barW / 2, y: topY - 6, 'text-anchor': 'middle', class: 'sc-label', fill: 'var(--text-secondary, #aaa)', 'font-size': '10', opacity: '0' });
        vLbl.textContent = sign + fmt(Math.abs(c.value));
        if (!prefersReducedMotion()) vLbl.style.animation = `sc-fadeIn 0.4s ease ${i * delay * 0.5 + animDuration * 0.7}ms forwards`;
        else vLbl.setAttribute('opacity', '1');
        g.appendChild(vLbl);
      }

      // X axis label
      const xLbl = svgEl('text', { x: barX + barW / 2, y: H + 20, 'text-anchor': 'middle', class: 'sc-label', fill: 'var(--text-secondary, #888)', 'font-size': '11' });
      xLbl.textContent = c.label.length > 6 ? c.label.slice(0, 5) + '…' : c.label;
      g.appendChild(xLbl);
    });

    // Zero line
    const zeroY = H - ((0 - scale.min) / yRange) * H;
    g.appendChild(svgEl('line', { x1: 0, y1: zeroY, x2: W, y2: zeroY, stroke: 'var(--text-secondary, #555)', 'stroke-width': '1.5' }));

    const wrap = document.createElement('div'); wrap.className = 'sc-wrap'; wrap.appendChild(svg);
    el.innerHTML = ''; el.appendChild(wrap);
    el.dispatchEvent(new CustomEvent('chart:ready', { bubbles: true }));
  }

  // ─────────────────────────────────────────────────────────────────────────
  // BULLET CHART
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Renders a bullet chart (target vs actual with qualitative bands).
   *
   * @param {string|Element} container
   * @param {Object} data
   *   @param {Array<{
   *     label: string,
   *     value: number,          actual value
   *     target: number,         target / reference marker
   *     max?: number,           axis max (default: auto)
   *     ranges?: number[],      up to 3 qualitative band boundaries [bad, ok, good]
   *     color?: string
   *   }>} data.items
   * @param {Object} [options]
   *   @param {number}  [options.width=560]
   *   @param {number}  [options.barHeight=28]
   *   @param {boolean} [options.showValues=true]
   *   @param {number}  [options.animDuration=650]
   *   @param {string}  [options.title]
   * @returns {ChartInstance}
   *
   * Data format example:
   *   {
   *     items: [
   *       { label: '销售额',   value: 270, target: 300, max: 400, ranges: [150, 220, 310] },
   *       { label: '用户增长', value: 85,  target: 80,  max: 100, ranges: [40,  60,  90]  },
   *     ]
   *   }
   */
  function bullet(container, data, options = {}) {
    injectCSS();
    const el = resolve(container);
    if (!el) { console.warn(`[SlideCharts] bullet: container not found — "${container}"`); return _noopInstance; }
    _renderBullet(el, data, options);
    return makeInstance(el, _renderBullet, data, options);
  }

  function _renderBullet(el, data, options = {}) {
    const {
      width = 560,
      barHeight = 28,
      showValues = true,
      animDuration = 650,
      title,
    } = options;

    const items = data.items || [];
    const labelW = 100, valueW = showValues ? 52 : 0, gap = 12;
    const barW = width - labelW - valueW - gap * 2;
    const rowH = barHeight + 20;
    const marginTop = title ? 44 : 12;
    const svgH = marginTop + items.length * rowH + 12;

    const svg = svgEl('svg', { viewBox: `0 0 ${width} ${svgH}`, class: 'sc-svg', role: 'img', 'aria-label': title || 'Bullet chart' });
    const defs = svgEl('defs'); svg.appendChild(defs);

    if (title) {
      const t = svgEl('text', { x: width / 2, y: 22, 'text-anchor': 'middle', class: 'sc-title', fill: 'var(--text-primary, #fff)', 'font-size': '14' });
      t.textContent = title; svg.appendChild(t);
    }

    items.forEach((item, i) => {
      const max = item.max || Math.max(item.value, item.target) * 1.25;
      const scale = barW / max;
      const y = marginTop + i * rowH;
      const color = getColor(i, item.color);

      // Label
      const lbl = svgEl('text', { x: gap, y: y + barHeight / 2 + 4, 'text-anchor': 'start', class: 'sc-label', fill: 'var(--text-primary, #eee)', 'font-size': '12' });
      lbl.textContent = item.label.length > 12 ? item.label.slice(0, 11) + '…' : item.label;
      svg.appendChild(lbl);

      const barX = labelW + gap;

      // Qualitative background bands
      const ranges = item.ranges || [max * 0.4, max * 0.7, max];
      const bandColors = ['rgba(255,255,255,0.05)', 'rgba(255,255,255,0.1)', 'rgba(255,255,255,0.17)'];
      let prevX = barX;
      ranges.forEach((r, ri) => {
        const bw = Math.min(r, max) * scale - (prevX - barX);
        if (bw <= 0) return;
        svg.appendChild(svgEl('rect', { x: prevX, y: y + barHeight * 0.1, width: bw, height: barHeight * 0.8, fill: bandColors[ri] || bandColors[bandColors.length - 1], rx: 2 }));
        prevX = barX + Math.min(r, max) * scale;
      });

      // Actual value bar (narrow, centered vertically)
      const actualW = Math.min(item.value, max) * scale;
      const bh = barHeight * 0.45;
      const by = y + (barHeight - bh) / 2;

      const gradId = uid('bltg');
      const grad = svgEl('linearGradient', { id: gradId, x1: '0', y1: '0', x2: '1', y2: '0' });
      grad.appendChild(svgEl('stop', { offset: '0%',   'stop-color': color, 'stop-opacity': '0.8' }));
      grad.appendChild(svgEl('stop', { offset: '100%', 'stop-color': color, 'stop-opacity': '1' }));
      defs.appendChild(grad);

      const actualRect = svgEl('rect', { x: barX, y: by, width: actualW, height: bh, rx: 2, fill: `url(#${gradId})`, class: 'sc-bullet-bar', 'transform-origin': `${barX}px ${by}px` });
      if (!prefersReducedMotion()) actualRect.style.animation = `sc-growX ${animDuration}ms cubic-bezier(0.4,0,0.2,1) ${i * 100}ms both`;
      attachTooltip(actualRect, item.label, `${fmt(item.value)} / ${fmt(item.target)} (${Math.round((item.value / item.target) * 100)}%)`, color);
      svg.appendChild(actualRect);

      // Target marker (vertical tick)
      const targetX = Math.min(item.target, max) * scale + barX;
      const tickH = barHeight * 0.85;
      const tickY = y + (barHeight - tickH) / 2;
      const tick = svgEl('rect', { x: targetX - 1.5, y: tickY, width: 3, height: tickH, fill: 'var(--text-primary, #fff)', rx: 1.5, class: 'sc-bullet-target', opacity: '0' });
      if (!prefersReducedMotion()) tick.style.animation = `sc-fadeIn 0.4s ease ${animDuration * 0.6 + i * 100}ms forwards`;
      else tick.setAttribute('opacity', '0.9');
      svg.appendChild(tick);

      // Values
      if (showValues) {
        const vx = barX + barW + gap;
        const vt = svgEl('text', { x: vx, y: y + barHeight / 2 + 4, 'text-anchor': 'start', class: 'sc-label', fill: 'var(--text-secondary, #aaa)', 'font-size': '11' });
        const pct = Math.round((item.value / item.target) * 100);
        vt.textContent = `${fmt(item.value)} / ${fmt(item.target)}`;
        if (!prefersReducedMotion()) vt.style.animation = `sc-fadeIn 0.4s ease ${animDuration * 0.7 + i * 100}ms both`;
        svg.appendChild(vt);
      }
    });

    const wrap = document.createElement('div'); wrap.className = 'sc-wrap'; wrap.appendChild(svg);
    el.innerHTML = ''; el.appendChild(wrap);
    el.dispatchEvent(new CustomEvent('chart:ready', { bubbles: true }));
  }

  // ─────────────────────────────────────────────────────────────────────────
  // SCATTER / BUBBLE CHART
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Renders a scatter plot (optionally with bubble sizing).
   *
   * @param {string|Element} container
   * @param {Object} data
   *   @param {Array<{
   *     label?: string,
   *     points: Array<{x:number, y:number, r?:number, label?:string}>
   *     color?: string
   *   }>} data.datasets
   * @param {Object} [options]
   *   @param {number}  [options.width=560]
   *   @param {number}  [options.height=360]
   *   @param {boolean} [options.showGrid=true]
   *   @param {boolean} [options.showLabels=false]   label each point
   *   @param {boolean} [options.showLegend=true]
   *   @param {number}  [options.dotRadius=6]        default dot radius (when r is absent)
   *   @param {boolean} [options.bubble=false]       enable bubble mode (use point.r for size)
   *   @param {string}  [options.xLabel]
   *   @param {string}  [options.yLabel]
   *   @param {number}  [options.animDuration=700]
   *   @param {string}  [options.title]
   * @returns {ChartInstance}
   */
  function scatter(container, data, options = {}) {
    injectCSS();
    const el = resolve(container);
    if (!el) { console.warn(`[SlideCharts] scatter: container not found — "${container}"`); return _noopInstance; }
    _renderScatter(el, data, options);
    return makeInstance(el, _renderScatter, data, options);
  }

  function _renderScatter(el, data, options = {}) {
    const {
      width = 560, height = 360,
      showGrid = true, showLabels = false, showLegend = true,
      dotRadius = 6, bubble = false,
      xLabel, yLabel,
      animDuration = 700, title,
    } = options;

    const margin = { top: title ? 52 : 24, right: 24, bottom: xLabel ? 64 : 48, left: yLabel ? 64 : 52 };
    const W = width  - margin.left - margin.right;
    const H = height - margin.top  - margin.bottom;

    const allX = data.datasets.flatMap(ds => ds.points.map(p => p.x));
    const allY = data.datasets.flatMap(ds => ds.points.map(p => p.y));
    const allR = bubble ? data.datasets.flatMap(ds => ds.points.map(p => p.r || dotRadius)) : [dotRadius];

    const xScale = niceScale(Math.min(...allX), Math.max(...allX));
    const yScale = niceScale(Math.min(...allY), Math.max(...allY));
    const maxR   = bubble ? Math.max(...allR) : dotRadius;

    const toSvgX = (x) => ((x - xScale.min) / (xScale.max - xScale.min)) * W;
    const toSvgY = (y) => H - ((y - yScale.min) / (yScale.max - yScale.min)) * H;

    const svg = svgEl('svg', { viewBox: `0 0 ${width} ${height}`, class: 'sc-svg', role: 'img', 'aria-label': title || 'Scatter chart' });
    const defs = svgEl('defs'); svg.appendChild(defs);
    const g = svgEl('g', { transform: `translate(${margin.left},${margin.top})` }); svg.appendChild(g);

    if (title) {
      const t = svgEl('text', { x: width / 2, y: -margin.top / 2 + 12, 'text-anchor': 'middle', class: 'sc-title', fill: 'var(--text-primary, #fff)', 'font-size': '14' });
      t.textContent = title; g.appendChild(t);
    }

    // Grid lines
    if (showGrid) {
      yScale.ticks.forEach(tick => {
        const y = toSvgY(tick);
        g.appendChild(svgEl('line', { x1: 0, y1: y, x2: W, y2: y, stroke: 'var(--text-secondary, #555)', 'stroke-opacity': '0.15', 'stroke-width': '1', 'stroke-dasharray': '4 4' }));
        const lbl = svgEl('text', { x: -8, y: y + 4, 'text-anchor': 'end', class: 'sc-label', fill: 'var(--text-secondary, #888)', 'font-size': '10' });
        lbl.textContent = fmt(tick); g.appendChild(lbl);
      });
      xScale.ticks.forEach(tick => {
        const x = toSvgX(tick);
        g.appendChild(svgEl('line', { x1: x, y1: 0, x2: x, y2: H, stroke: 'var(--text-secondary, #555)', 'stroke-opacity': '0.15', 'stroke-width': '1', 'stroke-dasharray': '4 4' }));
        const lbl = svgEl('text', { x, y: H + 16, 'text-anchor': 'middle', class: 'sc-label', fill: 'var(--text-secondary, #888)', 'font-size': '10' });
        lbl.textContent = fmt(tick); g.appendChild(lbl);
      });
    }

    // Axis labels
    if (xLabel) {
      const xl = svgEl('text', { x: W / 2, y: H + (xLabel ? 40 : 28), 'text-anchor': 'middle', class: 'sc-label', fill: 'var(--text-secondary, #aaa)', 'font-size': '12' });
      xl.textContent = xLabel; g.appendChild(xl);
    }
    if (yLabel) {
      const yl = svgEl('text', { x: -H / 2, y: -margin.left + 14, 'text-anchor': 'middle', class: 'sc-label', fill: 'var(--text-secondary, #aaa)', 'font-size': '12', transform: 'rotate(-90)' });
      yl.textContent = yLabel; g.appendChild(yl);
    }

    // Axes
    g.appendChild(svgEl('line', { x1: 0, y1: H, x2: W, y2: H, stroke: 'var(--text-secondary, #555)', 'stroke-width': '1.5' }));
    g.appendChild(svgEl('line', { x1: 0, y1: 0, x2: 0, y2: H, stroke: 'var(--text-secondary, #555)', 'stroke-width': '1.5' }));

    // Points
    let pointCount = 0;
    data.datasets.forEach((ds, di) => {
      const color = getColor(di, ds.color);
      ds.points.forEach((p, pi) => {
        const cx = toSvgX(p.x);
        const cy = toSvgY(p.y);
        const r  = bubble ? Math.max(3, (p.r || dotRadius) / maxR * 28) : dotRadius;
        const circle = svgEl('circle', {
          cx, cy, r,
          fill: color,
          'fill-opacity': '0.75',
          stroke: color,
          'stroke-width': '1',
          'stroke-opacity': '0.9',
          class: `sc-scatter-dot sc-series-${di}`,
          'aria-label': p.label || `(${p.x}, ${p.y})`,
        });
        if (!prefersReducedMotion()) {
          circle.style.opacity = '0';
          circle.style.transform = 'scale(0)';
          circle.style.transformOrigin = `${cx}px ${cy}px`;
          circle.style.transition = `opacity 0.3s ease ${pointCount * 30}ms, transform 0.35s cubic-bezier(0.34,1.56,0.64,1) ${pointCount * 30}ms`;
          requestAnimationFrame(() => requestAnimationFrame(() => { circle.style.opacity = '1'; circle.style.transform = 'scale(1)'; }));
        }
        attachTooltip(circle, p.label || `${ds.label || ''} (${p.x}, ${p.y})`, bubble ? `r=${p.r || dotRadius}` : `(${p.x}, ${p.y})`, color);
        g.appendChild(circle);

        if (showLabels && p.label) {
          const lt = svgEl('text', { x: cx, y: cy - r - 4, 'text-anchor': 'middle', class: 'sc-label', fill: 'var(--text-secondary, #aaa)', 'font-size': '9' });
          lt.textContent = p.label;
          if (!prefersReducedMotion()) lt.style.animation = `sc-fadeIn 0.3s ease ${pointCount * 30 + 300}ms both`;
          g.appendChild(lt);
        }
        pointCount++;
      });
    });

    const wrap = document.createElement('div'); wrap.className = 'sc-wrap'; wrap.appendChild(svg);
    if (showLegend && data.datasets.length > 1) {
      const legend = document.createElement('div'); legend.className = 'sc-legend';
      data.datasets.forEach((ds, i) => {
        const item = document.createElement('div'); item.className = 'sc-legend-item';
        const dot = document.createElement('span'); dot.className = 'sc-legend-dot'; dot.style.background = getColor(i, ds.color);
        item.appendChild(dot); item.appendChild(document.createTextNode(ds.label || `Series ${i + 1}`)); legend.appendChild(item);
      });
      wrap.appendChild(legend);
      makeLegendFilterable(legend, svg);
    }
    el.innerHTML = ''; el.appendChild(wrap);
    el.dispatchEvent(new CustomEvent('chart:ready', { bubbles: true }));
  }

  // ─────────────────────────────────────────────────────────────────────────
  // GAUGE / SPEEDOMETER CHART
  // ─────────────────────────────────────────────────────────────────────────

  /**
   * Renders a gauge (half-circle speedometer) chart.
   *
   * @param {string|Element} container
   * @param {Object} data
   *   @param {number}   data.value          current value
   *   @param {number}   [data.min=0]        minimum value
   *   @param {number}   [data.max=100]      maximum value
   *   @param {string}   [data.label]        center label text
   *   @param {string}   [data.unit]         unit suffix (e.g. '%', 'ms')
   *   @param {Array<{value:number, color:string, label?:string}>} [data.zones]
   *     Up to 4 color zones. Each zone spans from the previous zone's value to this one's value.
   *     If omitted, a single accent color arc is used.
   * @param {Object} [options]
   *   @param {number}  [options.width=320]
   *   @param {number}  [options.thickness=22]   arc stroke width
   *   @param {boolean} [options.showNeedle=true]
   *   @param {boolean} [options.showMinMax=true]
   *   @param {number}  [options.animDuration=900]
   *   @param {string}  [options.title]
   * @returns {ChartInstance}
   *
   * Data format example:
   *   {
   *     value: 72, min: 0, max: 100, label: '满意度', unit: '%',
   *     zones: [
   *       { value: 40,  color: 'var(--chart6, #ef4444)',  label: '差' },
   *       { value: 70,  color: 'var(--chart4, #f59e0b)',  label: '中' },
   *       { value: 100, color: 'var(--chart3, #10b981)',  label: '优' },
   *     ]
   *   }
   */
  function gauge(container, data, options = {}) {
    injectCSS();
    const el = resolve(container);
    if (!el) { console.warn(`[SlideCharts] gauge: container not found — "${container}"`); return _noopInstance; }
    _renderGauge(el, data, options);
    return makeInstance(el, _renderGauge, data, options);
  }

  function _renderGauge(el, data, options = {}) {
    const {
      width = 320,
      thickness = 22,
      showNeedle = true,
      showMinMax = true,
      animDuration = 900,
      title,
    } = options;

    const height = width * 0.6 + (title ? 32 : 0);
    const titleH = title ? 30 : 0;
    const cx = width / 2;
    const cy = height - 20 + titleH * 0.5;
    const R  = (width / 2) - thickness - 12;

    const min = data.min ?? 0;
    const max = data.max ?? 100;
    const value = Math.min(max, Math.max(min, data.value));
    const pct = (value - min) / (max - min); // 0..1

    // Gauge spans from -180° to 0° (left → right half circle)
    const START_DEG = -180;
    const END_DEG   = 0;
    const TOTAL_DEG = END_DEG - START_DEG; // 180

    function degToXY(deg, r) {
      const rad = (deg * Math.PI) / 180;
      return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
    }

    function arcPath(startDeg, endDeg, r, thick) {
      const s = degToXY(startDeg, r);
      const e = degToXY(endDeg,   r);
      const large = Math.abs(endDeg - startDeg) > 180 ? 1 : 0;
      return `M ${s.x} ${s.y} A ${r} ${r} 0 ${large} 1 ${e.x} ${e.y}`;
    }

    const svg = svgEl('svg', { viewBox: `0 0 ${width} ${height}`, class: 'sc-svg', role: 'img', 'aria-label': title || 'Gauge chart' });
    const defs = svgEl('defs'); svg.appendChild(defs);

    if (title) {
      const t = svgEl('text', { x: cx, y: 20, 'text-anchor': 'middle', class: 'sc-title', fill: 'var(--text-primary, #fff)', 'font-size': '14' });
      t.textContent = title; svg.appendChild(t);
    }

    // Background track
    const trackPath = arcPath(START_DEG, END_DEG, R, thickness);
    svg.appendChild(svgEl('path', { d: trackPath, fill: 'none', stroke: 'var(--surface, #222)', 'stroke-width': thickness, 'stroke-linecap': 'round' }));

    // Zones (or single arc)
    const zones = data.zones && data.zones.length > 0
      ? data.zones
      : [{ value: max, color: 'var(--accent, #6366f1)' }];

    let prevZoneVal = min;
    zones.forEach(zone => {
      const zStart = START_DEG + ((prevZoneVal - min) / (max - min)) * TOTAL_DEG;
      const zEnd   = START_DEG + ((Math.min(zone.value, max) - min) / (max - min)) * TOTAL_DEG;
      if (zEnd <= zStart) { prevZoneVal = zone.value; return; }
      const zPath = arcPath(zStart, zEnd, R, thickness);
      svg.appendChild(svgEl('path', { d: zPath, fill: 'none', stroke: zone.color, 'stroke-width': thickness, 'stroke-linecap': 'butt', class: 'sc-gauge-zone' }));
      prevZoneVal = zone.value;
    });

    // Animated value arc
    const valueDeg = START_DEG + pct * TOTAL_DEG;
    const valuePath = arcPath(START_DEG, valueDeg - 0.01, R, thickness * 0.55);
    const circumference = Math.PI * R;
    const valueLen = (pct * circumference);

    const valueArc = svgEl('path', {
      d: valuePath,
      fill: 'none',
      stroke: 'var(--text-primary, #fff)',
      'stroke-width': thickness * 0.55,
      'stroke-linecap': 'round',
      'stroke-opacity': '0',
      class: 'sc-gauge-value',
    });
    if (!prefersReducedMotion()) {
      valueArc.style.transition = `stroke-opacity 0.2s ease`;
      requestAnimationFrame(() => requestAnimationFrame(() => { valueArc.style.strokeOpacity = '0.9'; }));
    } else {
      valueArc.setAttribute('stroke-opacity', '0.9');
    }
    svg.appendChild(valueArc);

    // Needle
    if (showNeedle) {
      const needleDeg = START_DEG + pct * TOTAL_DEG;
      const needleRad = (needleDeg * Math.PI) / 180;
      const nx = cx + (R - thickness * 0.5) * Math.cos(needleRad);
      const ny = cy + (R - thickness * 0.5) * Math.sin(needleRad);
      const needle = svgEl('line', {
        x1: cx, y1: cy, x2: nx, y2: ny,
        stroke: 'var(--text-primary, #fff)',
        'stroke-width': '2.5',
        'stroke-linecap': 'round',
        class: 'sc-gauge-needle',
      });
      if (!prefersReducedMotion()) {
        needle.style.transformOrigin = `${cx}px ${cy}px`;
        needle.style.transform = `rotate(${START_DEG - needleDeg}deg)`;
        needle.style.transition = `transform ${animDuration}ms cubic-bezier(0.4,0,0.2,1)`;
        requestAnimationFrame(() => requestAnimationFrame(() => { needle.style.transform = 'rotate(0deg)'; }));
      }
      svg.appendChild(needle);
      // Center cap
      svg.appendChild(svgEl('circle', { cx, cy, r: thickness * 0.4, fill: 'var(--text-primary, #fff)', class: 'sc-gauge-cap' }));
    }

    // Value label
    const displayVal = fmt(value) + (data.unit || '');
    const valText = svgEl('text', { x: cx, y: cy - R * 0.22, 'text-anchor': 'middle', class: 'sc-title', fill: 'var(--text-primary, #fff)', 'font-size': String(Math.round(R * 0.28)) });
    valText.textContent = displayVal;
    if (!prefersReducedMotion()) valText.style.animation = `sc-fadeIn 0.5s ease ${animDuration * 0.5}ms both`;
    svg.appendChild(valText);

    if (data.label) {
      const lblText = svgEl('text', { x: cx, y: cy + R * 0.12, 'text-anchor': 'middle', class: 'sc-label', fill: 'var(--text-secondary, #aaa)', 'font-size': String(Math.round(R * 0.14)) });
      lblText.textContent = data.label;
      if (!prefersReducedMotion()) lblText.style.animation = `sc-fadeIn 0.5s ease ${animDuration * 0.6}ms both`;
      svg.appendChild(lblText);
    }

    // Min / Max labels
    if (showMinMax) {
      const minPt = degToXY(START_DEG, R + thickness + 8);
      const maxPt = degToXY(END_DEG,   R + thickness + 8);
      const minLbl = svgEl('text', { x: minPt.x, y: minPt.y + 4, 'text-anchor': 'middle', class: 'sc-label', fill: 'var(--text-secondary, #888)', 'font-size': '10' });
      minLbl.textContent = fmt(min); svg.appendChild(minLbl);
      const maxLbl = svgEl('text', { x: maxPt.x, y: maxPt.y + 4, 'text-anchor': 'middle', class: 'sc-label', fill: 'var(--text-secondary, #888)', 'font-size': '10' });
      maxLbl.textContent = fmt(max); svg.appendChild(maxLbl);
    }

    const wrap = document.createElement('div'); wrap.className = 'sc-wrap'; wrap.style.cssText = 'display:flex;flex-direction:column;align-items:center;';
    wrap.appendChild(svg);
    el.innerHTML = ''; el.appendChild(wrap);
    el.dispatchEvent(new CustomEvent('chart:ready', { bubbles: true }));
  }



  return {
    bar, line, area, donut, horizontalBar, progress, radar, sankey, treemap, waterfall, bullet, scatter, gauge,
    // Export palette for theme adapter integration
    PALETTE: PALETTE,
  };

})();
