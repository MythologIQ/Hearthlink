@echo off
title Hearthlink Native Frame
color 0B

echo.
echo  ╔═══════════════════════════════════════════════════════════════════════════════╗
echo  ║                         Hearthlink Native Frame                              ║
echo  ║                    Visual Container for Electron App                         ║
echo  ║                                 v1.3.0                                       ║
echo  ╚═══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 🖼️  Starting Hearthlink Native Frame...
echo.

:: Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js first.
    echo    Visit: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

:: Check if Cargo is installed
where cargo >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Cargo ^(Rust^) is not installed. Please install Rust first.
    echo    Visit: https://rustup.rs/
    echo.
    pause
    exit /b 1
)

:: Navigate to project directory
cd /d "%~dp0"

:: Check if we're in the right directory
if not exist "src-tauri\Cargo.toml" (
    echo ❌ Tauri project not found. Make sure you're in the Hearthlink directory.
    echo.
    pause
    exit /b 1
)

echo ✅ Environment checks passed
echo.

echo 🚀 Starting Native Frame...
echo.
echo 💡 The native frame will:
echo    • Create a visual container window
echo    • Auto-start and embed the Electron app
echo    • Provide native window controls
echo    • Show status and port information
echo    • Minimize to system tray when closed
echo.

:: Start the native frame
call npm run tauri:dev

echo.
echo 🛑 Native frame has been stopped
pause