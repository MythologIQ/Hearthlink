@echo off
echo ========================================
echo Hearthlink Status Check
echo ========================================
echo.

echo Checking for running processes...
echo.

echo Node.js processes:
tasklist | findstr node
echo.

echo Electron processes:
tasklist | findstr electron
echo.

echo Checking if build directory exists:
if exist "build\index.html" (
    echo ✅ Build directory exists
) else (
    echo ❌ Build directory missing
)
echo.

echo Checking if main.js exists:
if exist "main.js" (
    echo ✅ main.js exists
) else (
    echo ❌ main.js missing
)
echo.

echo Checking if package.json exists:
if exist "package.json" (
    echo ✅ package.json exists
) else (
    echo ❌ package.json missing
)
echo.

echo ========================================
echo Status check complete
echo ========================================
pause 