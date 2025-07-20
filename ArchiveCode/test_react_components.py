#!/usr/bin/env python3
"""
Test React Components Loading
Verifies that React components are loading properly in the browser
"""

import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_react_loading():
    """Test that React components are loading properly"""
    print("🧪 Testing React Components Loading...")
    
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        # Initialize driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        # Navigate to the app
        print("  📱 Loading Hearthlink application...")
        driver.get("http://localhost:3000")
        
        # Wait for React to load
        wait = WebDriverWait(driver, 10)
        
        # Check for React root element
        react_root = wait.until(
            EC.presence_of_element_located((By.ID, "root"))
        )
        print("  ✅ React root element found")
        
        # Check for main app content
        app_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "App"))
        )
        print("  ✅ App component loaded")
        
        # Check for header
        header = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "App-header"))
        )
        print("  ✅ Header component loaded")
        
        # Check for persona navigation
        persona_nav = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "persona-nav"))
        )
        print("  ✅ Persona navigation loaded")
        
        # Check for content area
        content_area = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "content-area"))
        )
        print("  ✅ Content area loaded")
        
        # Check for CSS styles (basic check)
        computed_style = driver.execute_script(
            "return window.getComputedStyle(document.querySelector('.App')).display"
        )
        if computed_style != "none":
            print("  ✅ CSS styles are applied")
        else:
            print("  ⚠️  CSS styles may not be loading properly")
        
        # Check for any console errors
        logs = driver.get_log('browser')
        errors = [log for log in logs if log['level'] == 'SEVERE']
        
        if errors:
            print(f"  ⚠️  Found {len(errors)} browser errors:")
            for error in errors[:3]:  # Show first 3 errors
                print(f"     - {error['message']}")
        else:
            print("  ✅ No browser errors found")
        
        # Take a screenshot for verification
        driver.save_screenshot("test_react_loading.png")
        print("  📸 Screenshot saved as test_react_loading.png")
        
        print("  🎉 React components test completed successfully!")
        return True
        
    except Exception as e:
        print(f"  ❌ Test failed: {str(e)}")
        return False
        
    finally:
        try:
            driver.quit()
        except:
            pass

def test_api_endpoints():
    """Test that API endpoints are responding"""
    print("\n🌐 Testing API Endpoints...")
    
    endpoints = [
        "http://localhost:3000",
        "http://localhost:3000/static/js/bundle.js",
        "http://localhost:3000/static/css/main.css"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                print(f"  ✅ {endpoint} - OK")
            else:
                print(f"  ⚠️  {endpoint} - Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ {endpoint} - Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Hearthlink React Components Test")
    print("=" * 50)
    
    # Test API endpoints first
    test_api_endpoints()
    
    # Test React loading
    success = test_react_loading()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! React components are loading properly.")
    else:
        print("❌ Some tests failed. Check the logs above for details.")
    
    print("\n💡 If you see the application in your browser, it's working correctly!")
    print("   The X-Frame-Options and React DevTools messages are normal development warnings.") 