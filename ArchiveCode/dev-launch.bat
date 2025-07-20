@echo off
title Hearthlink - Development Launch
color 0B
echo ================================
echo   HEARTHLINK DEVELOPMENT LAUNCH
echo ================================
echo.

cd /d "%~dp0"

:: Kill any existing processes
echo [DEV] Killing existing processes...
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im npm.exe >nul 2>&1
taskkill /f /im electron.exe >nul 2>&1

:: Start React development server in background
echo [DEV] Starting React development server...
start "React Dev Server" /min cmd /c "npm run start:react"

:: Wait for React server to start
echo [DEV] Waiting for React development server to start...
timeout /t 10 /nobreak >nul

:: Set development environment
set NODE_ENV=development
set ELECTRON_IS_DEV=1

:: Start Electron
echo [DEV] Starting Electron with development server...
echo [DEV] This will show the actual updated UI
echo.
electron .

echo [DEV] Electron closed
echo.
echo Press any key to close React server and exit...
pause >nul

:: Kill React server
taskkill /f /im node.exe >nul 2>&1
echo [DEV] React server stopped