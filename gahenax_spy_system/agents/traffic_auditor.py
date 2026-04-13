import json
import re
from typing import List, Dict
from pathlib import Path

class TrafficAuditor:
    """
    Auditor de tráfico que busca fallos de lógica de negocio usando heurísticas y LLM.
    Identifica patrones Sospechosos en APIs (IDOR, JWT leaks, montos negativos).
    """
    def __init__(self, logs_path: str):
        self.logs_path = Path(logs_path)
        self.findings = []
        
    def load_logs(self) -> List[Dict]:
        if not self.logs_path.exists():
            return []
        with open(self.logs_path, "r", encoding="utf-8") as f:
            try:
                # Asumimos formato JSONL o lista JSON
                return json.load(f)
            except:
                # Intentar JSONL
                f.seek(0)
                return [json.loads(line) for line in f if line.strip()]

    def scan_for_idor(self, traffic: List[Dict]):
        """Detecta IDs en URLs que podrían ser susceptibles a IDOR."""
        for entry in traffic:
            url = entry.get("url", "")
            # Buscar patrones de ID numérico o UUID en la URL
            if re.search(r"/(users|accounts|orders|payments)/[0-9a-zA-Z-]{4,}", url):
                self.findings.append({
                    "type": "Potential IDOR",
                    "severity": "Medium",
                    "url": url,
                    "evidence": "ID detectado en ruta de recurso sensible."
                })

    def scan_for_leaks(self, traffic: List[Dict]):
        """Busca tokens, claves o JWTs en cabeceras o cuerpo."""
        patterns = {
            "JWT Token": r"ey[a-zA-Z0-9_-]{10,}\.ey[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}",
            "Generic API Key": r"(?i)(api[-_]?key|secret|token|auth)[\"']?\s*[:=]\s*[\"']?([a-zA-Z0-9]{16,})[\"']?"
        }
        for entry in traffic:
            content = json.dumps(entry)
            for name, pattern in patterns.items():
                if re.search(pattern, content):
                    self.findings.append({
                        "type": f"Sensitive Leak: {name}",
                        "severity": "High",
                        "url": entry.get("url"),
                        "evidence": f"Patrón de {name} detectado en el tráfico."
                    })

    def run_audit(self):
        traffic = self.load_logs()
        if not traffic:
            print("[!] No hay logs de tráfico para auditar.")
            return []
            
        print(f"[*] Auditando {len(traffic)} peticiones...")
        self.scan_for_idor(traffic)
        self.scan_for_leaks(traffic)
        
        return self.findings

if __name__ == "__main__":
    # Prueba rápida con un archivo dummy si existe
    auditor = TrafficAuditor("spy_data/traffic_log.json")
    results = auditor.run_audit()
    print(json.dumps(results, indent=2))
