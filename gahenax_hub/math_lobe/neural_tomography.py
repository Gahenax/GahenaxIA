import numpy as np
import json
from typing import List, Dict, Any
from gahenax_hub.math_lobe.spectral_ops import riemann_init, hodge_metric

class NeuralTomography:
    """
    Motor de diagnóstico Gahenax para auditar otras inteligencias artificiales.
    Analiza la 'Salud Espectral' y la 'Rigidez de Hodge' de los outputs y pesos.
    """
    
    def scan_output_stream(self, outputs: List[float]) -> Dict[str, Any]:
        """Analiza una corriente de outputs (tokens/probabilidades) buscando filtraciones."""
        if not outputs:
            return {"status": "error", "message": "Stream vacío"}
            
        # 1. Detección de Rigidez Espectral (Riemann-GUE)
        data = np.array(outputs)
        diffs = np.diff(np.sort(data))
        avg_gap = np.mean(diffs) if len(diffs) > 0 else 1
        normalized_gaps = diffs / avg_gap if avg_gap > 0 else diffs
        
        # Varianza de gaps (Rigidez)
        spectral_rigidity = np.var(normalized_gaps)
        
        # 2. Veredicto
        status = "HEALTHY"
        if spectral_rigidity > 0.8:
            status = "GHOST_PRONE (High Entropy)"
        elif spectral_rigidity < 0.3:
            status = "SPECTRAL_LOCK (Overfitting/Rigid)"
            
        return {
            "status": status,
            "spectral_rigidity_index": float(spectral_rigidity),
            "riemann_alignment": "HIGH" if spectral_rigidity < 0.5 else "LOW",
            "recommendation": "Recalibrar pesos en Hodge-Space" if status == "GHOST_PRONE" else "OK"
        }

    def scan_weight_matrix(self, weights: np.ndarray) -> Dict[str, Any]:
        """Realiza una 'autopsia' de una matriz de pesos de una capa externa."""
        # Perturbar para medir rigidez de Hodge
        epsilon = 0.01
        ghost_noise = np.random.randn(*weights.shape) * epsilon
        perturbed_weights = weights + ghost_noise
        
        # Medir rigidez horizontal (Topología)
        rigidity = hodge_metric.calculate_rigidity(weights, perturbed_weights)
        
        is_ghost = rigidity < 0.95
        
        return {
            "hodge_rigidity": float(rigidity),
            "verdict": "STRUCTURAL_MASS" if not is_ghost else "GHOST_LAYER",
            "ghost_density": float(1.0 - rigidity) if is_ghost else 0.0,
            "stability": "HIGH" if rigidity > 0.99 else "MODERATE" if rigidity > 0.95 else "CRITICAL"
        }

# Singleton para el Diagnostic Hub
tomography_scanner = NeuralTomography()

if __name__ == "__main__":
    print("🧬 GAHENAX NEURAL TOMOGRAPHY v1.0")
    # Simulación de escaneo de un modelo 'Ghostly' (con ruido)
    ghost_weights = np.random.randn(64, 64) * 0.5
    report = tomography_scanner.scan_weight_matrix(ghost_weights)
    print(f"Reporte de Autopsia: {json.dumps(report, indent=2)}")
