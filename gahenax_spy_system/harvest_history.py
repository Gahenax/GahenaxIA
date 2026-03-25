# Gahenax History Harvester - Windows Launcher
import subprocess
import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GAHENAX_LAUNCHER = os.path.join(BASE_DIR, "gahenax_launcher.py")

def start():
    print("="*60)
    print(" GAHENAX HISTORY HARVESTER - MODO RÁPIDO ")
    print("="*60)
    
    # 1. Start components if not running
    print("1. Iniciando Dashboard y Agente de Telemetría...")
    subprocess.Popen([sys.executable, GAHENAX_LAUNCHER], creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(3)
    
    print("\n2. INSTRUCCIONES:")
    print("   a) Abre el juego en el navegador lanzado por Gahenax.")
    print("   b) Abre el PANEL DE HISTORIAL en Aviator.")
    print("   c) Copia el contenido de 'utils/history_harvester.js' y pégalo en la CONSOLA (F12).")
    print("\n💡 Esto cargará 100 rondas instantáneamente en el motor de análisis.")
    print("Repite esto un par de veces para llegar a las 624 muestras críticas.")
    
    input("\nPresiona ENTER cuando hayas terminado para cerrar este asistente...")

if __name__ == "__main__":
    start()
