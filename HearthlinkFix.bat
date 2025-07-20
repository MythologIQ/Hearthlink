@echo off
setlocal enabledelayedexpansion

:: Hearthlink Emergency Fix - Direct HTML Launch
echo ========================================
echo HEARTHLINK EMERGENCY LAUNCH
echo ========================================

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo [INFO] Testing environment...

:: Check if build exists
if not exist "build\index.html" (
    echo [ERROR] Build files missing. Running npm run build...
    npm run build
    if %errorlevel% neq 0 (
        echo [ERROR] Build failed. Trying fallback...
        goto FALLBACK
    )
)

echo [INFO] Launching via file protocol (bypassing Electron)...
start "" "file:///%PROJECT_DIR%build\index.html"

timeout /t 3 /nobreak >nul

echo [INFO] If app didn't open, trying browser fallback...
start "" http://localhost:3000
timeout /t 2 /nobreak >nul

goto END

:FALLBACK
echo [INFO] Using public test page...
if exist "public\test.html" (
    start "" "file:///%PROJECT_DIR%public\test.html"
) else (
    echo [ERROR] No fallback available. Manual intervention required.
)

:END
echo [INFO] Launch completed. Check browser windows.
pause