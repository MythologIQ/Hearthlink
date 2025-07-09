#!/usr/bin/env python3
"""
Create Hearthlink v1.1.0 Platinum+ Release Package

Packages the complete release with all documentation, source code, and assets.
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_release_package():
    """Create the complete release package."""
    
    # Release configuration
    VERSION = "v1.1.0"
    RELEASE_NAME = f"hearthlink_{VERSION}_platinum_plus_release"
    OUTPUT_DIR = "releases"
    
    print(f"Creating {RELEASE_NAME}.zip...")
    
    # Create output directory
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    
    # Define what to include in the release
    include_patterns = [
        # Source code
        "src/**/*",
        
        # Public documentation
        "docs/public/**/*",
        "README.md",
        "LICENSE.md",
        "SECURITY.md",
        "CODE_OF_CONDUCT.md",
        "SBOM.json",
        
        # Internal documentation (audit trail)
        "docs/internal/**/*",
        
        # Tests
        "tests/**/*",
        
        # Configuration
        "config/**/*",
        "*.py",
        "*.json",
        "*.md",
        "*.txt",
        "*.yml",
        "*.yaml",
        
        # Assets (if they exist)
        "assets/**/*",
        "public/**/*",
        
        # Voice/TTS assets (if they exist)
        "voice/**/*",
        "tts/**/*",
        "audio/**/*",
        
        # Examples
        "examples/**/*",
        
        # Scripts
        "scripts/**/*",
        "*.sh",
        "*.bat",
        "*.ps1"
    ]
    
    # Define what to exclude
    exclude_patterns = [
        "**/__pycache__/**",
        "**/*.pyc",
        "**/.git/**",
        "**/.gitignore",
        "**/node_modules/**",
        "**/.env",
        "**/.DS_Store",
        "**/Thumbs.db",
        "**/*.log",
        "**/releases/**",
        "**/.vscode/**",
        "**/.idea/**",
        "**/dist/**",
        "**/build/**",
        "**/coverage/**",
        "**/.pytest_cache/**"
    ]
    
    # Create the zip file
    zip_path = Path(OUTPUT_DIR) / f"{RELEASE_NAME}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add files based on patterns
        for pattern in include_patterns:
            for file_path in Path('.').glob(pattern):
                if file_path.is_file():
                    # Check if file should be excluded
                    should_exclude = False
                    for exclude_pattern in exclude_patterns:
                        if file_path.match(exclude_pattern):
                            should_exclude = True
                            break
                    
                    if not should_exclude:
                        # Add file to zip
                        arcname = str(file_path)
                        zipf.write(file_path, arcname)
                        print(f"  Added: {arcname}")
    
    # Create release manifest
    manifest_content = f"""Hearthlink {VERSION} Platinum+ Release
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Contents:
- Full source code (src/)
- Public documentation (docs/public/)
- Internal documentation/audit trail (docs/internal/)
- Tests (tests/)
- Configuration files
- Voice/TTS assets (if present)
- SBOM and security documentation
- README, LICENSE, etc.

Voice Commands Implemented:
- "Open user guide" - Access help documentation
- "Next week" / "Previous week" - Navigate dashboard
- "Add priority [text]" - Add priority items
- "Complete task [text]" - Log completions
- "Update self care [category] [day]" - Track self-care

Accessibility Features:
- WCAG 2.1 AA compliant
- Screen reader support
- Keyboard navigation
- Voice-first design
- High contrast mode support

Release Notes:
- Complete voice command implementation
- Comprehensive help system
- Enhanced accessibility features
- Full documentation suite
- Enterprise-grade security features
"""
    
    # Add manifest to zip
    with zipfile.ZipFile(zip_path, 'a', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr("RELEASE_MANIFEST.txt", manifest_content)
        print(f"  Added: RELEASE_MANIFEST.txt")
    
    print(f"\n✅ Release package created: {zip_path}")
    print(f"📦 Package size: {zip_path.stat().st_size / (1024*1024):.1f} MB")
    
    return zip_path

def verify_package_contents(zip_path):
    """Verify the package contains expected files."""
    print(f"\nVerifying package contents...")
    
    expected_files = [
        "README.md",
        "LICENSE.md",
        "SECURITY.md",
        "SBOM.json",
        "src/",
        "docs/public/",
        "docs/internal/",
        "tests/",
        "RELEASE_MANIFEST.txt"
    ]
    
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        file_list = zipf.namelist()
        
        missing_files = []
        for expected in expected_files:
            if not any(f.startswith(expected) for f in file_list):
                missing_files.append(expected)
        
        if missing_files:
            print(f"⚠️  Missing files: {missing_files}")
            return False
        else:
            print("✅ All expected files present")
            return True

if __name__ == "__main__":
    try:
        # Create the release package
        zip_path = create_release_package()
        
        # Verify contents
        if verify_package_contents(zip_path):
            print(f"\n🎉 Release package ready: {zip_path}")
            print("Ready for distribution!")
        else:
            print(f"\n⚠️  Package created but some files may be missing")
            
    except Exception as e:
        print(f"❌ Error creating release package: {e}")
        exit(1) 