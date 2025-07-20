@echo off
title Kill and Launch Hearthlink
color 0C
echo ================================
echo   KILL AND LAUNCH HEARTHLINK
echo ================================
echo.

cd /d "%~dp0"
echo Current directory: %CD%
echo.

echo [KILL] Killing any existing Electron processes...
taskkill /f /im electron.exe >nul 2>&1
echo [KILL] Electron processes killed (error level: %errorlevel%)
echo.

echo [KILL] Waiting 3 seconds for processes to fully close...
timeout /t 3 /nobreak >nul
echo.

echo [KILL] Building React app (this may take a few minutes)...
echo [KILL] The build process will run and then we'll launch...
echo.

call npm run build
set BUILD_ERROR=%errorlevel%
echo.
echo [KILL] Build completed with error level: %BUILD_ERROR%
echo.

if %BUILD_ERROR% neq 0 (
    echo [KILL] Build failed, cannot launch
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo [KILL] Build succeeded! Now launching Hearthlink...
echo.

echo [KILL] Checking for built files...
if exist "build\index.html" (
    echo [KILL] Found build\index.html
) else (
    echo [KILL] build\index.html not found
)

echo.
echo [KILL] Starting Hearthlink...
echo [KILL] This will open the Hearthlink window
echo.

call npm start
set START_ERROR=%errorlevel%

echo.
echo [KILL] Hearthlink closed with error level: %START_ERROR%
echo.

echo [KILL] Process completed
echo.
echo Press any key to exit...
pause >nul
echo [KILL] Final message - script ending normally