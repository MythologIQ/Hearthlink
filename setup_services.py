#!/usr/bin/env python3
"""
Hearthlink Services Setup Script
Helps users set up and configure Hearthlink services
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def install_python_deps():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✓ Python dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create environment file template"""
    env_path = Path(".env")
    
    if env_path.exists():
        print("✓ .env file already exists")
        return True
    
    env_content = """# Hearthlink Environment Configuration
# Copy this file to .env and fill in your API keys

# Claude API Key (for Synapse)
CLAUDE_API_KEY=your_claude_api_key_here

# Google AI Studio API Key (for Synapse)
GOOGLE_AI_KEY=your_google_ai_key_here

# Ollama URL (for local LLM)
OLLAMA_URL=http://localhost:11434

# Database settings
DATABASE_PATH=hearthlink_data/vault.db

# API server settings
API_PORT=8001
API_HOST=0.0.0.0
"""
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print("✓ Created .env template file")
        print("  Please edit .env file with your API keys")
        return True
    except Exception as e:
        print(f"✗ Failed to create .env file: {e}")
        return False

def create_data_directory():
    """Create data directory for Hearthlink"""
    data_dir = Path("hearthlink_data")
    data_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    (data_dir / "vault").mkdir(exist_ok=True)
    (data_dir / "logs").mkdir(exist_ok=True)
    (data_dir / "cache").mkdir(exist_ok=True)
    
    print("✓ Created data directories")
    return True

def check_ollama():
    """Check if Ollama is installed and running"""
    try:
        result = subprocess.run(["ollama", "list"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✓ Ollama is installed and running")
            print("  Available models:")
            for line in result.stdout.strip().split('\n')[1:]:  # Skip header
                if line.strip():
                    print(f"    - {line.split()[0]}")
            return True
        else:
            print("✗ Ollama is installed but not running")
            print("  Run: ollama serve")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("✗ Ollama not found")
        print("  Install from: https://ollama.ai")
        print("  Then run: ollama serve")
        return False

def suggest_ollama_models():
    """Suggest useful models to install"""
    print("\nRecommended Ollama models:")
    models = [
        ("llama2", "General purpose chat model"),
        ("codellama", "Code generation and analysis"),
        ("mistral", "Fast and efficient chat model"),
        ("llama2:13b", "Larger model for better results")
    ]
    
    for model, description in models:
        print(f"  ollama pull {model:15} # {description}")

def main():
    """Main setup function"""
    print("=" * 60)
    print("HEARTHLINK SERVICES SETUP")
    print("=" * 60)
    
    setup_steps = [
        ("Installing Python dependencies", install_python_deps),
        ("Creating environment file", create_env_file),
        ("Creating data directories", create_data_directory),
        ("Checking Ollama installation", check_ollama),
    ]
    
    results = []
    for step_name, step_func in setup_steps:
        print(f"\n{step_name}...")
        result = step_func()
        results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("SETUP SUMMARY")
    print("=" * 60)
    
    success_count = sum(results)
    total_steps = len(results)
    
    print(f"Completed: {success_count}/{total_steps} steps")
    
    if success_count == total_steps:
        print("\n🎉 Setup completed successfully!")
    else:
        print(f"\n⚠️  {total_steps - success_count} step(s) need attention.")
    
    print("\nNext steps:")
    print("1. Edit .env file with your API keys")
    print("2. Install Ollama models (if needed):")
    suggest_ollama_models()
    print("3. Run: python src/api/initialize_services.py")
    print("4. Start the application: npm run dev")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()