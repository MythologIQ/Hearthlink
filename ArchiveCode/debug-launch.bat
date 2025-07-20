@echo off
title Hearthlink - Debug Launch
cls
echo ================================
echo   HEARTHLINK DEBUG LAUNCH
echo ================================
echo.

:: Navigate to script directory
cd /d "%~dp0"

:: Show current directory and files
echo Current directory: %cd%
echo.
echo Checking key files:
if exist "package.json" (
    echo ✓ package.json found
) else (
    echo ✗ package.json missing
)

if exist "main.js" (
    echo ✓ main.js found
) else (
    echo ✗ main.js missing
)

if exist "public\index.html" (
    echo ✓ public\index.html found
) else (
    echo ✗ public\index.html missing
)

if exist "public\test.html" (
    echo ✓ public\test.html found
) else (
    echo ✗ public\test.html missing
)

if exist "public\assets\Hearthlink.png" (
    echo ✓ public\assets\Hearthlink.png found
) else (
    echo ✗ public\assets\Hearthlink.png missing
)

if exist "src\assets\Hearthlink.png" (
    echo ✓ src\assets\Hearthlink.png found
) else (
    echo ✗ src\assets\Hearthlink.png missing
)

if exist "node_modules" (
    echo ✓ node_modules found
) else (
    echo ✗ node_modules missing - will install
)

if exist "build" (
    echo ✓ build directory found
    dir build /b
) else (
    echo ✗ build directory missing
)

echo.
echo ================================
echo.

:: Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found
    pause
    exit /b 1
)

echo Node.js version:
node --version
echo.

:: Install dependencies if needed
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

:: Start with debug output
echo Starting Hearthlink with debug output...
echo.
echo This will show console output to help debug issues.
echo Look for any error messages or failed file loads.
echo.
echo Press Ctrl+C to stop
echo.

:: Start Electron with debug
set ELECTRON_ENABLE_LOGGING=1
set DEBUG=*
npm start

pause