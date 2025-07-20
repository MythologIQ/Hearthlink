#!/bin/bash

# Hearthlink v1.2.0 - Production Launcher Script
# Enhanced launcher with comprehensive system checks and startup options

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Application metadata
APP_NAME="Hearthlink"
APP_VERSION="1.3.0"
APP_DESC="Advanced AI Orchestration System with SuperClaude Integration"

# Default configuration
DEFAULT_MODE="enhanced"
DEFAULT_ENV="production"
VERBOSE=false
SKIP_CHECKS=false

# Port management options
CLEANUP_PORTS=false
FORCE_PORTS=false
AUTO_PORTS=false
CHECK_PORTS_ONLY=false

# Print banner
print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                              ║"
    echo "║                          🌟 HEARTHLINK v1.3.0 🌟                           ║"
    echo "║                                                                              ║"
    echo "║         Advanced AI Orchestration System with SuperClaude Integration       ║"
    echo "║                                                                              ║"
    echo "║  ✨ Alice Behavioral Analysis     🎭 Mimic Dynamic Personas                 ║"
    echo "║  🧠 Local LLM Integration         🤖 SuperClaude Advanced AI               ║"
    echo "║  🔊 Voice Interface Support       📊 Real-time Analytics                   ║"
    echo "║  🔒 Enhanced Security             🚀 Production Ready                      ║"
    echo "║                                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
}

# Print usage information
print_usage() {
    echo -e "${BLUE}Usage: $0 [OPTIONS]${NC}"
    echo
    echo -e "${YELLOW}Launch Modes:${NC}"
    echo "  --enhanced     Enhanced launcher with all features (default)"
    echo "  --standard     Standard Electron launcher"
    echo "  --development  Development mode with hot reload"
    echo "  --tauri        Native Tauri launcher"
    echo
    echo -e "${YELLOW}Environment Options:${NC}"
    echo "  --production   Production environment (default)"
    echo "  --development  Development environment"
    echo "  --testing      Testing environment"
    echo
    echo -e "${YELLOW}System Options:${NC}"
    echo "  --verbose      Enable verbose logging"
    echo "  --skip-checks  Skip system requirement checks"
    echo "  --health-check Run system health check only"
    echo "  --build        Build application before launching"
    echo
    echo -e "${YELLOW}Port Management:${NC}"
    echo "  --cleanup-ports    Terminate existing Hearthlink processes and free ports"
    echo "  --force-ports      Force terminate conflicting processes automatically"
    echo "  --auto-ports       Automatically find alternative ports for conflicts"
    echo "  --check-ports      Check port availability only (no launch)"
    echo
    echo -e "${YELLOW}Information:${NC}"
    echo "  --version      Show version information"
    echo "  --help         Show this help message"
    echo
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0                          # Launch with default settings"
    echo "  $0 --enhanced --verbose     # Enhanced mode with verbose logging"
    echo "  $0 --development --build    # Development mode with fresh build"
    echo "  $0 --cleanup-ports          # Clean up existing processes and launch"
    echo "  $0 --force-ports --auto-ports  # Auto-resolve all port conflicts"
    echo "  $0 --health-check           # Check system health only"
    echo "  $0 --check-ports            # Check port availability only"
    echo
}

# Print version information
print_version() {
    echo -e "${GREEN}$APP_NAME v$APP_VERSION${NC}"
    echo -e "${BLUE}$APP_DESC${NC}"
    echo
    echo -e "${YELLOW}System Information:${NC}"
    echo "  OS: $(uname -s) $(uname -r)"
    echo "  Architecture: $(uname -m)"
    echo "  Node.js: $(node --version 2>/dev/null || echo 'Not found')"
    echo "  NPM: $(npm --version 2>/dev/null || echo 'Not found')"
    echo "  Python: $(python3 --version 2>/dev/null || echo 'Not found')"
    echo
}

# Log with timestamp
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")
            echo -e "${GREEN}[$timestamp] INFO:${NC} $message"
            ;;
        "WARN")
            echo -e "${YELLOW}[$timestamp] WARN:${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}[$timestamp] ERROR:${NC} $message"
            ;;
        "DEBUG")
            if [ "$VERBOSE" = true ]; then
                echo -e "${BLUE}[$timestamp] DEBUG:${NC} $message"
            fi
            ;;
    esac
}

# Check system requirements
check_requirements() {
    log "INFO" "Checking system requirements..."
    
    local errors=0
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log "ERROR" "Node.js is required but not installed"
        errors=$((errors + 1))
    else
        local node_version=$(node --version | sed 's/v//')
        local major_version=$(echo $node_version | cut -d. -f1)
        if [ "$major_version" -lt 18 ]; then
            log "WARN" "Node.js v18+ recommended, found v$node_version"
        else
            log "DEBUG" "Node.js v$node_version ✓"
        fi
    fi
    
    # Check NPM
    if ! command -v npm &> /dev/null; then
        log "ERROR" "NPM is required but not installed"
        errors=$((errors + 1))
    else
        local npm_version=$(npm --version)
        log "DEBUG" "NPM v$npm_version ✓"
    fi
    
    # Check Python (optional)
    if command -v python3 &> /dev/null; then
        local python_version=$(python3 --version | sed 's/Python //')
        log "DEBUG" "Python v$python_version ✓"
    else
        log "WARN" "Python3 not found - some features may be limited"
    fi
    
    # Check required files
    local required_files=("package.json" "launcher.js" "main.js")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log "ERROR" "Required file missing: $file"
            errors=$((errors + 1))
        else
            log "DEBUG" "Required file found: $file ✓"
        fi
    done
    
    # Check node_modules
    if [ ! -d "node_modules" ]; then
        log "WARN" "Node modules not found - will attempt to install"
        install_dependencies
    else
        log "DEBUG" "Node modules found ✓"
    fi
    
    if [ $errors -gt 0 ]; then
        log "ERROR" "System requirements check failed with $errors errors"
        exit 1
    else
        log "INFO" "System requirements check passed ✓"
    fi
}

# Install dependencies
install_dependencies() {
    log "INFO" "Installing dependencies..."
    
    if ! npm install; then
        log "ERROR" "Failed to install dependencies"
        exit 1
    fi
    
    log "INFO" "Dependencies installed successfully ✓"
}

# Build application
build_application() {
    log "INFO" "Building application..."
    
    if npm run build; then
        log "INFO" "Application built successfully ✓"
    else
        log "WARN" "Build failed - attempting to launch anyway"
    fi
}

# Port management functions
find_available_port() {
    local start_port=$1
    local max_attempts=${2:-50}
    
    for ((i=0; i<max_attempts; i++)); do
        local test_port=$((start_port + i))
        if ! netstat -ln 2>/dev/null | grep -q ":$test_port " && ! lsof -Pi :$test_port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo $test_port
            return 0
        fi
    done
    
    echo ""
    return 1
}

get_process_info() {
    local port=$1
    local pid=$(lsof -ti:$port 2>/dev/null)
    
    if [ -n "$pid" ]; then
        local process_name=$(ps -p $pid -o comm= 2>/dev/null | tr -d '\n')
        local process_cmd=$(ps -p $pid -o args= 2>/dev/null | cut -c1-50)
        echo "$pid:$process_name:$process_cmd"
    else
        echo ""
    fi
}

terminate_port_process() {
    local port=$1
    local force=${2:-false}
    
    local process_info=$(get_process_info $port)
    if [ -n "$process_info" ]; then
        local pid=$(echo $process_info | cut -d: -f1)
        local process_name=$(echo $process_info | cut -d: -f2)
        
        log "INFO" "Terminating process $process_name (PID: $pid) on port $port"
        
        if [ "$force" = true ]; then
            kill -9 $pid 2>/dev/null
        else
            kill -15 $pid 2>/dev/null
            sleep 2
            # Check if process is still running
            if kill -0 $pid 2>/dev/null; then
                log "WARN" "Process $pid didn't terminate gracefully, using force"
                kill -9 $pid 2>/dev/null
            fi
        fi
        
        sleep 1
        
        # Verify termination
        if ! kill -0 $pid 2>/dev/null; then
            log "INFO" "Process $pid terminated successfully ✓"
            return 0
        else
            log "ERROR" "Failed to terminate process $pid"
            return 1
        fi
    else
        log "DEBUG" "No process found on port $port"
        return 0
    fi
}

check_and_resolve_ports() {
    log "INFO" "Checking port availability and resolving conflicts..."
    
    # Handle cleanup ports option
    if [ "$CLEANUP_PORTS" = true ]; then
        cleanup_ports
    fi
    
    # Define required ports and their purposes
    declare -A REQUIRED_PORTS=(
        ["3000"]="React Development Server"
        ["3001"]="React Production Server"
        ["8000"]="Python Backend API"
        ["8001"]="FastAPI Documentation"
    )
    
    # Define environment variables for dynamic port assignment
    declare -A PORT_ENV_VARS=(
        ["3000"]="REACT_APP_PORT"
        ["3001"]="REACT_PROD_PORT"
        ["8000"]="BACKEND_PORT"
        ["8001"]="DOCS_PORT"
    )
    
    local conflicts_found=false
    local resolution_needed=false
    declare -A port_resolutions=()
    
    # Check each required port
    for port in "${!REQUIRED_PORTS[@]}"; do
        local service_name="${REQUIRED_PORTS[$port]}"
        
        # Check if port is in use
        if netstat -ln 2>/dev/null | grep -q ":$port " || lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            conflicts_found=true
            local process_info=$(get_process_info $port)
            
            if [ -n "$process_info" ]; then
                local pid=$(echo $process_info | cut -d: -f1)
                local process_name=$(echo $process_info | cut -d: -f2)
                local process_cmd=$(echo $process_info | cut -d: -f3)
                
                log "WARN" "Port $port ($service_name) is occupied by:"
                log "WARN" "  PID: $pid | Process: $process_name"
                log "WARN" "  Command: $process_cmd"
                
                # Check if it's a Hearthlink process
                if echo "$process_cmd" | grep -q -E "(hearthlink|electron|react-scripts|node.*launcher)"; then
                    log "INFO" "Detected existing Hearthlink process on port $port"
                    
                    # Auto-terminate if force-ports is enabled
                    if [ "$FORCE_PORTS" = true ]; then
                        if terminate_port_process $port; then
                            log "INFO" "Port $port is now available ✓"
                        else
                            resolution_needed=true
                        fi
                    else
                        echo -n "Do you want to terminate the existing Hearthlink process? [Y/n]: "
                        read -r response
                        if [[ "$response" =~ ^[Yy]$ ]] || [[ -z "$response" ]]; then
                            if terminate_port_process $port; then
                                log "INFO" "Port $port is now available ✓"
                            else
                                resolution_needed=true
                            fi
                        else
                            resolution_needed=true
                        fi
                    fi
                else
                    log "INFO" "Non-Hearthlink process detected on port $port"
                    # Auto-terminate if force-ports is enabled for any process
                    if [ "$FORCE_PORTS" = true ]; then
                        log "WARN" "Force terminating non-Hearthlink process on port $port"
                        if terminate_port_process $port true; then
                            log "INFO" "Port $port is now available ✓"
                        else
                            resolution_needed=true
                        fi
                    else
                        resolution_needed=true
                    fi
                fi
            else
                log "WARN" "Port $port is in use but process details unavailable"
                resolution_needed=true
            fi
        else
            log "DEBUG" "Port $port ($service_name) available ✓"
        fi
    done
    
    # If resolution is needed, find alternative ports
    if [ "$resolution_needed" = true ] || [ "$AUTO_PORTS" = true ]; then
        log "INFO" "Resolving port conflicts by finding alternative ports..."
        
        for port in "${!REQUIRED_PORTS[@]}"; do
            local service_name="${REQUIRED_PORTS[$port]}"
            local env_var="${PORT_ENV_VARS[$port]}"
            
            # Check if this port still needs resolution
            if netstat -ln 2>/dev/null | grep -q ":$port " || lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
                log "INFO" "Finding alternative port for $service_name (originally $port)..."
                
                local new_port=$(find_available_port $port)
                if [ -n "$new_port" ]; then
                    port_resolutions[$port]=$new_port
                    export $env_var=$new_port
                    log "INFO" "Assigned port $new_port for $service_name ✓"
                else
                    log "ERROR" "Could not find available port for $service_name"
                    echo "Consider terminating other processes or restarting your system"
                    exit 1
                fi
            fi
        done
        
        # Display port resolution summary
        if [ ${#port_resolutions[@]} -gt 0 ]; then
            echo
            log "INFO" "Port Resolution Summary:"
            for original_port in "${!port_resolutions[@]}"; do
                local new_port="${port_resolutions[$original_port]}"
                local service_name="${REQUIRED_PORTS[$original_port]}"
                log "INFO" "  $service_name: $original_port → $new_port"
            done
            echo
        fi
    fi
    
    # Final verification
    local final_check_failed=false
    for port in "${!REQUIRED_PORTS[@]}"; do
        local service_name="${REQUIRED_PORTS[$port]}"
        local check_port=$port
        
        # Use resolved port if available
        if [ -n "${port_resolutions[$port]}" ]; then
            check_port="${port_resolutions[$port]}"
        fi
        
        if netstat -ln 2>/dev/null | grep -q ":$check_port " || lsof -Pi :$check_port -sTCP:LISTEN -t >/dev/null 2>&1; then
            log "ERROR" "Port conflict still exists on $check_port ($service_name)"
            final_check_failed=true
        fi
    done
    
    if [ "$final_check_failed" = true ]; then
        log "ERROR" "Port resolution failed. Please resolve conflicts manually or use --force-ports flag"
        echo
        echo "Manual resolution options:"
        echo "1. Kill conflicting processes: sudo lsof -ti:PORT | xargs kill -9"
        echo "2. Restart your system to clear all port conflicts"
        echo "3. Use alternative launch methods: npm run start -- --port NEWPORT"
        echo
        exit 1
    else
        log "INFO" "All required ports are available ✓"
    fi
}

# Enhanced port cleanup function
cleanup_ports() {
    log "INFO" "Cleaning up Hearthlink processes..."
    
    local hearthlink_ports=(3000 3001 8000 8001)
    local processes_killed=0
    
    for port in "${hearthlink_ports[@]}"; do
        local process_info=$(get_process_info $port)
        if [ -n "$process_info" ]; then
            local pid=$(echo $process_info | cut -d: -f1)
            local process_cmd=$(echo $process_info | cut -d: -f3)
            
            # Only kill if it looks like a Hearthlink process
            if echo "$process_cmd" | grep -q -E "(hearthlink|electron|react-scripts|node.*launcher)"; then
                log "INFO" "Terminating Hearthlink process on port $port (PID: $pid)"
                if terminate_port_process $port true; then
                    processes_killed=$((processes_killed + 1))
                fi
            fi
        fi
    done
    
    if [ $processes_killed -gt 0 ]; then
        log "INFO" "Terminated $processes_killed Hearthlink processes"
    else
        log "INFO" "No Hearthlink processes to terminate"
    fi
}

# Run health check
health_check() {
    log "INFO" "Running system health check..."
    
    # Check disk space
    local disk_usage=$(df . | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 90 ]; then
        log "WARN" "Disk usage is ${disk_usage}% - consider freeing space"
    else
        log "DEBUG" "Disk usage: ${disk_usage}% ✓"
    fi
    
    # Check memory
    local memory_info=$(free -m 2>/dev/null || echo "0 0 0")
    if [ "$memory_info" != "0 0 0" ]; then
        local total_memory=$(echo $memory_info | awk 'NR==2 {print $2}')
        local available_memory=$(echo $memory_info | awk 'NR==2 {print $7}')
        if [ "$available_memory" -lt 1024 ]; then
            log "WARN" "Low available memory: ${available_memory}MB"
        else
            log "DEBUG" "Available memory: ${available_memory}MB ✓"
        fi
    fi
    
    # Check port availability with conflict resolution
    check_and_resolve_ports
    
    log "INFO" "Health check completed ✓"
}

# Launch application
launch_application() {
    local mode=$1
    local environment=$2
    
    log "INFO" "Launching $APP_NAME in $mode mode (environment: $environment)..."
    
    # Set environment variables
    export NODE_ENV="$environment"
    export HEARTHLINK_LOG_LEVEL="${HEARTHLINK_LOG_LEVEL:-info}"
    export HEARTHLINK_MONITORING_ENABLED="${HEARTHLINK_MONITORING_ENABLED:-true}"
    
    if [ "$VERBOSE" = true ]; then
        export HEARTHLINK_LOG_LEVEL="debug"
        export DEBUG="*"
    fi
    
    # Display port information if ports were modified
    if [ -n "${REACT_APP_PORT}" ] || [ -n "${REACT_PROD_PORT}" ] || [ -n "${BACKEND_PORT}" ] || [ -n "${DOCS_PORT}" ]; then
        echo
        log "INFO" "Using custom port configuration:"
        [ -n "${REACT_APP_PORT}" ] && log "INFO" "  React Dev Server: ${REACT_APP_PORT}"
        [ -n "${REACT_PROD_PORT}" ] && log "INFO" "  React Prod Server: ${REACT_PROD_PORT}"
        [ -n "${BACKEND_PORT}" ] && log "INFO" "  Backend API: ${BACKEND_PORT}"
        [ -n "${DOCS_PORT}" ] && log "INFO" "  API Documentation: ${DOCS_PORT}"
        echo
    fi
    
    # Launch based on mode
    case $mode in
        "enhanced")
            log "INFO" "Starting enhanced launcher with Alice, Mimic, SuperClaude, and Local LLM integration..."
            npm run launch
            ;;
        "standard")
            log "INFO" "Starting standard Electron launcher..."
            npm run start
            ;;
        "development")
            log "INFO" "Starting development mode with hot reload..."
            npm run dev:enhanced
            ;;
        "tauri")
            log "INFO" "Starting native Tauri launcher..."
            npm run native
            ;;
        *)
            log "ERROR" "Unknown launch mode: $mode"
            exit 1
            ;;
    esac
}

# Handle cleanup on exit
cleanup() {
    log "INFO" "Cleaning up..."
    # Kill any background processes if needed
    exit 0
}

# Set up signal handlers
trap cleanup EXIT INT TERM

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --enhanced)
            DEFAULT_MODE="enhanced"
            shift
            ;;
        --standard)
            DEFAULT_MODE="standard"
            shift
            ;;
        --development)
            DEFAULT_MODE="development"
            DEFAULT_ENV="development"
            shift
            ;;
        --tauri)
            DEFAULT_MODE="tauri"
            shift
            ;;
        --production)
            DEFAULT_ENV="production"
            shift
            ;;
        --testing)
            DEFAULT_ENV="testing"
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --skip-checks)
            SKIP_CHECKS=true
            shift
            ;;
        --health-check)
            print_banner
            health_check
            exit 0
            ;;
        --build)
            BUILD_APP=true
            shift
            ;;
        --cleanup-ports)
            CLEANUP_PORTS=true
            shift
            ;;
        --force-ports)
            FORCE_PORTS=true
            shift
            ;;
        --auto-ports)
            AUTO_PORTS=true
            shift
            ;;
        --check-ports)
            CHECK_PORTS_ONLY=true
            shift
            ;;
        --version)
            print_version
            exit 0
            ;;
        --help)
            print_banner
            print_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_banner
    
    # Handle port-only check mode
    if [ "$CHECK_PORTS_ONLY" = true ]; then
        check_and_resolve_ports
        exit 0
    fi
    
    # Handle cleanup-only mode
    if [ "$CLEANUP_PORTS" = true ] && [ "$#" -eq 1 ]; then
        cleanup_ports
        log "INFO" "Port cleanup completed. Run without --cleanup-ports to launch."
        exit 0
    fi
    
    # System requirements check
    if [ "$SKIP_CHECKS" != true ]; then
        check_requirements
        health_check
    fi
    
    # Build if requested
    if [ "$BUILD_APP" = true ]; then
        build_application
    fi
    
    # Launch application
    launch_application "$DEFAULT_MODE" "$DEFAULT_ENV"
}

# Run main function
main "$@"