# 🚀 Alden AI Companion - Launcher Guide

## Quick Start

### Windows Users 🪟
**Double-click** one of these files:
- `launch_alden_windows.bat` (recommended)
- `launch_alden.bat` (alternative)

**Or run from Command Prompt:**
```cmd
python start_alden_direct.py
```

### Linux/macOS/WSL Users 🐧🍎
**Run from terminal:**
```bash
./launch_alden.sh
```

**Or directly:**
```bash
python3 start_alden_direct.py
```

## What Happens When You Launch

1. **Port Detection**: Automatically finds an available port (8888, 8000, 8080, etc.)
2. **Database Setup**: Creates user and agent records if needed
3. **Memory System**: Initializes Vault encrypted storage
4. **LLM Connection**: Connects to Ollama (llama3.2:3b model)
5. **API Server**: Starts FastAPI server with conversation endpoints

## Testing Alden

The launcher will show you the port Alden is running on. Test with:

### Windows (Command Prompt or PowerShell):
```cmd
curl http://localhost:8888/health
curl -X POST http://localhost:8888/conversation -H "Content-Type: application/json" -d "{\"message\": \"Hello Alden\"}"
```

### Linux/macOS/WSL:
```bash
curl http://localhost:8888/health
curl -X POST http://localhost:8888/conversation -H "Content-Type: application/json" -d '{"message": "Hello Alden"}'
```

## Requirements

- **Python 3.9+** (Windows: from python.org, Linux: package manager)
- **Ollama** running with llama3.2:3b model
- **Dependencies**: Automatically installed when you first run

## Troubleshooting

### "Python not found"
- **Windows**: Install from https://www.python.org/downloads/ and check "Add Python to PATH"
- **Linux**: `sudo apt install python3` (Ubuntu/Debian) or equivalent
- **macOS**: `brew install python3` or use the system Python

### "Port already in use"
The launcher automatically finds an available port. Check the console output for the actual port number.

### "Connection refused"
Make sure Ollama is running: `ollama serve`

## Features

✅ **Cross-platform compatibility**  
✅ **Automatic port detection**  
✅ **Database integration with memory persistence**  
✅ **Personality system with 10 adaptive traits**  
✅ **Encrypted Vault storage**  
✅ **FastAPI with conversation endpoints**  
✅ **Optimized response times**

---

**Alden is ready to be your AI companion!** 🤖✨