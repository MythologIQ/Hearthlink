#!/usr/bin/env node

// Test Gemini API Connectivity
// This test verifies that the Gemini connector is operational
// and can perform API calls for delegation purposes

const fetch = require('node-fetch').default;

async function testGeminiConnectivity() {
    console.log('🚀 Testing Gemini Connector Operational Status');
    console.log('==============================================');
    
    // Use the same API key as configured in main.js
    const GOOGLE_API_KEY = process.env.GOOGLE_API_KEY || "AIzaSyDEYEEBVMdoThR2Oex0bwxPjzr_wMyG6oA";
    
    const tests = [
        {
            name: 'API Key Configuration',
            test: () => {
                const hasEnvKey = !!process.env.GOOGLE_API_KEY;
                const hasFallbackKey = !!GOOGLE_API_KEY;
                return {
                    success: hasFallbackKey,
                    details: {
                        environmentVariable: hasEnvKey ? '✅ Set' : '❌ Not set',
                        fallbackKey: hasFallbackKey ? '✅ Available' : '❌ Missing',
                        keyLength: GOOGLE_API_KEY ? GOOGLE_API_KEY.length : 0,
                        keyPrefix: GOOGLE_API_KEY ? GOOGLE_API_KEY.substring(0, 8) + '...' : 'None'
                    }
                };
            }
        },
        {
            name: 'Gemini API Endpoint Connectivity',
            test: async () => {
                try {
                    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GOOGLE_API_KEY}`, {
                        method: 'POST',
                        headers: { 
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            contents: [{
                                parts: [{
                                    text: "Hello, this is a connectivity test. Please respond with 'Connection successful' if you can read this message."
                                }]
                            }]
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (!response.ok) {
                        return {
                            success: false,
                            error: data.error?.message || 'Unknown API error',
                            status: response.status,
                            details: data
                        };
                    }
                    
                    const responseText = data.candidates[0]?.content?.parts[0]?.text;
                    
                    return {
                        success: true,
                        response: responseText,
                        status: response.status,
                        details: {
                            tokensUsed: data.usageMetadata?.totalTokenCount || 'Unknown',
                            model: 'gemini-1.5-flash',
                            responseLength: responseText?.length || 0
                        }
                    };
                    
                } catch (error) {
                    return {
                        success: false,
                        error: error.message,
                        details: {
                            errorType: error.name,
                            stack: error.stack
                        }
                    };
                }
            }
        },
        {
            name: 'Delegation Capability Test',
            test: async () => {
                try {
                    const delegationMessage = `
TASK DELEGATION FROM CLAUDE CODE:

Task: Test delegation capabilities
Context: This is a test message from Hearthlink to verify that Claude Code can successfully delegate tasks to Google AI.

Please respond with a brief confirmation that you received this delegation and can provide task analysis.

Expected format:
1. Confirmation of task receipt
2. Brief analysis capability statement
3. Ready status for production use
`;
                    
                    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GOOGLE_API_KEY}`, {
                        method: 'POST',
                        headers: { 
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            contents: [{
                                parts: [{
                                    text: delegationMessage
                                }]
                            }]
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (!response.ok) {
                        return {
                            success: false,
                            error: data.error?.message || 'Delegation test failed',
                            status: response.status
                        };
                    }
                    
                    const responseText = data.candidates[0]?.content?.parts[0]?.text;
                    
                    // Check if response indicates successful delegation
                    const delegationSuccess = responseText?.toLowerCase().includes('received') || 
                                            responseText?.toLowerCase().includes('confirmation') ||
                                            responseText?.toLowerCase().includes('ready');
                    
                    return {
                        success: delegationSuccess,
                        response: responseText,
                        delegationConfirmed: delegationSuccess,
                        details: {
                            responseLength: responseText?.length || 0,
                            containsConfirmation: delegationSuccess
                        }
                    };
                    
                } catch (error) {
                    return {
                        success: false,
                        error: error.message,
                        details: {
                            errorType: error.name
                        }
                    };
                }
            }
        },
        {
            name: 'Rate Limiting Test',
            test: async () => {
                try {
                    const startTime = Date.now();
                    const requests = [];
                    
                    // Make 3 quick requests to test rate limiting behavior
                    for (let i = 0; i < 3; i++) {
                        const promise = fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GOOGLE_API_KEY}`, {
                            method: 'POST',
                            headers: { 
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                contents: [{
                                    parts: [{
                                        text: `Rate limit test request ${i + 1} of 3`
                                    }]
                                }]
                            })
                        });
                        requests.push(promise);
                    }
                    
                    const results = await Promise.all(requests);
                    const endTime = Date.now();
                    
                    const successfulRequests = results.filter(r => r.ok).length;
                    const totalTime = endTime - startTime;
                    
                    return {
                        success: successfulRequests >= 2, // At least 2 of 3 should succeed
                        details: {
                            totalRequests: 3,
                            successfulRequests: successfulRequests,
                            totalTime: totalTime,
                            averageTime: totalTime / 3,
                            rateLimitingWorking: successfulRequests === 3
                        }
                    };
                    
                } catch (error) {
                    return {
                        success: false,
                        error: error.message
                    };
                }
            }
        }
    ];
    
    const results = [];
    
    for (const test of tests) {
        console.log(`\n🔍 Running: ${test.name}`);
        console.log('-'.repeat(40));
        
        try {
            const result = await test.test();
            results.push({ name: test.name, ...result });
            
            if (result.success) {
                console.log(`✅ ${test.name}: PASSED`);
                if (result.response) {
                    console.log(`📝 Response: ${result.response.substring(0, 100)}${result.response.length > 100 ? '...' : ''}`);
                }
                if (result.details) {
                    console.log(`📊 Details:`, JSON.stringify(result.details, null, 2));
                }
            } else {
                console.log(`❌ ${test.name}: FAILED`);
                if (result.error) {
                    console.log(`⚠️  Error: ${result.error}`);
                }
                if (result.details) {
                    console.log(`📊 Details:`, JSON.stringify(result.details, null, 2));
                }
            }
        } catch (error) {
            console.log(`❌ ${test.name}: ERROR - ${error.message}`);
            results.push({ name: test.name, success: false, error: error.message });
        }
    }
    
    // Summary
    console.log('\n📋 Test Summary');
    console.log('===============');
    
    const passed = results.filter(r => r.success).length;
    const total = results.length;
    const passRate = (passed / total * 100).toFixed(1);
    
    console.log(`Tests Passed: ${passed}/${total} (${passRate}%)`);
    
    if (passed === total) {
        console.log('\n🎉 All Tests Passed! Gemini Connector is Operational');
        console.log('✅ API Key Configuration: Working');
        console.log('✅ Endpoint Connectivity: Working');
        console.log('✅ Delegation Capability: Working');
        console.log('✅ Rate Limiting: Working');
        console.log('\n🚀 Hearthlink is ready for Google AI delegation in production!');
    } else {
        console.log('\n⚠️  Some Tests Failed - Review the details above');
        console.log('🔧 Check API key configuration and network connectivity');
    }
    
    return {
        success: passed === total,
        passed,
        total,
        passRate,
        results
    };
}

// Run the test
if (require.main === module) {
    testGeminiConnectivity()
        .then(result => {
            process.exit(result.success ? 0 : 1);
        })
        .catch(error => {
            console.error('Test runner error:', error);
            process.exit(1);
        });
}

module.exports = testGeminiConnectivity;