@echo off
title Hearthlink Native Wrapper
color 0A

echo.
echo  ╔═══════════════════════════════════════════════════════════════════════════════╗
echo  ║                          Hearthlink Native Wrapper                           ║
echo  ║                                   v1.3.0                                     ║
echo  ╚═══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 🔗 Initializing Hearthlink Native Wrapper...
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

:: Navigate to project directory
cd /d "%~dp0"

:: Check if we're in the right directory
if not exist "package.json" (
    echo ❌ Not in the correct Hearthlink directory
    echo    Make sure this script is in the Hearthlink root folder
    echo.
    pause
    exit /b 1
)

:: Check if native-wrapper.js exists
if not exist "native-wrapper.js" (
    echo ❌ Native wrapper script not found
    echo    Make sure native-wrapper.js is in the current directory
    echo.
    pause
    exit /b 1
)

echo ✅ Environment checks passed
echo.

:: Create userData directory if it doesn't exist
if not exist "userData" mkdir userData
if not exist "userData\logs" mkdir userData\logs

echo 🚀 Starting Hearthlink Native Wrapper...
echo.
echo 💡 The wrapper will:
echo    • Auto-start the Electron application
echo    • Monitor and restart if it crashes
echo    • Persist in the background
echo    • Log all activities to userData\logs\native-wrapper.log
echo.
echo 🔄 To stop the wrapper, press Ctrl+C
echo.

:: Start the native wrapper
node native-wrapper.js start

echo.
echo 🛑 Native wrapper has been stopped
pause