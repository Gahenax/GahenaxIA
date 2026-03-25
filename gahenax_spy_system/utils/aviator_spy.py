# Gahenax Spy System v1.9 - Aviator Continuous Learning Engine
# Author: Antigravity AI
# Usage: python aviator_spy.py --cdp [--train]

import asyncio
import json
import os
import time
import argparse
from playwright.async_api import async_playwright

LOG_FILE = "aviator_telemetry.jsonl"
ALGO_FILE = "aviator_algo_seeds.jsonl"
TRAIN_FILE = "aviator_training_data.jsonl"
SESSION_DIR = "gahenax_user_session"

# WebSocket Hook v1.9 - Continuous Learning
JS_HOOK = """
(function() {
    const OriginalWebSocket = window.WebSocket;
    window.WebSocket = function(url, protocols) {
        const ws = new OriginalWebSocket(url, protocols);
        console.log("GAHENAX_LOG: [LIVE_CONNECT] " + url);
        
        // State for correlation
        let currentRound = null;
        let lastSeeds = null;

        ws.addEventListener('message', function(event) {
            const data = event.data;
            
            // 1. Capture Round Lifecycle
            if(data.includes('round_start')) {
                currentRound = { start_ts: Date.now(), multiplier: 1.0 };
                console.log("GAHENAX_LOG: [ROUND_START] " + data);
            }
            
            // 2. Capture Real-time Multiplier (Even without bets)
            if(data.includes('multiplier')) {
                console.log("GAHENAX_LOG: [TICK] " + data);
            }

            // 3. Capture Cryptographic Seeds
            if(data.includes('seed') || data.includes('hash')) {
                lastSeeds = data;
                console.log("GAHENAX_LOG: [SEED_DUMP] " + data);
            }

            // 4. Capture Final Result (Outcome)
            if(data.includes('round_finish')) {
                console.log("GAHENAX_LOG: [ROUND_END] " + data);
            }
        });

        const originalSend = ws.send;
        ws.send = function(data) {
            console.log("GAHENAX_LOG: [BET_ACTION] " + data);
            return originalSend.apply(this, arguments);
        };
        
        return ws;
    };
})();
"""

async def run_spy(cdp_mode=False):
    print(f"[*] Iniciando Gahenax Spy v1.9 | [Mente] MODO: Continuous Learning")
    
    async with async_playwright() as p:
        if cdp_mode:
            print("[+] Vinculando a Chrome Nativo...")
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            
            # Buscar la página correcta entre todas las abiertas
            page = None
            for p_candidate in context.pages:
                title = await p_candidate.title()
                url = p_candidate.url
                if "Aviator" in title or "launcher" in url:
                    page = p_candidate
                    print(f"[OK] Encontrado en Tab: {title} ({url})")
                    break
            
            if not page:
                print("[!] No se encontró la pestaña de Aviator. Usando la primera pestaña disponible.")
                page = context.pages[0] if context.pages else await context.new_page()
        else:
            # Lanzamiento con perfil persistente
            browser_context = await p.chromium.launch_persistent_context(
                user_data_dir=SESSION_DIR,
                headless=False,
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = await browser_context.new_page()
            await page.goto("https://www.wplay.co/casino")

        STAY_ALIVE_JS = open(os.path.join(os.path.dirname(__file__), "stay_alive.js"), "r").read()
        
        # Inyectar en el frame principal
        await page.add_init_script(JS_HOOK)
        await page.add_init_script(STAY_ALIVE_JS)
        
        # Inyectar recursivamente en frames existentes
        for frame in page.frames:
            try:
                await frame.evaluate(JS_HOOK)
                await frame.evaluate(STAY_ALIVE_JS)
                print(f"[+] Inyectado Hook + StayAlive en Frame: {frame.name or frame.url[:50]}...")
            except: pass
        
        # Recarga táctica para capturar el inicio del WebSocket (solo si no se detecta tráfico aún)
        print("[!] Activando RECARGA TÁCTICA + PROTECTOR DE SESIÓN...")
        await page.reload()
        
        def handle_console(msg):
            if msg.text.startswith("GAHENAX_LOG:"):
                line = msg.text.replace("GAHENAX_LOG: ", "")
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                
                # Clasificación por importancia para el Aprendizaje
                target_file = TRAIN_FILE if "[TICK]" in line or "[SEED_DUMP]" in line else LOG_FILE
                
                with open(target_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps({"ts": timestamp, "data": line}) + "\n")
                
                if "[SEED_DUMP]" in line:
                    print(f"[SEED] {timestamp} | SEED CAPTURADA (Aprendizaje Activo)")
                elif "[ROUND_START]" in line:
                    print(f"[START] {timestamp} | RONDA INICIADA (Monitoreando Pasivamente)")
                elif "[ROUND_END]" in line:
                    print(f"[END] {timestamp} | RONDA FINALIZADA.")

        page.on("console", handle_console)
        
        print("\n" + "="*50)
        print("[ARM] Gahenax Spy v1.9 (LEARNING ENGINE) ACTIVADO.")
        print(f"Dataset de Entrenamiento: {TRAIN_FILE}")
        print("[INFO] Estamos aprendiendo de CADA vuelo, apuestes o no.")
        print("="*50 + "\n")
        
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cdp", action="store_true", help="Monitorizar instancia activa")
    args = parser.parse_args()

    for f in [LOG_FILE, TRAIN_FILE]:
        if not os.path.exists(f):
            with open(f, "w") as _: pass
            
    try:
        asyncio.run(run_spy(cdp_mode=args.cdp))
    except KeyboardInterrupt:
        print("\n[STOP] Entrenamiento detenido.")
