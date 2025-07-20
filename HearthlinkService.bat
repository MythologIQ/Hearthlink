@echo off
setlocal enabledelayedexpansion

:: This script runs in background/minimized mode
:: It starts all Hearthlink services without user interaction

:: Set project paths
set "PROJECT_PATH=/mnt/g/MythologIQ/Hearthlink"
set "WIN_PROJECT_PATH=G:\MythologIQ\Hearthlink"

:: Create log directory
if not exist "%WIN_PROJECT_PATH%\logs" mkdir "%WIN_PROJECT_PATH%\logs"

:: Generate timestamp for logs
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set "DATE_STAMP=%%c%%a%%b"
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set "TIME_STAMP=%%a%%b"
set "LOG_FILE=%WIN_PROJECT_PATH%\logs\hearthlink_service_%DATE_STAMP%_%TIME_STAMP%.log"

:: Log start
echo [%date% %time%] Hearthlink Service Starting... >> "%LOG_FILE%"

:: Start Docker Desktop if not running
tasklist /fi "imagename eq Docker Desktop.exe" 2>nul | find /i "Docker Desktop.exe" >nul
if %errorlevel% neq 0 (
    echo [%date% %time%] Starting Docker Desktop... >> "%LOG_FILE%"
    
    :: Try multiple possible Docker locations
    if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
        start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    ) else if exist "C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe" (
        start "" "C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe"
    ) else if exist "%USERPROFILE%\AppData\Local\Docker\Docker Desktop.exe" (
        start "" "%USERPROFILE%\AppData\Local\Docker\Docker Desktop.exe"
    ) else (
        echo [%date% %time%] Docker Desktop not found in standard locations >> "%LOG_FILE%"
    )
    
    timeout /t 20 /nobreak >nul
)

:: Start WSL services in background
echo [%date% %time%] Starting WSL services... >> "%LOG_FILE%"

wsl -d Ubuntu -e bash -c "
    # Set up logging
    LOG_FILE='%PROJECT_PATH%/logs/hearthlink_service_%DATE_STAMP%_%TIME_STAMP%.log'
    exec >> \$LOG_FILE 2>&1
    
    echo '[$(date)] WSL Service Environment Starting...'
    
    # Change to project directory
    cd '%PROJECT_PATH%' || exit 1
    
    # Start Docker services
    if [ -f 'docker-compose.yml' ]; then
        echo '[$(date)] Starting Docker services...'
        docker-compose up -d 2>/dev/null || true
    fi
    
    # Start database services
    echo '[$(date)] Starting database services...'
    sudo service postgresql start 2>/dev/null || true
    sudo service redis-server start 2>/dev/null || true
    sudo service neo4j start 2>/dev/null || true
    
    # Wait for services
    sleep 5
    
    # Start Claude in background
    echo '[$(date)] Starting Claude with dangerous permissions...'
    if command -v tmux >/dev/null 2>&1; then
        tmux new-session -d -s 'hearthlink-claude' -c '%PROJECT_PATH%' 'claude --dangerously-skip-permissions'
        echo '[$(date)] Claude started in tmux session: hearthlink-claude'
    else
        nohup claude --dangerously-skip-permissions > logs/claude_output.log 2>&1 &
        echo '[$(date)] Claude started in background (PID: $!)'
    fi
    
    echo '[$(date)] Background services started successfully'
"

echo [%date% %time%] Hearthlink Service Started >> "%LOG_FILE%"

:: Exit silently
exit /b 0