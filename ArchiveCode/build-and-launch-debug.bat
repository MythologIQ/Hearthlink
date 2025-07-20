@echo off
title Hearthlink - DEBUG Build and Launch
color 0A
echo ================================
echo   HEARTHLINK DEBUG BUILD
echo ================================
echo.
echo [DEBUG] This terminal will NOT close automatically
echo [DEBUG] You must manually close it or press Ctrl+C
echo.
echo [LOG] Script started at %date% %time%
echo [LOG] Current directory: %CD%
echo [LOG] Script location: %~dp0
echo [LOG] Windows version: %OS%
echo [LOG] Computer name: %COMPUTERNAME%
echo [LOG] Username: %USERNAME%
echo.

:: Navigate to script directory
echo [LOG] Changing to script directory...
cd /d "%~dp0"
echo [LOG] Changed to directory: %CD%
echo.

:: Check Node.js
echo [LOG] Checking for Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Error level: %errorlevel%
    echo ERROR: Node.js not found. Please install Node.js from https://nodejs.org/
    echo [LOG] Pausing for user input...
    pause
    goto :end
)

echo [LOG] Node.js found successfully
echo Node.js version: 
node --version
echo [LOG] NPM version:
npm --version
echo.

:: Install dependencies if needed
echo [LOG] Checking for node_modules directory...
if not exist "node_modules" (
    echo [LOG] node_modules not found, installing dependencies...
    echo Installing dependencies...
    echo [LOG] Running: npm install
    npm install
    echo [LOG] npm install completed with error level: %errorlevel%
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies. Error level: %errorlevel%
        echo ERROR: Failed to install dependencies
        echo [LOG] Pausing for user input...
        pause
        goto :end
    )
    echo [LOG] Dependencies installed successfully
    echo Dependencies installed successfully
    echo.
) else (
    echo [LOG] node_modules directory found, skipping installation
)

:: Build React app
echo [LOG] Starting React build process...
echo Building React application...
echo This may take a few minutes...
echo [LOG] Running: npm run build
echo [LOG] Build started at %time%
echo.

npm run build
echo [LOG] Build completed at %time% with error level: %errorlevel%
if %errorlevel% neq 0 (
    echo [ERROR] Build failed with error level: %errorlevel%
    echo ERROR: Build failed
    echo.
    echo Common solutions:
    echo 1. Try: npm cache clean --force
    echo 2. Try: rmdir /s node_modules && npm install
    echo 3. Check for TypeScript errors
    echo.
    echo [LOG] Pausing for user input...
    pause
    goto :end
)

echo [LOG] Build completed successfully!
echo Build completed successfully!
echo.

:: Launch Hearthlink
echo [LOG] Preparing to launch Hearthlink...
echo Starting Hearthlink...
echo.
echo [LOG] Waiting for user input to start Hearthlink...
echo Press any key to start Hearthlink...
pause >nul
echo [LOG] User pressed key, continuing...

echo.
echo [LOG] Starting Hearthlink at %time%...
echo Starting Hearthlink... (Terminal will remain open)
echo [LOG] Running: npm start
echo [LOG] This terminal will stay open
echo.

npm start

echo [LOG] npm start completed at %time% with error level: %errorlevel%
if %errorlevel% neq 0 (
    echo [ERROR] Hearthlink failed to start with error level: %errorlevel%
    echo.
    echo ERROR: Hearthlink failed to start
    echo Error code: %errorlevel%
    echo.
)

:end
echo.
echo [LOG] Build and launch process completed at %time%
echo Build and launch process completed.
echo [LOG] This terminal will stay open for debugging
echo.
echo ================================
echo   TERMINAL STAYING OPEN
echo ================================
echo.
echo To close this terminal:
echo 1. Press Ctrl+C
echo 2. Type 'exit' and press Enter
echo 3. Close the window manually
echo.
echo [LOG] Entering infinite loop to keep terminal open...
:loop
timeout /t 30 /nobreak >nul
echo [LOG] Still running... %time%
goto :loop