@echo off
setlocal EnableDelayedExpansion

:: ========================================
:: Hearthlink Development Launch Script
:: Secure Launch Process with Logging
:: ========================================

:: CONFIGURATION
set APP_DIR=%~dp0
set LOG_DIR=%APP_DIR%logs
set LOG_FILE=%LOG_DIR%\hearthlink_launch_%DATE:/=-%_%TIME::=-%.log
set PYTHON_ENV=%APP_DIR%venv
set NODE_ENV=development

:: Create timestamp for unique log file
for /f "tokens=1-3 delims=:." %%a in ("%TIME%") do set TIMESTAMP=%%a-%%b-%%c
set LOG_FILE=%LOG_DIR%\hearthlink_launch_%DATE:/=-%_%TIMESTAMP%.log

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
echo Hearthlink Development Launch Log >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"
echo Launch Time: %DATE% %TIME% >> "%LOG_FILE%"
echo App Directory: %APP_DIR% >> "%LOG_FILE%"
echo Log File: %LOG_FILE% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

:: ========================================
:: ENVIRONMENT CHECK
:: ========================================
echo [%TIME%] Checking environment... >> "%LOG_FILE%"

:: Check if Python is available
python --version >> "%LOG_FILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found in PATH >> "%LOG_FILE%"
    echo [ERROR] Python not found in PATH
    goto :error_exit
)

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
:: PYTHON VIRTUAL ENVIRONMENT
:: ========================================
echo [%TIME%] Setting up Python virtual environment... >> "%LOG_FILE%"

:: Check if virtual environment exists
if not exist "%PYTHON_ENV%\Scripts\activate.bat" (
    echo [%TIME%] Creating Python virtual environment... >> "%LOG_FILE%"
    python -m venv "%PYTHON_ENV%" >> "%LOG_FILE%" 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment >> "%LOG_FILE%"
        echo [ERROR] Failed to create virtual environment
        goto :error_exit
    )
)

:: Activate virtual environment
echo [%TIME%] Activating virtual environment... >> "%LOG_FILE%"
call "%PYTHON_ENV%\Scripts\activate.bat" >> "%LOG_FILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Virtual environment activation had issues, continuing... >> "%LOG_FILE%"
)

:: Install Python dependencies if requirements.txt exists
if exist "%APP_DIR%requirements.txt" (
    echo [%TIME%] Installing Python dependencies... >> "%LOG_FILE%"
    pip install -r "%APP_DIR%requirements.txt" >> "%LOG_FILE%" 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [WARNING] Some Python dependencies may not have installed correctly >> "%LOG_FILE%"
    )
)

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
:: BACKEND SERVER LAUNCH
:: ========================================
echo [%TIME%] Starting backend server... >> "%LOG_FILE%"

:: Check if backend directory exists
if exist "%APP_DIR%src" (
    :: Start Python backend (adjust path as needed)
    start /min cmd /c "cd /d %APP_DIR% && %PYTHON_ENV%\Scripts\python.exe src\main.py >> "%LOG_FILE%" 2>&1"
    echo [%TIME%] Backend server started in background >> "%LOG_FILE%"
) else (
    echo [WARNING] Backend directory not found, skipping backend launch >> "%LOG_FILE%"
)

:: ========================================
:: FRONTEND DEVELOPMENT SERVER
:: ========================================
echo [%TIME%] Starting React development server... >> "%LOG_FILE%"

:: Start React development server
echo [%TIME%] Starting React development server... >> "%LOG_FILE%"
start /min cmd /c "cd /d %APP_DIR% && npm run react-start >> "%LOG_FILE%" 2>&1"
echo [%TIME%] React development server started in background >> "%LOG_FILE%"

:: Wait for React server to start
echo [%TIME%] Waiting for React server to initialize... >> "%LOG_FILE%"
timeout /t 5 /nobreak > nul

:: ========================================
:: ELECTRON DEVELOPMENT LAUNCH
:: ========================================
echo [%TIME%] Starting Electron development... >> "%LOG_FILE%"

:: Start Electron in development mode
start /min cmd /c "cd /d %APP_DIR% && npm run electron-dev >> "%LOG_FILE%" 2>&1"
echo [%TIME%] Electron development started in background >> "%LOG_FILE%"

:: ========================================
:: LAUNCH COMPLETE
:: ========================================
echo [%TIME%] ======================================== >> "%LOG_FILE%"
echo [%TIME%] Hearthlink Development Launch Complete >> "%LOG_FILE%"
echo [%TIME%] ======================================== >> "%LOG_FILE%"
echo [%TIME%] Services started: >> "%LOG_FILE%"
echo [%TIME%] - React Development Server >> "%LOG_FILE%"
echo [%TIME%] - Electron Development >> "%LOG_FILE%"
echo [%TIME%] - Python Backend (if available) >> "%LOG_FILE%"
echo [%TIME%] ======================================== >> "%LOG_FILE%"

:: Display success message
echo.
echo ========================================
echo Hearthlink Development Environment
echo ========================================
echo Launch completed successfully!
echo.
echo Services started:
echo - React Development Server
echo - Electron Development
echo - Python Backend (if available)
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
echo - Python not installed or not in PATH
echo - Node.js not installed or not in PATH
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