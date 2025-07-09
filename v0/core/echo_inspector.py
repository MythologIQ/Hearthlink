# core/echo_inspector.py

from .utils import now_timestamp
from .bridge_log import forge_log

def inspect_echo(echo_id, session_id, session_stats):
    """
    Inspects the round-trip time (RTT) of an echo response.

    Parameters:
        echo_id (str): The unique identifier for the echo message.
        session_id (str): The identifier for the current session.
        session_stats (dict): A dictionary tracking session-specific metrics, expected to have 'last_ping' timestamps.

    Behavior:
        - Calculates RTT as the difference between the current timestamp and the last recorded ping timestamp.
        - Appends RTT to the session-specific RTT history.
        - Logs the RTT and flags it if exceeding the threshold of 1.5 seconds.

    Returns:
        None
    """
    if session_id not in session_stats:
        return
    rtt = now_timestamp() - session_stats[session_id].get("last_ping", now_timestamp())
    session_stats[session_id]["rtt"].append(rtt)
    forge_log("info", f"[Echo] ID {echo_id} RTT: {rtt:.2f} seconds", sessionId=session_id, echoId=echo_id, rtt=rtt)
    if rtt > 1.5:
        forge_log("warning", f"[Echo] High RTT for {session_id}: {rtt:.2f} seconds", sessionId=session_id, echoId=echo_id, rtt=rtt)