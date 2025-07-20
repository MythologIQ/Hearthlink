@echo off
title Simple Launch
color 0E
echo ================================
echo   SIMPLE LAUNCH
echo ================================
echo.

cd /d "%~dp0"
echo Current directory: %CD%
echo.

echo [SIMPLE] Killing any existing Electron processes...
taskkill /f /im electron.exe >nul 2>&1
echo [SIMPLE] Done
echo.

echo [SIMPLE] Skipping build - using existing build directory
echo [SIMPLE] Launching Hearthlink directly...
echo.

if exist "build\index.html" (
    echo [SIMPLE] Found existing build - launching now...
    echo.
    echo Press any key to launch Hearthlink...
    pause >nul
    echo.
    call npm start
    echo.
    echo [SIMPLE] Hearthlink closed
) else (
    echo [SIMPLE] No build directory found
    echo [SIMPLE] You need to run build first
)

echo.
echo [SIMPLE] Launch completed
echo.
echo Press any key to exit...
pause >nul
echo [SIMPLE] Script ending