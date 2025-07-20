@echo off
echo 🔗 Starting Hearthlink Native Wrapper...

:: Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js first.
    echo Visit: https://nodejs.org/
    pause
    exit /b 1
)

:: Check if Cargo is installed
where cargo >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Cargo ^(Rust^) is not installed. Please install Rust first.
    echo Visit: https://rustup.rs/
    pause
    exit /b 1
)

:: Navigate to project directory
cd /d "%~dp0"

:: Check if we're in the right directory
if not exist "src-tauri\Cargo.toml" (
    echo ❌ Tauri project not found. Make sure you're in the Hearthlink directory.
    pause
    exit /b 1
)

:: Build React app
echo 🔧 Building React application...
call npm run build
if %errorlevel% neq 0 (
    echo ❌ Failed to build React application
    pause
    exit /b 1
)

:: Start the native wrapper
echo 🚀 Starting native wrapper in development mode...
call npm run tauri:dev

echo ✅ Native wrapper launched successfully!
echo 💡 The wrapper will persist in your system tray when closed.
echo 💡 Use the system tray menu to control Hearthlink.
pause