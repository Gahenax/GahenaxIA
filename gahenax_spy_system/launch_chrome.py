import subprocess
import os
import sys

def launch(url="https://www.wplay.co/"):
    # Chrome Path (Standard Windows) 
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
    ]
    
    chrome_exe = None
    for p in chrome_paths:
        if os.path.exists(p):
            chrome_exe = p
            break
            
    if not chrome_exe:
        print("Error: No se encontró chrome.exe")
        return

    user_data = r"C:\Users\jotam\OneDrive\Desktop\GahenaxAI\gahenax_spy_system\sessions\default"
    
    args = [
        chrome_exe,
        "--remote-debugging-port=9222",
        f"--user-data-dir={user_data}",
        url
    ]
    
    print(f" Lanzando Chrome en: {url}...")
    subprocess.Popen(args)
    print(" Navegador abierto con puerto 9222.")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "https://www.wplay.co/"
    launch(target)
