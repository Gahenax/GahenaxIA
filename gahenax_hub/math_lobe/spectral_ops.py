import numpy as np
from typing import Optional

class RiemannSpectralInitializer:
    """
    Inicializador de pesos basado en la rigidez espectral de los ceros de Riemann.
    Implementación pura en NumPy para máxima portabilidad.
    """
    
    @staticmethod
    def get_zeta_gaps(n: int) -> np.ndarray:
        # Aproximación de gaps GUE (Wigner Surmise para GUE)
        # P(s) = (32/pi^2) * s^2 * exp(-4s^2/pi)
        s_vals = np.linspace(0.01, 3, 1000)
        prob = (32 / (np.pi**2)) * (s_vals**2) * np.exp(-4 * (s_vals**2) / np.pi)
        prob /= prob.sum()
        return np.random.choice(s_vals, size=n, p=prob)

    def initialize(self, shape: tuple) -> np.ndarray:
        n = np.prod(shape)
        gaps = self.get_zeta_gaps(n)
        # Escalamiento He (Kaiming)
        fan_in = shape[0] if len(shape) > 1 else shape[0]
        std = np.sqrt(2.0 / fan_in)
        spectral_weights = (gaps - np.mean(gaps)) * std
        return spectral_weights.reshape(shape)

class HodgeRigidityMetric:
    """
    Métrica de rigidez basada en la Variación de Estructura de Hodge (VHS).
    Mide la estabilidad de una transformación ante perturbaciones 'Ghost'.
    """
    def __init__(self, epsilon: float = 0.01):
        self.epsilon = epsilon

    def calculate_rigidity(self, base_output: np.ndarray, perturbed_output: np.ndarray) -> float:
        # Similitud de coseno como proxy de rigidez horizontal
        dot_product = np.sum(base_output * perturbed_output, axis=-1)
        norms = np.linalg.norm(base_output, axis=-1) * np.linalg.norm(perturbed_output, axis=-1)
        # Evitar división por cero
        norms[norms == 0] = 1e-9
        cosine_sim = dot_product / norms
        return float(np.mean(cosine_sim))

# Inicializadores globales para Gahenax
riemann_init = RiemannSpectralInitializer()
hodge_metric = HodgeRigidityMetric()
