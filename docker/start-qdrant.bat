@echo off
REM Start Qdrant service for Hearthlink

set HEARTHLINK_ROOT=%~dp0..
set DOCKER_ROOT=%HEARTHLINK_ROOT%\docker
set QDRANT_HOME=%DOCKER_ROOT%\services\qdrant

echo Starting Qdrant for Hearthlink...

REM Start Qdrant with config
cd /d "%QDRANT_HOME%"
qdrant.exe --config-path "%DOCKER_ROOT%\config\qdrant\config.yaml"

pause