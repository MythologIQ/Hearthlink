# Hearthlink Human Verification Guide

## Purpose
This guide provides step-by-step instructions to launch and verify Hearthlink's foundation systems. **Success is defined as no simulation, no hallucination, only confirmed functionality.**

## Command Line Environment Setup

### Windows Users - Choose Your Terminal:

**Option A: PowerShell (Recommended)**
```powershell
# Open PowerShell as Administrator
# Press Win + X, select "Windows PowerShell (Admin)"
# Navigate to MythologIQ\Hearthlink directory:
cd "G:\MythologIQ\Hearthlink"
# OR if installed in default location:
cd "C:\Program Files\MythologIQ\Hearthlink"
```

**Option B: Command Prompt**
```cmd
# Open Command Prompt as Administrator
# Press Win + R, type "cmd", press Ctrl+Shift+Enter
# Navigate to MythologIQ\Hearthlink directory:
cd "G:\MythologIQ\Hearthlink"
# OR if installed in default location:
cd "C:\Program Files\MythologIQ\Hearthlink"
```

**Option C: Git Bash (If you have Git installed)**
```bash
# Open Git Bash
# Right-click in MythologIQ\Hearthlink folder and select "Git Bash Here"
# Or navigate manually:
cd /g/MythologIQ/Hearthlink
# OR if installed in default location:
cd "/c/Program Files/MythologIQ/Hearthlink"
```

**Option D: WSL (Windows Subsystem for Linux)**
```bash
# If you have WSL installed
# Open WSL terminal
# Navigate to Windows MythologIQ\Hearthlink directory:
cd /mnt/g/MythologIQ/Hearthlink
# OR if installed in default location:
cd "/mnt/c/Program Files/MythologIQ/Hearthlink"
```

### Linux/macOS Users:
```bash
# Open Terminal application
# Navigate to project directory:
cd /path/to/hearthlink
```

**🚨 IMPORTANT:** 
- Replace paths with your actual MythologIQ\Hearthlink installation location:
  - **G: Drive**: `G:\MythologIQ\Hearthlink` (current installation)
  - **Default**: `C:\Program Files\MythologIQ\Hearthlink` (standard installation)
- On Windows, use forward slashes (/) or double backslashes (\\) in paths
- You will need **3 separate terminal windows/tabs** open simultaneously
- **Windows 10/11 users:** PowerShell is recommended and comes pre-installed

### Quick Start for Windows Users:
1. **Press `Win + X`** and select **"Windows PowerShell (Admin)"**
2. **Navigate to MythologIQ\Hearthlink folder:** `cd "G:\MythologIQ\Hearthlink"`
3. **Follow the launch instructions below** using PowerShell commands

## System Requirements Verification

### Prerequisites Check
Before starting, verify these requirements in your chosen terminal:

**PowerShell/Command Prompt:**
```powershell
# Check Python version (3.10+ required)
python3 --version

# Check Node.js version (18+ recommended)
node --version

# Verify Ollama is running
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -ErrorAction Stop
    if ($response.models) { Write-Host "✅ Ollama running" } else { Write-Host "❌ Ollama no models" }
} catch { Write-Host "❌ Ollama not accessible" }

# Check project directory
if (Test-Path "hearthlink_data\hearthlink.db") { Write-Host "✅ Database exists" } else { Write-Host "❌ Database missing" }
```

**Git Bash/WSL (Linux commands):**
```bash
# Check Python version (3.10+ required)
python3 --version

# Check Node.js version (18+ recommended)
node --version

# Verify Ollama is running
curl -s http://localhost:11434/api/tags | grep -q "models" && echo "✅ Ollama running" || echo "❌ Ollama not accessible"

# Check project directory
ls -la hearthlink_data/hearthlink.db && echo "✅ Database exists" || echo "❌ Database missing"
```

**Expected Results:**
- Python 3.10+
- Node.js 18+
- Ollama accessible with models
- Database file exists

## Launch Instructions

### Step 1: Start Core Services

**Terminal 1 - Local LLM API:**
```bash
# Navigate to MythologIQ\Hearthlink directory
cd "G:\MythologIQ\Hearthlink"      # G: Drive installation
# OR
cd "C:\Program Files\MythologIQ\Hearthlink"  # Default installation
# Git Bash paths:
cd /g/MythologIQ/Hearthlink        # G: Drive (Git Bash)
cd "/c/Program Files/MythologIQ/Hearthlink"  # Default (Git Bash)
# WSL paths:
cd /mnt/g/MythologIQ/Hearthlink    # G: Drive (WSL)
cd "/mnt/c/Program Files/MythologIQ/Hearthlink"  # Default (WSL)

# Start Local LLM API
python3 src/api/local_llm_api.py
# OR on Windows if python3 doesn't work:
python src/api/local_llm_api.py

# Expected output:
# "Local LLM API Server running on http://localhost:8001"
# Keep this terminal open and running
```

**Terminal 2 - Alden API Service (open new terminal/tab):**
```bash
# Navigate to same MythologIQ\Hearthlink directory
cd "G:\MythologIQ\Hearthlink"      # G: Drive installation
# OR  
cd "C:\Program Files\MythologIQ\Hearthlink"  # Default installation

# Start Alden API Service  
python3 src/run_alden.py api --engine ollama --model llama3.2:3b --port 8000
# OR on Windows if python3 doesn't work:
python src/run_alden.py api --engine ollama --model llama3.2:3b --port 8000

# Expected output:
# "📡 API will be available at: http://127.0.0.1:8000"
# "✅ Vault connection initialized" 
# Keep this terminal open and running
```

### Step 2: Verify Service Health

**Terminal 3 - Testing (open new terminal/tab):**
```bash
# Navigate to MythologIQ\Hearthlink directory
cd "G:\MythologIQ\Hearthlink"      # G: Drive installation
# OR
cd "C:\Program Files\MythologIQ\Hearthlink"  # Default installation

# Test Local LLM Health
curl -s http://localhost:8001/api/health
# Expected: {"status": "healthy", "models_available": 4, "ollama_connected": true}

# Test Alden API Health  
curl -s http://127.0.0.1:8000/api/v1/alden/health
# Expected: {"status": "healthy", "service": "alden-api", "version": "1.0.0"}
```

**PowerShell Users (Recommended for Windows):**
```powershell
# Test Local LLM Health
Invoke-RestMethod -Uri "http://localhost:8001/api/health"
# Expected: status=healthy, models_available=4, ollama_connected=True

# Test Alden API Health
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/alden/health"
# Expected: status=healthy, service=alden-api, version=1.0.0

# OR open in browser:
# Navigate to: http://localhost:8001/api/health
# Navigate to: http://127.0.0.1:8000/api/v1/alden/health
```

**🚨 CRITICAL: If either health check fails, STOP and troubleshoot before proceeding.**

## Core Functionality Verification

### Test Scenario 1: Basic AI Conversation

**Objective:** Verify Alden can generate real AI responses through the full stack.

**Using curl (Linux/macOS/Git Bash/WSL):**
```bash
# Send message to Alden
curl -X POST http://127.0.0.1:8888/api/v1/alden/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello Alden, please introduce yourself and tell me about your capabilities."
  }'
```

**Using PowerShell (Windows):**
```powershell
# Send message to Alden
$body = @{
    message = "Hello Alden, please introduce yourself and tell me about your capabilities."
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8888/api/v1/alden/message" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body

# Expected Results:
# - "response": Contains multi-paragraph AI-generated introduction
# - "session_id": UUID format (e.g., "4225477e-4b21-4746-af64-a008c1e015c2")
# - "model": "llama3:latest" or similar
# - "response_time": Numeric value (should be < 15 seconds)
# - "usage": Token counts for prompt and completion
```

**Success Criteria:**
- ✅ Response contains coherent, contextual AI-generated content
- ✅ Session ID is generated and returned
- ✅ Response time is reasonable (<15s)
- ✅ Token usage statistics included

### Test Scenario 2: Memory Persistence

**Objective:** Verify conversations are saved and retrieved across interactions.

```bash
# First message in session
curl -X POST http://127.0.0.1:8888/api/v1/alden/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My name is [YOUR_NAME] and I work in [YOUR_FIELD]. Please remember this.",
    "session_id": "test-memory-session"
  }' | jq '.response'

# Second message referencing first
curl -X POST http://127.0.0.1:8888/api/v1/alden/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What do you remember about me?",
    "session_id": "test-memory-session"
  }' | jq '.response'
```

**Success Criteria:**
- ✅ Second response references your name and field from first message
- ✅ Alden demonstrates contextual awareness of conversation history
- ✅ Same session_id maintains conversation continuity

### Test Scenario 3: System Status and Health

**Objective:** Verify system monitoring and status reporting.

```bash
# Get comprehensive Alden status
curl -s http://127.0.0.1:8888/api/v1/alden/status | jq

# Expected sections:
# - "persona_id": "alden" 
# - "traits": Object with personality traits (openness, conscientiousness, etc.)
# - "llm_status": Object showing LLM health and connection info
# - "stats": Object with conversation statistics
```

**Success Criteria:**
- ✅ All status sections present and populated
- ✅ LLM status shows "connected": true
- ✅ Personality traits show numeric values
- ✅ Statistics reflect actual usage (increasing message counts)

## Performance Verification

### Test Scenario 4: Response Time Consistency

**Objective:** Verify system performance meets stated benchmarks.

```bash
# Time multiple requests
for i in {1..3}; do
  echo "Request $i:"
  time curl -s -X POST http://127.0.0.1:8000/api/v1/alden/message \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Test message $i: What is artificial intelligence?\"}" \
    | jq -r '.response_time'
  echo "---"
done
```

**Success Criteria:**
- ✅ All requests complete successfully
- ✅ Response times consistently under 15 seconds
- ✅ No timeouts or connection errors

### Test Scenario 5: Load Handling

**Objective:** Verify system handles multiple requests properly.

```bash
# Run load test (background processes)
for i in {1..3}; do
  curl -s -X POST http://127.0.0.1:8000/api/v1/alden/message \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Concurrent test $i\"}" &
done

# Wait for completion
wait
echo "All concurrent requests completed"
```

**Success Criteria:**
- ✅ All 3 concurrent requests complete successfully
- ✅ No errors or failures under concurrent load
- ✅ System remains responsive after load test

## Data Management Verification

### Test Scenario 6: Database Backup System

**Objective:** Verify backup and recovery systems work.

```bash
# Create backup
python3 src/database/backup_manager.py create --type manual

# Expected output:
# ✅ Backup created successfully: backup_YYYYMMDD_HHMMSS
# Database size: XXX,XXX bytes
# Vault files: X
# Duration: X.XXs

# List backups
python3 src/database/backup_manager.py list

# Check backup status
python3 src/database/backup_manager.py status
```

**Success Criteria:**
- ✅ Backup creation completes without errors
- ✅ Database and vault files are backed up
- ✅ Backup list shows created backup with success status
- ✅ Status shows positive success count and recent backup timestamp

### Test Scenario 7: Memory Management

**Objective:** Verify memory pruning and analysis systems.

```bash
# Check memory usage statistics
python3 src/memory/memory_pruning_manager.py stats

# Expected output showing current memory usage:
# Total conversations: X
# Database size: XXX,XXX bytes
# Vault size: X,XXX bytes

# Analyze conversations (if any exist)
python3 src/memory/memory_pruning_manager.py analyze
```

**Success Criteria:**
- ✅ Statistics command completes and shows database/vault sizes
- ✅ Analysis runs without errors
- ✅ Memory management system is operational

## Integration Verification

### Test Scenario 8: End-to-End Conversation Flow

**Objective:** Verify complete system integration from request to response.

```bash
# Extended conversation to test full integration
SESSION_ID="integration-test-$(date +%s)"

echo "Starting integration test with session: $SESSION_ID"

# Message 1: Introduction
curl -s -X POST http://127.0.0.1:8000/api/v1/alden/message \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Hi Alden, I'm testing the Hearthlink system. Can you explain what you are?\",
    \"session_id\": \"$SESSION_ID\"
  }" | jq -r '.response' > response1.txt

echo "Response 1 received ($(wc -w < response1.txt) words)"

# Message 2: Follow-up with context
curl -s -X POST http://127.0.0.1:8000/api/v1/alden/message \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Based on what you just told me, what makes you different from other AI assistants?\",
    \"session_id\": \"$SESSION_ID\"
  }" | jq -r '.response' > response2.txt

echo "Response 2 received ($(wc -w < response2.txt) words)"

# Message 3: Memory test
curl -s -X POST http://127.0.0.1:8000/api/v1/alden/message \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"What was the first thing I said to you in this conversation?\",
    \"session_id\": \"$SESSION_ID\"
  }" | jq -r '.response' > response3.txt

echo "Response 3 received ($(wc -w < response3.txt) words)"

echo "Integration test complete. Check response files for content quality."
```

**Success Criteria:**
- ✅ All 3 messages receive substantial AI responses (>50 words each)
- ✅ Response 2 builds on context from Response 1
- ✅ Response 3 accurately references the first message content
- ✅ Conversation maintains coherence throughout
- ✅ No errors, timeouts, or system failures

## Error Handling Verification

### Test Scenario 9: Invalid Request Handling

**Objective:** Verify system handles errors gracefully.

```bash
# Test empty message
curl -s -X POST http://127.0.0.1:8000/api/v1/alden/message \
  -H "Content-Type: application/json" \
  -d '{"message": ""}' | jq

# Test malformed JSON
curl -s -X POST http://127.0.0.1:8000/api/v1/alden/message \
  -H "Content-Type: application/json" \
  -d '{"invalid": json}' | jq

# Test invalid endpoint
curl -s http://127.0.0.1:8888/api/v1/alden/nonexistent | jq
```

**Success Criteria:**
- ✅ Empty message returns validation error (not system crash)
- ✅ Malformed JSON returns 400 Bad Request
- ✅ Invalid endpoint returns 404 Not Found
- ✅ System remains operational after error conditions

## Production Readiness Checklist

After completing all test scenarios, verify:

### System Stability
- [ ] All services started without errors
- [ ] Services remain running throughout testing
- [ ] No memory leaks or resource exhaustion observed
- [ ] System handles errors gracefully without crashes

### Performance Standards
- [ ] Response times consistently under 15 seconds
- [ ] Concurrent requests handled properly
- [ ] Load testing completed without failures
- [ ] Database operations complete quickly (<1s)

### Data Integrity
- [ ] Conversations saved and retrieved correctly
- [ ] Memory persistence working across sessions
- [ ] Backup system creates valid backups
- [ ] No data corruption or loss observed

### Integration Completeness
- [ ] Alden API communicates with Local LLM API
- [ ] Database stores conversation data
- [ ] Vault encryption protects sensitive data
- [ ] Memory management systems operational

### User Experience
- [ ] AI responses are coherent and contextual
- [ ] Conversation flow feels natural
- [ ] System provides helpful error messages
- [ ] Status information is accurate and useful

## Troubleshooting Guide

### Common Issues and Solutions

**Problem:** Health check fails for Local LLM API
```bash
# Solution: Check Ollama service
ollama list
# If no models, pull a model:
ollama pull llama3.1
```

**Problem:** Alden API fails to start with Vault error
```bash
# Solution: Verify vault key exists
ls -la config/vault_key.bin
# If missing, the service should create it automatically on first run
```

**Problem:** Slow response times (>20 seconds)
```bash
# Solution: Check system resources
top
# Check Ollama is not overloaded:
curl -s http://localhost:11434/api/tags
```

**Problem:** Memory/conversation not persisting
```bash
# Solution: Check database and vault
ls -la hearthlink_data/hearthlink.db hearthlink_data/vault_storage
# Check logs for database errors
```

**Problem:** Backup system fails
```bash
# Solution: Check permissions and disk space
df -h
ls -la hearthlink_data/
mkdir -p backups  # Create if missing
```

## Success Declaration

**The system passes human verification if:**

1. ✅ **All 9 test scenarios complete successfully**
2. ✅ **Production readiness checklist items are checked**
3. ✅ **No critical errors or system failures observed**
4. ✅ **AI responses demonstrate real intelligence and memory**
5. ✅ **Performance meets stated benchmarks**

## Next Steps After Verification

Upon successful verification:

1. **Document any issues found** for future improvement
2. **Create user feedback collection plan**
3. **Plan integration with frontend systems**
4. **Consider deployment to production environment**
5. **Begin advanced feature development**

---

**Remember: Success is defined as no simulation, no hallucination, only confirmed functionality.**

*Last Updated: 2025-07-24*  
*Verification Guide Version: 1.0*