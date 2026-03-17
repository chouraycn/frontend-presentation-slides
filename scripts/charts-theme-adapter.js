/**
 * charts-theme-adapter.js - 图表主题颜色适配系统
 * 
 * 功能:
 * 1. 自动从 DOM 读取模版主题颜色变量
 * 2. 提供智能配色方案
 * 3. 支持不同风格的颜色生成
 * 4. 与 charts.js 无缝集成
 */

const SlideChartsTheme = (() => {
  'use strict';

  // ── 主题风格预设 ────────────────────────────────────────────────
  const THEME_STYLES = {
    // Pash Orange 风格 - 橙色系
    'pash-orange': {
      base: '#FF5C00',
      secondary: '#FF8040',
      tertiary: '#FFA366',
      palette: [
        'var(--orange, #FF5C00)',
        'var(--orange-light, #FF8040)',
        'var(--chart3, #FFB366)',
        'var(--chart4, #FFE0CC)',
        'var(--chart5, #FF9933)',
        'var(--chart6, #CC4D00)',
      ]
    },
    
    // Claude Warmth 风格 - 暖色系
    'claude-warmth': {
      base: '#E8A879',
      secondary: '#F4C9A6',
      palette: [
        'var(--accent, #E8A879)',
        'var(--accent2, #F4C9A6)',
        'var(--chart3, #D48F6C)',
        'var(--chart4, #C37C5F)',
        'var(--chart5, #FFC7A0)',
        'var(--chart6, #B26D52)',
      ]
    },
    
    // ForAI White 风格 - 纯净白色系
    'forai-white': {
      base: '#2563EB',
      secondary: '#3B82F6',
      palette: [
        'var(--accent, #2563EB)',
        'var(--accent2, #3B82F6)',
        'var(--chart3, #1D4ED8)',
        'var(--chart4, #60A5FA)',
        'var(--chart5, #93C5FD)',
        'var(--chart6, #1E40AF)',
      ]
    },
    
    // HHart Red 风格 - 红色系
    'hhart-red': {
      base: '#E63946',
      secondary: '#F4A261',
      palette: [
        'var(--accent, #E63946)',
        'var(--accent2, #F4A261)',
        'var(--chart3, #F1FAEE)',
        'var(--chart4, #A8DADC)',
        'var(--chart5, #457B9D)',
        'var(--chart6, #1D3557)',
      ]
    },
    
    // Pitch Deck 风格 - 金色系
    'pitch-deck': {
      base: '#c9a84c',
      secondary: '#e8c97a',
      palette: [
        'var(--accent, #c9a84c)',
        'var(--accent2, #e8c97a)',
        'var(--chart3, #10b981)',
        'var(--chart4, #f59e0b)',
        'var(--chart5, #3b82f6)',
        'var(--chart6, #ef4444)',
      ]
    },
    
    // Tech Talk 风格 - 科技蓝系
    'tech-talk': {
      base: '#6366f1',
      secondary: '#ec4899',
      palette: [
        'var(--accent, #6366f1)',
        'var(--accent2, #ec4899)',
        'var(--chart3, #10b981)',
        'var(--chart4, #f59e0b)',
        'var(--chart5, #3b82f6)',
        'var(--chart6, #ef4444)',
      ]
    },
    
    // Product Launch 风格 - 活力橙
    'product-launch': {
      base: '#FF6B35',
      secondary: '#F7931E',
      palette: [
        'var(--accent, #FF6B35)',
        'var(--accent2, #F7931E)',
        'var(--chart3, #004E89)',
        'var(--chart4, #1A659E)',
        'var(--chart5, #FFBE0B)',
        'var(--chart6, #FB5607)',
      ]
    },
    
    // Quarterly Report 风格 - 专业蓝
    'quarterly-report': {
      base: '#1E3A8A',
      secondary: '#3B82F6',
      palette: [
        'var(--accent, #1E3A8A)',
        'var(--accent2, #3B82F6)',
        'var(--chart3, #10B981)',
        'var(--chart4, #F59E0B)',
        'var(--chart5, #6366F1)',
        'var(--chart6, #EF4444)',
      ]
    },
  };

  // ── 颜色工具函数 ──────────────────────────────────────────────────

  /**
   * 解析 CSS 变量或直接颜色值
   * @param {string} value - 'var(--name, fallback)' 或 '#FF0000'
   * @returns {string} 解析后的颜色值
   */
  function resolveColor(value) {
    if (!value) return '#6366f1';
    
    // 解析 CSS 变量
    const varMatch = value.match(/var\(([^,]+)(?:,\s*([^)]+))?\)/);
    if (varMatch) {
      const varName = varMatch[1].trim();
      const fallback = varMatch[2] ? varMatch[2].trim() : null;
      const computed = getComputedStyle(document.documentElement).getPropertyValue(varName);
      return computed ? computed.trim() : (fallback || '#6366f1');
    }
    
    return value;
  }

  /**
   * 从 DOM 读取所有可用的主题颜色变量
   * @returns {Object} 颜色变量对象
   */
  function readThemeColors() {
    const root = document.documentElement;
    const style = getComputedStyle(root);
    const colors = {};
    
    // 常用颜色变量列表
    const colorVars = [
      '--accent', '--accent2',
      '--chart3', '--chart4', '--chart5', '--chart6',
      '--primary', '--secondary', '--tertiary',
      '--color-primary', '--color-secondary',
      '--brand-color', '--brand-primary',
      '--orange', '--orange-light', '--orange-dim',
    ];
    
    colorVars.forEach(varName => {
      const value = style.getPropertyValue(varName);
      if (value && value.trim()) {
        colors[varName] = value.trim();
      }
    });
    
    return colors;
  }

  /**
   * 检测当前使用的主题风格
   * @returns {string|null} 主题名称
   */
  function detectTheme() {
    const colors = readThemeColors();
    
    // 检查特定主题的颜色特征
    if (colors['--orange']?.includes('FF5C00')) return 'pash-orange';
    if (colors['--accent']?.includes('E8A879')) return 'claude-warmth';
    if (colors['--accent']?.includes('c9a84c')) return 'pitch-deck';
    if (colors['--accent']?.includes('6366f1')) return 'tech-talk';
    if (colors['--accent']?.includes('2563EB')) return 'forai-white';
    if (colors['--accent']?.includes('E63946')) return 'hhart-red';
    if (colors['--accent']?.includes('FF6B35')) return 'product-launch';
    if (colors['--accent']?.includes('1E3A8A')) return 'quarterly-report';
    
    return null;
  }

  /**
   * 根据主色生成调色板
   * @param {string} baseColor - 基础颜色 (hex 或 hsl)
   * @param {number} count - 生成颜色数量
   * @returns {string[]} 颜色数组
   */
  function generatePalette(baseColor, count = 6) {
    const base = resolveColor(baseColor);
    const hsl = hexToHSL(base);
    const palette = [];
    
    for (let i = 0; i < count; i++) {
      const hue = (hsl.h + i * (360 / count)) % 360;
      const color = HSLToHex(hue, hsl.s, hsl.l);
      palette.push(color);
    }
    
    return palette;
  }

  /**
   * 生成单色系调色板（同色相不同明度）
   * @param {string} baseColor - 基础颜色
   * @param {number} count - 生成数量
   * @returns {string[]} 颜色数组
   */
  function generateMonochromePalette(baseColor, count = 6) {
    const base = resolveColor(baseColor);
    const hsl = hexToHSL(base);
    const palette = [];
    
    for (let i = 0; i < count; i++) {
      const lightness = 30 + (i * (60 / (count - 1)));
      const color = HSLToHex(hsl.h, hsl.s, Math.min(100, lightness));
      palette.push(color);
    }
    
    return palette;
  }

  /**
   * 生成渐变调色板（相邻色相）
   * @param {string} baseColor - 基础颜色
   * @param {number} count - 生成数量
   * @param {number} range - 色相范围（度）
   * @returns {string[]} 颜色数组
   */
  function generateAnalogousPalette(baseColor, count = 6, range = 30) {
    const base = resolveColor(baseColor);
    const hsl = hexToHSL(base);
    const palette = [];
    const startHue = hsl.h - range / 2;
    
    for (let i = 0; i < count; i++) {
      const hue = (startHue + (i * range / (count - 1))) % 360;
      const color = HSLToHex(hue < 0 ? hue + 360 : hue, hsl.s, hsl.l);
      palette.push(color);
    }
    
    return palette;
  }

  /**
   * 生成对比色系（互补色）
   * @param {string} baseColor - 基础颜色
   * @returns {string[]} 6种颜色（主色 + 互补色系列）
   */
  function generateComplementaryPalette(baseColor) {
    const base = resolveColor(baseColor);
    const hsl = hexToHSL(base);
    const compHue = (hsl.h + 180) % 360;
    
    return [
      base, // 主色
      HSLToHex(compHue, hsl.s, hsl.l), // 互补色
      HSLToHex(hsl.h, hsl.s, Math.max(20, hsl.l - 20)), // 主色深
      HSLToHex(compHue, hsl.s, Math.max(20, hsl.l - 20)), // 互补色深
      HSLToHex(hsl.h, hsl.s, Math.min(90, hsl.l + 20)), // 主色浅
      HSLToHex(compHue, hsl.s, Math.min(90, hsl.l + 20)), // 互补色浅
    ];
  }

  // ── 颜色转换函数 ────────────────────────────────────────────────

  function hexToHSL(hex) {
    hex = hex.replace('#', '');
    if (hex.length === 3) hex = hex.split('').map(c => c + c).join('');
    
    const r = parseInt(hex.substring(0, 2), 16) / 255;
    const g = parseInt(hex.substring(2, 4), 16) / 255;
    const b = parseInt(hex.substring(4, 6), 16) / 255;
    
    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h, s, l = (max + min) / 2;
    
    if (max === min) {
      h = s = 0;
    } else {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      
      switch (max) {
        case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
        case g: h = ((b - r) / d + 2) / 6; break;
        case b: h = ((r - g) / d + 4) / 6; break;
      }
    }
    
    return { h: h * 360, s: s * 100, l: l * 100 };
  }

  function HSLToHex(h, s, l) {
    s /= 100; l /= 100;
    const a = s * Math.min(l, 1 - l);
    const f = n => {
      const k = (n + h / 30) % 12;
      return l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
    };
    return '#' + [f(0), f(8), f(4)].map(x => {
      const hex = Math.round(x * 255).toString(16);
      return hex.length === 1 ? '0' + hex : hex;
    }).join('');
  }

  // ── 公开 API ─────────────────────────────────────────────────────

  return {
    /**
     * 获取当前主题的调色板
     * @param {Object} options - 配置选项
     *   @param {string} options.theme - 主题名称（可选，自动检测）
     *   @param {string} options.baseColor - 基础颜色（可选，覆盖主题）
     *   @param {string} options.style - 配色风格: 'default' | 'monochrome' | 'analogous' | 'complementary'
     *   @param {number} options.count - 颜色数量
     * @returns {string[]} 颜色数组
     */
    getPalette(options = {}) {
      const {
        theme = null,
        baseColor = null,
        style = 'default',
        count = 6
      } = options;
      
      // 如果指定了主题，使用预设调色板
      if (theme && THEME_STYLES[theme]) {
        return THEME_STYLES[theme].palette.slice(0, count);
      }
      
      // 自动检测主题
      const detected = detectTheme();
      if (detected && !baseColor) {
        return THEME_STYLES[detected].palette.slice(0, count);
      }
      
      // 从 DOM 读取基础颜色
      const colors = readThemeColors();
      const base = baseColor || colors['--accent'] || colors['--primary'] || '#6366f1';
      
      // 根据风格生成调色板
      switch (style) {
        case 'monochrome':
          return generateMonochromePalette(base, count);
        case 'analogous':
          return generateAnalogousPalette(base, count);
        case 'complementary':
          return generateComplementaryPalette(base).slice(0, count);
        case 'default':
        default:
          // 如果是 CSS 变量，返回变量本身；否则生成调色板
          if (base.includes('var(')) {
            const vars = [
              'var(--accent, #6366f1)',
              'var(--accent2, #ec4899)',
              'var(--chart3, #10b981)',
              'var(--chart4, #f59e0b)',
              'var(--chart5, #3b82f6)',
              'var(--chart6, #ef4444)',
            ];
            return vars.slice(0, count);
          }
          return generatePalette(base, count);
      }
    },

    /**
     * 获取单个颜色（带智能回退）
     * @param {number} index - 颜色索引
     * @param {Object} options - 配置选项
     * @returns {string} 颜色值
     */
    getColor(index, options = {}) {
      const palette = this.getPalette(options);
      return palette[index % palette.length];
    },

    /**
     * 读取当前 DOM 中的所有颜色变量
     */
    readThemeColors,

    /**
     * 检测当前主题
     */
    detectTheme,

    /**
     * 解析 CSS 变量或颜色值
     */
    resolveColor,

    /**
     * 更新图表引擎的默认调色板
     * @param {string[]} palette - 新的调色板
     */
    updateChartsPalette(palette) {
      if (typeof SlideCharts !== 'undefined' && SlideCharts.PALETTE) {
        SlideCharts.PALETTE = palette;
        return true;
      }
      return false;
    },

    /**
     * 自动应用主题到所有图表
     * @param {Object} options - 配置选项
     */
    applyToCharts(options = {}) {
      const palette = this.getPalette(options);
      this.updateChartsPalette(palette);
      return palette;
    },

    // 主题常量
    THEMES: THEME_STYLES,
  };
})();

// ── 自动初始化（可选）────────────────────────────────────────────
// 在页面加载完成后自动检测主题并应用到图表
document.addEventListener('DOMContentLoaded', () => {
  SlideChartsTheme.applyToCharts();
});
