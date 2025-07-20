@echo off
setlocal EnableDelayedExpansion

:: ========================================
:: Hearthlink Electron Development Launch
:: ========================================

:: CONFIGURATION
set APP_DIR=%~dp0
set LOG_DIR=%APP_DIR%logs
set LOG_FILE=%LOG_DIR%\electron_dev_%DATE:/=-%_%TIME::=-%.log

:: Create timestamp for unique log file
for /f "tokens=1-3 delims=:." %%a in ("%TIME%") do set TIMESTAMP=%%a-%%b-%%c
set LOG_FILE=%LOG_DIR%\electron_dev_%DATE:/=-%_%TIMESTAMP%.log

:: Ensure log directory exists
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: Clear any existing log file and start fresh
echo. > "%LOG_FILE%"

:: ========================================
:: LAUNCH HEADER
:: ========================================
echo ======================================== >> "%LOG_FILE%"
echo Hearthlink Electron Development Launch >> "%LOG_FILE%"
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
:: CLEANUP PREVIOUS PROCESSES
:: ========================================
echo [%TIME%] Cleaning up previous processes... >> "%LOG_FILE%"

:: Kill any existing Electron processes
taskkill /f /im electron.exe >> "%LOG_FILE%" 2>&1
timeout /t 2 /nobreak > nul

:: ========================================
:: BUILD CHECK
:: ========================================
echo [%TIME%] Checking build status... >> "%LOG_FILE%"

:: Check if build directory exists and is recent
if not exist "%APP_DIR%build\index.html" (
    echo [%TIME%] Build not found, creating build... >> "%LOG_FILE%"
    npm run build >> "%LOG_FILE%" 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Build failed >> "%LOG_FILE%"
        echo [ERROR] Build failed
        goto :error_exit
    )
) else (
    echo [%TIME%] Build found, checking if recent... >> "%LOG_FILE%"
    :: Check if build is older than 5 minutes
    forfiles /p "%APP_DIR%build" /s /m index.html /d -5 >> "%LOG_FILE%" 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [%TIME%] Build is recent, using existing build >> "%LOG_FILE%"
    ) else (
        echo [%TIME%] Build is old, rebuilding... >> "%LOG_FILE%"
        npm run build >> "%LOG_FILE%" 2>&1
        if %ERRORLEVEL% NEQ 0 (
            echo [ERROR] Build failed >> "%LOG_FILE%"
            echo [ERROR] Build failed
            goto :error_exit
        )
    )
)

:: ========================================
:: ELECTRON DEVELOPMENT LAUNCH
:: ========================================
echo [%TIME%] Starting Electron development... >> "%LOG_FILE%"

:: Set development environment variables
set NODE_ENV=development
set ELECTRON_START_URL=file://%APP_DIR%build/index.html

:: Log environment variables
echo [%TIME%] NODE_ENV=%NODE_ENV% >> "%LOG_FILE%"
echo [%TIME%] ELECTRON_START_URL=%ELECTRON_START_URL% >> "%LOG_FILE%"

:: Start Electron with development settings
echo [%TIME%] Launching Electron with development settings... >> "%LOG_FILE%"

:: Method 1: Direct electron launch
echo [%TIME%] Attempting direct electron launch... >> "%LOG_FILE%"
start /min cmd /c "cd /d %APP_DIR% && set NODE_ENV=development && set ELECTRON_START_URL=file://%APP_DIR%build/index.html && electron . >> "%LOG_FILE%" 2>&1"

:: Wait a moment for Electron to start
timeout /t 5 /nobreak > nul

:: Check if Electron process is running
tasklist /fi "imagename eq electron.exe" 2>nul | find /i "electron.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo [%TIME%] Electron started successfully via direct launch >> "%LOG_FILE%"
    echo [%TIME%] Electron process is running >> "%LOG_FILE%"
    goto :launch_success
) else (
    echo [%TIME%] Direct launch failed, trying npm start... >> "%LOG_FILE%"
    
    :: Method 2: npm start fallback
    start /min cmd /c "cd /d %APP_DIR% && set NODE_ENV=development && set ELECTRON_START_URL=file://%APP_DIR%build/index.html && npm start >> "%LOG_FILE%" 2>&1"
    
    :: Wait a moment for Electron to start
    timeout /t 5 /nobreak > nul
    
    :: Check if Electron process is running
    tasklist /fi "imagename eq electron.exe" 2>nul | find /i "electron.exe" >nul
    if %ERRORLEVEL% EQU 0 (
        echo [%TIME%] Electron started successfully via npm start >> "%LOG_FILE%"
        echo [%TIME%] Electron process is running >> "%LOG_FILE%"
        goto :launch_success
    ) else (
        echo [ERROR] Both launch methods failed >> "%LOG_FILE%"
        echo [ERROR] Both launch methods failed
        goto :error_exit
    )
)

:launch_success
:: ========================================
:: LAUNCH COMPLETE
:: ========================================
echo [%TIME%] ======================================== >> "%LOG_FILE%"
echo [%TIME%] Electron Development Launch Complete >> "%LOG_FILE%"
echo [%TIME%] ======================================== >> "%LOG_FILE%"
echo [%TIME%] Electron app should now be running >> "%LOG_FILE%"
echo [%TIME%] ======================================== >> "%LOG_FILE%"

:: Display success message
echo.
echo ========================================
echo Hearthlink Electron Development
echo ========================================
echo Launch completed successfully!
echo.
echo Electron app should now be running.
echo If you don't see the app window, check the log file.
echo.
echo Log file: %LOG_FILE%
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
echo - Build failed due to missing dependencies
echo - Port conflicts
echo - Permission issues
echo - Electron not installed
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