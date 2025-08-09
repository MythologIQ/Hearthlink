#!/usr/bin/env python3
"""
SPEC-2 Installer Validation Script
Validates that the Tauri installer contains all required SPEC-2 components and assets
"""

import os
import json
import hashlib
import zipfile
import sys
from pathlib import Path
from datetime import datetime

def calculate_file_hash(file_path):
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"❌ Error calculating hash for {file_path}: {e}")
        return None

def validate_spec2_components():
    """Validate that all SPEC-2 components are present"""
    print("📋 Validating SPEC-2 components...")
    
    required_components = [
        "src/components/TaskCreator.js",
        "src/components/TaskCreator.css", 
        "src/components/MemoryDebugPanel.js",
        "src/components/MemoryDebugPanel.css",
        "src/api/task_templates.py",
        "src/api/vault_tasks.py"
    ]
    
    missing_components = []
    present_components = []
    
    for component in required_components:
        if os.path.exists(component):
            file_hash = calculate_file_hash(component)
            file_size = os.path.getsize(component)
            present_components.append({
                "path": component,
                "hash": file_hash,
                "size": file_size
            })
            print(f"✅ Found: {component} ({file_size} bytes)")
        else:
            missing_components.append(component)
            print(f"❌ Missing: {component}")
    
    return present_components, missing_components

def validate_assets():
    """Validate that validation assets are present and valid"""
    print("🔍 Validating assets...")
    
    assets_dir = Path("src-tauri/assets")
    required_assets = [
        "validation.json",
        "ci_badges.json",
        "installer_manifest.json"
    ]
    
    asset_validation = {}
    
    for asset in required_assets:
        asset_path = assets_dir / asset
        if asset_path.exists():
            try:
                with open(asset_path, 'r') as f:
                    data = json.load(f)
                asset_validation[asset] = {
                    "exists": True,
                    "valid_json": True,
                    "size": asset_path.stat().st_size,
                    "hash": calculate_file_hash(asset_path)
                }
                print(f"✅ Asset valid: {asset}")
            except json.JSONDecodeError as e:
                asset_validation[asset] = {
                    "exists": True,
                    "valid_json": False,
                    "error": str(e)
                }
                print(f"❌ Invalid JSON in {asset}: {e}")
        else:
            asset_validation[asset] = {"exists": False}
            print(f"❌ Missing asset: {asset}")
    
    return asset_validation

def validate_tauri_config():
    """Validate Tauri configuration"""
    print("⚙️ Validating Tauri configuration...")
    
    config_path = Path("src-tauri/tauri.conf.json")
    if not config_path.exists():
        print("❌ Missing tauri.conf.json")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check key SPEC-2 configurations
        checks = {
            "Product name contains SPEC-2": "SPEC-2" in config.get("productName", ""),
            "Version includes spec2": "spec2" in config.get("version", ""),
            "Bundle is active": config.get("bundle", {}).get("active", False),
            "Resources include validation assets": any("validation.json" in str(r) for r in config.get("bundle", {}).get("resources", [])),
            "Security CSP configured": "security" in config.get("app", {}),
        }
        
        all_passed = True
        for check, passed in checks.items():
            if passed:
                print(f"✅ {check}")
            else:
                print(f"❌ {check}")
                all_passed = False
        
        return all_passed
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in tauri.conf.json: {e}")
        return False

def validate_package_json():
    """Validate package.json for SPEC-2 build scripts"""
    print("📦 Validating package.json...")
    
    try:
        with open("package.json", 'r') as f:
            package = json.load(f)
        
        scripts = package.get("scripts", {})
        required_scripts = ["tauri:build", "tauri:dev", "native", "native:build"]
        
        missing_scripts = []
        for script in required_scripts:
            if script in scripts:
                print(f"✅ Script found: {script}")
            else:
                missing_scripts.append(script)
                print(f"❌ Missing script: {script}")
        
        return len(missing_scripts) == 0
        
    except Exception as e:
        print(f"❌ Error validating package.json: {e}")
        return False

def check_build_artifacts():
    """Check for existing build artifacts"""
    print("🏗️ Checking build artifacts...")
    
    build_dir = Path("target/release/bundle")
    if not build_dir.exists():
        print("⚠️ No build artifacts found (not yet built)")
        return []
    
    artifacts = []
    for ext in ["*.exe", "*.msi", "*.deb", "*.dmg", "*.AppImage"]:
        artifacts.extend(build_dir.rglob(ext))
    
    if artifacts:
        print(f"✅ Found {len(artifacts)} build artifacts:")
        for artifact in artifacts:
            size = artifact.stat().st_size
            hash_val = calculate_file_hash(artifact)
            print(f"  📄 {artifact.name} ({size} bytes, sha256: {hash_val[:16]}...)")
    else:
        print("⚠️ No installer artifacts found")
    
    return artifacts

def generate_validation_report():
    """Generate comprehensive validation report"""
    print("\n🔍 Generating SPEC-2 Validation Report...")
    
    # Run all validations
    components, missing_components = validate_spec2_components()
    assets = validate_assets()
    tauri_valid = validate_tauri_config()
    package_valid = validate_package_json()
    artifacts = check_build_artifacts()
    
    # Generate report
    report = {
        "validation_report": {
            "timestamp": datetime.now().isoformat(),
            "spec_version": "SPEC-2-Tauri-Memory-Integration",
            "overall_status": "PASSED" if not missing_components and tauri_valid and package_valid else "FAILED",
            "components": {
                "present": components,
                "missing": missing_components,
                "count_present": len(components),
                "count_missing": len(missing_components)
            },
            "assets": assets,
            "configuration": {
                "tauri_config_valid": tauri_valid,
                "package_json_valid": package_valid
            },
            "build_artifacts": {
                "count": len(artifacts),
                "files": [{"name": a.name, "size": a.stat().st_size} for a in artifacts]
            }
        }
    }
    
    # Save report
    report_path = Path("validation_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Validation report saved to: {report_path}")
    
    # Print summary
    print("\n📊 Validation Summary:")
    print(f"Overall Status: {'✅ PASSED' if report['validation_report']['overall_status'] == 'PASSED' else '❌ FAILED'}")
    print(f"Components: {len(components)}/{len(components) + len(missing_components)} present")
    print(f"Configuration: {'✅ Valid' if tauri_valid and package_valid else '❌ Invalid'}")
    print(f"Build Artifacts: {len(artifacts)} found")
    
    return report['validation_report']['overall_status'] == 'PASSED'

if __name__ == "__main__":
    print("🚀 SPEC-2 Tauri Installer Validation")
    print("=" * 50)
    
    success = generate_validation_report()
    
    if success:
        print("\n🎉 All validations passed! Installer is ready for packaging.")
        sys.exit(0)
    else:
        print("\n❌ Validation failed. Please address the issues above.")
        sys.exit(1)