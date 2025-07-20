#!/bin/sh

# Simple Claude Code Setup - Skip dependency checks
echo "🚀 Claude Code Setup (dependency checks skipped)"
echo "==============================================="

echo "Assuming Node.js, Python, and Git are available..."
echo ""

# Check if Claude Code is already installed
if command -v claude-code >/dev/null 2>&1; then
    echo "✅ Claude Code is already installed!"
    echo "Version: $(claude-code --version)"
    echo ""
    echo "Initializing Claude Code for Hearthlink..."
    claude-code init --type=electron --backend=python
    echo ""
    echo "🎉 Setup complete!"
else
    echo "📋 Claude Code Installation Instructions:"
    echo "========================================"
    echo "Since Claude Code is not found, please install it using:"
    echo ""
    echo "Option 1 - npm (if npm works in WSL):"
    echo "  npm install -g @anthropic-ai/claude-code"
    echo ""
    echo "Option 2 - pip (if pip works in WSL):"
    echo "  pip install claude-code"
    echo ""
    echo "Option 3 - Manual download from Anthropic"
    echo ""
    echo "After installation, run:"
    echo "  claude-code init --type=electron --backend=python"
fi

echo ""
echo "📁 Your project is ready with:"
echo "   - Complete context file (.claude-context.md)"
echo "   - Helper scripts (hearthlink-claude.sh)"
echo "   - Development environment (start-hearthlink-dev.sh)"
echo ""
echo "🚀 Next steps:"
echo "   1. Install Claude Code (see instructions above)"
echo "   2. Run: claude-code init --type=electron --backend=python"
echo "   3. Start with: ./hearthlink-claude.sh backend"
