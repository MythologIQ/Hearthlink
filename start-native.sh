#!/bin/bash

# Hearthlink Native Wrapper Launcher
# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Function to print colored output
print_colored() {
    echo -e "${1}${2}${NC}"
}

# Function to print header
print_header() {
    echo
    print_colored $CYAN "╔═══════════════════════════════════════════════════════════════════════════════╗"
    print_colored $CYAN "║                          Hearthlink Native Wrapper                           ║"
    print_colored $CYAN "║                                   v1.3.0                                     ║"
    print_colored $CYAN "╚═══════════════════════════════════════════════════════════════════════════════╝"
    echo
}

# Function to check dependencies
check_dependencies() {
    print_colored $BLUE "🔗 Initializing Hearthlink Native Wrapper..."
    echo
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        print_colored $RED "❌ Node.js is not installed. Please install Node.js first."
        print_colored $WHITE "   Visit: https://nodejs.org/"
        echo
        exit 1
    fi
    
    # Check if we're in the right directory
    if [ ! -f "package.json" ]; then
        print_colored $RED "❌ Not in the correct Hearthlink directory"
        print_colored $WHITE "   Make sure this script is in the Hearthlink root folder"
        echo
        exit 1
    fi
    
    # Check if native-wrapper.js exists
    if [ ! -f "native-wrapper.js" ]; then
        print_colored $RED "❌ Native wrapper script not found"
        print_colored $WHITE "   Make sure native-wrapper.js is in the current directory"
        echo
        exit 1
    fi
    
    print_colored $GREEN "✅ Environment checks passed"
    echo
}

# Function to setup directories
setup_directories() {
    # Create userData directory if it doesn't exist
    mkdir -p userData/logs
}

# Function to start the wrapper
start_wrapper() {
    print_colored $GREEN "🚀 Starting Hearthlink Native Wrapper..."
    echo
    print_colored $YELLOW "💡 The wrapper will:"
    print_colored $WHITE "   • Auto-start the Electron application"
    print_colored $WHITE "   • Monitor and restart if it crashes"
    print_colored $WHITE "   • Persist in the background"
    print_colored $WHITE "   • Log all activities to userData/logs/native-wrapper.log"
    echo
    print_colored $YELLOW "🔄 To stop the wrapper, press Ctrl+C"
    echo
    
    # Start the native wrapper
    node native-wrapper.js start
    
    echo
    print_colored $RED "🛑 Native wrapper has been stopped"
}

# Main execution
main() {
    print_header
    check_dependencies
    setup_directories
    start_wrapper
}

# Run the main function
main "$@"