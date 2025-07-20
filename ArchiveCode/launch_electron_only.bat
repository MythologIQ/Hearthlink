@echo off
setlocal enabledelayedexpansion

:: ========================================
:: HEARTHLINK ELECTRON LAUNCHER
:: ========================================
:: This launcher starts only the Electron app without Python backend
:: to avoid hanging issues during development

:: Set application directory
set APP_DIR=%~dp0
cd /d "%APP_DIR%"

:: Set log directory
set LOG_DIR=%APP_DIR%logs
set DATE=%date:~-4,4%-%date:~-10,2%-%date:~-7,2%
for /f "tokens=1-3 delims=:." %%a in ("%TIME%") do set TIMESTAMP=%%a-%%b-%%c
set LOG_FILE=%LOG_DIR%\hearthlink_electron_%DATE%_%TIMESTAMP%.log

:: Ensure log directory exists
if not exist "%LOG_DIR%" (
    echo Creating log directory: %LOG_DIR%
    mkdir "%LOG_DIR%"
)

:: Clear any existing log file and start fresh
echo. > "%LOG_FILE%"

:: ========================================
:: LAUNCH HEADER
:: ========================================
echo ======================================== >> "%LOG_FILE%"
echo Hearthlink Electron Launch Log >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"
echo Launch Time: %DATE% %TIME% >> "%LOG_FILE%"
echo App Directory: %APP_DIR% >> "%LOG_FILE%"
echo Log File: %LOG_FILE% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

:: ========================================
:: ENVIRONMENT CHECK
:: ========================================
echo [%TIME%] Checking environment... >> "%LOG_FILE%"

:: Check if Node.js is available
node --version >> "%LOG_FILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js not found in PATH >> "%LOG_FILE%"
    echo [ERROR] Node.js not found in PATH
    goto :error_exit
)

:: Check if npm is available
npm --version >> "%LOG_FILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] npm not found in PATH >> "%LOG_FILE%"
    echo [ERROR] npm not found in PATH
    goto :error_exit
)

echo [%TIME%] Environment check passed >> "%LOG_FILE%"

:: ========================================
:: NODE.JS DEPENDENCIES
:: ========================================
echo [%TIME%] Checking Node.js dependencies... >> "%LOG_FILE%"

:: Check if node_modules exists
if not exist "%APP_DIR%node_modules" (
    echo [%TIME%] Installing Node.js dependencies... >> "%LOG_FILE%"
    npm install --legacy-peer-deps >> "%LOG_FILE%" 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install Node.js dependencies >> "%LOG_FILE%"
        echo [ERROR] Failed to install Node.js dependencies
        goto :error_exit
    )
)

:: ========================================
:: BUILD REACT APP
:: ========================================
echo [%TIME%] Building React app... >> "%LOG_FILE%"

:: Check if build directory exists
if not exist "%APP_DIR%build" (
    echo [%TIME%] Building React app for production... >> "%LOG_FILE%"
    npm run build >> "%LOG_FILE%" 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to build React app >> "%LOG_FILE%"
        echo [ERROR] Failed to build React app
        goto :error_exit
    )
) else (
    echo [%TIME%] Build directory exists, skipping build >> "%LOG_FILE%"
)

:: ========================================
:: ELECTRON LAUNCH
:: ========================================
echo [%TIME%] Starting Electron app... >> "%LOG_FILE%"

:: Start Electron app
echo [%TIME%] Launching Hearthlink Electron app... >> "%LOG_FILE%"
start /min cmd /c "cd /d %APP_DIR% && npm start >> "%LOG_FILE%" 2>&1"
echo [%TIME%] Electron app started >> "%LOG_FILE%"

:: ========================================
:: LAUNCH COMPLETE
:: ========================================
echo [%TIME%] ======================================== >> "%LOG_FILE%"
echo [%TIME%] Hearthlink Electron Launch Complete >> "%LOG_FILE%"
echo [%TIME%] ======================================== >> "%LOG_FILE%"
echo [%TIME%] Services started: >> "%LOG_FILE%"
echo [%TIME%] - Electron App >> "%LOG_FILE%"
echo [%TIME%] ======================================== >> "%LOG_FILE%"

:: Display success message
echo.
echo ========================================
echo Hearthlink Electron App
echo ========================================
echo Launch completed successfully!
echo.
echo Services started:
echo - Electron App
echo.
echo Log file: %LOG_FILE%
echo.
echo The Hearthlink app should now be running!
echo.
echo Press any key to open log file...
pause > nul

:: Open log file in default text editor
start notepad "%LOG_FILE%"

goto :end

:: ========================================
:: ERROR HANDLING
:: ========================================
:error_exit
echo.
echo ========================================
echo LAUNCH FAILED
echo ========================================
echo Check the log file for details: %LOG_FILE%
echo.
echo Common issues:
echo - Node.js not installed or not in PATH
echo - npm not installed or not in PATH
echo - Insufficient permissions
echo - Port conflicts
echo.
echo Press any key to open log file...
pause > nul
start notepad "%LOG_FILE%"
exit /b 1

:: ========================================
:: END
:: ========================================
:end
echo [%TIME%] Launch script completed >> "%LOG_FILE%"
endlocal 