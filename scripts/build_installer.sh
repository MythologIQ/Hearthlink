#!/bin/bash

# SPEC-2 Tauri Installer Build Script
# Packages Hearthlink with validation assets and CI badges

set -e

echo "🚀 Building SPEC-2 Tauri Installer with Validation Assets..."

# Build configuration
BUILD_DIR="target/release/bundle"
ASSETS_DIR="src-tauri/assets"
VERSION="1.3.0-spec2"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Create assets directory if it doesn't exist
mkdir -p "$ASSETS_DIR"

# Validate SPEC-2 components exist
echo "📋 Validating SPEC-2 components..."

REQUIRED_COMPONENTS=(
    "src/components/TaskCreator.js"
    "src/components/TaskCreator.css"
    "src/components/MemoryDebugPanel.js"
    "src/components/MemoryDebugPanel.css"
    "src/api/task_templates.py"
    "src/api/vault_tasks.py"
)

for component in "${REQUIRED_COMPONENTS[@]}"; do
    if [[ ! -f "$component" ]]; then
        echo "❌ Missing required component: $component"
        exit 1
    fi
    echo "✅ Found: $component"
done

# Update validation timestamp
echo "🔄 Updating validation timestamps..."
if [[ -f "$ASSETS_DIR/validation.json" ]]; then
    sed -i 's/"build_timestamp": "[^"]*"/"build_timestamp": "'$TIMESTAMP'"/' "$ASSETS_DIR/validation.json"
fi

if [[ -f "$ASSETS_DIR/ci_badges.json" ]]; then
    sed -i 's/"generated_at": "[^"]*"/"generated_at": "'$TIMESTAMP'"/' "$ASSETS_DIR/ci_badges.json"
fi

# Compile TypeScript before build
echo "🔧 Compiling TypeScript..."
npm run compile:ts

# Build React frontend
echo "🏗️ Building React frontend..."
npm run build

# Build Tauri application
echo "📦 Building Tauri application..."
npm run tauri:build

# Verify bundle was created
if [[ ! -d "$BUILD_DIR" ]]; then
    echo "❌ Build failed - no bundle directory found"
    exit 1
fi

echo "✅ Build completed successfully!"

# List built artifacts
echo "📄 Built artifacts:"
find "$BUILD_DIR" -name "*.exe" -o -name "*.deb" -o -name "*.dmg" -o -name "*.AppImage" 2>/dev/null || echo "No installer artifacts found (this may be expected depending on platform)"

# Calculate checksums for validation
echo "🔐 Calculating checksums..."
if command -v sha256sum >/dev/null 2>&1; then
    find "$BUILD_DIR" -type f \( -name "*.exe" -o -name "*.deb" -o -name "*.dmg" -o -name "*.AppImage" \) -exec sha256sum {} \;
elif command -v shasum >/dev/null 2>&1; then
    find "$BUILD_DIR" -type f \( -name "*.exe" -o -name "*.deb" -o -name "*.dmg" -o -name "*.AppImage" \) -exec shasum -a 256 {} \;
else
    echo "⚠️ No checksum utility found"
fi

echo "🎉 SPEC-2 Tauri installer build complete!"
echo "📁 Artifacts location: $BUILD_DIR"
echo "🔖 Version: $VERSION"
echo "⏰ Build time: $TIMESTAMP"