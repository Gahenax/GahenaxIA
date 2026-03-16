"""
P-ATLAS-NP integration for GahenaxIA.
Adapts the SAT-instance complexity atlas from github.com/Gahenax/P-ATLAS-NP
to the Gahenax text-inference domain.

Mapping:
  SAT instance            → Gahenax query + context
  target_H (hardness)     → ua_spend (recorded in CMR)
  target_D (difficulty)   → h_rigidity (contract compliance cost)
  Spectral features       → Text structure / concept density
  Thermodynamic features  → Query uncertainty / phase state
  Algebraic features      → Logical reducibility / retrieval fraction
  Frontier (kNN)          → UA-variance boundary: where Governor cost is unpredictable
  AdversarialGates        → 7 validation gates on the feature space quality
  AtlasLedger             → Chain-validated JSONL audit trail (port of P-ATLAS-NP Ledger)
"""
from .extractor import GahenaxSignatureExtractor
from .compressor import VectorCompressor
from .atlas import build_frontier_knn
from .classifier import GahenaxAtlasClassifier, ComplexityAssessment
from .gates import GahenaxAdversarialGates
from .ledger import AtlasLedger

__all__ = [
    "GahenaxSignatureExtractor",
    "VectorCompressor",
    "build_frontier_knn",
    "GahenaxAtlasClassifier",
    "ComplexityAssessment",
    "GahenaxAdversarialGates",
    "AtlasLedger",
]

