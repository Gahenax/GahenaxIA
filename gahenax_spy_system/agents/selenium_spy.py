# Gahenax Spy Agent v18.5 (Brute Force Sniffer)
import time
import json
import base64
import requests
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Standard Pathing
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
if BASE_DIR not in sys.path: sys.path.insert(0, BASE_DIR)
import config

PORT = config.DASHBOARD_PORT

def capture_loop(driver):
    last_val = ""
    print("Agent v18.5: Brute Force DOM Sniffer Active.")
    
    while True:
        try:
            # 1. Heartbeat
            try: requests.post(f"http://localhost:{PORT}/telemetry", json={"type": "hb"}, timeout=0.1)
            except: pass

            # 2. Tabs
            handles = driver.window_handles
            for h in handles:
                try:
                    driver.switch_to.window(h)
                    title = driver.title
                    
                    if "Aviator" in title or "launcher" in driver.current_url:
                        def scan(d, depth=0):
                            nonlocal last_val
                            
                            # BRUTE FORCE: Get ALL text elements 
                            # and look for anything that looks like a number with x or dot
                            elements = d.find_elements(By.XPATH, "//*[text()]")
                            for el in elements:
                                try:
                                    t = el.text.strip().lower()
                                    if not t or len(t) > 8: continue
                                    
                                    # Logic: must have a dot and be mostly numeric
                                    clean = t.replace("x","").replace(",",".").strip()
                                    if "." in clean and clean.replace(".","").isdigit():
                                        if clean != last_val:
                                            last_val = clean
                                            print(f"SIGNAL DETECTED: {clean}x (Source: '{t}')")
                                            requests.post(f"http://localhost:{PORT}/telemetry", 
                                                          json={"ts": time.time(), "data": json.dumps({"multiplier": clean})}, 
                                                          timeout=0.1)
                                except: continue
                            
                            if depth < 8:
                                frames = d.find_elements(By.TAG_NAME, "iframe")
                                for i in range(len(frames)):
                                    try:
                                        d.switch_to.frame(i)
                                        scan(d, depth + 1)
                                        d.switch_to.parent_frame()
                                    except: continue
                        
                        scan(driver)
                except: continue
                
        except Exception as e: pass
        time.sleep(0.5)

if __name__ == "__main__":
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    try:
        driver = webdriver.Chrome(options=options)
        capture_loop(driver)
    except Exception as e:
        print(f"CRITICAL: Chrome Link Failed -> {e}")
