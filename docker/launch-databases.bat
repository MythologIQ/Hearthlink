@echo off
REM Launch all Hearthlink database services

set HEARTHLINK_ROOT=%~dp0..
set DOCKER_ROOT=%HEARTHLINK_ROOT%\docker

echo Launching Hearthlink Database Services...
echo =====================================

REM Check if services are set up
if not exist "%DOCKER_ROOT%\services" (
    echo Setting up services first...
    call "%DOCKER_ROOT%\start-services.bat"
)

echo Starting services in background...

REM Start Redis
echo Starting Redis...
start "Hearthlink Redis" cmd /c "%DOCKER_ROOT%\start-redis.bat"

REM Wait a moment
timeout /t 3 /nobreak >nul

REM Start Neo4j
echo Starting Neo4j...
start "Hearthlink Neo4j" cmd /c "%DOCKER_ROOT%\start-neo4j.bat"

REM Wait a moment
timeout /t 3 /nobreak >nul

REM Start Qdrant
echo Starting Qdrant...
start "Hearthlink Qdrant" cmd /c "%DOCKER_ROOT%\start-qdrant.bat"

echo All services launched! Check individual windows for status.
echo Services will be available at:
echo   Neo4j: http://localhost:7474 (bolt://localhost:7687)
echo   Redis: localhost:6379
echo   Qdrant: http://localhost:6333
echo.
echo Press any key to continue...
pause >nul