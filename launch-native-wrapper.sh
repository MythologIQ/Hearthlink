#!/bin/bash

# Hearthlink Native Wrapper Launcher Script

echo "🔗 Starting Hearthlink Native Wrapper..."

# Check if Tauri is installed
if ! command -v cargo &> /dev/null; then
    echo "❌ Cargo (Rust) is not installed. Please install Rust first."
    echo "Visit: https://rustup.rs/"
    exit 1
fi

# Navigate to project directory
cd "$(dirname "$0")"

# Check if we're in the right directory
if [ ! -f "src-tauri/Cargo.toml" ]; then
    echo "❌ Tauri project not found. Make sure you're in the Hearthlink directory."
    exit 1
fi

# Build and run the native wrapper
echo "🔧 Building native wrapper..."
npm run build

echo "🚀 Starting native wrapper in development mode..."
npm run tauri:dev

echo "✅ Native wrapper launched successfully!"
echo "💡 The wrapper will persist in your system tray when closed."
echo "💡 Use the system tray menu to control Hearthlink."