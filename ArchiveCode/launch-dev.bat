@echo off
title Hearthlink - Development Mode
cls
echo ================================
echo  HEARTHLINK DEVELOPMENT LAUNCH
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
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

:: Start in development mode
echo Starting Hearthlink in development mode...
echo.
echo [INFO] This will start both React dev server and Electron
echo [INFO] React will be available at http://localhost:3000
echo [INFO] Electron will launch automatically
echo.
echo Press Ctrl+C to stop both servers
echo.

:: Start React dev server in background
start "React Dev Server" cmd /c "npm run start:react"

:: Wait for React to start
echo Waiting for React dev server to start...
timeout /t 10 /nobreak

:: Start Electron
echo Starting Electron...
set NODE_ENV=development
npm start

echo.
echo Development servers stopped.
pause