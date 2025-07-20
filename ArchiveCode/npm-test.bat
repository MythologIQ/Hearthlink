@echo off
title NPM Test
color 0B
echo ================================
echo   NPM COMMAND TEST
echo ================================
echo.
echo Testing npm commands one by one...
echo.

cd /d "%~dp0"
echo Current directory: %CD%
echo.

echo [TEST] Testing npm --version...
npm --version
echo [TEST] npm --version completed with error level: %errorlevel%
echo.

echo [TEST] Testing npm list...
npm list --depth=0
echo [TEST] npm list completed with error level: %errorlevel%
echo.

echo [TEST] Testing npm run (should show available scripts)...
npm run
echo [TEST] npm run completed with error level: %errorlevel%
echo.

echo [TEST] All npm tests completed
echo.
echo Press any key to exit...
pause >nul
echo [TEST] Final message - script ending normally