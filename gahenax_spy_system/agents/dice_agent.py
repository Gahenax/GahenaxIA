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

# Importar lógica de predicción RNG
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dice_rng_checker

class DiceAgent:
    def __init__(self):
        self.driver = None
        self.server_seed = None
        self.client_seed = None
        self.next_nonce = 1

    def connect(self):
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            print(" [DICE AGENT] Conectado al navegador.")
            return True
        except Exception as e:
            print(f" [DICE ERROR] {e}")
            return False

    def capture_seeds(self):
        """
        Intenta capturar los seeds del DOM o de las variables globales de FaucetPay.
        """
        try:
            # Ejemplo para FaucetPay: extraemos del script de la página o del modal de Provably Fair
            # Esto es placeholder, requiere inspección del DOM actual
            seeds = self.driver.execute_script("return {s: window.SERVER_SEED, c: window.CLIENT_SEED, n: window.NONCE};")
            if seeds and seeds['s']:
                self.server_seed = seeds['s']
                self.client_seed = seeds['c']
                self.next_nonce = seeds['n']
                print(f" [PULSE] Seeds Capturados! Next Nonce: {self.next_nonce}")
                return True
        except:
            pass
        return False

    def predict_next(self):
        if self.server_seed and self.client_seed:
            roll = dice_rng_checker.calculate_roll(self.server_seed, self.client_seed, self.next_nonce)
            print(f" [PREDICTION] Nonce {self.next_nonce} -> Roll: {roll:.2f}")
            return roll
        return None

    def monitor(self):
        print(" [DICE AGENT] Monitoreando juego...")
        while True:
            try:
                if 'dice' not in self.driver.current_url.lower():
                    time.sleep(2)
                    continue

                # Inyectar el JS Agent si no está presente
                active = self.driver.execute_script("return window.GahenaxDice !== undefined;")
                if not active:
                    print(" [DICE] Inyectando Pulse Agent JS...")
                    with open(os.path.join(os.path.dirname(__file__), "dice_pulse_agent.js"), "r") as f:
                        self.driver.execute_script(f.read())

                # Si tenemos seeds, predecimos
                if not self.server_seed:
                    self.capture_seeds()
                
                prediction = self.predict_next()
                if prediction:
                    # Pasar predicción al JS
                    self.driver.execute_script(f"window.GahenaxDice.state.nextRollPredict = {prediction};")

            except Exception as e:
                pass
            time.sleep(1)

if __name__ == "__main__":
    agent = DiceAgent()
    if agent.connect():
        agent.monitor()
