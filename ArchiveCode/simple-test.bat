@echo off
title Simple Test
color 0E
echo ================================
echo   SIMPLE TEST
echo ================================
echo.
echo This is a simple test to see if ANY batch file stays open
echo.
echo Current time: %time%
echo Current directory: %CD%
echo.
echo Press any key to continue...
pause >nul
echo.
echo You pressed a key.
echo.
echo Now entering infinite loop...
echo This should run forever unless you press Ctrl+C
echo.
:loop
echo Still running at %time%
timeout /t 2 /nobreak >nul
goto :loop