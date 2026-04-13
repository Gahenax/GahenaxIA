# Gahenax VPN Orchestrator v5.0 (OpenVPN Wrapper)
# Author: Antigravity AI
# Usage: python vpn_manager.py --config profile.ovpn

import subprocess
import os
import sys
import time

class VPNManager:
    def __init__(self, config_dir="../vpn_configs"):
        self.config_dir = config_dir
        self.process = None
        self.current_ip = "N/A"

    def get_public_ip(self):
        try:
            import httpx
            res = httpx.get("https://api.ipify.org?format=json")
            return res.json().get("ip", "Unknown")
        except:
            return "Disconnected"

    def connect(self, config_file):
        config_path = os.path.join(self.config_dir, config_file)
        if not os.path.exists(config_path):
            print(f" Configuración no encontrada: {config_path}")
            return False

        print(f" Conectando a VPN usando: {config_file}...")
        
        # En Windows OpenVPN requiere privilegios o el CLI específico
        # Intentamos con el comando 'openvpn' (debe estar en el PATH)
        cmd = ["openvpn", "--config", config_path]
        
        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(5) # Esperar a que Handshake ocurra
            self.current_ip = self.get_public_ip()
            print(f" VPN Conectada. Nueva IP: {self.current_ip}")
            return True
        except Exception as e:
            print(f" Error al iniciar OpenVPN: {e}")
            return False

    def disconnect(self):
        if self.process:
            self.process.terminate()
            self.process = None
            print(" VPN Desconectada.")

    def burn_current_ip(self, reason="Detected/Banned"):
        ip = self.get_public_ip()
        if ip == "Disconnected" or ip == "N/A":
            return False
            
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        record = {"ip": ip, "ts": timestamp, "reason": reason}
        
        log_path = "../utils/burned_ips.jsonl"
        with open(log_path, "a", encoding="utf-8") as f:
            import json
            f.write(json.dumps(record) + "\n")
        
        print(f" IP QUEMADA: {ip} | Motivo: {reason}")
        return True

if __name__ == "__main__":
    # Test simple
    manager = VPNManager()
    if len(sys.argv) > 1:
        manager.connect(sys.argv[1])
    else:
        print(" Uso: python vpn_manager.py <config.ovpn>")
