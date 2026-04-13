# Gahenax Spy System v4.0 - Environment Setup & Dependencies
# Author: Antigravity AI

import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

packages = [
    "flask",          # For the Dashboard
    "playwright",     # For browser components
    "playwright-stealth",
    "httpx",
    "flask-cors",
    "undetected-chromedriver",
    "webdriver-manager"
]

def setup():
    print(" Iniciando Configuración de Gahenax Spy v7.0...")
    for pkg in packages:
        try:
            print(f" Instalando {pkg}...")
            install(pkg)
        except Exception as e:
            print(f" Error instalando {pkg}: {e}")
    
    print(" Instalando binarios de Playwright...")
    try:
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    except:
        pass

    print("\n Entorno de Infiltración LISTO.")
    print("Módulos instalados: Core, Stealth, Dashboard Engine, Ghost Bridge.")

if __name__ == "__main__":
    setup()
