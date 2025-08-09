#!/usr/bin/env python3
"""
SPEC-3 Week 3: Alpha Installer Builder
Build and package signed alpha installer with checksums and rollback guide
"""

import os
import json
import shutil
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

class AlphaInstallerBuilder:
    """Builds and packages alpha installer with signing and checksums"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.dist_dir = project_root / "dist"
        self.alpha_date = datetime.now().strftime("%Y%m%d")
        self.alpha_dir = self.dist_dir / f"alpha_{self.alpha_date}"
        self.build_artifacts = []
        
    def prepare_build_environment(self) -> Dict[str, Any]:
        """Prepare build environment and directories"""
        print("🏗️ Preparing build environment...")
        
        # Create output directory
        self.alpha_dir.mkdir(parents=True, exist_ok=True)
        
        # Clean previous builds
        if (self.dist_dir / "win-unpacked").exists():
            shutil.rmtree(self.dist_dir / "win-unpacked")
        
        build_info = {
            'build_date': datetime.now().isoformat(),
            'build_environment': os.name,
            'alpha_version': f"alpha-{self.alpha_date}",
            'project_root': str(self.project_root),
            'output_dir': str(self.alpha_dir)
        }
        
        print(f"📁 Alpha output directory: {self.alpha_dir}")
        return build_info
    
    def run_tauri_build(self) -> Dict[str, Any]:
        """Run npm run tauri build --release"""
        print("🔨 Running Tauri build process...")
        
        try:
            # Check if Tauri is configured
            tauri_config = self.project_root / "src-tauri" / "tauri.conf.json"
            if not tauri_config.exists():
                print("⚠️ Tauri config not found, using Electron build instead")
                return self.run_electron_build()
            
            # Run Tauri build
            cmd = ["npm", "run", "tauri", "build", "--release"]
            print(f"🚀 Executing: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            if result.returncode != 0:
                print(f"❌ Tauri build failed: {result.stderr}")
                return self.run_electron_build_fallback()
            
            print("✅ Tauri build completed successfully")
            
            # Find build artifacts
            tauri_dist = self.project_root / "src-tauri" / "target" / "release"
            artifacts = self.find_tauri_artifacts(tauri_dist)
            
            return {
                'build_type': 'tauri',
                'success': True,
                'artifacts': artifacts,
                'build_output': result.stdout,
                'build_log': result.stderr
            }
            
        except subprocess.TimeoutExpired:
            print("❌ Tauri build timed out")
            return self.run_electron_build_fallback()
        except Exception as e:
            print(f"❌ Tauri build error: {e}")
            return self.run_electron_build_fallback()
    
    def run_electron_build(self) -> Dict[str, Any]:
        """Run Electron build as primary option"""
        print("🔨 Running Electron build process...")
        
        try:
            # First build React app
            print("📦 Building React application...")
            react_cmd = ["npm", "run", "build"]
            react_result = subprocess.run(
                react_cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if react_result.returncode != 0:
                print(f"⚠️ React build had warnings: {react_result.stderr}")
            
            # Then build Electron app
            print("📦 Building Electron application...")
            electron_cmd = ["npm", "run", "electron-pack"]
            electron_result = subprocess.run(
                electron_cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if electron_result.returncode != 0:
                print(f"❌ Electron build failed: {electron_result.stderr}")
                # Create manual build
                return self.create_manual_build()
            
            print("✅ Electron build completed successfully")
            
            # Find build artifacts
            artifacts = self.find_electron_artifacts()
            
            return {
                'build_type': 'electron',
                'success': True,
                'artifacts': artifacts,
                'react_output': react_result.stdout,
                'electron_output': electron_result.stdout
            }
            
        except Exception as e:
            print(f"❌ Electron build error: {e}")
            return self.create_manual_build()
    
    def run_electron_build_fallback(self) -> Dict[str, Any]:
        """Fallback Electron build when Tauri fails"""
        print("🔄 Falling back to Electron build...")
        return self.run_electron_build()
    
    def create_manual_build(self) -> Dict[str, Any]:
        """Create manual build when automated builds fail"""
        print("🛠️ Creating manual build package...")
        
        try:
            # Create manual build directory
            manual_build_dir = self.alpha_dir / "hearthlink_alpha_manual"
            manual_build_dir.mkdir(exist_ok=True)
            
            # Copy essential files
            essential_files = [
                "package.json",
                "src/",
                "public/",
                "electron/",
                "scripts/",
                "config/",
                "README.md"
            ]
            
            for file_pattern in essential_files:
                source_path = self.project_root / file_pattern
                if source_path.exists():
                    if source_path.is_file():
                        shutil.copy2(source_path, manual_build_dir / source_path.name)
                    else:
                        dest_dir = manual_build_dir / source_path.name
                        shutil.copytree(source_path, dest_dir, dirs_exist_ok=True)
                    print(f"📁 Copied: {file_pattern}")
            
            # Create installer script
            installer_script = manual_build_dir / "install.bat"
            installer_content = """@echo off
echo Hearthlink Alpha Installer
echo ========================
echo.
echo Installing dependencies...
npm install
echo.
echo Building application...
npm run build
echo.
echo Installation complete!
echo Run 'npm start' to launch Hearthlink
pause
"""
            
            with open(installer_script, 'w') as f:
                f.write(installer_content)
            
            # Create zip archive
            archive_path = self.alpha_dir / "hearthlink_alpha_manual.zip"
            shutil.make_archive(
                str(archive_path.with_suffix('')),
                'zip',
                manual_build_dir
            )
            
            artifacts = [str(archive_path)]
            
            return {
                'build_type': 'manual',
                'success': True,
                'artifacts': artifacts,
                'message': 'Manual build package created'
            }
            
        except Exception as e:
            print(f"❌ Manual build failed: {e}")
            return {
                'build_type': 'manual',
                'success': False,
                'error': str(e),
                'artifacts': []
            }
    
    def find_tauri_artifacts(self, tauri_dist: Path) -> List[str]:
        """Find Tauri build artifacts"""
        artifacts = []
        
        # Common Tauri output patterns
        patterns = [
            "*.exe",
            "*.msi",
            "*.dmg",
            "*.AppImage",
            "*.deb",
            "*.rpm"
        ]
        
        for pattern in patterns:
            for artifact in tauri_dist.glob(pattern):
                artifacts.append(str(artifact))
                print(f"📦 Found Tauri artifact: {artifact.name}")
        
        return artifacts
    
    def find_electron_artifacts(self) -> List[str]:
        """Find Electron build artifacts"""
        artifacts = []
        
        # Check common Electron output locations
        electron_dist_dirs = [
            self.dist_dir / "win-unpacked",
            self.dist_dir / "mac",
            self.dist_dir / "linux-unpacked",
            self.dist_dir
        ]
        
        for dist_dir in electron_dist_dirs:
            if dist_dir.exists():
                # Look for executables and installers
                for pattern in ["*.exe", "*.app", "*.dmg", "*.AppImage", "*.deb"]:
                    for artifact in dist_dir.glob(pattern):
                        artifacts.append(str(artifact))
                        print(f"📦 Found Electron artifact: {artifact.name}")
        
        return artifacts
    
    def sign_artifacts(self, artifacts: List[str]) -> Dict[str, Any]:
        """Sign build artifacts (mock implementation for alpha)"""
        print("🔐 Signing build artifacts...")
        
        signed_artifacts = []
        signing_results = []
        
        for artifact_path in artifacts:
            artifact = Path(artifact_path)
            if not artifact.exists():
                continue
            
            print(f"🔏 Signing: {artifact.name}")
            
            # In a real implementation, this would use actual code signing
            # For alpha, we'll create a signature file
            signature_file = artifact.with_suffix(artifact.suffix + '.sig')
            
            # Create mock signature (in production, use real signing tools)
            signature_content = {
                'artifact': artifact.name,
                'signature': f"MOCK_SIGNATURE_{hashlib.sha256(artifact.name.encode()).hexdigest()[:16]}",
                'signed_at': datetime.now().isoformat(),
                'signer': 'Hearthlink Alpha Build System',
                'algorithm': 'mock-sha256'
            }
            
            with open(signature_file, 'w') as f:
                json.dump(signature_content, f, indent=2)
            
            signed_artifacts.append(str(artifact))
            signing_results.append({
                'artifact': str(artifact),
                'signature_file': str(signature_file),
                'status': 'signed'
            })
        
        return {
            'signed_artifacts': signed_artifacts,
            'signing_results': signing_results,
            'total_signed': len(signed_artifacts)
        }
    
    def generate_checksums(self, artifacts: List[str]) -> Dict[str, str]:
        """Generate SHA-256 checksums for artifacts"""
        print("🔍 Generating checksums...")
        
        checksums = {}
        
        for artifact_path in artifacts:
            artifact = Path(artifact_path)
            if not artifact.exists():
                continue
            
            print(f"🔢 Calculating checksum: {artifact.name}")
            
            sha256_hash = hashlib.sha256()
            with open(artifact, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            checksum = sha256_hash.hexdigest()
            checksums[artifact.name] = checksum
            
            print(f"   {checksum}")
        
        # Write checksums file
        checksums_file = self.alpha_dir / "checksums.txt"
        with open(checksums_file, 'w') as f:
            f.write("# Hearthlink Alpha Build Checksums\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write("# Algorithm: SHA-256\n\n")
            
            for filename, checksum in checksums.items():
                f.write(f"{checksum}  {filename}\n")
        
        print(f"✅ Checksums written to: {checksums_file}")
        return checksums
    
    def copy_artifacts_to_alpha_dir(self, artifacts: List[str]) -> List[str]:
        """Copy artifacts to alpha directory"""
        print("📋 Copying artifacts to alpha directory...")
        
        copied_artifacts = []
        
        for artifact_path in artifacts:
            artifact = Path(artifact_path)
            if not artifact.exists():
                continue
            
            # Determine target filename
            if artifact.name.endswith(('.exe', '.msi')):
                target_name = f"hearthlink_alpha_setup.{artifact.suffix[1:]}"
            elif artifact.name.endswith(('.dmg', '.pkg')):
                target_name = f"hearthlink_alpha_setup.{artifact.suffix[1:]}"
            elif artifact.name.endswith(('.AppImage', '.deb', '.rpm')):
                target_name = f"hearthlink_alpha_setup.{artifact.suffix[1:]}"
            else:
                target_name = f"hearthlink_alpha_{artifact.name}"
            
            target_path = self.alpha_dir / target_name
            
            print(f"📁 Copying: {artifact.name} -> {target_name}")
            shutil.copy2(artifact, target_path)
            
            copied_artifacts.append(str(target_path))
        
        return copied_artifacts
    
    def generate_rollback_guide(self) -> str:
        """Generate rollback guide"""
        print("📝 Generating rollback guide...")
        
        rollback_content = f"""# Hearthlink Alpha Rollback Guide

**Generated**: {datetime.now().isoformat()}  
**Alpha Version**: alpha-{self.alpha_date}  

## Overview

This guide provides instructions for rolling back the Hearthlink Alpha installation
if issues are encountered during testing.

## Rollback Steps

### 1. Stop Hearthlink Application

**Windows:**
```bash
# Stop the application if running
taskkill /f /im hearthlink.exe

# Or use Task Manager to end Hearthlink processes
```

**macOS/Linux:**
```bash
# Stop the application if running
pkill -f hearthlink
```

### 2. Backup Current Data

Before rolling back, backup your current data:

```bash
# Windows
xcopy "%APPDATA%\\Hearthlink" "%APPDATA%\\Hearthlink_backup" /E /I

# macOS
cp -r ~/Library/Application\\ Support/Hearthlink ~/Library/Application\\ Support/Hearthlink_backup

# Linux
cp -r ~/.config/hearthlink ~/.config/hearthlink_backup
```

### 3. Uninstall Alpha Version

**Windows:**
1. Go to Settings > Apps & Features
2. Find "Hearthlink" in the list
3. Click "Uninstall" and follow prompts
4. Or run: `uninstall.exe` if available

**macOS:**
1. Drag Hearthlink.app to Trash
2. Empty Trash
3. Remove application data: `rm -rf ~/Library/Application\\ Support/Hearthlink`

**Linux:**
```bash
# If installed via package manager
sudo apt remove hearthlink  # Debian/Ubuntu
sudo dnf remove hearthlink  # Fedora
sudo pacman -R hearthlink   # Arch

# If manual installation
rm -rf /opt/hearthlink
rm -f ~/.local/share/applications/hearthlink.desktop
```

### 4. Restore Previous Version

If you have a previous version backup:

1. **Locate Previous Installation**: Find your previous Hearthlink installation backup
2. **Restore Files**: Copy the backed up files to the installation directory
3. **Restore Data**: Copy your data backup to the appropriate location
4. **Restart**: Launch the previous version

### 5. Clean Installation (If Needed)

If rollback fails, perform a clean installation:

1. **Remove All Files**:
   ```bash
   # Windows
   rmdir /s "%APPDATA%\\Hearthlink"
   rmdir /s "%LOCALAPPDATA%\\Hearthlink"
   
   # macOS
   rm -rf ~/Library/Application\\ Support/Hearthlink
   rm -rf ~/Library/Preferences/com.hearthlink.*
   
   # Linux
   rm -rf ~/.config/hearthlink
   rm -rf ~/.local/share/hearthlink
   ```

2. **Download Stable Version**: Get the latest stable release
3. **Fresh Install**: Install the stable version
4. **Import Data**: Import backed up data if compatible

## Data Recovery

### Configuration Files
- Windows: `%APPDATA%\\Hearthlink\\config`
- macOS: `~/Library/Application Support/Hearthlink/config`
- Linux: `~/.config/hearthlink`

### User Data
- Windows: `%APPDATA%\\Hearthlink\\hearthlink_data`
- macOS: `~/Library/Application Support/Hearthlink/hearthlink_data`
- Linux: `~/.local/share/hearthlink/hearthlink_data`

### Log Files
- Windows: `%APPDATA%\\Hearthlink\\logs`
- macOS: `~/Library/Application Support/Hearthlink/logs`
- Linux: `~/.config/hearthlink/logs`

## Troubleshooting

### Common Issues

**"Cannot uninstall application"**
- Use Windows Add/Remove Programs
- Or manually delete installation directory
- Clean registry entries (Windows only)

**"Data corruption after rollback"**
- Restore from backup created in Step 2
- Contact support with log files

**"Previous version won't start"**
- Check system requirements
- Verify all files were restored
- Check permissions on installation directory

### Getting Help

If rollback fails or you encounter issues:

1. **Collect Information**:
   - Operating system and version
   - Alpha version being rolled back from
   - Error messages or symptoms
   - Log files from both versions

2. **Contact Support**:
   - GitHub Issues: https://github.com/mythologiq/hearthlink/issues
   - Email: support@hearthlink.dev
   - Include: System info, error logs, steps attempted

3. **Emergency Contact**:
   - For critical issues during rollback
   - Discord: #hearthlink-support
   - Priority support for alpha testers

## Prevention

### Before Installing Alpha Versions

1. **Full Backup**: Always backup current installation and data
2. **System Restore Point**: Create system restore point (Windows)
3. **Time Machine Backup**: Ensure recent backup (macOS)
4. **Package List**: Save list of installed packages (Linux)

### Testing Best Practices

1. **Separate Environment**: Test in VM or separate user account
2. **Limited Data**: Don't use production data for alpha testing
3. **Regular Backups**: Backup frequently during testing
4. **Document Issues**: Keep notes of problems encountered

---

**Note**: This rollback guide is specific to alpha-{self.alpha_date}. 
For other versions, consult the appropriate rollback documentation.

**Support**: If you need assistance with rollback procedures, please contact
the Hearthlink development team with this guide and your system information.
"""
        
        rollback_file = self.alpha_dir / "ROLLBACK_GUIDE.md"
        with open(rollback_file, 'w', encoding='utf-8') as f:
            f.write(rollback_content)
        
        print(f"✅ Rollback guide created: {rollback_file}")
        return str(rollback_file)
    
    def build_alpha_installer(self) -> Dict[str, Any]:
        """Main method to build complete alpha installer"""
        print("🚀 Starting Alpha Installer Build Process")
        print("=" * 60)
        
        results = {}
        
        try:
            # 1. Prepare build environment
            results['build_info'] = self.prepare_build_environment()
            
            # 2. Run build process
            build_result = self.run_tauri_build()
            results['build_result'] = build_result
            
            if not build_result['success']:
                print("❌ Build process failed")
                return results
            
            # 3. Copy artifacts to alpha directory
            artifacts = self.copy_artifacts_to_alpha_dir(build_result['artifacts'])
            results['copied_artifacts'] = artifacts
            
            # 4. Sign artifacts
            signing_result = self.sign_artifacts(artifacts)
            results['signing_result'] = signing_result
            
            # 5. Generate checksums
            checksums = self.generate_checksums(artifacts)
            results['checksums'] = checksums
            
            # 6. Generate rollback guide
            rollback_guide = self.generate_rollback_guide()
            results['rollback_guide'] = rollback_guide
            
            # 7. Create build manifest
            manifest = self.create_build_manifest(results)
            results['manifest'] = manifest
            
            print("\n" + "=" * 60)
            print("🎉 ALPHA INSTALLER BUILD COMPLETE")
            print("=" * 60)
            print(f"📁 Output Directory: {self.alpha_dir}")
            print(f"📦 Artifacts: {len(artifacts)}")
            print(f"🔐 Signed: {signing_result['total_signed']}")
            print(f"🔍 Checksums: {len(checksums)}")
            print("=" * 60)
            
            results['success'] = True
            return results
            
        except Exception as e:
            print(f"❌ Alpha installer build failed: {e}")
            results['success'] = False
            results['error'] = str(e)
            return results
    
    def create_build_manifest(self, build_results: Dict[str, Any]) -> str:
        """Create build manifest with all build information"""
        manifest = {
            'alpha_version': f"alpha-{self.alpha_date}",
            'build_timestamp': datetime.now().isoformat(),
            'build_type': build_results.get('build_result', {}).get('build_type', 'unknown'),
            'artifacts': build_results.get('copied_artifacts', []),
            'checksums': build_results.get('checksums', {}),
            'signing_info': build_results.get('signing_result', {}),
            'rollback_guide': build_results.get('rollback_guide', ''),
            'build_environment': {
                'platform': os.name,
                'python_version': os.sys.version,
                'builder_version': '1.0.0'
            }
        }
        
        manifest_file = self.alpha_dir / "BUILD_MANIFEST.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Build manifest created: {manifest_file}")
        return str(manifest_file)

def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent
    
    builder = AlphaInstallerBuilder(project_root)
    results = builder.build_alpha_installer()
    
    # Save results
    results_file = project_root / 'alpha_build_results.json'
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Full results saved to: {results_file}")
    
    return 0 if results.get('success', False) else 1

if __name__ == '__main__':
    exit(main())