@echo off
title Hearthlink - Fix and Launch
color 0A
echo ================================
echo   HEARTHLINK FIX AND LAUNCH
echo ================================
echo.

:: Navigate to script directory
cd /d "%~dp0"

:: Kill any existing processes
echo [FIX] Killing existing processes...
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im npm.exe >nul 2>&1
taskkill /f /im electron.exe >nul 2>&1
echo [FIX] Processes killed

:: Clear build directory
echo [FIX] Clearing build directory...
rmdir /s /q build >nul 2>&1
echo [FIX] Build directory cleared

:: Fix permissions and create build directory
echo [FIX] Creating build directory...
mkdir build >nul 2>&1
mkdir build\assets >nul 2>&1
mkdir build\static >nul 2>&1

:: Copy assets manually to avoid permission issues
echo [FIX] Copying assets manually...
copy "public\assets\*" "build\assets\" >nul 2>&1
copy "src\assets\*" "build\assets\" >nul 2>&1

:: Run development server instead of build
echo [FIX] Starting development server...
echo This will show the updated UI with proper launch page
echo.
echo Press any key to start development server...
pause >nul

:: Start React development server
echo [FIX] Starting React development server...
start /min npm run start

:: Wait for React server to start
echo [FIX] Waiting for React server to start...
timeout /t 5 /nobreak >nul

:: Start Electron with development server
echo [FIX] Starting Electron with development server...
set ELECTRON_IS_DEV=1
npm run electron-dev

echo [FIX] Process completed
pause