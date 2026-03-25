import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def debug_websocket_logs():
    print("🧪 [DIAGNOSTIC] Intentando conectar a Chrome en puerto 9222...")
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print("✅ Conectado. Escuchando frames por 30 segundos...")
        
        start_time = time.time()
        while time.time() - start_time < 30:
            logs = driver.get_log('performance')
            for entry in logs:
                msg = json.loads(entry['message'])['message']
                if msg['method'] == 'Network.webSocketFrameReceived':
                    payload = msg['params']['response']['payloadData']
                    print(f"📡 FRAME DETECTADO: {payload[:100]}")
            time.sleep(1)
        
        print("⌛ Diagnóstico finalizado.")
        driver.quit()
    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")

if __name__ == "__main__":
    debug_websocket_logs()
