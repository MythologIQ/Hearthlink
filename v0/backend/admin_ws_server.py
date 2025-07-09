# admin_ws_server.py
# Diagnostic WebSocket Interface for Nexus

import asyncio
import websockets
import json
from core.utils import now_timestamp
from core.bridge_log import forge_log, register_admin_socket, unregister_admin_socket

PORT = 8766

def format_log(message, level="info", **kwargs):
    return json.dumps({
        "type": "log",
        "level": level,
        "timestamp": now_timestamp(),
        "message": message,
        **kwargs
    })

async def handle_admin(ws, path):
    register_admin_socket(ws)
    forge_log("info", "[AdminWS] Admin connected")
    try:
        async for message in ws:
            try:
                data = json.loads(message)
                if data.get("type") == "trace":
                    await ws.send(format_log("Diagnostic trace received.", level="trace", origin="admin"))
                else:
                    await ws.send(format_log("Unknown admin command.", level="warn"))
            except Exception as e:
                await ws.send(format_log(f"Malformed admin message: {str(e)}", level="error"))
    finally:
        unregister_admin_socket(ws)
        forge_log("info", "[AdminWS] Admin disconnected")

async def main():
    forge_log("info", f"[AdminWS] Starting admin WebSocket on port {PORT}")
    server = await websockets.serve(handle_admin, "0.0.0.0", PORT)
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        forge_log("info", "[AdminWS] Shutdown initiated")
