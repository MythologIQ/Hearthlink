@echo off
REM Start Neo4j service for Hearthlink

set HEARTHLINK_ROOT=%~dp0..
set DOCKER_ROOT=%HEARTHLINK_ROOT%\docker
set NEO4J_HOME=%DOCKER_ROOT%\services\neo4j\neo4j-community-5.15.0
set NEO4J_DATA=%DOCKER_ROOT%\data\neo4j

echo Starting Neo4j for Hearthlink...

REM Set Neo4j environment variables
set NEO4J_CONF=%DOCKER_ROOT%\config\neo4j
set NEO4J_AUTH=neo4j/hearthlink_neo4j_2025

REM Start Neo4j
cd /d "%NEO4J_HOME%"
bin\neo4j.bat console

pause