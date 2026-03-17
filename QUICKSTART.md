# Frontend Presentation Slides - Quick Start

> **What it does**: Create stunning, zero-dependency HTML presentations from scratch, from PPT/PPTX, or using 8 professional templates.

## 🚀 5-Minute Setup

```bash
# 1. Install dependencies
pip3 install python-pptx Pillow beautifulsoup4

# 2. Create your first presentation
python3 scripts/generate_slides.py --expand "My amazing topic" --slides 10 --output my_deck.html

# 3. Open in browser
open my_deck.html
```

That's it! No npm, no build tools, no fuss.

## 🎨 Choose Your Style

| Template | Best For | Preview |
|----------|----------|---------|
| **Dark Elegance** | Investor pitches, fundraising | Deep navy + gold |
| **Vibrant Energy** | Tech talks, conferences | Purple + pink |
| **Clean Minimal** | Business reviews, OKRs | White + blue |
| **Claude Warmth** | Brand stories, culture | Cream + terracotta |
| **Warm Inspire** | Product launches | Dark amber + orange |
| **ForAI White** | Design portfolios | Pure white + ink |
| **Pash Orange** | Agency pitches | White + orange |
| **Hhart Red** | Creative studios | Near-black + crimson |

**See all templates visually**: Open `assets/index.html` in your browser

## 📋 Common Commands

### From a topic description
```bash
python3 scripts/generate_slides.py --expand "Topic" --slides 12 --template tech-talk --output deck.html
```

### From PPT/PPTX
```bash
# Extract
python3 scripts/extract_pptx.py presentation.pptx --output extracted/

# Convert to HTML
python3 scripts/generate_slides.py extracted/slides.json --template pitch-deck --output deck.html
```

### Export options
```bash
# To PDF
python3 scripts/export_pdf.py deck.html --open

# To PPTX
python3 scripts/export_pptx.py deck.html --open

# To MP4 video
python3 scripts/export_video.py deck.html --duration 5 --open
```

### Offline-ready
```bash
# Embed all images
python3 scripts/embed_images.py deck.html

# Inline fonts
python3 scripts/inline_fonts.py deck.html --output deck-offline.html
```

## 🎯 Key Features

✨ **Zero dependencies** - Single HTML file with inline CSS/JS
🎭 **8 handcrafted templates** - Professional, not "AI aesthetic"
📊 **9 chart types** - Bar, line, area, donut, radar, sankey, etc.
🎤 **Presenter mode** - Press `[P]` for speaker notes + timer
🔄 **Two-way conversion** - PPT ↔ HTML
📱 **Mobile responsive** - Works on any device
🎬 **Export anywhere** - PDF, PPTX, MP4
💬 **Interactive modules** - Polls, quizzes, word clouds, timers
🔍 **Content audit** - Auto-check for quality issues

## 🎮 Keyboard Shortcuts

While presenting:
- `← →` or `↑ ↓` - Navigate slides
- `Space` / `Shift+Space` - Next/previous
- `[P]` - Open presenter view
- `[F]` - Fullscreen
- `[B]` - Blackout screen
- `[L]` - Laser pointer mode

## 📚 Documentation

- **Full guide**: `SKILL.md` (detailed workflow)
- **Install help**: `INSTALL.md`
- **Design patterns**: `references/style-guide.md`
- **Troubleshooting**: `references/troubleshooting.md`

## 🎯 When to Use This

✅ **Perfect for**:
- Quick presentations from a topic
- Converting PPT to web format
- Creating mobile-friendly decks
- Presentations with charts/data
- Offline presentations (conference no-wifi)

❌ **Not ideal for**:
- Highly branded corporate decks (use templates as base)
- Very complex animations (keep it simple)
- Real-time data dashboards (use web frameworks instead)

## 💡 Pro Tips

1. **Start with a template** - It's faster than from scratch
2. **Use the visual gallery** - `assets/index.html` lets you see before choosing
3. **Test offline** - Run `inline_fonts.py` + `embed_images.py` for no-wifi venues
4. **Presenter mode is your friend** - `[P]` shows notes, timer, and next slide
5. **Export before presenting** - PDF/PPTX backup never hurts

## 🆘 Need Help?

1. Check `references/troubleshooting.md`
2. Run `python3 test_skill.py` to verify installation
3. Open `setup.html` for a visual walkthrough

## 📦 File Structure

```
frontend-presentation-slides/
├── SKILL.md              # Complete usage guide
├── scripts/              # All utility scripts
├── assets/
│   ├── templates/        # 8 ready-to-use templates
│   ├── style-previews/   # Visual previews
│   └── demos/            # Feature demos
└── references/           # Design guides
```

---

**Made with ❤️ by chouray**
**License**: MIT
**Repository**: https://github.com/chouray/frontend-presentation-slides
