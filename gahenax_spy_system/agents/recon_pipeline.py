import subprocess
import os
import json
import sys
from pathlib import Path

class ReconPipeline:
    def __init__(self, domain, output_dir="recon_results"):
        self.domain = domain
        self.output_dir = Path(output_dir) / domain
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.subdomains_file = self.output_dir / "subdomains.txt"
        self.live_hosts_file = self.output_dir / "live_hosts.txt"
        self.nuclei_results_file = self.output_dir / "nuclei_results.json"

    def run_subfinder(self):
        print(f"[*] Ejecutando Subfinder para {self.domain}...")
        try:
            subprocess.run([r"C:\Users\jotam\go\bin\subfinder.exe", "-d", self.domain, "-o", str(self.subdomains_file)], check=True)
        except Exception as e:
            print(f"[!] Error en Subfinder: {e}")

    def run_amass(self):
        print(f"[*] Ejecutando Amass (pasivo) para {self.domain}...")
        try:
            subprocess.run([r"C:\Users\jotam\go\bin\amass.exe", "enum", "-passive", "-d", self.domain, "-o", str(self.output_dir / "amass_subs.txt")], check=True)
        except Exception as e:
            print(f"[!] Error en Amass: {e}")

    def filter_live(self):
        print("[*] Filtrando hosts activos con HTTPX...")
        try:
            subprocess.run([r"C:\Users\jotam\go\bin\httpx.exe", "-l", str(self.subdomains_file), "-o", str(self.live_hosts_file)], check=True)
        except Exception as e:
            print(f"[!] Error en HTTPX: {e}")

    def run_nuclei(self):
        print("[*] Lanzando Nuclei sobre los hosts activos...")
        try:
            subprocess.run([r"C:\Users\jotam\go\bin\nuclei.exe", "-l", str(self.live_hosts_file), "-json-export", str(self.nuclei_results_file)], check=True)
        except Exception as e:
            print(f"[!] Error en Nuclei: {e}")

    def execute_full_scan(self):
        self.run_subfinder()
        self.filter_live()
        self.run_nuclei()
        
        # Cargar resultados para el orquestador
        hosts = []
        if self.live_hosts_file.exists():
            with open(self.live_hosts_file, "r") as f:
                hosts = [line.strip() for line in f if line.strip()]
        
        print(f" Recon completo para {self.domain}. Resultados en {self.output_dir}")
        return {
            "http_hosts": hosts,
            "output_dir": str(self.output_dir),
            "nuclei_file": str(self.nuclei_results_file)
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python recon_pipeline.py <dominio>")
        sys.exit(1)
    
    target_domain = sys.argv[1]
    pipeline = ReconPipeline(target_domain)
    pipeline.execute_full_scan()
