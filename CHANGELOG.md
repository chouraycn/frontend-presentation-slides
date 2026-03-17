# Changelog

All notable changes to Frontend Presentation Slides will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-03-17

### Added
- Initial stable release
- **Core Engine**: Zero-dependency HTML presentation generator
- **Templates**: 8 professional templates
  - Dark Elegance (Pitch Deck)
  - Vibrant Energy (Tech Talk)
  - Clean Minimal (Quarterly Report)
  - Claude Warmth (Brand Story)
  - Warm Inspire (Product Launch)
  - ForAI White (Design Portfolio)
  - Pash Orange (Agency Pitch)
  - Hhart Red Power (Creative Studio)
- **PPTX Import**: Full PPT/PPTX to HTML conversion pipeline
- **PPTX Export**: HTML to editable PowerPoint export
- **Chart Engine**: Zero-dependency SVG chart library with 9 chart types
  - Bar chart, Line chart, Area chart, Donut chart
  - Horizontal bar, Progress bars, Radar chart, Sankey diagram
- **Interactive Modules**: Real-time audience engagement
  - Live polls with vote tally
  - Multiple-choice quizzes with answer reveal
  - Word clouds (static preset + live input)
  - Countdown/stopwatch timers
  - Star/emoji ratings
  - QR code generation
- **Presenter Mode**: Two-window synchronization
  - Current slide preview
  - Next slide preview
  - Speaker notes panel
  - Elapsed time counter
  - Navigation controls
  - Laser pointer
  - Blackout screen
- **Export Options**:
  - PDF export (Playwright, Puppeteer, WeasyPrint)
  - PPTX export (round-trip)
  - MP4 video export (FFmpeg)
- **Offline Support**:
  - Font inlining (Google Fonts to Base64)
  - Image embedding (Base64 data URIs)
- **Content Quality**: AI-powered audit tool
  - Text density analysis
  - Data gap detection
  - Title variety check
  - Readability scoring
  - Narrative flow analysis
- **Collaboration**: Review comments workflow
  - JSON-based comment format
  - Support for 5 actions: replace, insert, delete, highlight, note
  - Dry-run preview mode
  - Automatic backup creation
- **Navigation**:
  - Keyboard (arrows, space, home, end)
  - Touch/swipe support
  - Mouse wheel (debounced)
  - Progress bar
  - Navigation dots
- **View Transitions API**: Cinematic slide-to-slide transitions
- **Accessibility**:
  - Semantic HTML
  - ARIA labels
  - Reduced motion support
  - Keyboard navigation
  - Screen reader friendly

### Scripts Included
- `generate_slides.py` - Core AI → HTML generator
- `extract_pptx.py` - PPTX content extraction (v2)
- `export_pdf.py` - PDF export with multiple backends
- `export_pptx.py` - HTML → PPTX round-trip export
- `export_video.py` - HTML → MP4 video export
- `inline_fonts.py` - Google Fonts inlining
- `embed_images.py` - Image embedding (Base64)
- `parse_html.py` - HTML → JSON reverse-edit
- `apply_comments.py` - Review comments application
- `audit_deck.py` - Content quality audit
- `charts.js` - Zero-dependency SVG chart engine
- `interactive.js` - Interactive slide modules
- `patch_templates.py` - Template utilities

### Documentation
- SKILL.md (924 lines) - Complete workflow guide
- README.md - Project overview and features
- README.zh.md - Chinese documentation
- INSTALL.md - Installation instructions
- QUICKSTART.md - 5-minute setup guide
- RELEASE_CHECKLIST.md - Release verification
- RELEASE_SUMMARY.md - Release summary
- references/style-guide.md - Design patterns and best practices
- references/troubleshooting.md - Common issues and solutions

### Visual Assets
- 8 template HTML files (fully functional presentations)
- 8 template JSON files (metadata and configuration)
- 8 style preview HTML files (single-slide demos)
- 3 demo HTML files (charts, presenter mode, all features)
- Interactive visual gallery (assets/index.html)

### Dependencies
- **Core**:
  - python-pptx >= 0.6.21
  - Pillow >= 9.0.0
  - beautifulsoup4 >= 4.11.0
- **Optional**:
  - playwright >= 1.30.0 (PDF export)
  - pyppeteer >= 1.0.2 (PDF export)
  - requests >= 2.28.0 (font inlining)
  - anthropic >= 0.18.0 (LLM expansion)
  - openai >= 1.0.0 (LLM expansion)

### Quality
- 28/28 tests passed (100% success rate)
- All Python scripts compile without errors
- All JSON files valid
- Complete documentation coverage
- No known critical bugs

### Browser Support
- Chrome/Edge: 111+ (full feature support)
- Safari: 18+ (full feature support)
- Firefox: All modern versions (graceful fallback)

### File Format Support
- **Input**: PPT, PPTX, JSON outline
- **Output**: HTML, PDF, PPTX, MP4

## [Unreleased]

### Planned (Future Versions)
- [ ] WebP image support
- [ ] Additional slide transition animations
- [ ] Template customization UI
- [ ] Real-time collaboration features
- [ ] Export to Google Slides
- [ ] Export to Canva
- [ ] AI-powered slide suggestions
- [ ] Automatic layout optimization

---

[1.0.0]: https://github.com/chouray/frontend-presentation-slides/releases/tag/v1.0.0
