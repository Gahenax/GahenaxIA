import requests
import json
import time

# Simulating a history harvest from the console
PORT = 5000

def test_batch_harvest():
    print("🧪 Testing Batch History Harvesting...")
    
    # Simulating 5 rounds extracted from history
    multipliers = [1.50, 2.75, 1.00, 15.22, 1.99]
    
    payload = {
        "ts": time.time(),
        "data": json.dumps({
            "multiplier": multipliers,
            "type": "history_harvest",
            "count": len(multipliers)
        })
    }
    
    try:
        res = requests.post(f"http://localhost:{PORT}/telemetry", json=payload, timeout=2)
        if res.status_code == 200:
            print("✅ Batch sent successfully.")
            print(f"Server response: {res.json()}")
        else:
            print(f"❌ Server returned status {res.status_code}")
    except Exception as e:
        print(f"❌ Failed to connect to dashboard: {e}")

if __name__ == "__main__":
    test_batch_harvest()
