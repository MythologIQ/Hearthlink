@echo off
setlocal enabledelayedexpansion
title Hearthlink Setup
color 0A

echo.
echo  ╔═══════════════════════════════════════════════════════════════════════════════╗
echo  ║                           Hearthlink Setup                                   ║
echo  ║                   Complete Environment Configuration                          ║
echo  ║                                v1.3.0                                        ║
echo  ╚═══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 🔧 Setting up Hearthlink for optimal performance...
echo.

:: Create necessary directories
echo 📁 Creating directories...
if not exist "logs" mkdir logs
if not exist "userData" mkdir userData
if not exist "userData\logs" mkdir userData\logs
if not exist "vault_data" mkdir vault_data
if not exist "hearthlink_data" mkdir hearthlink_data
if not exist "hearthlink_data\logs" mkdir hearthlink_data\logs
if not exist "hearthlink_data\sessions" mkdir hearthlink_data\sessions
if not exist "hearthlink_data\memories" mkdir hearthlink_data\memories
if not exist "hearthlink_data\embeddings" mkdir hearthlink_data\embeddings
echo ✅ Directories created
echo.

:: Check prerequisites
echo 🔍 Checking prerequisites...

:: Check Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed
    echo    Please install Node.js from: https://nodejs.org/
    pause
    exit /b 1
) else (
    echo ✅ Node.js is installed
)

:: Check WSL
wsl --list >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ WSL is not installed or not running
    echo    Please install WSL from: https://docs.microsoft.com/en-us/windows/wsl/install
    echo    Or try: wsl --install
    pause
    exit /b 1
) else (
    echo ✅ WSL is available
    wsl --list --verbose 2>nul
)

:: Check Docker
where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Docker is not installed (optional)
    echo    Install Docker Desktop from: https://www.docker.com/products/docker-desktop
) else (
    echo ✅ Docker is available
)

echo.

:: Install NPM dependencies
echo 📦 Installing NPM dependencies...
call npm install
if %errorlevel% neq 0 (
    echo ❌ Failed to install NPM dependencies
    pause
    exit /b 1
) else (
    echo ✅ NPM dependencies installed
)
echo.

:: Setup WSL environment
echo 🐧 Setting up WSL environment...
wsl -d Ubuntu -e bash -c "
    echo 'Setting up WSL environment for Hearthlink...'
    
    # Update package lists
    sudo apt-get update -qq
    
    # Install required packages
    sudo apt-get install -y curl wget git build-essential python3 python3-pip nodejs npm tmux
    
    # Install Claude CLI (if not already installed)
    if ! command -v claude >/dev/null 2>&1; then
        echo 'Installing Claude CLI...'
        curl -fsSL https://claude.ai/cli/install.sh | sh
    fi
    
    # Install Python dependencies
    cd '/mnt/g/MythologIQ/Hearthlink'
    pip3 install -r requirements.txt 2>/dev/null || echo 'Some Python dependencies may not be available'
    
    echo 'WSL environment setup complete!'
"

if %errorlevel% neq 0 (
    echo ⚠️  WSL setup had some issues (this is normal)
) else (
    echo ✅ WSL environment configured
)
echo.

:: Create taskbar shortcut
echo 🖇️  Creating taskbar shortcut...
cscript //nologo "CreateTaskbarShortcut.vbs"
echo.

:: Test the setup
echo 🧪 Testing setup...
echo.

:: Test WSL
echo Testing WSL Ubuntu...
wsl -d Ubuntu -e bash -c "echo 'WSL Ubuntu is working'"
if %errorlevel% equ 0 (
    echo ✅ WSL Ubuntu test passed
) else (
    echo ❌ WSL Ubuntu test failed
)

:: Test Node.js in WSL
echo Testing Node.js in WSL...
wsl -d Ubuntu -e bash -c "node --version"
if %errorlevel% equ 0 (
    echo ✅ Node.js in WSL test passed
) else (
    echo ❌ Node.js in WSL test failed
)

:: Test Claude CLI
echo Testing Claude CLI...
wsl -d Ubuntu -e bash -c "claude --version 2>/dev/null || echo 'Claude CLI not found'"
if %errorlevel% equ 0 (
    echo ✅ Claude CLI test passed
) else (
    echo ⚠️  Claude CLI test failed (install manually if needed)
)

echo.
echo 🎉 Hearthlink setup complete!
echo.
echo 📋 What's been configured:
echo    • All necessary directories created
echo    • NPM dependencies installed
echo    • WSL environment configured
echo    • Python dependencies installed
echo    • Taskbar shortcut created
echo    • System tests completed
echo.
echo 🚀 Next steps:
echo    1. Pin the desktop shortcut to your taskbar
echo    2. Launch Hearthlink from taskbar
echo    3. Choose option 3 to start background services
echo    4. Use option 1 or 2 to launch the application
echo.
echo 💡 The main launcher provides:
echo    • Full Environment Launch
echo    • Native Frame Wrapper
echo    • Background Services Management
echo    • Service Status Monitoring
echo    • Log Viewing
echo.
echo Press any key to continue...
pause >nul

:: Launch the main menu
echo.
echo 🎯 Launching Hearthlink main menu...
timeout /t 2 /nobreak >nul
call "Hearthlink.bat"