#!/bin/sh

# Simple Claude Code Setup for sh (no bash required)
# Basic setup without advanced bash features

echo "🚀 Claude Code Setup (sh compatible)"
echo "====================================="

PROJECT_TYPE="electron"
BACKEND_TYPE="python"

# Check basic dependencies
echo "Checking dependencies..."

if command -v node >/dev/null 2>&1; then
    echo "✓ Node.js found: $(node --version)"
else
    echo "✗ Node.js not found - please install Node.js 16+"
    exit 1
fi

if command -v python3 >/dev/null 2>&1; then
    echo "✓ Python found: $(python3 --version)"
else
    echo "✗ Python3 not found - please install Python 3.8+"
    exit 1
fi

if command -v git >/dev/null 2>&1; then
    echo "✓ Git found"
else
    echo "✗ Git not found - please install Git"
    exit 1
fi

# Note about Claude Code installation
echo ""
echo "📋 Claude Code Installation Notes:"
echo "=================================="
echo "Since this is a limited environment, you'll need to:"
echo "1. Install Claude Code manually using one of these methods:"
echo "   - npm install -g @anthropic-ai/claude-code"
echo "   - pip install claude-code"
echo "   - Download from Anthropic's website"
echo ""
echo "2. After Claude Code is installed, run:"
echo "   claude-code init --type=electron --backend=python"
echo ""
echo "3. Use the helper scripts:"
echo "   ./hearthlink-claude.sh status    # Check system"
echo "   ./hearthlink-claude.sh backend   # Integrate Python backend"
echo "   ./hearthlink-claude.sh conference # Build multi-LLM system"
echo ""

# Check if Claude Code is already installed
if command -v claude-code >/dev/null 2>&1; then
    echo "✅ Claude Code is already installed!"
    echo "Version: $(claude-code --version)"
    echo ""
    echo "Initializing Claude Code for Hearthlink..."
    claude-code init --type=electron --backend=python
    echo ""
    echo "🎉 Setup complete! You can now use:"
    echo "  ./hearthlink-claude.sh status"
    echo "  ./hearthlink-claude.sh backend"
else
    echo "⚠️  Claude Code not found. Please install it first:"
    echo "   npm install -g @anthropic-ai/claude-code"
    echo "   (or alternative installation method)"
    echo ""
    echo "Then run this script again."
fi

echo ""
echo "📁 Project context ready at: .claude-context.md"
echo "🛠️  Helper scripts ready:"
echo "   - hearthlink-claude.sh (Claude Code commands)"
echo "   - start-hearthlink-dev.sh (dev environment)"
