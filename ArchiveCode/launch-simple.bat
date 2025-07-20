@echo off
cls
echo ================================
echo    HEARTHLINK QUICK LAUNCH
echo ================================
echo.

:: Navigate to script directory
cd /d "%~dp0"

:: Check for Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

:: Install dependencies if needed
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

:: Start Hearthlink
echo Starting Hearthlink...
echo.
npm start

pause