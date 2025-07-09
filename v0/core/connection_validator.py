# core/connection_validator.py

import asyncio
from core.utils import now_timestamp
from core.bridge_log import forge_log

async def start_heartbeat(connected_clients, session_stats, unregister_fn):
    while True:
        to_disconnect = []
        for session_id, ws in connected_clients.items():
            try:
                await ws.ping()
                session_stats[session_id]["last_ping"] = now_timestamp()
            except:
                to_disconnect.append(session_id)
        for sid in to_disconnect:
            unregister_fn(sid, connected_clients)
            forge_log("warning", f"[Heartbeat] Disconnected stale client {sid}", sessionId=sid)
        await asyncio.sleep(30)
