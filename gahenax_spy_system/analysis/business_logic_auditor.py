import json
import time
from typing import List, Dict
from collections import Counter

class BusinessLogicAuditor:
    """
    Especializado en fallos que no son detectados por firmas:
    - Race Conditions (frecuencia/tiempo)
    - RNG Prediction (secuencias)
    - Parameter Pollution / Overflows
    """
    def __init__(self):
        self.findings = []

    def audit_transfers(self, traffic: List[Dict]):
        """Detecta montos negativos o inconsistencias en flujos de pago."""
        for entry in traffic:
            body = entry.get("body", {})
            if isinstance(body, str):
                try: body = json.loads(body)
                except: continue
            
            # Revisar campos como 'amount', 'qty', 'balance'
            for key, value in body.items():
                if any(x in key.lower() for x in ["amount", "qty", "total", "value"]):
                    if isinstance(value, (int, float)) and value < 0:
                        self.findings.append({
                            "type": "Negative Amount Manipulation",
                            "severity": "Critical",
                            "url": entry.get("url"),
                            "evidence": f"Petición enviada con {key}={value}."
                        })

    def audit_race_condition(self, traffic: List[Dict]):
        """Detecta ráfagas de peticiones idénticas en ms (potencial Race Condition)."""
        timestamps = [e.get("timestamp", 0) for e in traffic]
        signatures = [f"{e.get('method')}:{e.get('url')}" for e in traffic]
        
        counts = Counter(signatures)
        for sig, count in counts.items():
            if count > 5: # Umbral de ráfaga
                self.findings.append({
                    "type": "Potential Race Condition Trace",
                    "severity": "Medium",
                    "url": sig,
                    "evidence": f"Se detectaron {count} peticiones idénticas en la sesión."
                })

    def audit_rng_patterns(self, sequence: List[str]):
        """Integración simplificada de dice_rng_checker."""
        # Si la secuencia es puramente W/L o números
        if len(sequence) < 10: return
        
        # Analizar rachas
        streaks = []
        curr = 0
        for x in sequence:
            if x == 'L': curr += 1
            else:
                if curr > 0: streaks.append(curr)
                curr = 0
        
        if max(streaks or [0]) > 10:
            self.findings.append({
                "type": "Abnormal RNG Distribution (P-ATLAS)",
                "severity": "High",
                "evidence": f"Detección de racha 'Black Swan' de {max(streaks)} rojos."
            })

    def run_full_audit(self, traffic, rng_sequence=None):
        self.audit_transfers(traffic)
        self.audit_race_condition(traffic)
        if rng_sequence:
            self.audit_rng_patterns(rng_sequence)
        return self.findings

if __name__ == "__main__":
    auditor = BusinessLogicAuditor()
    # Mock data
    traffic = [
        {"url": "/api/withdraw", "method": "POST", "body": {"amount": -100}, "timestamp": time.time()},
        {"url": "/api/bet", "method": "POST", "body": {"id": 1}, "timestamp": time.time()},
        {"url": "/api/bet", "method": "POST", "body": {"id": 1}, "timestamp": time.time() + 0.01},
        {"url": "/api/bet", "method": "POST", "body": {"id": 1}, "timestamp": time.time() + 0.02},
        {"url": "/api/bet", "method": "POST", "body": {"id": 1}, "timestamp": time.time() + 0.03},
        {"url": "/api/bet", "method": "POST", "body": {"id": 1}, "timestamp": time.time() + 0.04},
        {"url": "/api/bet", "method": "POST", "body": {"id": 1}, "timestamp": time.time() + 0.05},
    ]
    results = auditor.run_full_audit(traffic, ["L"]*12)
    print(json.dumps(results, indent=2))
