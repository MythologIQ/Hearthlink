#!/usr/bin/env node
/**
 * Multi-Agent Memory Sync End-to-End Tests
 * Validates real-time conflict resolution between Alden, Alice, Sentry, Mimic
 */

const axios = require('axios');
const { v4: uuidv4 } = require('uuid');

// Test configuration
const CONFIG = {
    memorySyncUrl: process.env.MEMORY_SYNC_URL || 'http://localhost:8003',
    postgresUrl: process.env.POSTGRES_URL || 'postgresql://hearthlink_test:test_password_123@localhost:5432/hearthlink_test',
    redisUrl: process.env.REDIS_URL || 'redis://localhost:6379/0',
    testTimeout: 30000 // 30 seconds
};

// Agent configurations
const AGENTS = {
    sentry: { id: 'sentry', priority: 1 },
    alden: { id: 'alden', priority: 2 },
    alice: { id: 'alice', priority: 3 },
    mimic: { id: 'mimic', priority: 4 }
};

// Test data generators
const generateMemoryData = (agentId, content, tags = [], importance = 0.5) => ({
    agentId,
    memoryId: `test_memory_${uuidv4()}`,
    operation: 'create',
    content,
    importance,
    priority: tags.includes('security') ? 'critical' : 'normal',
    metadata: {
        sessionId: `test_session_${Date.now()}`,
        agentPriority: AGENTS[agentId].priority,
        tags,
        testRun: true,
        timestamp: new Date().toISOString()
    }
});

// Utility functions
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const syncMemory = async (syncData) => {
    try {
        const response = await axios.post(`${CONFIG.memorySyncUrl}/api/sync-memory`, syncData, {
            timeout: 5000,
            headers: { 'Content-Type': 'application/json' }
        });
        return response.data;
    } catch (error) {
        throw new Error(`Memory sync failed: ${error.message}`);
    }
};

const resolveConflict = async (conflictId, strategy) => {
    try {
        const response = await axios.post(
            `${CONFIG.memorySyncUrl}/api/resolve-conflict/${conflictId}`,
            { strategy, resolution: 'approve' },
            { timeout: 5000 }
        );
        return response.data;
    } catch (error) {
        throw new Error(`Conflict resolution failed: ${error.message}`);
    }
};

const getConflictStatus = async (conflictId) => {
    try {
        const response = await axios.get(`${CONFIG.memorySyncUrl}/api/conflicts/${conflictId}`, {
            timeout: 5000
        });
        return response.data;
    } catch (error) {
        throw new Error(`Get conflict status failed: ${error.message}`);
    }
};

// Test suites
const testAgentPriorityConflict = async () => {
    console.log('\n🧪 Testing Agent Priority Conflict Resolution...');
    
    // Create simultaneous memories from different agents
    const memoryId = `conflict_test_${uuidv4()}`;
    
    const aliceMemory = generateMemoryData('alice', 'User is experiencing anxiety about work deadline', ['mood', 'analysis'], 0.7);
    const sentryMemory = generateMemoryData('sentry', 'SECURITY ALERT: Suspicious login attempt detected from IP 192.168.1.100', ['security', 'threat'], 0.9);
    
    // Force same memory ID to create conflict
    aliceMemory.memoryId = memoryId;
    sentryMemory.memoryId = memoryId;
    
    // Send Alice's memory first
    const aliceResult = await syncMemory(aliceMemory);
    console.log(`✅ Alice memory synced: ${aliceResult.syncId}`);
    
    // Send Sentry's memory immediately after (should create conflict)
    const sentryResult = await syncMemory(sentryMemory);
    console.log(`✅ Sentry memory synced: ${sentryResult.syncId}`);
    
    if (sentryResult.conflictId) {
        console.log(`🔄 Conflict detected: ${sentryResult.conflictId}`);
        
        // Wait for automatic resolution
        await sleep(2000);
        
        const conflictStatus = await getConflictStatus(sentryResult.conflictId);
        
        if (conflictStatus.status === 'resolved' && conflictStatus.resolution.strategy === 'SECURITY_OVERRIDE') {
            console.log('✅ PASS: Security override policy correctly prioritized Sentry');
            return true;
        } else if (conflictStatus.status === 'resolved' && conflictStatus.resolution.strategy === 'AGENT_PRIORITY') {
            console.log('✅ PASS: Agent priority correctly prioritized Sentry over Alice');
            return true;
        } else {
            console.log(`❌ FAIL: Unexpected resolution - Status: ${conflictStatus.status}, Strategy: ${conflictStatus.resolution?.strategy}`);
            return false;
        }
    } else {
        console.log('❌ FAIL: Expected conflict was not detected');
        return false;
    }
};

const testTimestampResolution = async () => {
    console.log('\n🧪 Testing Timestamp-Based Resolution...');
    
    const memoryId = `timestamp_test_${uuidv4()}`;
    
    // Create memories from same-priority agents with clear time difference
    const aldenMemory1 = generateMemoryData('alden', 'User asked about project timeline', ['conversation'], 0.6);
    aldenMemory1.memoryId = memoryId;
    
    const aldenMemory2 = generateMemoryData('alden', 'User provided updated project requirements and new deadline', ['conversation', 'important'], 0.8);
    aldenMemory2.memoryId = memoryId;
    
    // Send first memory
    const result1 = await syncMemory(aldenMemory1);
    console.log(`✅ First Alden memory synced: ${result1.syncId}`);
    
    // Wait to ensure timestamp difference
    await sleep(1500);
    
    // Send second memory (should override due to later timestamp)
    const result2 = await syncMemory(aldenMemory2);
    console.log(`✅ Second Alden memory synced: ${result2.syncId}`);
    
    if (result2.conflictId) {
        console.log(`🔄 Conflict detected: ${result2.conflictId}`);
        
        await sleep(2000);
        
        const conflictStatus = await getConflictStatus(result2.conflictId);
        
        if (conflictStatus.status === 'resolved' && conflictStatus.resolution.strategy === 'TIMESTAMP_WINDOW') {
            console.log('✅ PASS: Timestamp-based resolution worked correctly');
            return true;
        } else {
            console.log(`❌ FAIL: Expected TIMESTAMP_WINDOW strategy, got: ${conflictStatus.resolution?.strategy}`);
            return false;
        }
    } else {
        console.log('❌ FAIL: Expected conflict was not detected');
        return false;
    }
};

const testContentMerging = async () => {
    console.log('\n🧪 Testing Content Merging...');
    
    const memoryId = `merge_test_${uuidv4()}`;
    
    // Create similar content from same agent
    const mimicMemory1 = generateMemoryData('mimic', 'User enjoys creative writing and storytelling', ['persona', 'creative'], 0.6);
    mimicMemory1.memoryId = memoryId;
    
    const mimicMemory2 = generateMemoryData('mimic', 'User enjoys creative writing and narrative development', ['persona', 'creative'], 0.6);
    mimicMemory2.memoryId = memoryId;
    
    // Send both memories
    const result1 = await syncMemory(mimicMemory1);
    console.log(`✅ First Mimic memory synced: ${result1.syncId}`);
    
    await sleep(500);
    
    const result2 = await syncMemory(mimicMemory2);
    console.log(`✅ Second Mimic memory synced: ${result2.syncId}`);
    
    if (result2.conflictId) {
        console.log(`🔄 Conflict detected: ${result2.conflictId}`);
        
        await sleep(2000);
        
        const conflictStatus = await getConflictStatus(result2.conflictId);
        
        if (conflictStatus.status === 'resolved' && conflictStatus.resolution.strategy === 'CONTENT_MERGE') {
            console.log('✅ PASS: Content merging strategy worked correctly');
            console.log(`📝 Merged content preview: ${conflictStatus.resolution.result.content?.substring(0, 100)}...`);
            return true;
        } else {
            console.log(`❌ FAIL: Expected CONTENT_MERGE strategy, got: ${conflictStatus.resolution?.strategy}`);
            return false;
        }
    } else {
        console.log('❌ FAIL: Expected conflict was not detected');
        return false;
    }
};

const testSecurityOverride = async () => {
    console.log('\n🧪 Testing Security Override Policy...');
    
    const memoryId = `security_test_${uuidv4()}`;
    
    // Create high-priority Alice memory
    const aliceMemory = generateMemoryData('alice', 'User reports feeling stressed about work situation', ['mood', 'high'], 0.9);
    aliceMemory.memoryId = memoryId;
    aliceMemory.priority = 'high';
    
    // Create security-related Sentry memory (should override despite lower individual importance)
    const sentryMemory = generateMemoryData('sentry', 'Security incident: Failed authentication attempts exceeded threshold', ['security', 'incident'], 0.7);
    sentryMemory.memoryId = memoryId;
    sentryMemory.priority = 'critical';
    
    // Send Alice memory first
    const aliceResult = await syncMemory(aliceMemory);
    console.log(`✅ Alice high-priority memory synced: ${aliceResult.syncId}`);
    
    // Send Sentry security memory
    const sentryResult = await syncMemory(sentryMemory);
    console.log(`✅ Sentry security memory synced: ${sentryResult.syncId}`);
    
    if (sentryResult.conflictId) {
        console.log(`🔄 Conflict detected: ${sentryResult.conflictId}`);
        
        await sleep(2000);
        
        const conflictStatus = await getConflictStatus(sentryResult.conflictId);
        
        if (conflictStatus.status === 'resolved' && 
            (conflictStatus.resolution.strategy === 'SECURITY_OVERRIDE' || 
             conflictStatus.resolution.strategy === 'AGENT_PRIORITY')) {
            console.log('✅ PASS: Security override policy prioritized Sentry correctly');
            return true;
        } else {
            console.log(`❌ FAIL: Security override failed - Strategy: ${conflictStatus.resolution?.strategy}`);
            return false;
        }
    } else {
        console.log('❌ FAIL: Expected conflict was not detected');
        return false;
    }
};

const testConcurrentMultiAgent = async () => {
    console.log('\n🧪 Testing Concurrent Multi-Agent Operations...');
    
    const baseMemoryId = `concurrent_test_${uuidv4()}`;
    
    // Create simultaneous operations from all agents
    const operations = Object.keys(AGENTS).map(agentId => {
        const memory = generateMemoryData(
            agentId, 
            `Concurrent test from ${agentId} agent with specific context and details`,
            [agentId, 'concurrent_test'],
            0.5 + (AGENTS[agentId].priority * 0.1)
        );
        memory.memoryId = `${baseMemoryId}_${agentId}`;
        return syncMemory(memory);
    });
    
    // Execute all operations simultaneously
    const results = await Promise.allSettled(operations);
    
    let successCount = 0;
    let conflictCount = 0;
    
    for (let i = 0; i < results.length; i++) {
        const result = results[i];
        const agentId = Object.keys(AGENTS)[i];
        
        if (result.status === 'fulfilled') {
            successCount++;
            if (result.value.conflictId) {
                conflictCount++;
                console.log(`🔄 ${agentId} operation created conflict: ${result.value.conflictId}`);
            } else {
                console.log(`✅ ${agentId} operation completed successfully: ${result.value.syncId}`);
            }
        } else {
            console.log(`❌ ${agentId} operation failed: ${result.reason.message}`);
        }
    }
    
    console.log(`📊 Results: ${successCount}/4 successful, ${conflictCount} conflicts detected`);
    
    if (successCount === 4) {
        console.log('✅ PASS: All concurrent operations handled successfully');
        return true;
    } else {
        console.log('❌ FAIL: Some concurrent operations failed');
        return false;
    }
};

// Main test runner
const runTests = async () => {
    console.log('🚀 Starting Multi-Agent Memory Sync E2E Tests');
    console.log(`📍 Memory Sync URL: ${CONFIG.memorySyncUrl}`);
    
    // Health check
    try {
        await axios.get(`${CONFIG.memorySyncUrl}/health`, { timeout: 5000 });
        console.log('✅ Memory sync service is healthy');
    } catch (error) {
        console.error('❌ Memory sync service health check failed:', error.message);
        process.exit(1);
    }
    
    const testSuite = process.argv.find(arg => arg.startsWith('--test='))?.split('=')[1];
    
    let testResults;
    
    if (testSuite) {
        // Run specific test
        switch (testSuite) {
            case 'priority':
                testResults = [await testAgentPriorityConflict()];
                break;
            case 'timestamp':
                testResults = [await testTimestampResolution()];
                break;
            case 'merge':
                testResults = [await testContentMerging()];
                break;
            case 'security':
                testResults = [await testSecurityOverride()];
                break;
            case 'concurrent':
                testResults = [await testConcurrentMultiAgent()];
                break;
            default:
                console.error(`❌ Unknown test suite: ${testSuite}`);
                process.exit(1);
        }
    } else {
        // Run all tests
        testResults = await Promise.all([
            testAgentPriorityConflict(),
            testTimestampResolution(),
            testContentMerging(),
            testSecurityOverride(),
            testConcurrentMultiAgent()
        ]);
    }
    
    const passedTests = testResults.filter(result => result === true).length;
    const totalTests = testResults.length;
    
    console.log('\n📊 Test Results Summary:');
    console.log(`✅ Passed: ${passedTests}/${totalTests}`);
    console.log(`❌ Failed: ${totalTests - passedTests}/${totalTests}`);
    
    if (passedTests === totalTests) {
        console.log('\n🎉 All multi-agent sync tests passed!');
        process.exit(0);
    } else {
        console.log('\n💥 Some tests failed!');
        process.exit(1);
    }
};

// Execute tests
if (require.main === module) {
    runTests().catch(error => {
        console.error('💥 Test execution failed:', error);
        process.exit(1);
    });
}

module.exports = {
    testAgentPriorityConflict,
    testTimestampResolution,
    testContentMerging,
    testSecurityOverride,
    testConcurrentMultiAgent
};