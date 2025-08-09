@echo off
REM Windows batch script to start Hearthlink database services
REM This script downloads and starts Neo4j, Redis, and Qdrant

set HEARTHLINK_ROOT=%~dp0..
set DOCKER_ROOT=%HEARTHLINK_ROOT%\docker
set DATA_ROOT=%DOCKER_ROOT%\data
set CONFIG_ROOT=%DOCKER_ROOT%\config

echo Starting Hearthlink database services...

REM Create services directory
if not exist "%DOCKER_ROOT%\services" mkdir "%DOCKER_ROOT%\services"

REM Download and setup Redis (Windows compatible)
echo Setting up Redis...
if not exist "%DOCKER_ROOT%\services\redis" (
    mkdir "%DOCKER_ROOT%\services\redis"
    cd "%DOCKER_ROOT%\services\redis"
    curl -L -o redis.zip https://github.com/microsoftarchive/redis/releases/download/win-3.2.100/Redis-x64-3.2.100.zip
    powershell -command "Expand-Archive -Path redis.zip -DestinationPath . -Force"
    del redis.zip
)

REM Download and setup Neo4j
echo Setting up Neo4j...
if not exist "%DOCKER_ROOT%\services\neo4j" (
    mkdir "%DOCKER_ROOT%\services\neo4j"
    cd "%DOCKER_ROOT%\services\neo4j"
    curl -L -o neo4j.zip https://neo4j.com/artifact.php?name=neo4j-community-5.15.0-windows.zip
    powershell -command "Expand-Archive -Path neo4j.zip -DestinationPath . -Force"
    del neo4j.zip
)

REM Download and setup Qdrant
echo Setting up Qdrant...
if not exist "%DOCKER_ROOT%\services\qdrant" (
    mkdir "%DOCKER_ROOT%\services\qdrant"
    cd "%DOCKER_ROOT%\services\qdrant"
    curl -L -o qdrant.exe https://github.com/qdrant/qdrant/releases/latest/download/qdrant-x86_64-pc-windows-msvc.exe
)

echo All services configured! Use start-redis.bat, start-neo4j.bat, start-qdrant.bat to launch individual services.
pause