@echo off
title Hearthlink - AI Orchestration Hub
echo.
echo ================================
echo    HEARTHLINK LAUNCH SYSTEM
echo ================================
echo.

:: Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

:: Check if npm is available
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: npm is not available
    echo Please ensure npm is installed with Node.js
    pause
    exit /b 1
)

echo [INFO] Node.js version: 
node --version
echo [INFO] npm version: 
npm --version
echo.

:: Navigate to Hearthlink directory
cd /d "%~dp0"
echo [INFO] Working directory: %cd%
echo.

:: Check if package.json exists
if not exist "package.json" (
    echo ERROR: package.json not found
    echo Please run this script from the Hearthlink project root
    pause
    exit /b 1
)

:: Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo [INFO] Installing dependencies...
    echo [WARNING] This may take a few minutes...
    npm install
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed
    echo.
)

:: Check if we need to build
if not exist "build" (
    echo [INFO] Build directory not found, creating production build...
    echo [WARNING] This may take several minutes...
    
    npm run build
    if %errorlevel% neq 0 (
        echo [WARNING] Build failed, continuing anyway...
        echo [INFO] Hearthlink will run in development mode
        echo.
    ) else (
        echo [SUCCESS] Production build created
        echo.
    )
) else (
    echo [INFO] Build directory found
)

:: Launch Hearthlink
echo.
echo ================================
echo    HEARTHLINK STARTING...
echo ================================
echo.
echo Features Available:
echo  * Alden AI Orchestrator
echo  * Project Command System
echo  * Synapse Gateway
echo  * Core Orchestration
echo  * StarCraft UI Theme
echo  * Memory and Learning System
echo.
echo [INFO] Starting Hearthlink...
echo [INFO] Press Ctrl+C to stop Hearthlink
echo.

:: Start Electron (this matches the package.json "start" script)
npm start

echo.
echo ================================
echo    HEARTHLINK SHUTDOWN
echo ================================
echo.
echo Thank you for using Hearthlink!
echo.
pause