# socket_handler.py – Final Form (Updated + SOP Compliant)
import json
import asyncio
import logging
import time
import os

# Dependency stubs and safe imports
try:
    from ui_bridge import submit_prompt
except ImportError:
    def submit_prompt(session_id, prompt):
        logging.info(f"Stubbed submit_prompt for session {session_id}: {prompt}")
        return {"response": f"Alden echoes: {prompt}"}

# Placeholder for now_timestamp if not imported
def now_timestamp():
    return int(time.time())

# Placeholder for safe_send if not imported
async def safe_send(connection, message_dict):
    try:
        if connection and connection.open:
            await connection.send(json.dumps(message_dict))
    except Exception as e:
        logging.error(f"Failed to send message: {e}. Message: {message_dict}")

# Placeholder for forge_log if not imported
# For this example, we'll just use the standard logging module for telemetry as well.
def forge_log(service, event_type, payload):
    logging.info(f"FORGE_LOG - Service: {service}, Type: {event_type}, Payload: {payload}")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

connected_clients = {}  # session_id -> connection object
client_sessions = {}    # connection object -> session_id
tab_heartbeats = {}     # session_id -> last_seen_timestamp
replay_buffer = {}      # session_id -> (timestamp, data)

HEARTBEAT_INTERVAL = 30  # seconds
BUFFER_TTL = 60          # seconds
MEMORY_TTL = 120         # seconds
CLEANUP_INTERVAL = 60    # seconds

VALID_TOKENS = set(os.environ.get("VALID_TOKENS", "").split(","))

def verify_console_auth(token):
    if not token:
        logging.warning("Auth verification failed: No token provided.")
        return False
    if token in VALID_TOKENS:
        logging.info(f"Auth verification successful for token (first 5 chars): {token[:5]}...")
        return True
    logging.warning(f"Auth verification failed: Invalid token (first 5 chars): {token[:5]}...")
    return False

def route_input_to_alden(session_id, prompt, connection):
    try:
        result = submit_prompt(session_id, prompt)
        logging.info(f"Alden response for session {session_id}: {result}")
        return {
            "type": "response",
            "source": "alden",
            "payload": {"content": result.get("response", "[No reply from Alden]")},
            "sessionId": session_id
        }
    except Exception as e:
        logging.error(f"Exception in Alden route for session {session_id}: {e}", exc_info=True)
        return {
            "type": "error",
            "message": f"Exception processing your request with Alden: {str(e)}",
            "sessionId": session_id
        }

async def memory_cleanup_loop(ttl=MEMORY_TTL, interval=CLEANUP_INTERVAL):
    while True:
        await asyncio.sleep(interval)
        now = now_timestamp()
        stale_sessions_ids = [
            sid for sid, last_seen in tab_heartbeats.items()
            if (now - last_seen) > ttl
        ]

        for sid in stale_sessions_ids:
            logging.info(f"MemoryCleaner: Expiring stale session: {sid}")
            connection_to_close = connected_clients.pop(sid, None)
            if connection_to_close:
                client_sessions.pop(connection_to_close, None)
                try:
                    if connection_to_close.open:
                        await connection_to_close.close(code=1000, reason="Session expired due to inactivity")
                    logging.info(f"MemoryCleaner: Closed connection for session: {sid}")
                except Exception as e:
                    logging.warning(f"MemoryCleaner: Error closing connection for session {sid}: {e}", exc_info=False)
            tab_heartbeats.pop(sid, None)
            replay_buffer.pop(sid, None)

        # Clean expired entries from replay_buffer
        expired_replays = [sid for sid, (ts, _) in replay_buffer.items() if (now - ts) > BUFFER_TTL]
        for sid in expired_replays:
            replay_buffer.pop(sid, None)
        logging.info(f"ReplayCleaner: {len(expired_replays)} replay buffer entries expired.")
        logging.info(f"MemoryCleaner: Cleanup finished. {len(stale_sessions_ids)} sessions expired.")

def is_console_verified(connection):
    session_id = client_sessions.get(connection)
    return bool(session_id and session_id in connected_clients)

# --- Main Server Setup (optional, not included in runtime module if externally managed) ---
# Example usage:
# import websockets
# async def main():
#     asyncio.create_task(memory_cleanup_loop())
#     async with websockets.serve(handle_connection, "localhost", 8765):
#         await asyncio.Future()
# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         logging.info("Server shutting down...")

async def handle_connection(connection, path):
    session_id = None
    client_ip = connection.remote_address
    logging.info(f"New connection attempt from {client_ip}")

    try:
        while True:
            raw_message = await connection.recv()
            try:
                data = json.loads(raw_message)
            except json.JSONDecodeError:
                logging.warning(f"Invalid JSON received from {client_ip} (session: {session_id}): {raw_message}")
                await safe_send(connection, {"type": "error", "message": "Invalid JSON format."})
                continue

            msg_type = data.get("type")
            if not msg_type:
                logging.warning(f"Message missing 'type' field: {data}")
                await safe_send(connection, {"type": "error", "message": "Missing message type."})
                continue

            current_message_session_id = data.get("sessionId")

            if not session_id and msg_type == "handshake":
                session_id = current_message_session_id
            elif not session_id:
                logging.warning(f"Message received from {client_ip} without established session_id and not a handshake: {msg_type}")
                await safe_send(connection, {"type": "error", "message": "Session not initialized. Please handshake."})
                continue
            elif current_message_session_id and session_id != current_message_session_id:
                logging.warning(f"Session ID mismatch from {client_ip}. Expected {session_id}, got {current_message_session_id}.")
                await safe_send(connection, {"type": "error", "message": "Session ID mismatch."})
                continue

            active_session_id = session_id
            auth_token = data.get("auth")

            if msg_type == "handshake":
                if not active_session_id:
                    logging.warning(f"Handshake from {client_ip} missing sessionId.")
                    await safe_send(connection, {"type": "error", "message": "Handshake requires sessionId."})
                    return

                logging.info(f"Handshake received: session={active_session_id}, source={data.get('source')}, auth_present={bool(auth_token)}")
                if not verify_console_auth(auth_token):
                    await safe_send(connection, {"type": "error", "message": "Unauthorized", "sessionId": active_session_id})
                    await connection.close(code=1008, reason="Invalid authentication token")
                    return

                if active_session_id in connected_clients and connected_clients[active_session_id] != connection:
                    old_conn = connected_clients[active_session_id]
                    client_sessions.pop(old_conn, None)
                    try:
                        if old_conn.open:
                            await old_conn.send(json.dumps({"type": "alert", "message": "New connection for this session established. This tab is being disconnected.", "sessionId": active_session_id}))
                            await old_conn.close(code=1000, reason="Session superseded")
                    except Exception as e_old_conn:
                        logging.error(f"Error closing superseded connection for session {active_session_id}: {e_old_conn}")

                connected_clients[active_session_id] = connection
                client_sessions[connection] = active_session_id
                tab_heartbeats[active_session_id] = now_timestamp()

                await safe_send(connection, {
                    "type": "ack",
                    "verified": True,
                    "message": "Handshake successful. Connection established.",
                    "sessionId": active_session_id
                })

            elif not is_console_verified(connection):
                await safe_send(connection, {"type": "error", "message": "Unauthorized. Please complete handshake.", "sessionId": active_session_id})
                continue

            elif msg_type == "ping":
                ping_id = data.get("id")
                timestamp = data.get("timestamp")
                await safe_send(connection, {
                    "type": "echo",
                    "id": ping_id,
                    "timestamp": timestamp,
                    "server_received_at": now_timestamp(),
                    "sessionId": active_session_id
                })
                tab_heartbeats[active_session_id] = now_timestamp()

            elif msg_type == "tab_alive":
                tab_heartbeats[active_session_id] = now_timestamp()
                await safe_send(connection, {"type": "ack_tab_alive", "sessionId": active_session_id, "timestamp": now_timestamp()})

            elif msg_type == "input":
                target = data.get("target")
                prompt = data.get("payload", {}).get("content", "")

                if not prompt:
                    logging.warning(f"Empty prompt received for session {active_session_id}. Full message: {data}")
                    await safe_send(connection, {
                        "type": "error",
                        "message": "Missing input content.",
                        "sessionId": active_session_id
                    })
                    continue

                if target == "alden":
                    reply = route_input_to_alden(active_session_id, prompt, connection)
                    await safe_send(connection, reply)
                else:
                    await safe_send(connection, {
                        "type": "error",
                        "message": f"Unhandled input target: {target}",
                        "sessionId": active_session_id
                    })

            elif msg_type == "command":
                payload = data.get("payload")
                await safe_send(connection, {
                    "type": "ack_command",
                    "sessionId": active_session_id,
                    "timestamp": now_timestamp()
                })
                replay_buffer[active_session_id] = (now_timestamp(), data)

            elif msg_type == "telemetry":
                payload = data.get("payload")
                await safe_send(connection, {
                    "type": "ack_telemetry",
                    "sessionId": active_session_id,
                    "timestamp": now_timestamp()
                })
                forge_log("bridgekeeper", "telemetry", payload)

            else:
                await safe_send(connection, {
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}",
                    "sessionId": active_session_id
                })

    except asyncio.CancelledError:
        logging.info(f"Connection task cancelled for session {session_id} ({client_ip}).")
    except Exception as e:
        if isinstance(e, (ConnectionAbortedError, ConnectionResetError)) or 'ConnectionClosed' in type(e).__name__:
            logging.info(f"Connection closed (session: {session_id}, ip: {client_ip}): {e}")
        else:
            logging.error(f"WebSocket handler exception for session {session_id} ({client_ip}): {e}", exc_info=True)
            if connection.open:
                await safe_send(connection, {
                    "type": "error",
                    "message": f"Server error: {str(e)}",
                    "sessionId": session_id
                })
    finally:
        logging.info(f"Disconnecting client: session={session_id}, ip={client_ip}")
        if connection in client_sessions:
            retrieved_session_id = client_sessions.pop(connection, None)
            if retrieved_session_id:
                connected_clients.pop(retrieved_session_id, None)
                tab_heartbeats.pop(retrieved_session_id, None)
                replay_buffer.pop(retrieved_session_id, None)
                logging.info(f"Cleaned up resources for session: {retrieved_session_id}")
            else:
                logging.warning(f"Connection not found in client_sessions during cleanup for IP: {client_ip}")
        elif session_id:
            connected_clients.pop(session_id, None)
            tab_heartbeats.pop(session_id, None)
            replay_buffer.pop(session_id, None)
            logging.info(f"Cleaned up resources for partially registered session: {session_id}")

        if connection.open:
            try:
                await connection.close(code=1000, reason="Connection cleanup")
            except Exception as e_close:
                logging.error(f"Error during final connection close for session {session_id}: {e_close}")
        logging.info(f"Client {client_ip} (session: {session_id}) fully disconnected.")
