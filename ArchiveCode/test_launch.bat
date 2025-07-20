@echo off
setlocal EnableDelayedExpansion

echo ========================================
echo Hearthlink Test Launch
echo ========================================
echo Test Time: %DATE% %TIME%

:: CONFIGURATION
set APP_DIR=%~dp0
set LOG_DIR=%APP_DIR%logs
set LOG_FILE=%LOG_DIR%\test_launch.log
set PYTHON_ENV=%APP_DIR%venv

echo App Directory: %APP_DIR%
echo Python Env: %PYTHON_ENV%
echo Log File: %LOG_FILE%

:: Ensure log directory exists
if not exist "%LOG_DIR%" (
    echo Creating log directory: %LOG_DIR%
    mkdir "%LOG_DIR%"
)

:: Clear log file
echo. > "%LOG_FILE%"

:: Test 1: Environment check
echo [%TIME%] Testing environment check... >> "%LOG_FILE%"
python --version >> "%LOG_FILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found >> "%LOG_FILE%"
    echo [ERROR] Python not found
    goto :end
)
echo [%TIME%] Python check passed >> "%LOG_FILE%"

node --version >> "%LOG_FILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js not found >> "%LOG_FILE%"
    echo [ERROR] Node.js not found
    goto :end
)
echo [%TIME%] Node.js check passed >> "%LOG_FILE%"

:: Test 2: Virtual environment check
echo [%TIME%] Testing virtual environment... >> "%LOG_FILE%"
if not exist "%PYTHON_ENV%\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found >> "%LOG_FILE%"
    echo [ERROR] Virtual environment not found
    goto :end
)
echo [%TIME%] Virtual environment found >> "%LOG_FILE%"

:: Test 3: Virtual environment activation
echo [%TIME%] Testing virtual environment activation... >> "%LOG_FILE%"
call "%PYTHON_ENV%\Scripts\activate.bat" >> "%LOG_FILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to activate virtual environment >> "%LOG_FILE%"
    echo [ERROR] Failed to activate virtual environment
    goto :end
)
echo [%TIME%] Virtual environment activated >> "%LOG_FILE%"

:: Test 4: Node modules check
echo [%TIME%] Testing Node.js dependencies... >> "%LOG_FILE%"
if not exist "%APP_DIR%node_modules" (
    echo [WARNING] node_modules not found, will install >> "%LOG_FILE%"
) else (
    echo [%TIME%] node_modules found >> "%LOG_FILE%"
)

:: Test 5: Start React dev server
echo [%TIME%] Testing React dev server start... >> "%LOG_FILE%"
start /min cmd /c "cd /d %APP_DIR% && npm run react-start >> "%LOG_FILE%" 2>&1"
echo [%TIME%] React dev server started >> "%LOG_FILE%"

:: Test 6: Start Electron
echo [%TIME%] Testing Electron start... >> "%LOG_FILE%"
timeout /t 3 /nobreak > nul
start /min cmd /c "cd /d %APP_DIR% && npm run electron-dev >> "%LOG_FILE%" 2>&1"
echo [%TIME%] Electron started >> "%LOG_FILE%"

echo [%TIME%] All tests completed successfully >> "%LOG_FILE%"
echo.
echo ========================================
echo Test completed successfully!
echo Check log file: %LOG_FILE%
echo ========================================

:end
echo [%TIME%] Test script ended >> "%LOG_FILE%"
pause 