// Test Google API Integration
// Run this with: node test_google_api.js

const fetch = require('node-fetch');

async function testGoogleAPI() {
    const GOOGLE_API_KEY = process.env.GOOGLE_API_KEY || "YOUR_API_KEY_HERE";
    
    if (GOOGLE_API_KEY === "YOUR_API_KEY_HERE") {
        console.log("❌ Please set your Google API key in the environment variable GOOGLE_API_KEY or update main.js");
        return;
    }
    
    try {
        console.log("🔄 Testing Google API connection...");
        
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${GOOGLE_API_KEY}`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                contents: [{
                    parts: [{
                        text: "Hello, this is a test message. Please respond with a brief confirmation."
                    }]
                }]
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            console.log("❌ Google API Error:", data.error?.message || 'Unknown error');
            return;
        }
        
        console.log("✅ Google API connection successful!");
        console.log("📝 Response:", data.candidates[0]?.content?.parts[0]?.text || 'No response');
        
    } catch (error) {
        console.log("❌ Test failed:", error.message);
    }
}

testGoogleAPI();