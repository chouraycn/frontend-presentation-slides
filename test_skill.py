#!/usr/bin/env python3
"""
test_skill.py — Comprehensive test suite for frontend-presentation-slides skill
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# Colors for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[0;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

def print_header(msg):
    print(f"\n{BLUE}{'='*60}{NC}")
    print(f"{BLUE}{msg}{NC}")
    print(f"{BLUE}{'='*60}{NC}\n")

def print_success(msg):
    print(f"{GREEN}✓{NC} {msg}")

def print_error(msg):
    print(f"{RED}✗{NC} {msg}")

def print_warning(msg):
    print(f"{YELLOW}⚠{NC} {msg}")

def check_file_exists(filepath, required=True):
    """Check if a file exists."""
    path = Path(filepath)
    if path.exists():
        print_success(f"File exists: {filepath}")
        return True
    else:
        if required:
            print_error(f"Missing required file: {filepath}")
        else:
            print_warning(f"Optional file missing: {filepath}")
        return not required

def check_python_syntax(filepath):
    """Check Python file syntax."""
    try:
        result = subprocess.run(
            ['python3', '-m', 'py_compile', filepath],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print_success(f"Python syntax OK: {filepath}")
            return True
        else:
            print_error(f"Python syntax error in {filepath}")
            print(f"  Error: {result.stderr}")
            return False
    except Exception as e:
        print_error(f"Failed to check {filepath}: {e}")
        return False

def check_json_valid(filepath):
    """Check if JSON file is valid."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json.load(f)
        print_success(f"Valid JSON: {filepath}")
        return True
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON in {filepath}: {e}")
        return False
    except Exception as e:
        print_error(f"Failed to read {filepath}: {e}")
        return False

def count_files(directory, pattern, expected=None):
    """Count files matching pattern."""
    path = Path(directory)
    files = list(path.glob(pattern))
    count = len(files)
    
    if expected:
        if count == expected:
            print_success(f"Found {count}/{expected} {pattern} files in {directory}")
            return True
        else:
            print_error(f"Expected {expected} {pattern} files, found {count} in {directory}")
            return False
    else:
        print_success(f"Found {count} {pattern} files in {directory}")
        return True

def run_script_help(script_path):
    """Test if a script can run --help."""
    try:
        result = subprocess.run(
            ['python3', script_path, '--help'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and 'usage:' in result.stdout.lower():
            print_success(f"Script runs: {script_path}")
            return True
        else:
            print_error(f"Script failed: {script_path}")
            return False
    except Exception as e:
        print_error(f"Cannot run {script_path}: {e}")
        return False

def main():
    """Run all tests."""
    print_header("Frontend Presentation Slides - Skill Test Suite")

    # Test counters
    total_tests = 0
    passed_tests = 0

    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Test 1: Required files
    print_header("Test 1: Required Files")
    required_files = [
        'SKILL.md',
        'README.md',
        'INSTALL.md',
        'requirements.txt',
        'setup.html',
        '.codebuddy-plugin/plugin.json',
        'marketplace.json',
    ]
    total_tests += len(required_files)
    for f in required_files:
        if check_file_exists(f, required=True):
            passed_tests += 1

    # Test 2: Python scripts syntax
    print_header("Test 2: Python Scripts Syntax")
    python_scripts = [
        'scripts/generate_slides.py',
        'scripts/extract_pptx.py',
        'scripts/export_pdf.py',
        'scripts/export_pptx.py',
        'scripts/export_video.py',
        'scripts/inline_fonts.py',
        'scripts/embed_images.py',
        'scripts/parse_html.py',
        'scripts/apply_comments.py',
        'scripts/audit_deck.py',
    ]
    total_tests += len(python_scripts)
    for script in python_scripts:
        if check_file_exists(script):
            if check_python_syntax(script):
                passed_tests += 1

    # Test 3: Template files
    print_header("Test 3: Template Files (8 required)")
    total_tests += 1
    if count_files('assets/templates', '*.html', 8):
        passed_tests += 1

    # Test 4: Style preview files
    print_header("Test 4: Style Preview Files (8 required)")
    total_tests += 1
    if count_files('assets/style-previews', '*.html', 8):
        passed_tests += 1

    # Test 5: JSON config files
    print_header("Test 5: JSON Config Files")
    json_files = [
        '.codebuddy-plugin/plugin.json',
        'marketplace.json',
    ]
    total_tests += len(json_files)
    for f in json_files:
        if check_json_valid(f):
            passed_tests += 1

    # Test 6: Template JSON metadata
    print_header("Test 6: Template JSON Metadata (8 required)")
    total_tests += 1
    if count_files('assets/templates', '*.json', 8):
        passed_tests += 1

    # Test 7: JavaScript files
    print_header("Test 7: JavaScript Utility Files")
    js_files = [
        'scripts/charts.js',
        'scripts/interactive.js',
    ]
    total_tests += len(js_files)
    for f in js_files:
        if check_file_exists(f):
            passed_tests += 1

    # Test 8: Demo files
    print_header("Test 8: Demo Files")
    total_tests += 1
    demo_count = len(list(Path('assets/demos').glob('*.html')))
    if demo_count > 0:
        print_success(f"Found {demo_count} demo files")
        passed_tests += 1
    else:
        print_warning("No demo files found (optional)")

    # Test 9: Scripts functionality
    print_header("Test 9: Script Functionality (--help test)")
    test_scripts = [
        'scripts/generate_slides.py',
        'scripts/extract_pptx.py',
    ]
    for script in test_scripts:
        if Path(script).exists():
            total_tests += 1
            if run_script_help(script):
                passed_tests += 1

    # Test 10: SKILL.md completeness
    print_header("Test 10: SKILL.md Content Check")
    total_tests += 1
    try:
        with open('SKILL.md', 'r', encoding='utf-8') as f:
            content = f.read()
            required_sections = [
                'Phase 0:',
                'Phase 1:',
                'Phase 2:',
                'Phase 3:',
                'Phase 4:',
                'template-pitch-deck',
                'template-tech-talk',
            ]
            missing = [s for s in required_sections if s not in content]
            if not missing:
                print_success("SKILL.md contains all required sections")
                passed_tests += 1
            else:
                print_error(f"SKILL.md missing sections: {missing}")
    except Exception as e:
        print_error(f"Failed to check SKILL.md: {e}")

    # Summary
    print_header("Test Summary")
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total tests:  {total_tests}")
    print(f"Passed:       {passed_tests}")
    print(f"Failed:       {total_tests - passed_tests}")
    print(f"Success rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print(f"\n{GREEN}✓ Skill is ready for packaging!{NC}")
        return 0
    elif success_rate >= 70:
        print(f"\n{YELLOW}⚠ Skill has minor issues, review above warnings.{NC}")
        return 0
    else:
        print(f"\n{RED}✗ Skill has critical issues, fix before packaging.{NC}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
