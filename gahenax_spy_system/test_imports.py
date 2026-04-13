import sys
import os

# Test logic for Gahenax Spy System
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "analysis"))
sys.path.append(os.path.join(BASE_DIR, "dashboard"))
sys.path.append(os.path.join(BASE_DIR, "agents"))
sys.path.append(os.path.join(BASE_DIR, "utils"))

results = []

def check(name, module_name):
    try:
        __import__(module_name)
        results.append(f" {name}: OK")
    except ImportError as e:
        results.append(f" {name}: ERROR ({e})")

print(" GAHENAX SYSTEM IMPORT AUDIT")
print("==============================")
check("Config", "config")
check("Provably Fair Logic", "provably_fair_logic")
check("Temporal Tracker", "temporal_spectral_tracker")
check("Selenium UC", "undetected_chromedriver")
check("Requests", "requests")
check("Flask", "flask")

for r in results:
    print(r)

if any("ERROR" in r for r in results):
    print("\n ALERTA: Fallo de integridad de dependencias detectado.")
    sys.exit(1)
else:
    print("\n INTEGRIDAD CONFIRMADA.")
    sys.exit(0)
