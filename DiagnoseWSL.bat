@echo off
setlocal enabledelayedexpansion
title WSL Diagnostic
color 0E

echo.
echo  ╔═══════════════════════════════════════════════════════════════════════════════╗
echo  ║                            WSL Diagnostic                                    ║
echo  ║                      Troubleshoot WSL Issues                                 ║
echo  ║                                v1.3.0                                        ║
echo  ╚═══════════════════════════════════════════════════════════════════════════════╝
echo.

echo 🔍 Diagnosing WSL installation...
echo.

:: Check if WSL command exists
where wsl >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ WSL command not found in PATH
    echo    WSL may not be installed or not in PATH
    goto INSTALL_WSL
) else (
    echo ✅ WSL command found
)

:: Check WSL version
echo 📊 Checking WSL version...
wsl --version 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  WSL --version failed, trying alternative...
    wsl --help | findstr "Windows Subsystem for Linux" >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ WSL is installed (older version)
    ) else (
        echo ❌ WSL version check failed
    )
) else (
    echo ✅ WSL version check passed
)

:: List WSL distributions
echo 📋 Listing WSL distributions...
wsl --list 2>nul
if %errorlevel% neq 0 (
    echo ❌ No WSL distributions found
    goto INSTALL_UBUNTU
) else (
    echo ✅ WSL distributions found
)

:: Check if Ubuntu is installed
echo 🐧 Checking for Ubuntu distribution...
wsl --list | findstr "Ubuntu" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ubuntu distribution not found
    goto INSTALL_UBUNTU
) else (
    echo ✅ Ubuntu distribution found
)

:: Test Ubuntu functionality
echo 🧪 Testing Ubuntu functionality...
wsl -d Ubuntu echo "Ubuntu test successful" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Ubuntu test failed
    echo    Ubuntu may not be properly configured
    goto CONFIGURE_UBUNTU
) else (
    echo ✅ Ubuntu is working
)

:: Test project directory access
echo 📁 Testing project directory access...
wsl -d Ubuntu -e bash -c "ls /mnt/g/MythologIQ/Hearthlink >/dev/null 2>&1"
if %errorlevel% neq 0 (
    echo ❌ Cannot access project directory from WSL
    echo    Path: /mnt/g/MythologIQ/Hearthlink
    goto DIRECTORY_ISSUE
) else (
    echo ✅ Project directory accessible from WSL
)

:: Test Claude CLI
echo 🤖 Testing Claude CLI...
wsl -d Ubuntu -e bash -c "command -v claude >/dev/null 2>&1"
if %errorlevel% neq 0 (
    echo ❌ Claude CLI not found
    goto INSTALL_CLAUDE
) else (
    echo ✅ Claude CLI found
)

echo.
echo 🎉 WSL diagnostic complete - everything looks good!
echo.
echo 📋 WSL Status:
echo    • WSL is installed and working
echo    • Ubuntu distribution is available
echo    • Project directory is accessible
echo    • Claude CLI is installed
echo.
echo 🚀 You can now run the full Hearthlink setup!
echo.
pause
goto END

:INSTALL_WSL
echo.
echo 🛠️  WSL Installation Required
echo.
echo To install WSL, run one of these commands as Administrator:
echo    wsl --install
echo    or
echo    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
echo.
echo After installation, restart your computer and run this diagnostic again.
echo.
pause
goto END

:INSTALL_UBUNTU
echo.
echo 🐧 Ubuntu Installation Required
echo.
echo To install Ubuntu:
echo    1. Open Microsoft Store
echo    2. Search for "Ubuntu"
echo    3. Install "Ubuntu" (latest version)
echo    4. Launch Ubuntu and complete setup
echo.
echo Or run: wsl --install -d Ubuntu
echo.
pause
goto END

:CONFIGURE_UBUNTU
echo.
echo ⚙️  Ubuntu Configuration Required
echo.
echo To configure Ubuntu:
echo    1. Open Ubuntu from Start Menu
echo    2. Complete the initial setup (username/password)
echo    3. Run: sudo apt update
echo    4. Run this diagnostic again
echo.
pause
goto END

:DIRECTORY_ISSUE
echo.
echo 📁 Directory Access Issue
echo.
echo The project directory is not accessible from WSL.
echo This could be because:
echo    1. The drive is not mounted properly
echo    2. WSL needs to be restarted
echo    3. Permissions issue
echo.
echo Try:
echo    1. Restart WSL: wsl --shutdown, then wsl
echo    2. Check if G: drive exists: dir G:\
echo    3. Run this diagnostic again
echo.
pause
goto END

:INSTALL_CLAUDE
echo.
echo 🤖 Claude CLI Installation Required
echo.
echo To install Claude CLI in WSL:
echo    1. Open Ubuntu terminal
echo    2. Run: curl -fsSL https://claude.ai/cli/install.sh | sh
echo    3. Follow the installation instructions
echo    4. Run this diagnostic again
echo.
pause
goto END

:END
echo.
echo 👋 WSL Diagnostic completed
echo.