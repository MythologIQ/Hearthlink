#!/bin/bash

# Universal Claude Code Setup Script
# Flexible setup for Claude Code across any project type

set -e  # Exit on any error

echo "🚀 Universal Claude Code Setup"
echo "=============================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_header() { echo -e "${BLUE}[STEP]${NC} $1"; }

# Configuration variables
INSTALL_GLOBAL=true
SETUP_PROJECT=false
PROJECT_TYPE=""
BACKEND_TYPE=""
FORCE_REINSTALL=false

# Usage function
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

OPTIONS:
    -p, --project           Initialize Claude Code in current directory
    -t, --type TYPE         Project type (electron, web, api, cli, python, etc.)
    -b, --backend TYPE      Backend type (python, node, go, rust, etc.)
    -g, --global-only       Install globally only (default)
    -f, --force             Force reinstall even if already installed
    -h, --help              Show this help message

EXAMPLES:
    $0                              # Install Claude Code globally
    $0 -p -t electron -b python     # Setup for Electron + Python project
    $0 -p -t web -b node            # Setup for web app with Node backend
    $0 -p -t api -b python          # Setup for Python API project
    $0 -f                           # Force reinstall Claude Code

EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--project)
                SETUP_PROJECT=true
                INSTALL_GLOBAL=false
                shift
                ;;
            -t|--type)
                PROJECT_TYPE="$2"
                shift 2
                ;;
            -b|--backend)
                BACKEND_TYPE="$2"
                shift 2
                ;;
            -g|--global-only)
                INSTALL_GLOBAL=true
                SETUP_PROJECT=false
                shift
                ;;
            -f|--force)
                FORCE_REINSTALL=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
}

# Auto-detect project type
detect_project_type() {
    print_header "Auto-detecting project type..."
    
    if [[ -f "package.json" ]]; then
        if grep -q "electron" package.json; then
            PROJECT_TYPE="electron"
            print_status "Detected: Electron application"
        elif grep -q "react" package.json; then
            PROJECT_TYPE="react"
            print_status "Detected: React application"
        elif grep -q "vue" package.json; then
            PROJECT_TYPE="vue"
            print_status "Detected: Vue application"
        elif grep -q "next" package.json; then
            PROJECT_TYPE="nextjs"
            print_status "Detected: Next.js application"
        else
            PROJECT_TYPE="web"
            print_status "Detected: Web application"
        fi
    elif [[ -f "requirements.txt" ]] || [[ -f "pyproject.toml" ]]; then
        PROJECT_TYPE="python"
        print_status "Detected: Python project"
    elif [[ -f "go.mod" ]]; then
        PROJECT_TYPE="go"
        print_status "Detected: Go project"
    elif [[ -f "Cargo.toml" ]]; then
        PROJECT_TYPE="rust"
        print_status "Detected: Rust project"
    elif [[ -f "pom.xml" ]]; then
        PROJECT_TYPE="java"
        print_status "Detected: Java project"
    else
        PROJECT_TYPE="generic"
        print_status "Using: Generic project type"
    fi
}

# Auto-detect backend type
detect_backend_type() {
    if [[ -n "$BACKEND_TYPE" ]]; then
        return
    fi
    
    print_header "Auto-detecting backend type..."
    
    if [[ -f "requirements.txt" ]] || [[ -f "pyproject.toml" ]] || [[ -d "backend" && -f "backend/main.py" ]]; then
        BACKEND_TYPE="python"
        print_status "Detected: Python backend"
    elif [[ -f "server.js" ]] || [[ -f "app.js" ]] || [[ -d "backend" && -f "backend/package.json" ]]; then
        BACKEND_TYPE="node"
        print_status "Detected: Node.js backend"
    elif [[ -f "go.mod" ]]; then
        BACKEND_TYPE="go"
        print_status "Detected: Go backend"
    elif [[ -f "Cargo.toml" ]]; then
        BACKEND_TYPE="rust"
        print_status "Detected: Rust backend"
    else
        BACKEND_TYPE="none"
        print_status "No backend detected"
    fi
}

# Check operating system
check_os() {
    print_header "Checking operating system..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_status "Detected Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_status "Detected macOS"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="windows"
        print_status "Detected Windows"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Check dependencies
check_dependencies() {
    print_header "Checking dependencies..."
    
    # Node.js check
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | cut -d 'v' -f 2 | cut -d '.' -f 1)
        if [ "$NODE_VERSION" -ge 16 ]; then
            print_status "Node.js $(node --version) ✓"
        else
            print_warning "Node.js version 16+ recommended. Current: $(node --version)"
        fi
    else
        print_warning "Node.js not found (optional for some projects)"
    fi
    
    # Python check
    if command -v python3 &> /dev/null; then
        print_status "Python $(python3 --version) ✓"
    else
        print_warning "Python not found (optional for some projects)"
    fi
    
    # Git check
    if command -v git &> /dev/null; then
        print_status "Git $(git --version | cut -d ' ' -f 3) ✓"
    else
        print_error "Git is required for Claude Code"
        exit 1
    fi
}

# Install Claude Code globally
install_claude_code() {
    print_header "Installing Claude Code..."
    
    # Check if already installed
    if command -v claude-code &> /dev/null && [[ "$FORCE_REINSTALL" == false ]]; then
        print_status "Claude Code already installed: $(claude-code --version)"
        return
    fi
    
    # Multiple installation methods (actual method depends on Anthropic's distribution)
    if command -v npm &> /dev/null; then
        print_status "Installing via npm..."
        npm install -g @anthropic-ai/claude-code
    elif command -v pip &> /dev/null; then
        print_status "Installing via pip..."
        pip install claude-code
    elif command -v brew &> /dev/null && [[ "$OS" == "macos" ]]; then
        print_status "Installing via Homebrew..."
        brew install anthropic/tap/claude-code
    elif command -v curl &> /dev/null; then
        print_status "Installing via direct download..."
        curl -sSL https://install.anthropic.com/claude-code | bash
    else
        print_error "No suitable package manager found"
        print_error "Please install npm, pip, or brew first"
        exit 1
    fi
    
    # Verify installation
    if command -v claude-code &> /dev/null; then
        print_status "Claude Code installed successfully!"
        claude-code --version
    else
        print_error "Claude Code installation failed"
        exit 1
    fi
}

# Initialize project-specific setup
init_project() {
    if [[ "$SETUP_PROJECT" == false ]]; then
        return
    fi
    
    print_header "Initializing Claude Code project..."
    
    # Auto-detect if not specified
    if [[ -z "$PROJECT_TYPE" ]]; then
        detect_project_type
    fi
    
    if [[ -z "$BACKEND_TYPE" ]]; then
        detect_backend_type
    fi
    
    # Initialize based on project type
    case $PROJECT_TYPE in
        electron)
            claude-code init --type=electron --backend="$BACKEND_TYPE"
            ;;
        react|vue|nextjs)
            claude-code init --type=web --frontend="$PROJECT_TYPE" --backend="$BACKEND_TYPE"
            ;;
        python)
            claude-code init --type=python --framework=auto-detect
            ;;
        go)
            claude-code init --type=go
            ;;
        rust)
            claude-code init --type=rust
            ;;
        *)
            claude-code init --type=generic --backend="$BACKEND_TYPE"
            ;;
    esac
    
    print_status "Project initialized for $PROJECT_TYPE with $BACKEND_TYPE backend"
    
    # Create generic context file
    create_context_file
}

# Create minimal context file
create_context_file() {
    print_header "Creating project context..."
    
    cat > .claude-context.md << EOF
# Project Context for Claude Code

## Project Type
$PROJECT_TYPE

## Backend
$BACKEND_TYPE

## Auto-detected Structure
$(ls -la | head -10)

## Available Commands
Run \`claude-code help\` for available commands specific to this project type.

## Custom Instructions
Add any project-specific instructions or context here.
EOF

    print_status "Context file created: .claude-context.md"
}

# Create universal helper script
create_helper_script() {
    if [[ "$SETUP_PROJECT" == false ]]; then
        return
    fi
    
    print_header "Creating helper scripts..."
    
    cat > claude-helper.sh << 'EOF'
#!/bin/bash
# Universal Claude Code helper script

echo "🤖 Claude Code Helper"
echo "===================="

if [[ $# -eq 0 ]]; then
    echo "Available commands:"
    echo "  ./claude-helper.sh help           # Show Claude Code help"
    echo "  ./claude-helper.sh status         # Show project status"
    echo "  ./claude-helper.sh quick [task]   # Quick development task"
    echo "  ./claude-helper.sh chat           # Start interactive session"
    exit 0
fi

case $1 in
    help)
        claude-code help
        ;;
    status)
        echo "Project Status:"
        claude-code status
        ;;
    quick)
        shift
        claude-code quick "$@"
        ;;
    chat)
        claude-code chat
        ;;
    *)
        claude-code "$@"
        ;;
esac
EOF

    chmod +x claude-helper.sh
    print_status "Helper script created: ./claude-helper.sh"
}

# Main execution
main() {
    parse_args "$@"
    
    print_header "Starting Claude Code setup..."
    echo "Global install: $INSTALL_GLOBAL"
    echo "Project setup: $SETUP_PROJECT"
    echo "Project type: ${PROJECT_TYPE:-auto-detect}"
    echo "Backend type: ${BACKEND_TYPE:-auto-detect}"
    echo ""
    
    check_os
    check_dependencies
    install_claude_code
    
    if [[ "$SETUP_PROJECT" == true ]]; then
        init_project
        create_helper_script
    fi
    
    echo ""
    echo "🎉 Claude Code setup complete!"
    echo "=============================="
    
    if [[ "$SETUP_PROJECT" == true ]]; then
        print_status "Project initialized in: $(pwd)"
        print_status "Run: ./claude-helper.sh help"
        print_status "Or: claude-code help"
    else
        print_status "Claude Code installed globally"
        print_status "Run: claude-code help"
        print_status "Or: $0 --project to setup current directory"
    fi
    
    print_status "Check https://docs.anthropic.com for latest documentation"
}

# Run main function
main "$@"