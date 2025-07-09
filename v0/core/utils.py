# core/utils.py

import time
import dis
import json
import asyncio
from datetime import datetime

def now_timestamp():
    return time.time()

def now_iso():
    """Returns current UTC time as ISO 8601 string."""
    return datetime.utcnow().isoformat()

def delta_seconds(start, end):
    """Calculates difference in seconds between two timestamps."""
    return end - start

def jitter_backoff(attempt, base=0.5, factor=2, cap=30):
    """
    Generates exponential backoff with jitter.
    Useful for retry delays.

    Parameters:
    - attempt: int, the retry count
    - base: float, base wait time in seconds
    - factor: float, multiplier per attempt
    - cap: float, maximum wait time

    Returns:
    - float, delay time in seconds
    """
    import random
    delay = min(cap, base * (factor ** attempt))
    return delay * random.uniform(0.8, 1.2)

def no_direct_send(fn):
    bytecode = dis.Bytecode(fn)
    for instr in bytecode:
        if instr.opname == "LOAD_ATTR" and instr.argval == "send":
            raise RuntimeError("Direct .send call detected. Use safe_send().")
    return fn

async def safe_send(socket, message):
    try:
        if socket.closed:
            return False
        payload = message if isinstance(message, str) else json.dumps(message)
        await socket.send(payload)
        return True
    except Exception as e:
        print(f"[safe_send] Failed to send message: {e}")
        return False
