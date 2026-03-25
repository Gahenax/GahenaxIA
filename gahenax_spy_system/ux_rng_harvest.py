import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def harvest_ux_rng():
    print("UX HARVEST: Conectando a puerto 9222...")
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print("UX HARVEST: Escuchando transmision de red...")
        
        results = []
        start_time = time.time()
        
        # Escuchar por 60 segundos o hasta capturar 50 eventos
        while time.time() - start_time < 60 and len(results) < 50:
            logs = driver.get_log('performance')
            for entry in logs:
                msg = json.loads(entry['message'])['message']
                if msg['method'] == 'Network.webSocketFrameReceived':
                    payload = msg['params']['response']['payloadData']
                    # Intentar detectar patron de resultado de dados (JSON en base64 o texto)
                    try:
                        # FaucetPay usa a veces codificacion base64 para frames binarios
                        # o texto plano para JSON.
                        if "win" in payload or "loss" in payload or "amount" in payload:
                            results.append(payload)
                            print(f"UX DATA DETECTADA: {payload[:50]}...")
                    except:
                        pass
            time.sleep(0.5)
            
        print(f"UX HARVEST FINALIZADO. Eventos capturados: {len(results)}")
        with open("ux_rng_history.json", "w") as f:
            json.dump(results, f)
            
    except Exception as e:
        print(f"ERROR UX HARVEST: {e}")

if __name__ == "__main__":
    harvest_ux_rng()
