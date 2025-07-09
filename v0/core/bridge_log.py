# core/bridge_log.py — Unified logging output

import json
import logging
import os
from core.utils import now_timestamp

LOG_FILE = "nexus_bridge.log"
admin_sockets = set()  # Sockets connected to admin_ws_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def forge_log(level, message, **context):
    entry = {
        "timestamp": now_timestamp(),
        "level": level,
        "message": message,
        **context
    }
    logging_func = getattr(logging, level, logging.info)
    logging_func(f"{message} | {json.dumps(context)}")
    notify_admins(entry)

def notify_admins(entry):
    msg = json.dumps({"type": "log", **entry})
    stale = []
    for ws in admin_sockets:
        try:
            import asyncio
            asyncio.create_task(ws.send(msg))
        except:
            stale.append(ws)
    for ws in stale:
        admin_sockets.remove(ws)

# Used in admin_ws_server.py to bind admin clients
def register_admin_socket(ws):
    admin_sockets.add(ws)

def unregister_admin_socket(ws):
    if ws in admin_sockets:
        admin_sockets.remove(ws)
