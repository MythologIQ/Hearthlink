@echo off
setlocal enabledelayedexpansion

:: Direct Electron launch without npm scripts
if not "%1"=="MINIMIZED" start /min cmd /c "%~dpnx0 MINIMIZED" & exit

set "WIN_PROJECT_PATH=G:\MythologIQ\Hearthlink"
cd /d "%WIN_PROJECT_PATH%"

:: Generate timestamp for logs
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set "DATE_STAMP=%%c%%a%%b"
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set "TIME_STAMP=%%a%%b"
set "LOG_FILE=%WIN_PROJECT_PATH%\logs\hearthlink_direct2_%DATE_STAMP%_%TIME_STAMP%.log"

echo [%date% %time%] Starting Hearthlink Direct2... >> "%LOG_FILE%"

:: Launch Electron directly bypassing npm
echo [%date% %time%] Launching Electron directly... >> "%LOG_FILE%"
electron . >> "%LOG_FILE%" 2>&1

echo [%date% %time%] Electron process completed >> "%LOG_FILE%"