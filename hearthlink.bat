@echo off
setlocal enabledelayedexpansion

:: Hearthlink Direct Launch
:: This launcher starts Hearthlink immediately without command prompt menus
:: Dev menu is available within the application interface

title Hearthlink - Direct Launch

:: Set project paths
set "PROJECT_PATH=/mnt/g/MythologIQ/Hearthlink"
set "WIN_PROJECT_PATH=G:\MythologIQ\Hearthlink"

:: Quick launch via HearthlinkDirect
echo 🚀 Starting Hearthlink...
call "%WIN_PROJECT_PATH%\HearthlinkDirect.bat"

:: If direct launch fails, provide minimal fallback
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Direct launch failed. Attempting fallback...
    echo.
    
    :: Start services manually
    start /min "" "HearthlinkService.bat"
    timeout /t 3 /nobreak >nul
    
    :: Try regular launch
    wsl -d Ubuntu -e bash -c "cd '%PROJECT_PATH%' && npm run launch"
)

:: Keep window open only if there's an error
if %errorlevel% neq 0 (
    echo.
    echo ❌ Launch failed. Check logs for details.
    pause
)