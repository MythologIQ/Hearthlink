#!/usr/bin/env python3
"""
Validation script for Codespaces development environment
Tests that all required dependencies and tools are properly installed
"""

import sys
import subprocess
import importlib
from pathlib import Path

def check_command(cmd, version_flag="--version"):
    """Check if a command exists and can be executed"""
    try:
        result = subprocess.run([cmd, version_flag], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, "Command not found"

def check_python_package(package):
    """Check if a Python package can be imported"""
    try:
        importlib.import_module(package)
        return True
    except ImportError:
        return False

def validate_environment():
    """Validate the complete development environment"""
    print("🔍 Validating Hearthlink Codespaces Environment...\n")
    
    # Check Node.js and npm
    print("📦 Checking Node.js environment:")
    node_ok, node_version = check_command("node")
    npm_ok, npm_version = check_command("npm")
    
    print(f"  Node.js: {'✅' if node_ok else '❌'} {node_version}")
    print(f"  npm: {'✅' if npm_ok else '❌'} {npm_version}")
    
    # Check Python
    print("\n🐍 Checking Python environment:")
    python_ok, python_version = check_command("python3")
    pip_ok, pip_version = check_command("pip", "--version")
    
    print(f"  Python: {'✅' if python_ok else '❌'} {python_version}")
    print(f"  pip: {'✅' if pip_ok else '❌'} {pip_version}")
    
    # Check Python packages
    print("\n📚 Checking Python packages:")
    required_packages = ["fastapi", "uvicorn", "pydantic", "requests", "cryptography", "websockets"]
    
    for package in required_packages:
        installed = check_python_package(package)
        print(f"  {package}: {'✅' if installed else '❌'}")
    
    # Check Rust
    print("\n🦀 Checking Rust environment:")
    rust_ok, rust_version = check_command("rustc")
    cargo_ok, cargo_version = check_command("cargo")
    tauri_ok, tauri_version = check_command("cargo", "tauri --version")
    
    print(f"  Rust: {'✅' if rust_ok else '❌'} {rust_version}")
    print(f"  Cargo: {'✅' if cargo_ok else '❌'} {cargo_version}")
    print(f"  Tauri CLI: {'✅' if tauri_ok else '❌'} {tauri_version}")
    
    # Check directory structure
    print("\n📁 Checking project structure:")
    required_dirs = ["src", "src/api", "src/core", "config", "logs"]
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        exists = dir_path.exists()
        print(f"  {dir_name}: {'✅' if exists else '❌'}")
    
    # Check critical files
    print("\n📄 Checking critical files:")
    required_files = [
        "package.json", 
        "requirements.txt", 
        "src/api/core_api.py",
        "test_api_health.py"
    ]
    
    for file_name in required_files:
        file_path = Path(file_name)
        exists = file_path.exists()
        print(f"  {file_name}: {'✅' if exists else '❌'}")
    
    print("\n🎉 Environment validation complete!")
    
    # Quick API test
    print("\n🚀 Quick API smoke test:")
    print("  To test the Core API, run:")
    print("    python -m uvicorn src.api.core_api:app --host 127.0.0.1 --port 8000")
    print("  Then in another terminal:")
    print("    ./test_api_health.py")

if __name__ == "__main__":
    validate_environment()