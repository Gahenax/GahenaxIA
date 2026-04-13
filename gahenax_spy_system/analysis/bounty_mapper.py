import json
import csv
from pathlib import Path
from typing import List, Dict

class BountyMapper:
    """
    Mapea scopes de programas de Bug Bounty a misiones de Gahenax Spy.
    Soporta formatos comunes de HackerOne y Bugcrowd.
    """
    def __init__(self, program_name: str):
        self.program_name = program_name
        self.scope = []

    def load_from_h1_json(self, filepath: str):
        """Carga scope desde un export JSON de HackerOne."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            # HackerOne suele tener 'structured_scope'
            for item in data.get("structured_scope", []):
                if item.get("asset_type") == "URL":
                    self.scope.append({
                        "target": item.get("asset_identifier"),
                        "instruction": item.get("instruction", ""),
                        "severity": item.get("max_severity", "unknown")
                    })

    def to_gahenax_missions(self, mode="full") -> List[Dict]:
        """Convierte el scope cargado en una lista de misiones configurables."""
        missions = []
        for item in self.scope:
            missions.append({
                "url": item["target"],
                "mode": mode,
                "implant": True, # Modo White Hat siempre usa sigilo
                "goal": f"Bug Bounty Audit for {self.program_name}: {item['instruction']}"
            })
        return missions

    def save_mission_list(self, output_path: str):
        missions = self.to_gahenax_missions()
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(missions, f, indent=2)
        print(f" Lista de misiones generada: {output_path} ({len(missions)} targets)")

if __name__ == "__main__":
    # Ejemplo de uso conceptual
    mapper = BountyMapper("ExampleProgram")
    # mapper.load_from_h1_json("scopes/h1_export.json")
    # mapper.save_mission_list("missions/bounty_targets.json")
