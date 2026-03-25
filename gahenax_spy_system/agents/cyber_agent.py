"""
gahenax_spy_system/agents/cyber_agent.py
AGENT 0 — CyberAgent (Stealth Engine)
Sigil: GHOST — infiltración profunda y evasión de WAF.

Este agente envuelve el Cyber-Scraper 2077 (Node.js/Puppeteer)
y actúa como la Wave 0 del protocolo de espionaje.
"""
from __future__ import annotations

import json
import os
import subprocess
from typing import Optional
from pathlib import Path

from gahenax_spy_system.models import CyberProfile


class CyberAgent:
    """
    Wrapper para el motor de captura Puppeteer-Stealth.
    Inyecta el semantic hook y recupera el bridge JSON.
    """

    def __init__(self, node_path: str = "node", script_path: Optional[str] = None):
        self.node_path = node_path
        # Intentar localizar el script en el entorno de Gahenax
        if script_path:
            self.script_path = script_path
        else:
            # Por defecto, buscar en Limpiamax-page
            root = Path(__file__).parent.parent.parent
            self.script_path = str(root / "Limpiamax-page" / "scrape.mjs")

    def run(self, url: str, output_dir: str, implant: bool = False, goal: Optional[str] = None, use_tor: bool = False) -> CyberProfile:
        """
        Ejecuta el scraper de Node.js como subproceso.
        """
        profile = CyberProfile(url=url, output_dir=output_dir, mode="implant" if implant else "standard")
        
        cmd = [
            self.node_path, 
            self.script_path, 
            url, 
            output_dir, 
            "0"  # recursion off by default for agentic analysis
        ]
        
        if implant:
            cmd.append("--implant")
        if goal:
            cmd.append(f"--goal={goal}")
        if use_tor:
            cmd.append("--tor")

        print(f"🚀 [CyberAgent] Iniciando infiltración en {url}...")
        try:
            # Ejecutar y esperar a que termine (el scraper de Node tiene sus propios scrolls/timeouts)
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            # 1. Leer agent_reasoning.json generado por Node
            reasoning_path = Path(output_dir) / "agent_reasoning.json"
            if reasoning_path.exists():
                with open(reasoning_path, "r", encoding="utf-8") as f:
                    reason = json.load(f)
                    profile.status = reason.get("status", "Unknown")
                    profile.identity = reason.get("identity", "Unknown")
                    profile.timestamp = reason.get("timestamp", "")
                    profile.assets_count = reason.get("assetsExtracted", 0)
                    profile.reasoning_file = str(reasoning_path)

            # 2. Leer semantic_bridge.json (el hook inyectado)
            bridge_path = Path(output_dir) / "semantic_bridge.json"
            if bridge_path.exists():
                with open(bridge_path, "r", encoding="utf-8") as f:
                    profile.bridge_data = json.load(f)
                    print(f"🧠 [CyberAgent] Bridge semántico capturado ({len(profile.bridge_data.get('links', []))} links).")
            
        except subprocess.CalledProcessError as e:
            profile.status = "Failed"
            print(f"❌ [CyberAgent] Error en subproceso Node: {e.stderr}")
        except Exception as e:
            profile.status = "Error"
            print(f"❌ [CyberAgent] Error inesperado: {str(e)}")

        return profile
