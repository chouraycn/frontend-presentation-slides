#!/bin/bash
# Package script for frontend-presentation-slides skill

set -e  # Exit on error

echo "📦 Packaging Frontend Presentation Slides..."

# Configuration
PACKAGE_NAME="frontend-presentation-slides"
VERSION="1.0.0"
OUTPUT_DIR="dist"
PACKAGE_FILE="${OUTPUT_DIR}/${PACKAGE_NAME}-v${VERSION}.tar.gz"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Clean previous builds
echo -e "${BLUE}Step 1: Cleaning previous builds...${NC}"
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# Step 2: Verify file structure
echo -e "${BLUE}Step 2: Verifying file structure...${NC}"
required_files=(
    "SKILL.md"
    "README.md"
    "INSTALL.md"
    "requirements.txt"
    "setup.html"
    ".codebuddy-plugin/plugin.json"
    "scripts/generate_slides.py"
    "scripts/extract_pptx.py"
    "scripts/charts.js"
    "scripts/interactive.js"
    "assets/index.html"
    "assets/templates/template-pitch-deck.html"
    "assets/templates/template-tech-talk.html"
    "assets/templates/template-quarterly-report.html"
    "assets/templates/template-claude-warmth.html"
    "assets/templates/template-product-launch.html"
    "assets/templates/template-forai-white.html"
    "assets/templates/template-pash-orange.html"
    "assets/templates/template-hhart-red.html"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo -e "\033[0;31m❌ Missing required files:${NC}"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    exit 1
fi
echo -e "${GREEN}✓ All required files present${NC}"

# Step 3: Check Python scripts syntax
echo -e "${BLUE}Step 3: Validating Python scripts...${NC}"
for script in scripts/*.py; do
    if python3 -m py_compile "$script" 2>/dev/null; then
        echo "  ✓ $(basename $script)"
    else
        echo -e "\033[0;31m  ✗ $(basename $script) has syntax errors${NC}"
        exit 1
    fi
done

# Step 4: Count assets
echo -e "${BLUE}Step 4: Counting assets...${NC}"
template_count=$(ls -1 assets/templates/*.html 2>/dev/null | wc -l)
preview_count=$(ls -1 assets/style-previews/*.html 2>/dev/null | wc -l)
demo_count=$(ls -1 assets/demos/*.html 2>/dev/null | wc -l)
script_count=$(ls -1 scripts/*.py scripts/*.js 2>/dev/null | wc -l)

echo "  Templates: $template_count/8"
echo "  Previews: $preview_count/8"
echo "  Demos: $demo_count"
echo "  Scripts: $script_count"

if [ "$template_count" -lt 8 ]; then
    echo -e "\033[0;31m❌ Missing templates (expected 8, found $template_count)${NC}"
    exit 1
fi

if [ "$preview_count" -lt 8 ]; then
    echo -e "\033[0;31m❌ Missing style previews (expected 8, found $preview_count)${NC}"
    exit 1
fi

# Step 5: Create package
echo -e "${BLUE}Step 5: Creating package...${NC}"

# Create temporary directory for packaging
TEMP_DIR="$OUTPUT_DIR/${PACKAGE_NAME}"
mkdir -p "$TEMP_DIR"

# Copy all necessary files
rsync -av \
    --exclude='.git' \
    --exclude='.DS_Store' \
    --exclude='dist' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.claude-design' \
    --exclude='presentation*.html' \
    --exclude='*.pptx' \
    --exclude='images' \
    . "$TEMP_DIR/"

# Create tar.gz archive
cd "$OUTPUT_DIR"
tar -czf "$PACKAGE_FILE" "$PACKAGE_NAME"
cd ..

# Get file size
FILE_SIZE=$(du -h "$PACKAGE_FILE" | cut -f1)

echo -e "${GREEN}✓ Package created: $PACKAGE_FILE ($FILE_SIZE)${NC}"

# Step 6: Generate checksum
echo -e "${BLUE}Step 6: Generating checksum...${NC}"
if command -v shasum &> /dev/null; then
    CHECKSUM=$(shasum -a 256 "$PACKAGE_FILE" | cut -d' ' -f1)
    echo "$CHECKSUM  $PACKAGE_FILE" > "$OUTPUT_DIR/SHA256SUMS.txt"
    echo -e "${GREEN}✓ Checksum: $CHECKSUM${NC}"
elif command -v sha256sum &> /dev/null; then
    CHECKSUM=$(sha256sum "$PACKAGE_FILE" | cut -d' ' -f1)
    echo "$CHECKSUM  $PACKAGE_FILE" > "$OUTPUT_DIR/SHA256SUMS.txt"
    echo -e "${GREEN}✓ Checksum: $CHECKSUM${NC}"
else
    echo -e "\033[0;33m⚠ Warning: shasum/sha256sum not found, skipping checksum${NC}"
fi

# Step 7: Create installation manifest
echo -e "${BLUE}Step 7: Creating installation manifest...${NC}"
cat > "$OUTPUT_DIR/MANIFEST.txt" << EOF
Frontend Presentation Slides v${VERSION}
========================================

Package Contents:
- SKILL.md: Main skill definition
- scripts/: Python and JavaScript utilities
- assets/templates/: 8 ready-to-use templates
- assets/style-previews/: Visual style previews
- assets/demos/: Feature demonstrations
- requirements.txt: Python dependencies
- INSTALL.md: Installation instructions

Templates Included:
1. Dark Elegance (pitch-deck)
2. Vibrant Energy (tech-talk)
3. Clean Minimal (quarterly-report)
4. Claude Warmth (claude-warmth)
5. Warm Inspire (product-launch)
6. ForAI White (forai-white)
7. Pash Orange (pash-orange)
8. Hhart Red Power (hhart-red)

Installation:
1. Extract: tar -xzf ${PACKAGE_FILE}
2. Install deps: cd ${PACKAGE_NAME} && pip3 install -r requirements.txt
3. Use: Follow instructions in SKILL.md

Created: $(date)
Package: ${PACKAGE_FILE}
Size: ${FILE_SIZE}
EOF

echo -e "${GREEN}✓ Manifest created${NC}"

# Summary
echo -e "\n${GREEN}🎉 Packaging complete!${NC}"
echo ""
echo "Package location: $PACKAGE_FILE"
echo "Size: $FILE_SIZE"
echo ""
echo "Installation:"
echo "  tar -xzf $PACKAGE_FILE"
echo "  cd ${PACKAGE_NAME}"
echo "  pip3 install -r requirements.txt"
echo ""
echo "Files included in package:"
ls -lh "$PACKAGE_FILE"
