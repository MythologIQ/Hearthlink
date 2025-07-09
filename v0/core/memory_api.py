# memory_api.py – Core memory storage for Nexus agents

import json
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MEMORY_FILE = "nexus_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def snapshot_memory(agent, skills, patterns):
    mem = load_memory()
    mem[agent] = {
        "skills": skills,
        "patterns": patterns
    }
    save_memory(mem)

@app.post("/memory")
async def store_agent_memory(request: Request):
    payload = await request.json()
    agent = payload.get("agent")
    skills = payload.get("skills", {})
    patterns = payload.get("patterns", {})

    snapshot_memory(agent, skills, patterns)
    return {"status": "ok"}
