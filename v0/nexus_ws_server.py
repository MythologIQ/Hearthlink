# nexus_ws_server.py
# Orchestrator for the Nexus Bridgekeeper WebSocket infrastructure

from core.socket_handler import handle_connection
from core.connection_validator import start_heartbeat
from core.echo_inspector import inspect_echo
import asyncio
import websockets
import logging
import os

PORT = 8765

connected_clients = {}
session_stats = {}

async def nexus_handler(connection):
    print(f"[DEBUG] ServerConnection received: {connection}")
    await handle_connection(connection, connected_clients, session_stats)

async def main():
    logging.basicConfig(level=logging.INFO)
    print(f"[DEBUG] Loaded from: {os.path.abspath(__file__)}")
    server = await websockets.serve(
        nexus_handler,
        "0.0.0.0",
        PORT
    )
    logging.info(f"[Nexus] WebSocket server started on port {PORT}")
    asyncio.create_task(start_heartbeat(connected_clients, session_stats))
    await server.wait_closed()

if __name__ == "__main__":
    print("[DEBUG] Executing nexus_ws_server.py - ACTIVE SCRIPT")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("[Nexus] WebSocket server shutdown initiated")
