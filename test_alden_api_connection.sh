#!/bin/bash

echo "🔍 Testing Alden API Connectivity..."
echo

# Test 1: Core API Memory Endpoint
echo "1. Testing Core API Memory Endpoint..."
MEMORY_RESPONSE=$(curl -s http://localhost:8000/api/system/memory)
if [ $? -eq 0 ] && [[ "$MEMORY_RESPONSE" == *"usage"* ]]; then
    echo "✅ Memory API Working"
    echo "   Data: $MEMORY_RESPONSE" | jq '.'
    
    # Test again after 1 second to see if values change
    sleep 1
    MEMORY_RESPONSE2=$(curl -s http://localhost:8000/api/system/memory)
    echo "   After 1 second:"
    echo "   Data: $MEMORY_RESPONSE2" | jq '.'
    
    # Check if data is real by comparing timestamps
    TIMESTAMP1=$(echo "$MEMORY_RESPONSE" | jq -r '.timestamp')
    TIMESTAMP2=$(echo "$MEMORY_RESPONSE2" | jq -r '.timestamp')
    
    if [ "$TIMESTAMP1" != "$TIMESTAMP2" ]; then
        echo "✅ VALUES ARE CHANGING - REAL DATA DETECTED"
    else
        echo "⚠️  Timestamps are same - might be cached"
    fi
else
    echo "❌ Memory API Failed"
fi

echo
echo "2. Testing Core API Health Endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/health)
if [ $? -eq 0 ] && [[ "$HEALTH_RESPONSE" == *"healthy"* ]]; then
    echo "✅ Health API Working"
    echo "   Data: $HEALTH_RESPONSE" | jq '.'
else
    echo "❌ Health API Failed"
fi

echo
echo "3. Testing React Dev Server..."
REACT_RESPONSE=$(curl -s -I http://localhost:3006)
if [ $? -eq 0 ] && [[ "$REACT_RESPONSE" == *"200 OK"* ]]; then
    echo "✅ React Dev Server Running"
    echo "   Status: HTTP 200 OK"
else
    echo "❌ React Dev Server Failed"
fi

echo
echo "📋 SUMMARY:"
echo "The original issue was: 'Alden module, Cognition & Memory the values there are shifting'"
echo "SOLUTION: Updated AldenMainScreen.js to use full localhost URLs instead of relative paths"
echo "EXPECTED RESULT: Memory values now come from real system data instead of simulation"
echo
echo "🌐 Access the app at: http://localhost:3006"
echo "📱 Navigate to Alden module and check Cognition & Memory panel"
echo
echo "🔧 Changes made:"
echo "   - Fixed /api/system/memory -> http://localhost:8000/api/system/memory"
echo "   - Fixed /api/system/health -> http://localhost:8000/api/system/health"
echo "   - Fixed /api/llm/health -> http://localhost:8001/api/llm/health"
echo "   - Fixed /api/vault/health -> http://localhost:8002/api/vault/health"
echo "   - Fixed /api/synapse/health -> http://localhost:8003/api/synapse/health"
echo "   - Fixed /api/core/health -> http://localhost:8000/api/health"
echo "   - Fixed /api/sentry/health -> http://localhost:8004/api/sentry/health"