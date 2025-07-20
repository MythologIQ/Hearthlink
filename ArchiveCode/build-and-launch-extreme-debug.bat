@echo off
title EXTREME DEBUG - Cannot Close
color 0C
echo ================================
echo   EXTREME DEBUG MODE
echo ================================
echo.
echo [EXTREME] This should be IMPOSSIBLE to close
echo [EXTREME] If this closes, there's a system issue
echo.

:: Prevent script from closing
setlocal EnableDelayedExpansion

:: Log everything to file as well
set LOGFILE=extreme-debug.log
echo [EXTREME] Starting extreme debug at %date% %time% > %LOGFILE%
echo [EXTREME] Starting extreme debug at %date% %time%

:: Test basic functionality first
echo [EXTREME] Testing basic echo... >> %LOGFILE%
echo [EXTREME] Testing basic echo...

:: Test pause functionality
echo [EXTREME] Testing pause... >> %LOGFILE%
echo [EXTREME] Testing pause...
echo Press any key to continue with extreme debug...
pause >nul
echo [EXTREME] Pause worked >> %LOGFILE%
echo [EXTREME] Pause worked

:: Navigate to script directory
echo [EXTREME] Current directory: %CD% >> %LOGFILE%
echo [EXTREME] Current directory: %CD%
cd /d "%~dp0"
echo [EXTREME] Changed to directory: %CD% >> %LOGFILE%
echo [EXTREME] Changed to directory: %CD%

:: Check if Node.js exists
echo [EXTREME] Checking Node.js... >> %LOGFILE%
echo [EXTREME] Checking Node.js...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [EXTREME] Node.js not found! >> %LOGFILE%
    echo [EXTREME] Node.js not found!
    goto :extreme_end
)

echo [EXTREME] Node.js found >> %LOGFILE%
echo [EXTREME] Node.js found
node --version >> %LOGFILE%
node --version

:: Check if npm exists
echo [EXTREME] Checking npm... >> %LOGFILE%
echo [EXTREME] Checking npm...
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo [EXTREME] npm not found! >> %LOGFILE%
    echo [EXTREME] npm not found!
    goto :extreme_end
)

echo [EXTREME] npm found >> %LOGFILE%
echo [EXTREME] npm found
npm --version >> %LOGFILE%
npm --version

:: Check package.json
echo [EXTREME] Checking package.json... >> %LOGFILE%
echo [EXTREME] Checking package.json...
if not exist "package.json" (
    echo [EXTREME] package.json not found! >> %LOGFILE%
    echo [EXTREME] package.json not found!
    goto :extreme_end
)

echo [EXTREME] package.json found >> %LOGFILE%
echo [EXTREME] package.json found

:: Try to run npm start without build first
echo [EXTREME] Attempting npm start... >> %LOGFILE%
echo [EXTREME] Attempting npm start...
echo [EXTREME] This may fail but let's see what happens...
echo Press any key to try npm start...
pause >nul

echo [EXTREME] Running npm start now... >> %LOGFILE%
echo [EXTREME] Running npm start now...

:: Run npm start and capture output
npm start >> %LOGFILE% 2>&1
set NPM_EXIT_CODE=%errorlevel%

echo [EXTREME] npm start completed with exit code: %NPM_EXIT_CODE% >> %LOGFILE%
echo [EXTREME] npm start completed with exit code: %NPM_EXIT_CODE%

:extreme_end
echo [EXTREME] Reached extreme_end label >> %LOGFILE%
echo [EXTREME] Reached extreme_end label

echo ================================
echo   EXTREME DEBUG COMPLETE
echo ================================
echo.
echo [EXTREME] Script completed at %date% %time% >> %LOGFILE%
echo [EXTREME] Script completed at %date% %time%
echo [EXTREME] Check extreme-debug.log for full output
echo.
echo [EXTREME] Now entering FORCED infinite loop...
echo [EXTREME] This should NEVER end on its own
echo [EXTREME] Press Ctrl+C to break out
echo.

:infinite_loop
echo [EXTREME] Loop iteration at %time% - Terminal still open
timeout /t 5 /nobreak >nul 2>&1
goto :infinite_loop