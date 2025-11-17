#!/usr/bin/env python3
"""Quick test with proxy configuration"""
import os
import sys
from pathlib import Path

# Add project root to path (go up 2 levels: tests/scrapers/ -> tests/ -> root/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Paths
CHROME_PATH = "/root/.cache/ms-playwright/chromium-1194/chrome-linux/chrome"
CHROMEDRIVER_PATH = "/tmp/chromedriver-linux64/chromedriver"

# Get proxy from environment
proxy_url = os.environ.get('HTTP_PROXY', '')
print(f"Using proxy: {proxy_url[:80]}...")

options = Options()
options.binary_location = CHROME_PATH
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument(f'--proxy-server={proxy_url}')

service = Service(executable_path=CHROMEDRIVER_PATH)

print("Starting Chrome...")
driver = webdriver.Chrome(service=service, options=options)
driver.set_page_load_timeout(30)

print("Fetching TechDocs homepage...")
driver.get("https://techdocs.genetec.com/")

print("Waiting for page load...")
import time
time.sleep(5)

print(f"Page title: {driver.title}")

try:
    page_source = driver.page_source
    print(f"Page source length: {len(page_source)}")

    # Check if content loaded
    if "JavaScript" in page_source and "enabled" in page_source:
        print("⚠️ JavaScript warning found - SPA needs rendering")
    else:
        print("✅ Page loaded successfully!")
        print("First 500 chars of content:")
        print(page_source[:500])
except Exception as e:
    print(f"Could not get page source: {e}")
finally:
    driver.quit()
    print("✅ Test complete!")
