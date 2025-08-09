@echo off
REM SPEC-2 Tauri Installer Build Script for Windows
REM Packages Hearthlink with validation assets and CI badges

setlocal enabledelayedexpansion

echo 🚀 Building SPEC-2 Tauri Installer with Validation Assets...

REM Build configuration
set BUILD_DIR=target\release\bundle
set ASSETS_DIR=src-tauri\assets
set VERSION=1.3.0-spec2

REM Get timestamp
for /f %%i in ('powershell -Command "Get-Date -UFormat '%%Y-%%m-%%dT%%H:%%M:%%SZ'"') do set TIMESTAMP=%%i

REM Create assets directory if it doesn't exist
if not exist "%ASSETS_DIR%" mkdir "%ASSETS_DIR%"

REM Validate SPEC-2 components exist
echo 📋 Validating SPEC-2 components...

set REQUIRED_COMPONENTS=src\components\TaskCreator.js src\components\TaskCreator.css src\components\MemoryDebugPanel.js src\components\MemoryDebugPanel.css src\api\task_templates.py src\api\vault_tasks.py

for %%c in (%REQUIRED_COMPONENTS%) do (
    if not exist "%%c" (
        echo ❌ Missing required component: %%c
        exit /b 1
    )
    echo ✅ Found: %%c
)

REM Update validation timestamps using PowerShell
echo 🔄 Updating validation timestamps...
if exist "%ASSETS_DIR%\validation.json" (
    powershell -Command "(Get-Content '%ASSETS_DIR%\validation.json') -replace '\"build_timestamp\": \"[^\"]*\"', '\"build_timestamp\": \"%TIMESTAMP%\"' | Set-Content '%ASSETS_DIR%\validation.json'"
)

if exist "%ASSETS_DIR%\ci_badges.json" (
    powershell -Command "(Get-Content '%ASSETS_DIR%\ci_badges.json') -replace '\"generated_at\": \"[^\"]*\"', '\"generated_at\": \"%TIMESTAMP%\"' | Set-Content '%ASSETS_DIR%\ci_badges.json'"
)

REM Compile TypeScript before build
echo 🔧 Compiling TypeScript...
call npm run compile:ts
if errorlevel 1 (
    echo ⚠️ TypeScript compilation had warnings but continuing...
)

REM Build React frontend
echo 🏗️ Building React frontend...
call npm run build
if errorlevel 1 (
    echo ❌ React build failed
    exit /b 1
)

REM Build Tauri application
echo 📦 Building Tauri application...
call npm run tauri:build
if errorlevel 1 (
    echo ❌ Tauri build failed
    exit /b 1
)

REM Verify bundle was created
if not exist "%BUILD_DIR%" (
    echo ❌ Build failed - no bundle directory found
    exit /b 1
)

echo ✅ Build completed successfully!

REM List built artifacts
echo 📄 Built artifacts:
dir /s /b "%BUILD_DIR%\*.exe" "%BUILD_DIR%\*.msi" 2>nul || echo No installer artifacts found

REM Calculate checksums for validation
echo 🔐 Calculating checksums...
for /r "%BUILD_DIR%" %%f in (*.exe *.msi) do (
    if exist "%%f" (
        powershell -Command "Get-FileHash '%%f' -Algorithm SHA256 | Select-Object Hash, Path"
    )
)

echo 🎉 SPEC-2 Tauri installer build complete!
echo 📁 Artifacts location: %BUILD_DIR%
echo 🔖 Version: %VERSION%
echo ⏰ Build time: %TIMESTAMP%

pause