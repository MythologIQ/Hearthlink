@echo off
title Install and Run Hearthlink
color 0A
echo ================================
echo   INSTALL AND RUN HEARTHLINK
echo ================================
echo.

cd /d "%~dp0"
echo Current directory: %CD%
echo.

echo [INSTALL] Installing electron locally...
echo This will take a few minutes...
echo.

call npm install electron --save-dev
echo [INSTALL] Electron install completed with error level: %errorlevel%
echo.

echo [INSTALL] Installing all dependencies...
call npm install
echo [INSTALL] npm install completed with error level: %errorlevel%
echo.

echo [INSTALL] Building React app...
call npm run build
echo [INSTALL] Build completed with error level: %errorlevel%
echo.

echo [INSTALL] Checking if electron was installed...
if exist "node_modules\.bin\electron.exe" (
    echo [INSTALL] Found electron.exe in node_modules
    echo.
    echo Press any key to start Hearthlink...
    pause >nul
    echo.
    echo [INSTALL] Starting Hearthlink with local electron...
    "node_modules\.bin\electron.exe" main.js
    echo [INSTALL] Hearthlink closed with error level: %errorlevel%
) else (
    echo [INSTALL] electron.exe still not found after install
)

echo.
echo [INSTALL] Install and run completed
echo.
echo Press any key to exit...
pause >nul
echo [INSTALL] Final message - script ending normally