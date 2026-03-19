# 前端演示文稿幻灯片

> 一个 WorkBuddy / CodeBuddy 技能插件，用于创建**零依赖、动画丰富的 HTML 演示文稿** — 完全在浏览器中运行，无需 npm，无需构建工具。

---

## 功能概览

- **从零创建** — 描述你的主题，生成一份完整的 HTML 动效演示文稿
- **PPT/PPTX 转换** — 上传 PowerPoint 文件，获得像素级还原的网页版
- **8 套精心设计的模板** — 通过视觉风格选择，而非抽象文字描述
- **智能模板匹配** — 根据内容与配色信号自动选择最合适的模板
- **全屏导航** — 方向键、滚动、触摸滑动
- **PDF 导出** — 通过 Puppeteer 或浏览器打印一键导出

---

## 模板一览

| 风格名称 | 最适用场景 | 核心配色 |
|---|---|---|
| **Dark Elegance（暗夜典雅）** | 投资人路演、募资演讲、奢侈品牌 | 深海军蓝 `#0d0d1a` + 金色 `#c9a84c` |
| **Vibrant Energy（活力能量）** | 技术分享、大会演讲、AI 创业公司 | 深紫 `#0a0014` + 紫罗兰 `#7c3aed` + 粉红 `#ec4899` |
| **Clean Minimal（简洁极简）** | 业务季报、OKR 汇报、内部演示 | 暖白 `#fafaf8` + 蓝色 `#2563eb` |
| **Claude Warmth（温暖叙述）** | 品牌故事、文化演讲、温情叙事 | 奶油色 `#F6F0E8` + 赤陶红 `#DA7756` |
| **Warm Inspire（暖色发布）** | 产品发布、功能揭晓、戏剧性亮相 | 深琥珀 `#110800` + 金色 `#f59e0b` |
| **ForAI White（纯白编辑）** | 设计作品集、创意机构提案、极简编辑风 | 纯白 `#ffffff` + 墨色 `#0a0a0a` |
| **Pash Orange（橙色机构）** | 创意机构/工作室提案、橙色品牌 | 白色 `#FFFFFF` + 纯橙 `#FF5C00` |
| **Hhart Red Power（红色力量）** | 创意工作室、红色品牌、摄影类演示 | 近黑 `#0a0a0a` + 深红 `#C8102E` |

在本地打开 `assets/index.html` 可视化浏览所有模板。

---

## 安装方式

在 WorkBuddy / CodeBuddy 中，直接从应用市场安装此技能，或手动添加：

```bash
# 方式 A：从市场安装（搜索 "frontend-presentation-slides"）

# 方式 B：克隆仓库到技能目录
git clone https://github.com/chouraycn/frontend-presentation-slides \
  ~/.codebuddy/skills/frontend-presentation-slides
```

---

## 使用方法

用自然语言描述需求即可，技能会自动识别模式：

```
帮我做一个 10 页的 B2B SaaS 投资人 Pitch Deck
```
```
把我上传的 keynote.pptx 转换成网页版演示文稿
```
```
用 Vibrant Energy 模板做一个技术分享，主题：Rust 入门
```
```
使用橙色配色做一个品牌故事演示文稿
```

### 触发词

`制作幻灯片` · `创建演示文稿` · `做PPT` · `生成slides` · `PPT转HTML` · `pitch deck` · `网页版幻灯片` · `投资人演讲` · `融资路演` · `技术分享` · `季度报告` · `产品发布`

---

## 目录结构

```
frontend-presentation-slides/
├── SKILL.md                          # 技能定义（WorkBuddy 入口点）
├── .codebuddy-plugin/
│   └── plugin.json                   # 应用市场插件清单
├── assets/
│   ├── index.html                    # 可视化模板展示库
│   ├── templates/                    # 8 套即用 HTML 模板
│   │   ├── template-pitch-deck.html
│   │   ├── template-tech-talk.html
│   │   ├── template-quarterly-report.html
│   │   ├── template-claude-warmth.html
│   │   ├── template-product-launch.html
│   │   ├── template-forai-white.html
│   │   ├── template-pash-orange.html
│   │   └── template-hhart-red.html
│   ├── style-previews/               # 单页风格预览
│   └── demos/                        # 功能演示（图表）
├── scripts/
│   ├── generate_slides.py            # 核心 AI → HTML 生成器
│   ├── extract_pptx.py               # PPTX → 幻灯片 JSON 提取器
│   ├── export_pdf.py                 # HTML → PDF（via Puppeteer/Playwright）
│   ├── export_pptx.py                # HTML → PPTX 反向导出
│   ├── export_video.py               # HTML → MP4 视频导出
│   ├── inline_fonts.py               # 内联 Web 字体（支持离线）
│   ├── embed_images.py               # 外部图片转 base64 内嵌
│   ├── parse_html.py                 # 解析已有 HTML 幻灯片 → JSON
│   ├── apply_comments.py             # 应用审阅批注到幻灯片
│   ├── audit_deck.py                 # 内容质量审计工具
│   ├── charts.js                     # 零依赖 SVG 图表引擎
│   └── interactive.js                # 零依赖交互组件
└── references/                       # 设计规范与故障排查文档
```

---

## 脚本参考

| 脚本 | 用途 | 环境要求 |
|---|---|---|
| `scripts/generate_slides.py` | AI 结构化 JSON → HTML 幻灯片 | Python 3.10+ |
| `scripts/extract_pptx.py` | 解析 .pptx，输出结构化幻灯片数据 | `python-pptx` |
| `scripts/export_pdf.py` | 无头 Chrome PDF 导出 | `pyppeteer` 或 `playwright` |
| `scripts/export_pptx.py` | HTML 幻灯片反向转 .pptx | `python-pptx` |
| `scripts/export_video.py` | HTML 幻灯片导出为 MP4 视频 | `playwright`、`ffmpeg` |
| `scripts/inline_fonts.py` | 内联 Google Fonts，支持离线 HTML | Python 3.10+ |
| `scripts/embed_images.py` | 外部图片内嵌为 base64 数据 URI | Python 3.10+ |
| `scripts/parse_html.py` | 已有 HTML 幻灯片解析回 JSON | Python 3.10+ |
| `scripts/apply_comments.py` | 应用替换/插入/删除/高亮/备注审阅操作 | Python 3.10+ |
| `scripts/audit_deck.py` | 内容质量审计（文字长度、对比度、重复检测） | Python 3.10+ |
| `scripts/charts.js` | 零依赖 SVG 图表引擎（9 种图表类型） | Node.js 16+ |
| `scripts/interactive.js` | 零依赖交互组件（投票、问答、词云等） | Node.js 16+ |

---

## 核心设计理念

1. **零依赖** — 每份输出均为单个 `.html` 文件，CSS 与 JS 全部内联
2. **所见即所得** — 风格预览让用户直接选视觉效果，无需靠文字描述抽象风格
3. **独特设计** — 告别"AI 审美"，每套模板都像手工打造
4. **生产级质量** — 代码注释完善、无障碍可访问、性能优化到位

---

## 智能模板检测

技能内置 `detect_template` 引擎，通过以下维度对 8 套模板打分：

- **关键词信号** — 主题专属词汇（金融术语、技术栈、设计语言……）
- **结构信号** — 幻灯片类型、图表数量、是否含 CTA
- **配色信号** — 显式颜色字段（`palette`、`bg_color`、`accent_color`）及 hex/rgb 值被解析后映射至最接近的模板色彩标识

---

## 配色主题化（`template-quarterly-report`）

季报模板支持一键换色主题：只需修改 `:root` 中的 `--cover-bg`，再同步更新 `--glow-*` 系列变量，即可将封面、Slide 2、Slide 4 的背景色与光晕动效一起切换：

```css
:root {
  --cover-bg:   #1458ea;   /* ← 改这里即可切换主题色 */

  /* 以下变量与 --cover-bg 对应，同步更新 */
  --glow-core:   rgba(20, 88, 234, 0.90);
  --glow-mid:    rgba(20, 88, 234, 0.45);
  --glow-outer:  rgba(20, 88, 234, 0.40);
  --glow-bright: rgba(120,160,255, 0.55);
  --glow-sheen:  rgba(200,220,255, 0.60);
}
```

---

## 开源许可

MIT © chouray
