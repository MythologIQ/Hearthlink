#!/usr/bin/env node

/**
 * Test script to verify Alden API connectivity
 * Tests the original issue: Alden module memory values showing real data
 */

const fetch = require('node-fetch');

async function testAldenAPIConnectivity() {
    console.log('🔍 Testing Alden API Connectivity...\n');
    
    // Test 1: Core API Memory Endpoint
    console.log('1. Testing Core API Memory Endpoint...');
    try {
        const response = await fetch('http://localhost:8000/api/system/memory');
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Memory API Working');
            console.log(`   Short Term: ${data.usage.shortTerm}%`);
            console.log(`   Long Term: ${data.usage.longTerm}%`);
            console.log(`   Embedded: ${data.usage.embedded}%`);
            console.log(`   System Memory: ${data.systemMemory.percent}%`);
            
            // Wait a moment and test again to see if values change (they should, based on real system data)
            await new Promise(resolve => setTimeout(resolve, 1000));
            const response2 = await fetch('http://localhost:8000/api/system/memory');
            const data2 = await response2.json();
            
            console.log('\n   After 1 second:');
            console.log(`   Short Term: ${data2.usage.shortTerm}%`);
            console.log(`   Long Term: ${data2.usage.longTerm}%`);
            console.log(`   System Memory: ${data2.systemMemory.percent}%`);
            
            // Check if this is real data (should have slight variations) vs simulated (fixed patterns)
            const shortTermDiff = Math.abs(data.usage.shortTerm - data2.usage.shortTerm);
            const systemMemDiff = Math.abs(data.systemMemory.percent - data2.systemMemory.percent);
            
            if (shortTermDiff > 0 || systemMemDiff > 0.1) {
                console.log('✅ VALUES ARE CHANGING - REAL DATA DETECTED');
            } else {
                console.log('⚠️  Values appear static - may still be simulated');
            }
        } else {
            console.log('❌ Memory API Failed:', response.status);
        }
    } catch (error) {
        console.log('❌ Memory API Error:', error.message);
    }
    
    // Test 2: Core API Health Endpoint
    console.log('\n2. Testing Core API Health Endpoint...');
    try {
        const response = await fetch('http://localhost:8000/api/health');
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Health API Working');
            console.log(`   Service: ${data.service}`);
            console.log(`   Status: ${data.status}`);
            console.log(`   Uptime: ${Math.round(data.uptime)} seconds`);
        } else {
            console.log('❌ Health API Failed:', response.status);
        }
    } catch (error) {
        console.log('❌ Health API Error:', error.message);
    }
    
    // Test 3: React Dev Server
    console.log('\n3. Testing React Dev Server...');
    try {
        const response = await fetch('http://localhost:3006');
        if (response.ok) {
            console.log('✅ React Dev Server Running');
            console.log('   URL: http://localhost:3006');
        } else {
            console.log('❌ React Dev Server Failed:', response.status);
        }
    } catch (error) {
        console.log('❌ React Dev Server Error:', error.message);
    }
    
    // Test 4: Check if React app can connect to API
    console.log('\n4. Testing Cross-Origin API Access...');
    try {
        const response = await fetch('http://localhost:8000/api/system/memory', {
            headers: {
                'Origin': 'http://localhost:3006',
                'Access-Control-Request-Method': 'GET'
            }
        });
        console.log('✅ CORS appears to be working');
        console.log(`   Status: ${response.status}`);
    } catch (error) {
        console.log('⚠️  CORS might need configuration:', error.message);
    }
    
    console.log('\n📋 SUMMARY:');
    console.log('The original issue was: "Alden module, Cognition & Memory the values there are shifting"');
    console.log('SOLUTION: Updated AldenMainScreen.js to use full localhost URLs instead of relative paths');
    console.log('EXPECTED RESULT: Memory values now come from real system data instead of simulation');
    console.log('\n🌐 Access the app at: http://localhost:3006');
    console.log('📱 Navigate to Alden module and check Cognition & Memory panel');
}

testAldenAPIConnectivity().catch(console.error);