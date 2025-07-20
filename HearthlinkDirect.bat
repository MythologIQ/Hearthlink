@echo off
setlocal enabledelayedexpansion

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
set "LOG_FILE=%WIN_PROJECT_PATH%\logs\hearthlink_direct_%DATE_STAMP%_%TIME_STAMP%.log"

:: Log start
echo [%date% %time%] Hearthlink Direct Launch Starting... >> "%LOG_FILE%"

:: Start background services silently
echo [%date% %time%] Starting background services... >> "%LOG_FILE%"
start /min "" "%WIN_PROJECT_PATH%\HearthlinkService.bat"

:: Wait a moment for services to initialize
timeout /t 2 /nobreak >nul

:: Launch Hearthlink directly
echo [%date% %time%] Launching Hearthlink Native Frame... >> "%LOG_FILE%"
cd /d "%WIN_PROJECT_PATH%"

:: Try native frame first, fallback to regular launch
echo [%date% %time%] Attempting to start native frame... >> "%LOG_FILE%"
npm run native:frame >> "%LOG_FILE%" 2>&1
if %errorlevel% neq 0 (
    echo [%date% %time%] Native frame failed with error %errorlevel%, trying regular launch... >> "%LOG_FILE%"
    npm run launch >> "%LOG_FILE%" 2>&1
) else (
    echo [%date% %time%] Native frame started successfully >> "%LOG_FILE%"
)

echo [%date% %time%] Hearthlink Direct Launch Completed >> "%LOG_FILE%"