@echo off
title Hearthlink - Build and Launch
cls
echo ================================
echo   HEARTHLINK BUILD AND LAUNCH
echo ================================
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
echo [LOG] Directory contents:
dir /b
echo.

:: Check Node.js
echo [LOG] Checking for Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Error level: %errorlevel%
    echo ERROR: Node.js not found. Please install Node.js from https://nodejs.org/
    echo [LOG] Pausing for user input...
    pause
    echo [LOG] Exiting with error code 1
    exit /b 1
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
        echo [LOG] Exiting with error code 1
        exit /b 1
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
    echo [LOG] Exiting with error code 1
    exit /b 1
)

echo [LOG] Build completed successfully!
echo Build completed successfully!
echo.

:: Check build directory
echo [LOG] Verifying build directory structure...
if exist "build\index.html" (
    echo [LOG] build/index.html found
    echo ✓ build/index.html created
) else (
    echo [LOG] build/index.html NOT found
    echo ✗ build/index.html not found
    echo Build may have failed
    echo [LOG] Pausing for user input...
    pause
    echo [LOG] Exiting with error code 1
    exit /b 1
)

if exist "build\static" (
    echo [LOG] build/static directory found
    echo ✓ build/static directory created
) else (
    echo [LOG] build/static directory NOT found
    echo ✗ build/static directory not found
)

:: Copy assets to build directory
echo [LOG] Starting asset copy process...
echo Copying assets...
if not exist "build\assets" (
    echo [LOG] Creating build/assets directory...
    mkdir "build\assets"
    echo [LOG] build/assets directory created
) else (
    echo [LOG] build/assets directory already exists
)

if exist "src\assets" (
    echo [LOG] Copying from src/assets to build/assets...
    xcopy "src\assets\*" "build\assets\" /Y /Q
    echo [LOG] xcopy completed with error level: %errorlevel%
    echo ✓ Assets copied from src to build directory
) else (
    echo [LOG] src/assets directory not found
)

if exist "public\assets" (
    echo [LOG] Copying from public/assets to build/assets...
    xcopy "public\assets\*" "build\assets\" /Y /Q
    echo [LOG] xcopy completed with error level: %errorlevel%
    echo ✓ Public assets copied to build directory
) else (
    echo [LOG] public/assets directory not found
)

:: Verify Loading.png is copied
echo [LOG] Verifying Loading.png...
if exist "build\assets\Loading.png" (
    echo [LOG] Loading.png found in build directory
    echo ✓ Loading.png found in build directory
) else (
    echo [LOG] Loading.png missing from build directory
    echo ✗ Loading.png missing - copying manually
    if exist "src\assets\Loading.png" (
        echo [LOG] Copying Loading.png from src/assets...
        copy "src\assets\Loading.png" "build\assets\Loading.png"
        echo [LOG] Manual copy completed with error level: %errorlevel%
        echo ✓ Loading.png copied manually
    ) else (
        echo [LOG] Loading.png not found in src/assets either
    )
)

echo.
echo ================================
echo   LAUNCHING HEARTHLINK
echo ================================
echo.

:: Launch Hearthlink
echo [LOG] Preparing to launch Hearthlink...
echo Starting Hearthlink...
echo.
echo ================================
echo   HEARTHLINK SHOULD NOW LAUNCH
echo ================================
echo.
echo If Hearthlink window doesn't appear:
echo 1. Check for any error messages above
echo 2. Look for the Hearthlink window in taskbar
echo 3. Try Alt+Tab to find the window
echo.
echo [LOG] Waiting for user input to start Hearthlink...
echo Press any key to start Hearthlink...
pause >nul
echo [LOG] User pressed key, continuing...

echo.
echo [LOG] Starting Hearthlink at %time%...
echo Starting Hearthlink... (Terminal will remain open)
echo [LOG] Running: start /wait npm start
echo [LOG] This terminal will stay open until Hearthlink closes
echo.

start /wait npm start

echo [LOG] npm start completed at %time% with error level: %errorlevel%
if %errorlevel% neq 0 (
    echo [ERROR] Hearthlink failed to start with error level: %errorlevel%
    echo.
    echo ERROR: Hearthlink failed to start
    echo Error code: %errorlevel%
    echo.
    echo Troubleshooting:
    echo 1. Check if another instance is running
    echo 2. Try: taskkill /f /im electron.exe
    echo 3. Run debug-launch.bat for more info
    echo.
) else (
    echo [LOG] Hearthlink closed normally
    echo.
    echo Hearthlink has been closed.
)

echo.
echo [LOG] Build and launch process completed at %time%
echo Build and launch process completed.
echo [LOG] Waiting for final user input before exit...
echo Press any key to exit...
pause
echo [LOG] Script ending at %time%