#!/usr/bin/env python3
"""
create_package.py - Simple package creator for frontend-presentation-slides

Creates a tar.gz package without requiring bash or special permissions.
"""

import os
import tarfile
from pathlib import Path
from datetime import datetime

def main():
    print("📦 Creating Frontend Presentation Slides package...")
    
    # Configuration
    package_name = "frontend-presentation-slides"
    version = "1.0.0"
    output_dir = Path("dist")
    output_file = output_dir / f"{package_name}-v{version}.tar.gz"
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Files to include
    include_patterns = [
        "SKILL.md",
        "README.md",
        "README.zh.md",
        "INSTALL.md",
        "QUICKSTART.md",
        "RELEASE_CHECKLIST.md",
        "RELEASE_SUMMARY.md",
        "CHANGELOG.md",
        "requirements.txt",
        "setup.html",
        "marketplace.json",
        ".codebuddy-plugin/",
        "scripts/",
        "assets/",
        "references/",
    ]
    
    # Files to exclude
    exclude_patterns = [
        ".git",
        "__pycache__",
        "*.pyc",
        ".DS_Store",
        ".claude-design",
        "dist",
        "presentation*.html",
        "*.pptx",
        "images/",
    ]
    
    # Create temporary directory
    temp_dir = output_dir / package_name
    if temp_dir.exists():
        import shutil
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files
    print("  Copying files...")
    copied_count = 0
    
    def should_include(path):
        """Check if path should be included."""
        path_str = str(path)
        
        # Check exclude patterns
        for pattern in exclude_patterns:
            if pattern in path_str or path.name.startswith(pattern):
                return False
        
        # Check include patterns
        for pattern in include_patterns:
            if path_str.startswith(pattern) or path.name.startswith(pattern):
                return True
        
        return False
    
    # Walk through source directory
    src_dir = Path(".")
    for item in src_dir.rglob("*"):
        if item.is_file() and should_include(item):
            # Create destination path
            rel_path = item.relative_to(src_dir)
            dest_path = temp_dir / rel_path
            
            # Create directory if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            import shutil
            shutil.copy2(item, dest_path)
            copied_count += 1
    
    print(f"  ✓ Copied {copied_count} files")
    
    # Create tar.gz archive
    print("  Creating archive...")
    with tarfile.open(output_file, "w:gz") as tar:
        tar.add(temp_dir, arcname=package_name)
    
    # Get file size
    file_size = output_file.stat().st_size
    size_mb = file_size / (1024 * 1024)
    
    # Cleanup temp directory
    import shutil
    shutil.rmtree(temp_dir)
    
    print(f"\n✓ Package created: {output_file}")
    print(f"  Size: {size_mb:.2f} MB ({file_size:,} bytes)")
    print(f"\nInstallation:")
    print(f"  tar -xzf {output_file.name}")
    print(f"  cd {package_name}")
    print(f"  pip3 install -r requirements.txt")
    
    return 0

if __name__ == "__main__":
    try:
        exit(main())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
