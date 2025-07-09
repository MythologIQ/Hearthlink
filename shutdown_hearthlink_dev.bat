@echo off
setlocal EnableDelayedExpansion

:: ========================================
:: Hearthlink Development Shutdown Script
:: Clean Process Termination
:: ========================================

:: CONFIGURATION
set APP_DIR=%~dp0
set LOG_DIR=%APP_DIR%logs
set LOG_FILE=%LOG_DIR%\hearthlink_shutdown_%DATE:/=-%_%TIME::=-%.log

:: Create timestamp for unique log file
for /f "tokens=1-3 delims=:." %%a in ("%TIME%") do set TIMESTAMP=%%a-%%b-%%c
set LOG_FILE=%LOG_DIR%\hearthlink_shutdown_%DATE:/=-%_%TIMESTAMP%.log

:: Ensure log directory exists
if not exist "%LOG_DIR%" (
    mkdir "%LOG_DIR%"
)

:: ========================================
:: SHUTDOWN HEADER
:: ========================================
echo ======================================== >> "%LOG_FILE%"
echo Hearthlink Development Shutdown Log >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"
echo Shutdown Time: %DATE% %TIME% >> "%LOG_FILE%"
echo App Directory: %APP_DIR% >> "%LOG_FILE%"
echo Log File: %LOG_FILE% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

:: ========================================
:: PROCESS TERMINATION
:: ========================================
echo [%TIME%] Starting process termination... >> "%LOG_FILE%"

:: Kill Node.js processes (React dev server, Electron)
echo [%TIME%] Terminating Node.js processes... >> "%LOG_FILE%"
taskkill /f /im node.exe >> "%LOG_FILE%" 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [%TIME%] Node.js processes terminated >> "%LOG_FILE%"
) else (
    echo [%TIME%] No Node.js processes found or already terminated >> "%LOG_FILE%"
)

:: Kill Python processes (backend server)
echo [%TIME%] Terminating Python processes... >> "%LOG_FILE%"
taskkill /f /im python.exe >> "%LOG_FILE%" 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [%TIME%] Python processes terminated >> "%LOG_FILE%"
) else (
    echo [%TIME%] No Python processes found or already terminated >> "%LOG_FILE%"
)

:: Kill Electron processes specifically
echo [%TIME%] Terminating Electron processes... >> "%LOG_FILE%"
taskkill /f /im electron.exe >> "%LOG_FILE%" 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [%TIME%] Electron processes terminated >> "%LOG_FILE%"
) else (
    echo [%TIME%] No Electron processes found or already terminated >> "%LOG_FILE%"
)

:: Kill any remaining cmd processes that might be running our servers
echo [%TIME%] Terminating development server processes... >> "%LOG_FILE%"
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq cmd.exe" /fo table /nh ^| findstr /i "cmd"') do (
    taskkill /f /pid %%i >> "%LOG_FILE%" 2>&1
)

:: ========================================
:: PORT CLEANUP
:: ========================================
echo [%TIME%] Checking for port conflicts... >> "%LOG_FILE%"

:: Check common development ports
for %%p in (3000 3001 5000 8000 8080) do (
    netstat -ano | findstr :%%p >> "%LOG_FILE%" 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo [%TIME%] Port %%p is still in use >> "%LOG_FILE%"
    ) else (
        echo [%TIME%] Port %%p is free >> "%LOG_FILE%"
    )
)

:: ========================================
:: TEMPORARY FILE CLEANUP
:: ========================================
echo [%TIME%] Cleaning temporary files... >> "%LOG_FILE%"

:: Clean npm cache if needed
if exist "%APP_DIR%node_modules\.cache" (
    echo [%TIME%] Cleaning npm cache... >> "%LOG_FILE%"
    rmdir /s /q "%APP_DIR%node_modules\.cache" >> "%LOG_FILE%" 2>&1
)

:: Clean Python cache files
if exist "%APP_DIR%__pycache__" (
    echo [%TIME%] Cleaning Python cache... >> "%LOG_FILE%"
    rmdir /s /q "%APP_DIR%__pycache__" >> "%LOG_FILE%" 2>&1
)

:: Clean any .pyc files
for /r "%APP_DIR%" %%f in (*.pyc) do (
    del "%%f" >> "%LOG_FILE%" 2>&1
)

:: ========================================
:: LOG ROTATION
:: ========================================
echo [%TIME%] Managing log files... >> "%LOG_FILE%"

:: Keep only last 10 log files
set LOG_COUNT=0
for %%f in ("%LOG_DIR%\hearthlink_*.log") do (
    set /a LOG_COUNT+=1
    if !LOG_COUNT! GTR 10 (
        del "%%f" >> "%LOG_FILE%" 2>&1
        echo [%TIME%] Removed old log file: %%f >> "%LOG_FILE%"
    )
)

:: ========================================
:: SHUTDOWN COMPLETE
:: ========================================
echo [%TIME%] ======================================== >> "%LOG_FILE%"
echo [%TIME%] Hearthlink Development Shutdown Complete >> "%LOG_FILE%"
echo [%TIME%] ======================================== >> "%LOG_FILE%"
echo [%TIME%] Services terminated: >> "%LOG_FILE%"
echo [%TIME%] - React Development Server >> "%LOG_FILE%"
echo [%TIME%] - Electron Development >> "%LOG_FILE%"
echo [%TIME%] - Python Backend >> "%LOG_FILE%"
echo [%TIME%] - Temporary files cleaned >> "%LOG_FILE%"
echo [%TIME%] - Log files rotated >> "%LOG_FILE%"
echo [%TIME%] ======================================== >> "%LOG_FILE%"

:: Display completion message
echo.
echo ========================================
echo Hearthlink Development Shutdown
echo ========================================
echo Shutdown completed successfully!
echo.
echo Services terminated:
echo - React Development Server
echo - Electron Development
echo - Python Backend
echo - Temporary files cleaned
echo - Log files rotated
echo.
echo Log file: %LOG_FILE%
echo.
echo Press any key to open log file...
pause > nul

:: Open log file in default text editor
start notepad "%LOG_FILE%"

:: ========================================
:: END
:: ========================================
:end
echo [%TIME%] Shutdown script completed >> "%LOG_FILE%"
endlocal 