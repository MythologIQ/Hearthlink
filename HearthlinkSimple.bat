@echo off
setlocal enabledelayedexpansion

:: Simple Hearthlink launcher without Tauri complexity
:: This launches Electron directly with proper logging

:: Hide the console window immediately
if not "%1"=="MINIMIZED" start /min cmd /c "%~dpnx0 MINIMIZED" & exit

:: Set project paths
set "PROJECT_PATH=/mnt/g/MythologIQ/Hearthlink"
set "WIN_PROJECT_PATH=G:\MythologIQ\Hearthlink"

:: Create log directory
if not exist "%WIN_PROJECT_PATH%\logs" mkdir "%WIN_PROJECT_PATH%\logs"

:: Generate timestamp for logs
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set "DATE_STAMP=%%c%%a%%b"
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set "TIME_STAMP=%%a%%b"
set "LOG_FILE=%WIN_PROJECT_PATH%\logs\hearthlink_simple_%DATE_STAMP%_%TIME_STAMP%.log"

:: Log start
echo [%date% %time%] Hearthlink Simple Launch Starting... >> "%LOG_FILE%"

:: Start background services silently
echo [%date% %time%] Starting background services... >> "%LOG_FILE%"
start /min "" "%WIN_PROJECT_PATH%\HearthlinkService.bat"

:: Wait for services to initialize
timeout /t 3 /nobreak >nul

:: Change to project directory
cd /d "%WIN_PROJECT_PATH%"

:: Launch Electron directly
echo [%date% %time%] Launching Electron directly... >> "%LOG_FILE%"
npm run launch >> "%LOG_FILE%" 2>&1

echo [%date% %time%] Hearthlink Simple Launch Completed >> "%LOG_FILE%"