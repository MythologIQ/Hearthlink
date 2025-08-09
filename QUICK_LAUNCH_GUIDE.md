# 🚀 Hearthlink Launch Guide

## Quick Start (Windows)

### Option 1: Native App (Recommended)
```bash
# Start backend services
npm run services:start

# In another terminal, launch the app
npm run native
```

### Option 2: Windows Batch File
```cmd
# Double-click in Windows Explorer
HearthlinkService.bat
```

### Option 3: Manual Step-by-Step
```bash
# 1. Start services
python3 service_orchestrator.py

# 2. Wait 5 seconds, then in another terminal
npm run native
```

## Verification Steps

1. **Backend Running**: Check that services show [OK] status
2. **UI Opens**: Native window should appear with Hearthlink interface
3. **Alden Available**: Click on ALDEN in the radial menu
4. **Chat Works**: Type a message and get a response

## Troubleshooting

- **Services won't start**: Make sure Ollama is running first
- **UI won't open**: Try `npm run build` first
- **No response from Alden**: Check service logs for errors

## Current Status

✅ Alden persona fully functional with memory
✅ Backend services configured and tested
✅ UI components exist for Alden interface
⚠️  Final UI-to-backend connection needs verification

The system is ready for launch - you just need to start the services
and open the native app to begin using Alden!
