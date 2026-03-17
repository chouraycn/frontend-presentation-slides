# Installation Guide

## Quick Install

```bash
# 1. Clone or download this skill
cd ~/.codebuddy/skills/
git clone https://github.com/chouray/frontend-presentation-slides

# 2. Install Python dependencies
cd frontend-presentation-slides
pip3 install -r requirements.txt
```

## Optional Dependencies

The skill works with core dependencies, but some features require optional packages:

```bash
# For PDF export (headless Chrome)
pip3 install playwright
playwright install chromium

# OR using Puppeteer
pip3 install pyppeteer

# For offline font inlining (Google Fonts download)
pip3 install requests

# For AI-powered topic expansion (--expand mode)
pip3 install anthropic  # Anthropic Claude
# OR
pip3 install openai     # OpenAI GPT
```

## Minimum Requirements

- Python 3.8+
- pip3

## Testing Your Installation

```bash
# Test the core generator
python3 scripts/generate_slides.py --help

# Test PPTX extraction (requires a .pptx file)
python3 scripts/extract_pptx.py --help

# Open the visual gallery
open assets/index.html
```

## Troubleshooting

**"Module not found" errors**
```bash
# Reinstall dependencies
pip3 install -r requirements.txt --upgrade
```

**"Permission denied" on scripts**
```bash
# Make Python scripts executable (Unix/Linux/macOS)
chmod +x scripts/*.py
```

**PDF export fails**
```bash
# Install Chromium for Playwright
playwright install chromium
```

## Next Steps

- Open `setup.html` in a browser for a visual setup wizard
- Read `SKILL.md` for detailed usage instructions
- Browse `assets/templates/` for 8 ready-to-use templates
