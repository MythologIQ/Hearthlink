@echo off
setlocal enabledelayedexpansion
title Hearthlink Quick Setup
color 0A

echo.
echo  ╔═══════════════════════════════════════════════════════════════════════════════╗
echo  ║                        Hearthlink Quick Setup                                ║
echo  ║                     Skip Prerequisites - Direct Setup                        ║
echo  ║                                v1.3.0                                        ║
echo  ╚═══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 🚀 Setting up Hearthlink (skipping prerequisite checks)...
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

:: Install NPM dependencies
echo 📦 Installing NPM dependencies...
call npm install
if %errorlevel% neq 0 (
    echo ⚠️  NPM install had issues - continuing anyway
) else (
    echo ✅ NPM dependencies installed
)
echo.

:: Create taskbar shortcut
echo 🖇️  Creating taskbar shortcut...
cscript //nologo "CreateTaskbarShortcut.vbs"
echo.

:: Test basic functionality
echo 🧪 Testing basic functionality...

:: Test Node.js
echo Testing Node.js...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Node.js is working
) else (
    echo ❌ Node.js test failed
)

:: Test WSL (without stopping on failure)
echo Testing WSL...
wsl echo "WSL test" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ WSL is working
) else (
    echo ⚠️  WSL test failed - you may need to configure it manually
)

echo.
echo 🎉 Quick setup complete!
echo.
echo 📋 What's been done:
echo    • All necessary directories created
echo    • NPM dependencies installed (if possible)
echo    • Taskbar shortcut created
echo    • Basic functionality tested
echo.
echo 🚀 Next steps:
echo    1. Pin the desktop shortcut to your taskbar
echo    2. Launch Hearthlink from taskbar
echo    3. Try the different launch options
echo.
echo 💡 If WSL isn't working properly:
echo    • Run: wsl --install
echo    • Or install Ubuntu from Microsoft Store
echo    • Then try the full setup again
echo.
echo Press any key to launch Hearthlink...
pause >nul

:: Launch the main menu
echo.
echo 🎯 Launching Hearthlink main menu...
timeout /t 2 /nobreak >nul
call "Hearthlink.bat"