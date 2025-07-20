@echo off
setlocal enabledelayedexpansion

:: Hearthlink Quick Fix - Windows Native Launcher
echo ========================================
echo HEARTHLINK QUICK FIX LAUNCHER
echo ========================================

cd /d "%~dp0"

echo [1/4] Environment Check...
echo Platform: Windows
echo Directory: %CD%

echo [2/4] Checking dependencies...
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install --prefer-offline --no-audit
    if %errorlevel% neq 0 (
        echo Warning: npm install had issues, continuing...
    )
)

echo [3/4] Building application...
if not exist "build\index.html" (
    echo Building React app...
    call npm run build
    if %errorlevel% neq 0 (
        echo Build failed, trying emergency launch...
        goto EMERGENCY
    )
)

echo [4/4] Launching application...

:: Try Electron launch first
echo Attempting Electron launch...
call npm run launch
if %errorlevel% equ 0 (
    echo Success! Application launched via Electron.
    goto END
)

:EMERGENCY
echo Electron launch failed, trying emergency methods...

:: Method 1: Direct file protocol
if exist "build\index.html" (
    echo Method 1: File protocol launch...
    start "" "%CD%\build\index.html"
    timeout /t 3 /nobreak >nul
)

:: Method 2: Local test page
if exist "public\test.html" (
    echo Method 2: Test page launch...
    start "" "%CD%\public\test.html"
    timeout /t 3 /nobreak >nul
)

:: Method 3: Development server
echo Method 3: Starting development server...
echo Note: This will start a local server. Keep this window open.
echo Access the app at: http://localhost:3005
call npm run start:react

:END
echo.
echo ========================================
echo Launch completed. Check your browser.
echo ========================================
pause