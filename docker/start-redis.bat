@echo off
REM Start Redis service for Hearthlink

set HEARTHLINK_ROOT=%~dp0..
set DOCKER_ROOT=%HEARTHLINK_ROOT%\docker
set REDIS_HOME=%DOCKER_ROOT%\services\redis

echo Starting Redis for Hearthlink...

REM Start Redis with config
cd /d "%REDIS_HOME%"
redis-server.exe "%DOCKER_ROOT%\config\redis\redis.conf"

pause