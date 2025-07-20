@echo off
echo Starting Hearthlink...
echo.

:: Check if build exists
if not exist "build\index.html" (
    echo Building React app...
    npm run build
    if errorlevel 1 (
        echo Build failed!
        pause
        exit /b 1
    )
)

:: Start Electron directly
echo Starting Electron app...
electron . 