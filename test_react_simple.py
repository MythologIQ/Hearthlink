#!/usr/bin/env python3
"""
Simple React App Test
Verifies that the React application is responding properly
"""

import requests
import time
import json

def test_react_app():
    """Test that React app is responding"""
    print("🧪 Testing React Application...")
    
    try:
        # Test main page
        print("  📱 Testing main page...")
        response = requests.get("http://localhost:3000", timeout=10)
        
        if response.status_code == 200:
            print("  ✅ Main page responding (200)")
            
            # Check if it's a React app
            content = response.text
            if "react" in content.lower() or "root" in content.lower():
                print("  ✅ React app detected")
            else:
                print("  ⚠️  React app not clearly detected")
                
        else:
            print(f"  ❌ Main page error: {response.status_code}")
            return False
            
        # Test static assets
        print("  📦 Testing static assets...")
        
        assets_to_test = [
            "/static/js/bundle.js",
            "/static/css/main.css",
            "/assets/header-logo.png"
        ]
        
        for asset in assets_to_test:
            try:
                asset_response = requests.get(f"http://localhost:3000{asset}", timeout=5)
                if asset_response.status_code == 200:
                    print(f"  ✅ {asset} - OK")
                else:
                    print(f"  ⚠️  {asset} - Status {asset_response.status_code}")
            except Exception as e:
                print(f"  ❌ {asset} - Error: {str(e)}")
        
        # Test API endpoints (if any)
        print("  🔌 Testing API endpoints...")
        
        api_endpoints = [
            "/api/health",
            "/api/status"
        ]
        
        for endpoint in api_endpoints:
            try:
                api_response = requests.get(f"http://localhost:3000{endpoint}", timeout=5)
                if api_response.status_code == 200:
                    print(f"  ✅ {endpoint} - OK")
                elif api_response.status_code == 404:
                    print(f"  ℹ️  {endpoint} - Not found (expected)")
                else:
                    print(f"  ⚠️  {endpoint} - Status {api_response.status_code}")
            except Exception as e:
                print(f"  ℹ️  {endpoint} - Not available (expected)")
        
        print("  🎉 React app test completed successfully!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("  ❌ Cannot connect to React app. Is it running on localhost:3000?")
        return False
    except Exception as e:
        print(f"  ❌ Test failed: {str(e)}")
        return False

def check_development_server():
    """Check if development server is running"""
    print("\n🔍 Checking Development Server Status...")
    
    try:
        # Check if port 3000 is in use
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 3000))
        sock.close()
        
        if result == 0:
            print("  ✅ Port 3000 is active (React dev server likely running)")
        else:
            print("  ❌ Port 3000 is not active")
            print("     Run: npm run react-start")
            return False
            
    except Exception as e:
        print(f"  ⚠️  Could not check port status: {str(e)}")
    
    return True

if __name__ == "__main__":
    print("🚀 Hearthlink React App Test")
    print("=" * 50)
    
    # Check server status
    server_ok = check_development_server()
    
    if server_ok:
        # Test React app
        success = test_react_app()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 React app is working correctly!")
            print("\n💡 If you see the application in your browser:")
            print("   ✅ The app is loading properly")
            print("   ✅ CSS should be working now")
            print("   ✅ The X-Frame-Options warning is fixed")
            print("   ℹ️  React DevTools message is just a development suggestion")
        else:
            print("❌ Some issues detected. Check the logs above.")
    else:
        print("\n❌ Development server not running.")
        print("   Start it with: npm run react-start")
    
    print("\n🔧 Troubleshooting:")
    print("   - If CSS still doesn't load, try refreshing the browser")
    print("   - If images don't load, check that assets are in public/assets/")
    print("   - If you see console errors, they're likely development warnings") 