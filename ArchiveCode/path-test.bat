@echo off
title PATH and NPM Test
color 0F
echo ================================
echo   PATH AND NPM ANALYSIS
echo ================================
echo.

cd /d "%~dp0"
echo Current directory: %CD%
echo.

echo [TEST] Current PATH:
echo %PATH%
echo.

echo [TEST] Where is node located?
where node
echo Error level: %errorlevel%
echo.

echo [TEST] Where is npm located?
where npm
echo Error level: %errorlevel%
echo.

echo [TEST] Node version direct call:
node --version
echo Error level: %errorlevel%
echo.

echo [TEST] NPM version direct call:
npm --version
echo Error level: %errorlevel%
echo.

echo [TEST] Testing npm with full path...
for /f "tokens=*" %%i in ('where npm 2^>nul') do (
    echo Found npm at: %%i
    echo [TEST] Running npm --version with full path...
    "%%i" --version
    echo Error level: %errorlevel%
)

echo.
echo [TEST] PATH test completed
echo.
echo Press any key to exit...
pause >nul
echo [TEST] Final message - script ending normally