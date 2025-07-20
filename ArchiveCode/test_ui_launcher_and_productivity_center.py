#!/usr/bin/env python3
"""
Selenium UI Test Suite for Hearthlink Main Menu, Alden, Core, Vault, Synapse
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_main_radial_menu():
    print("\n🧪 Testing Main Radial Menu UI...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)
    try:
        driver.get("http://localhost:3000")
        wait = WebDriverWait(driver, 10)
        # Check for main radial menu and 7 module icons
        menu = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "main-radial-menu")))
        print("  ✅ Main radial menu loaded")
        icons = driver.find_elements(By.CLASS_NAME, "module-icon")
        assert len(icons) == 7, f"Expected 7 module icons, found {len(icons)}"
        print("  ✅ 7 module icons found on main menu")
        # Check for sci-fi theme (dark bg, branding)
        branding = driver.find_element(By.CLASS_NAME, "mythologiq-brand")
        assert branding.is_displayed(), "MythologIQ branding not visible"
        print("  ✅ MythologIQ branding visible")
        return driver, icons
    except Exception as e:
        print(f"  ❌ Main radial menu test failed: {e}")
        driver.quit()
        raise

def test_module_navigation(driver, icons):
    print("\n🧪 Testing Module Navigation...")
    module_map = {icon.get_attribute("data-module"): icon for icon in icons}
    for module in ["Alden", "Core/Nexus", "Vault", "Synapse"]:
        assert module in module_map, f"{module} icon missing"
        ActionChains(driver).move_to_element(module_map[module]).click().perform()
        time.sleep(1)
        if module == "Alden":
            # Alden's radial menu
            alden_menu = driver.find_element(By.CLASS_NAME, "alden-radial-menu")
            assert alden_menu.is_displayed(), "Alden radial menu not visible"
            print("  ✅ Alden radial menu loads")
            # Productivity Center access
            prod_center = driver.find_element(By.CLASS_NAME, "productivity-center-icon")
            prod_center.click()
            time.sleep(1)
            header = driver.find_element(By.CLASS_NAME, "productivity-center-header")
            assert header.is_displayed(), "Productivity Center did not load"
            print("  ✅ Productivity Center loads from Alden menu")
            # Return to main menu
            home_btn = driver.find_element(By.CLASS_NAME, "launcher-home-btn")
            home_btn.click()
            time.sleep(1)
        elif module == "Core/Nexus":
            core_panel = driver.find_element(By.CLASS_NAME, "core-main-panel")
            assert core_panel.is_displayed(), "Core/Nexus main panel not visible"
            print("  ✅ Core/Nexus main panel loads")
            # Test at least one feature/component
            feature = driver.find_element(By.CLASS_NAME, "core-feature")
            assert feature.is_displayed(), "Core feature not visible"
            print("  ✅ Core feature visible")
            home_btn = driver.find_element(By.CLASS_NAME, "launcher-home-btn")
            home_btn.click()
            time.sleep(1)
        elif module == "Vault":
            vault_panel = driver.find_element(By.CLASS_NAME, "vault-main-panel")
            assert vault_panel.is_displayed(), "Vault main panel not visible"
            print("  ✅ Vault main panel loads")
            # Test at least one feature/component
            memory = driver.find_element(By.CLASS_NAME, "vault-memory")
            assert memory.is_displayed(), "Vault memory not visible"
            print("  ✅ Vault memory visible")
            home_btn = driver.find_element(By.CLASS_NAME, "launcher-home-btn")
            home_btn.click()
            time.sleep(1)
        elif module == "Synapse":
            synapse_panel = driver.find_element(By.CLASS_NAME, "synapse-main-panel")
            assert synapse_panel.is_displayed(), "Synapse main panel not visible"
            print("  ✅ Synapse main panel loads")
            # Test at least one feature/component
            plugin_mgr = driver.find_element(By.CLASS_NAME, "synapse-plugin-manager")
            assert plugin_mgr.is_displayed(), "Synapse plugin manager not visible"
            print("  ✅ Synapse plugin manager visible")
            home_btn = driver.find_element(By.CLASS_NAME, "launcher-home-btn")
            home_btn.click()
            time.sleep(1)

def test_theme_and_navigation(driver):
    print("\n🧪 Testing Theme and Navigation Consistency...")
    body = driver.find_element(By.TAG_NAME, "body")
    bg_color = body.value_of_css_property("background-color")
    assert "rgb(20, 20, 30)" in bg_color or "#" in bg_color, "Dark mode not applied"
    print("  ✅ Dark mode theme detected")
    nav = driver.find_element(By.CLASS_NAME, "main-nav")
    assert nav.is_displayed(), "Navigation bar not visible"
    print("  ✅ Navigation bar visible and styled")

def run_all():
    driver, icons = test_main_radial_menu()
    try:
        test_module_navigation(driver, icons)
        test_theme_and_navigation(driver)
        print("\n🎉 All UI tests passed!")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_all() 