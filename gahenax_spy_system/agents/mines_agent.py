import time
import os
import sys
import threading
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By
except ImportError:
    print("Por favor instala selenium: pip install selenium webdriver-manager")
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HEATMAP_STATE = {
    "total_games": 0,
    "heatmap": [0.0] * 25,
    "mine_counts": [0] * 25
}

last_grid_state = []

class DashboardHandler(SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.end_headers()

    def do_GET(self):
        if self.path == '/heatmap.json':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            if HEATMAP_STATE["total_games"] > 0:
                for i in range(25):
                    HEATMAP_STATE["heatmap"][i] = HEATMAP_STATE["mine_counts"][i] / HEATMAP_STATE["total_games"]
                    
            self.wfile.write(json.dumps(HEATMAP_STATE).encode())
        else:
            super().do_GET()

    def log_message(self, format, *args):
        pass

def start_server():
    os.chdir(os.path.join(os.path.dirname(__file__), "..", "dashboard"))
    server = HTTPServer(('localhost', 8080), DashboardHandler)
    server.serve_forever()


class LocalSpy:
    def __init__(self):
        self.driver = None

    def connect(self):
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            print("[RADAR DOM] Conectado exitosamente al navegador.")
            return True
        except Exception as e:
            print(f"[RADAR ERROR] {e}")
            return False

    def scan_dom(self):
        global last_grid_state
        print("[RADAR DOM] Escaneando la cuadricula de FaucetPay Mines en tiempo real...")
        
        while True:
            try:
                # Comprobar que estamos en Mines
                if 'mines' not in self.driver.current_url.lower():
                    time.sleep(2)
                    continue

                # Las clases pueden variar, pero usualmente los botones de minas estan en un div grid
                # FaucetPay usa clases autogeneradas como style_body...
                # Buscamos el grid de 25 botones
                grid_parent = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'style_body__')]")
                if not grid_parent:
                    time.sleep(1)
                    continue
                
                # El ultimo grid_parent suele ser el del juego
                buttons = grid_parent[-1].find_elements(By.XPATH, "./button")
                
                if len(buttons) == 25:
                    current_state = []
                    mines_found_this_frame = 0
                    
                    for btn in buttons:
                        html = btn.get_attribute('innerHTML').lower()
                        # FaucetPay muestra una bomba como imagen, icono o SVG. 
                        # Una celda no descubierta esta vacia (o tiene un icono bloqueado).
                        # Una gema tiene un estilo, una bomba tiene otro.
                        # Vamos a detectar "bomb", "mine", transparencias o si contiene cierto SVG de bomba.
                        
                        is_mine = False
                        if "bomb" in html or "mine" in html:
                            is_mine = True
                        elif "opacity: 0.45" in html or "opacity:0.45" in html:
                            # A veces las minas reveladas tienen opacidad diferente
                            is_mine = True
                        elif "width=" in html and "height=" in html and ("#434be9" in html or "fill=" in html):
                            # Esto requiere inspeccion visual. Por ahora asumimos que si el innerHTML cambia
                            # y es distinto al estado virgen, revisamos si es bomba.
                            # Para simplificar, FaucetPay a menudo usa una clase especifica para la bomba.
                            btn_class = btn.get_attribute('class').lower()
                            if "loss" in btn_class or "bomb" in btn_class or "mine" in btn_class:
                                is_mine = True
                                
                        current_state.append(is_mine)
                        if is_mine:
                            mines_found_this_frame += 1

                    # Si es la primera vez que detectamos minas en esta ronda
                    if sum(current_state) > 0 and sum(last_grid_state) == 0:
                        HEATMAP_STATE["total_games"] += 1
                        for i in range(25):
                            if current_state[i]:
                                HEATMAP_STATE["mine_counts"][i] += 1
                        print(f" [RADAR] ¡Minas reveladas! Total minas encontradas: {mines_found_this_frame}. Actualizando matriz...")

                    last_grid_state = current_state

            except Exception as e:
                # Evitar spam de errores al recargar
                pass

            time.sleep(1.5)

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    spy = LocalSpy()
    if spy.connect():
        spy.scan_dom()
