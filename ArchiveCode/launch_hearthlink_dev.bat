@echo off
setlocal

:: Set up log file
set APP_DIR=%~dp0
set LOG_DIR=%APP_DIR%logs
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
set LOG_FILE=%LOG_DIR%\hearthlink_launch_%DATE:/=-%_%TIME::=-%.log
for /f "tokens=1-3 delims=:." %%a in ("%TIME%") do set TIMESTAMP=%%a-%%b-%%c
set LOG_FILE=%LOG_DIR%\hearthlink_launch_%DATE:/=-%_%TIMESTAMP%.log

echo ======================================== > "%LOG_FILE%"
echo Hearthlink Minimal Launch Log >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"
echo Launch Time: %DATE% %TIME% >> "%LOG_FILE%"
echo App Directory: %APP_DIR% >> "%LOG_FILE%"
echo Log File: %LOG_FILE% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

:: Set environment variables and launch
set NODE_ENV=development
set ELECTRON_START_URL=file://%APP_DIR%build/index.html

echo [%TIME%] Launching Electron with npm start... >> "%LOG_FILE%"
cd /d %APP_DIR%
call npm start >> "%LOG_FILE%" 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Launch failed, check log file: %LOG_FILE%
    pause
    exit /b 1
)

echo [%TIME%] Launch completed successfully! >> "%LOG_FILE%"
pause
exit /b 0