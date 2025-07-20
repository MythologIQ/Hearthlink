@echo off
echo Testing Hearthlink launch from Windows...
echo.

REM Change to the correct directory (WSL path converted to Windows)
cd /d "G:\MythologIQ\Hearthlink"

echo Current directory: %CD%
echo.

REM Try to launch with npm start
echo Attempting npm start...
npm start

pause