@echo off
echo ========================================
echo ELECTRON REPAIR TOOL
echo ========================================

cd /d "%~dp0"

echo [1/5] Backing up current installation...
if exist "node_modules\electron" (
    ren "node_modules\electron" "electron_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%"
)

echo [2/5] Clearing npm cache...
npm cache clean --force

echo [3/5] Removing corrupted Electron...
rmdir /s /q "node_modules\.bin" 2>nul
rmdir /s /q "node_modules\electron" 2>nul

echo [4/5] Reinstalling Electron for Windows...
npm install electron@28.0.0 --no-save --platform=win32 --arch=x64

echo [5/5] Testing installation...
echo Testing Electron binary...
timeout /t 5 >nul
"%~dp0node_modules\.bin\electron.cmd" --version

if %errorlevel% equ 0 (
    echo ✅ Electron repair completed successfully!
) else (
    echo ❌ Repair failed. Try manual installation.
)

pause