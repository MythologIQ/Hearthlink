#!/usr/bin/env python3
"""
SPEC-3 Week 3: Simple Alpha Package Creator
Creates a portable alpha package with checksums and documentation
"""

import os
import json
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

def create_alpha_package():
    """Create a portable alpha package"""
    project_root = Path(__file__).parent.parent
    alpha_date = datetime.now().strftime("%Y%m%d")
    dist_dir = project_root / "dist"
    alpha_dir = dist_dir / f"alpha_{alpha_date}"
    
    print("🚀 Creating Hearthlink Alpha Package")
    print("=" * 50)
    
    # Create directories
    alpha_dir.mkdir(parents=True, exist_ok=True)
    
    # Files to include in alpha package
    essential_files = [
        "package.json",
        "README.md",
        "CLAUDE.md",
        "electron/main.js",
        "electron/main.ts",
        "electron/bootstrap.js",
        "electron/bootstrap.ts",
        "electron/window.ts",
        "preload/",
        "src/components/",
        "src/api/bug_reporting.py",
        "src/utils/error_wrapper.py",
        "public/",
        "scripts/hl",
        "scripts/bug_cli.py",
        "config/grafana_bug_dashboard.json",
        "TECH_DEBT_REMOVAL_LOG.md",
        "ARCHIVE_MANIFEST.json"
    ]
    
    # Create package structure
    package_dir = alpha_dir / "hearthlink_alpha_portable"
    package_dir.mkdir(exist_ok=True)
    
    print("📦 Packaging essential files...")
    
    packaged_files = []
    total_size = 0
    
    for file_pattern in essential_files:
        source_path = project_root / file_pattern
        
        if not source_path.exists():
            print(f"⚠️ Skipping missing: {file_pattern}")
            continue
        
        try:
            if source_path.is_file():
                dest_path = package_dir / file_pattern
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                with open(source_path, 'rb') as src, open(dest_path, 'wb') as dst:
                    content = src.read()
                    dst.write(content)
                
                file_size = len(content)
                total_size += file_size
                packaged_files.append({
                    'path': file_pattern,
                    'size': file_size,
                    'type': 'file'
                })
                print(f"✅ Packaged: {file_pattern} ({file_size:,} bytes)")
                
            elif source_path.is_dir():
                dest_path = package_dir / file_pattern
                dest_path.mkdir(parents=True, exist_ok=True)
                
                # Copy directory contents selectively
                dir_size = 0
                for item in source_path.rglob('*'):
                    if item.is_file() and not should_exclude_file(item):
                        rel_path = item.relative_to(source_path)
                        target_file = dest_path / rel_path
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(item, 'rb') as src, open(target_file, 'wb') as dst:
                            content = src.read()
                            dst.write(content)
                        
                        dir_size += len(content)
                
                total_size += dir_size
                packaged_files.append({
                    'path': file_pattern,
                    'size': dir_size,
                    'type': 'directory'
                })
                print(f"✅ Packaged: {file_pattern}/ ({dir_size:,} bytes)")
                
        except Exception as e:
            print(f"❌ Failed to package {file_pattern}: {e}")
    
    # Create launcher scripts
    print("🚀 Creating launcher scripts...")
    
    # Windows launcher
    windows_launcher = package_dir / "HearthlinkAlpha.bat"
    with open(windows_launcher, 'w') as f:
        f.write("""@echo off
title Hearthlink Alpha
echo ========================================
echo    Hearthlink Alpha Version
echo ========================================
echo.
echo Starting Hearthlink...
echo.
cd /d "%~dp0"
if exist "node_modules" (
    npm start
) else (
    echo Installing dependencies...
    npm install
    echo.
    echo Starting Hearthlink...
    npm start
)
pause
""")
    
    # Unix launcher
    unix_launcher = package_dir / "hearthlink-alpha.sh"
    with open(unix_launcher, 'w') as f:
        f.write("""#!/bin/bash
echo "========================================"
echo "    Hearthlink Alpha Version"
echo "========================================"
echo
echo "Starting Hearthlink..."
echo
cd "$(dirname "$0")"
if [ -d "node_modules" ]; then
    npm start
else
    echo "Installing dependencies..."
    npm install
    echo
    echo "Starting Hearthlink..."
    npm start
fi
""")
    
    os.chmod(unix_launcher, 0o755)
    
    # Create README for alpha testers
    alpha_readme = package_dir / "ALPHA_README.md"
    with open(alpha_readme, 'w') as f:
        f.write(f"""# Hearthlink Alpha Version

**Version**: alpha-{alpha_date}  
**Build Date**: {datetime.now().isoformat()}  
**Package Type**: Portable Alpha Release  

## What's New in This Alpha

✅ **Tech Debt Removal**: Cleaned up simulation code and mock implementations  
✅ **Bug Reporting System**: Complete in-app and CLI bug reporting workflow  
✅ **Standardized Error Handling**: New error wrapper utilities  
✅ **Grafana Dashboard**: Bug reporting metrics and monitoring  
✅ **Comprehensive Testing**: Unit, UI, and CLI tests for bug reporting  

## Quick Start

### Windows
1. Double-click `HearthlinkAlpha.bat`
2. Wait for dependencies to install (first run only)
3. Hearthlink will start automatically

### macOS/Linux
1. Open terminal in this directory
2. Run: `./hearthlink-alpha.sh`
3. Wait for dependencies to install (first run only)
4. Hearthlink will start automatically

### Manual Start
If the launchers don't work:
```bash
npm install
npm start
```

## Alpha Features to Test

### Bug Reporting System
- **Feedback Button**: Look for floating feedback button in bottom-right
- **Bug Categories**: Test different bug report categories (bug, feature, UI, performance)
- **File Attachments**: Try attaching screenshots and log files
- **CLI Reporting**: Use `scripts/hl bug --interactive` for command-line reporting

### Tech Debt Improvements
- **Error Handling**: Notice improved error messages and recovery
- **Performance**: Should feel more responsive with simulation code removed
- **Stability**: Fewer crashes with better error boundaries

## Known Issues
- Some features may be incomplete in alpha
- Debug logging is more verbose than final release
- UI polish is ongoing

## Reporting Issues
Use the built-in bug reporting system:
1. Click the "Feedback" button (bottom-right)
2. Select appropriate category
3. Describe the issue in detail
4. Attach screenshots if helpful

Or use the CLI:
```bash
# From the hearthlink directory
python scripts/bug_cli.py --interactive
```

## System Requirements
- Node.js 16+ (18+ recommended)
- Python 3.10+ for backend features
- 4GB RAM minimum
- 1GB free disk space

## Support
- **Alpha Issues**: Use the built-in bug reporting
- **General Help**: Check CLAUDE.md for usage instructions
- **Emergency**: Contact development team

## Important Notes
⚠️ **Alpha Software**: This is pre-release software. Backup important data.  
⚠️ **Testing Only**: Not recommended for production use.  
⚠️ **Feedback Needed**: Your testing and feedback is crucial for improving Hearthlink.  

Thank you for testing Hearthlink Alpha!
""")
    
    # Create build manifest
    manifest = {
        'version': f'alpha-{alpha_date}',
        'build_date': datetime.now().isoformat(),
        'package_type': 'portable_alpha',
        'total_files': len(packaged_files),
        'total_size_bytes': total_size,
        'files': packaged_files,
        'features': [
            'Tech debt removal',
            'Bug reporting system',
            'Standardized error handling',
            'Grafana dashboard integration',
            'Comprehensive test suite'
        ],
        'requirements': {
            'nodejs': '16+',
            'python': '3.10+',
            'ram': '4GB',
            'disk': '1GB'
        }
    }
    
    manifest_file = package_dir / "BUILD_MANIFEST.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"📋 Created build manifest: {manifest_file}")
    
    # Create ZIP archive
    print("📦 Creating ZIP archive...")
    
    zip_path = alpha_dir / f"hearthlink_alpha_{alpha_date}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(package_dir)
                zipf.write(file_path, arcname)
    
    # Generate checksums
    print("🔍 Generating checksums...")
    
    sha256_hash = hashlib.sha256()
    with open(zip_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    
    checksum = sha256_hash.hexdigest()
    
    checksums_file = alpha_dir / "checksums.txt"
    with open(checksums_file, 'w') as f:
        f.write(f"# Hearthlink Alpha Checksums\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n")
        f.write(f"# Algorithm: SHA-256\n\n")
        f.write(f"{checksum}  {zip_path.name}\n")
    
    # Create rollback guide
    rollback_guide = alpha_dir / "ROLLBACK_GUIDE.md"
    with open(rollback_guide, 'w') as f:
        f.write(f"""# Hearthlink Alpha Rollback Guide

## Quick Rollback
1. Stop Hearthlink if running
2. Delete the alpha directory
3. Restore previous Hearthlink installation
4. Restart with previous version

## Data Backup
Before testing alpha:
- Backup: `~/.config/hearthlink` (Linux)
- Backup: `%APPDATA%\\Hearthlink` (Windows)  
- Backup: `~/Library/Application Support/Hearthlink` (macOS)

## Restore Process
1. Stop alpha version
2. Restore backed up data
3. Reinstall stable version
4. Import settings if compatible

For detailed rollback instructions, see the main documentation.
""")
    
    # Final summary
    zip_size = zip_path.stat().st_size
    
    print("\n" + "=" * 60)
    print("🎉 ALPHA PACKAGE CREATED SUCCESSFULLY")
    print("=" * 60)
    print(f"📦 Package: {zip_path.name}")
    print(f"📁 Size: {zip_size:,} bytes ({zip_size/1024/1024:.1f} MB)")
    print(f"🔍 SHA-256: {checksum}")
    print(f"📋 Files: {len(packaged_files)}")
    print(f"📂 Output: {alpha_dir}")
    print("=" * 60)
    print("\nDeliverables:")
    print(f"  - {zip_path}")
    print(f"  - {checksums_file}")
    print(f"  - {rollback_guide}")
    print(f"  - {manifest_file}")
    print("=" * 60)
    
    return {
        'success': True,
        'package_path': str(zip_path),
        'checksum': checksum,
        'size_bytes': zip_size,
        'files_count': len(packaged_files),
        'output_dir': str(alpha_dir)
    }

def should_exclude_file(file_path: Path) -> bool:
    """Check if file should be excluded from package"""
    exclude_patterns = [
        '.git',
        'node_modules',
        '__pycache__',
        '.pyc',
        '.log',
        '.tmp',
        'coverage',
        'test-results',
        '.env',
        'userData',
        'dist',
        'build'
    ]
    
    file_str = str(file_path)
    return any(pattern in file_str for pattern in exclude_patterns)

if __name__ == '__main__':
    result = create_alpha_package()
    exit(0 if result['success'] else 1)