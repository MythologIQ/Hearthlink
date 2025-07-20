@echo off
title Direct Electron Test
color 0D
echo ================================
echo   DIRECT ELECTRON TEST
echo ================================
echo.
echo Bypassing npm start and running electron directly...
echo.

cd /d "%~dp0"
echo Current directory: %CD%
echo.

echo [TEST] Checking if electron is installed...
if exist "node_modules\.bin\electron.exe" (
    echo [TEST] Found electron.exe in node_modules
    echo [TEST] Running electron directly...
    echo.
    echo Press any key to start electron...
    pause >nul
    echo.
    echo [TEST] Starting electron main.js...
    "node_modules\.bin\electron.exe" main.js
    echo [TEST] Electron closed with error level: %errorlevel%
) else (
    echo [TEST] electron.exe not found in node_modules\.bin\
    echo [TEST] Checking global electron...
    where electron >nul 2>&1
    if %errorlevel% equ 0 (
        echo [TEST] Found global electron
        echo [TEST] Running global electron...
        echo.
        echo Press any key to start electron...
        pause >nul
        echo.
        echo [TEST] Starting electron main.js...
        electron main.js
        echo [TEST] Electron closed with error level: %errorlevel%
    ) else (
        echo [TEST] No electron found anywhere
    )
)

echo.
echo [TEST] Direct electron test completed
echo.
echo Press any key to exit...
pause >nul
echo [TEST] Final message - script ending normally