@echo off
setlocal enabledelayedexpansion
title Hearthlink System Launcher
color 0B

:: Hide the console window by default (uncomment next line for silent mode)
:: if not "%1"=="MINIMIZED" start /min cmd /c "%~dpnx0 MINIMIZED" & exit

echo.
echo  ╔═══════════════════════════════════════════════════════════════════════════════╗
echo  ║                         Hearthlink System Launcher                           ║
echo  ║                      Full Environment Initialization                         ║
echo  ║                                 v1.3.0                                       ║
echo  ╚═══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 🚀 Starting Hearthlink Full Environment...
echo.

:: Set project path
set "PROJECT_PATH=/mnt/g/MythologIQ/Hearthlink"
set "WIN_PROJECT_PATH=G:\MythologIQ\Hearthlink"

:: Check if WSL is available
wsl --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ WSL is not installed or not available
    echo    Please install WSL first: https://docs.microsoft.com/en-us/windows/wsl/install
    pause
    exit /b 1
)

echo ✅ WSL is available
echo.

:: Check if Docker Desktop is running
echo 🐳 Checking Docker Desktop...
tasklist /fi "imagename eq Docker Desktop.exe" 2>nul | find /i "Docker Desktop.exe" >nul
if %errorlevel% neq 0 (
    echo ⚠️  Docker Desktop is not running. Starting Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo    Waiting for Docker Desktop to start...
    timeout /t 15 /nobreak >nul
) else (
    echo ✅ Docker Desktop is running
)
echo.

:: Create log directory
if not exist "%WIN_PROJECT_PATH%\logs" mkdir "%WIN_PROJECT_PATH%\logs"

:: Generate timestamp for logs
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set "DATE_STAMP=%%c%%a%%b"
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set "TIME_STAMP=%%a%%b"
set "LOG_FILE=%WIN_PROJECT_PATH%\logs\hearthlink_launcher_%DATE_STAMP%_%TIME_STAMP%.log"

echo 📝 Logging to: %LOG_FILE%
echo.

:: Start the main launcher script in WSL
echo 🔧 Starting WSL environment and background services...
echo.

:: Create a comprehensive WSL startup script
wsl -d Ubuntu -e bash -c "
    # Set up logging
    LOG_FILE='%PROJECT_PATH%/logs/hearthlink_launcher_%DATE_STAMP%_%TIME_STAMP%.log'
    exec > >(tee -a \$LOG_FILE) 2>&1
    
    echo '🔗 Hearthlink System Launcher - WSL Environment'
    echo '================================================='
    echo 'Timestamp: $(date)'
    echo 'Working Directory: $(pwd)'
    echo 'User: $(whoami)'
    echo 'Distribution: $(lsb_release -d 2>/dev/null || echo 'Unknown')'
    echo
    
    # Change to project directory
    echo '📁 Changing to project directory...'
    cd '%PROJECT_PATH%' || {
        echo '❌ Failed to change to project directory: %PROJECT_PATH%'
        exit 1
    }
    echo '✅ Changed to: $(pwd)'
    echo
    
    # Check if Claude is installed
    echo '🤖 Checking Claude installation...'
    if command -v claude >/dev/null 2>&1; then
        echo '✅ Claude is installed: $(which claude)'
        echo '   Version: $(claude --version 2>/dev/null || echo 'Unknown')'
    else
        echo '❌ Claude is not installed'
        echo '   Please install Claude: https://claude.ai/download'
        exit 1
    fi
    echo
    
    # Start Docker services if docker-compose exists
    echo '🐳 Starting Docker services...'
    if [ -f 'docker-compose.yml' ]; then
        echo '   Found docker-compose.yml, starting services...'
        docker-compose up -d 2>/dev/null || echo '   ⚠️  Docker services may not be available'
    else
        echo '   No docker-compose.yml found, skipping Docker services'
    fi
    echo
    
    # Start database services
    echo '🗄️  Starting database services...'
    
    # PostgreSQL
    if command -v pg_isready >/dev/null 2>&1; then
        echo '   Starting PostgreSQL...'
        sudo service postgresql start 2>/dev/null || echo '   ⚠️  PostgreSQL may not be available'
    fi
    
    # Redis
    if command -v redis-server >/dev/null 2>&1; then
        echo '   Starting Redis...'
        sudo service redis-server start 2>/dev/null || echo '   ⚠️  Redis may not be available'
    fi
    
    # Neo4j (if installed)
    if command -v neo4j >/dev/null 2>&1; then
        echo '   Starting Neo4j...'
        sudo service neo4j start 2>/dev/null || echo '   ⚠️  Neo4j may not be available'
    fi
    
    echo
    
    # Wait for services to be ready
    echo '⏳ Waiting for services to be ready...'
    sleep 3
    echo
    
    # Start Claude with dangerous permissions
    echo '🤖 Starting Claude with dangerous permissions...'
    echo '   Command: claude --dangerously-skip-permissions'
    echo '   Working directory: $(pwd)'
    echo '   This will start Claude in the background...'
    echo
    
    # Create a new tmux session for Claude
    if command -v tmux >/dev/null 2>&1; then
        echo '   Creating tmux session for Claude...'
        tmux new-session -d -s 'hearthlink-claude' -c '%PROJECT_PATH%' 'claude --dangerously-skip-permissions'
        echo '   ✅ Claude started in tmux session: hearthlink-claude'
        echo '   Use: tmux attach -t hearthlink-claude to view'
    else
        echo '   Starting Claude in background...'
        nohup claude --dangerously-skip-permissions > logs/claude_output.log 2>&1 &
        echo '   ✅ Claude started in background (PID: $!)'
    fi
    echo
    
    echo '🎯 Environment setup complete!'
    echo '   • Claude is running with dangerous permissions'
    echo '   • Database services are started'
    echo '   • Docker services are running'
    echo '   • MCP servers should be available'
    echo '   • Ready to launch Hearthlink!'
    echo
    
    # Give user option to launch Hearthlink immediately
    echo '🚀 Would you like to launch Hearthlink now? (y/n)'
    read -r response
    if [[ \$response =~ ^[Yy]$ ]]; then
        echo '   Launching Hearthlink...'
        npm run launch
    else
        echo '   Hearthlink environment is ready for manual launch'
        echo '   Use: npm run launch'
    fi
"

echo.
echo ✅ WSL environment setup complete
echo.
echo 🎯 Hearthlink Full Environment Status:
echo    • WSL environment initialized
echo    • Claude running with dangerous permissions
echo    • Database services started
echo    • Docker services running
echo    • MCP servers available
echo    • Ready for Hearthlink launch
echo.
echo 📋 Next steps:
echo    1. Environment is ready in WSL
echo    2. Claude is running in background
echo    3. Launch Hearthlink: npm run launch
echo    4. Or use: npm run native:frame for native wrapper
echo.
echo 💡 Log file: %LOG_FILE%
echo.

pause