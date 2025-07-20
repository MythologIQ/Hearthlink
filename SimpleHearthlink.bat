@echo off
setlocal enabledelayedexpansion
title Hearthlink - Simple Mode
color 0B

echo.
echo  ╔═══════════════════════════════════════════════════════════════════════════════╗
echo  ║                          Hearthlink - Simple Mode                           ║
echo  ║                        Works without full WSL setup                         ║
echo  ║                                 v1.3.0                                       ║
echo  ╚═══════════════════════════════════════════════════════════════════════════════╝
echo.

:MENU
echo 🔗 Choose your launch option:
echo.
echo  [1] 🚀 Launch Hearthlink (Windows Native)
echo  [2] 🖼️  Launch Native Frame Wrapper
echo  [3] 🔧 Try WSL Launch (if available)
echo  [4] 🛠️  Run WSL Diagnostic
echo  [5] 📊 Check System Status
echo  [6] ❌ Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto LAUNCH_NATIVE
if "%choice%"=="2" goto LAUNCH_FRAME
if "%choice%"=="3" goto LAUNCH_WSL
if "%choice%"=="4" goto DIAGNOSTIC
if "%choice%"=="5" goto STATUS
if "%choice%"=="6" goto EXIT

echo Invalid choice. Please try again.
timeout /t 2 /nobreak >nul
goto MENU

:LAUNCH_NATIVE
echo.
echo 🚀 Launching Hearthlink (Windows Native)...
echo.
cd /d "%~dp0"
npm run launch
goto END

:LAUNCH_FRAME
echo.
echo 🖼️  Launching Native Frame Wrapper...
echo.
cd /d "%~dp0"
npm run native:frame
goto END

:LAUNCH_WSL
echo.
echo 🔧 Trying WSL Launch...
echo.
wsl --list >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ WSL not available
    echo    Use option 4 to diagnose WSL issues
    timeout /t 3 /nobreak >nul
    goto MENU
) else (
    echo ✅ WSL available, launching...
    wsl -d Ubuntu -e bash -c "cd '/mnt/g/MythologIQ/Hearthlink' && npm run launch"
)
goto END

:DIAGNOSTIC
echo.
echo 🛠️  Running WSL Diagnostic...
echo.
call "DiagnoseWSL.bat"
goto MENU

:STATUS
echo.
echo 📊 System Status Check...
echo.

:: Check Node.js
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Node.js is installed
    node --version
) else (
    echo ❌ Node.js not found
)

:: Check NPM
npm --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ NPM is installed
    npm --version
) else (
    echo ❌ NPM not found
)

:: Check WSL
wsl --list >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ WSL is available
    wsl --list --verbose 2>nul
) else (
    echo ❌ WSL not available
)

:: Check Docker
where docker >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker is installed
) else (
    echo ❌ Docker not found
)

:: Check Electron
where electron >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Electron is available
) else (
    echo ⚠️  Electron not in PATH (normal if using npm)
)

echo.
pause
goto MENU

:EXIT
echo.
echo 👋 Thanks for using Hearthlink!
echo.
exit /b 0

:END
echo.
echo 🎯 Hearthlink session ended
echo.
pause
goto MENU