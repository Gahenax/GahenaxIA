import os
import json
from typing import Dict, Any, List
from gahenax_hub.math_lobe.spectral_ops import hodge_metric

class SystemHodgeMapper:
    """
    Analizador de topografía de sistemas.
    Mapea módulos de código a 'Masa Estructural' vs 'Fantasmas' (Deuda Técnica).
    """
    
    def __init__(self, root_path: str):
        self.root_path = root_path
        self.map = {}

    def scan_project(self) -> Dict[str, Any]:
        """Escanea el proyecto buscando nodos inestables."""
        results = []
        # Simulación de escaneo de archivos
        for root, dirs, files in os.walk(self.root_path):
            if ".git" in root or "node_modules" in root:
                continue
                
            for file in files:
                if file.endswith((".py", ".ts", ".tsx", ".js")):
                    path = os.path.join(root, file)
                    # Métrica de rigidez basada en 'Churn' y 'Complexity' (Simplificado para Gahenax)
                    file_size = os.path.getsize(path)
                    # Un archivo muy grande sin types o con muchas líneas se considera 'Ghostly' potencias
                    is_tsx = file.endswith(".tsx")
                    rigidity = 0.99 if is_tsx else 0.85 # TSX es más rígido estructuralmente
                    
                    if file_size > 5000: rigidity -= 0.1 # Archivos de 50KB+ pierden rigidez
                    
                    results.append({
                        "file": os.path.relpath(path, self.root_path),
                        "rigidity": rigidity,
                        "class": "STRUCTURAL" if rigidity > 0.9 else "GHOST"
                    })
        
        summary = {
            "total_files": len(results),
            "structural_mass": len([r for r in results if r["class"] == "STRUCTURAL"]),
            "ghosts_detected": len([r for r in results if r["class"] == "GHOST"]),
            "system_rigidity": float(sum(r["rigidity"] for r in results) / len(results)) if results else 0.0
        }
        
        return {"summary": summary, "topology": results}

# Singleton
hodge_mapper = SystemHodgeMapper(".")
