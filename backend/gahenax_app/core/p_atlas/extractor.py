"""
GahenaxSignatureExtractor
-------------------------
Adapts P-ATLAS-NP's SignatureExtractor to the Gahenax text-inference domain.

Domain-agnostic: works on any query regardless of field (science, law, art,
engineering, philosophy, medicine, business, etc.). The extractor measures
LINGUISTIC STRUCTURE, not domain vocabulary.

Instead of SAT clause graphs, we operate on:
  - Raw query text
  - Optional context dict (assumptions, findings, mode)

Three feature families (matching P-ATLAS-NP taxonomy):

  SPECTRAL  → structural topology of the query
    spectral_complexity_proxy   : normalized text length × sentence complexity
    concept_specificity         : unique tokens / total tokens (vocabulary breadth)
    structural_depth_proxy      : avg clause nesting depth (subordinate conjunctions)

  THERMODYNAMIC → phase / uncertainty state
    thermo_uncertainty_proxy    : open question markers density
    thermo_negation_signal      : negations per sentence (phase instability)
    thermo_open_assumption_frac : fraction of assumptions that are OPEN (if context given)

  ALGEBRAIC → logical reducibility
    algebra_reducible_proxy     : retrieval-pattern terms (factual, definition, list queries)
    algebra_assumption_density  : assumption markers per sentence
    algebra_horn_fraction       : fraction of sentences that are single-polarity assertions

  DOMAIN (meta-features for cross-domain calibration)
    domain_technical_density    : density of technical/specialist register markers
    domain_multi_field_signal   : presence of cross-domain linking terms
"""
from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Simple tokenizer helpers (zero-dependency)
# ---------------------------------------------------------------------------

_SENTENCE_SPLIT = re.compile(r'[.!?]+')
_WORD = re.compile(r'\b\w+\b', re.UNICODE)

# Uncertainty / question markers (ES + EN)
_QUESTION_MARKERS = frozenset([
    'qué', 'cómo', 'cuándo', 'cuánto', 'cuál', 'cuáles', 'por qué', 'dónde',
    'quién', 'quiénes',
    'what', 'how', 'when', 'where', 'why', 'who', 'which', 'whose',
    '?',
])

# Negation tokens
_NEGATIONS = frozenset(['no', 'not', 'nunca', 'jamás', 'sin', 'ni', 'ningún',
                         'never', 'neither', 'nor'])

# Assumption markers (conditional/causal)
_ASSUMPTION_MARKERS = frozenset([
    'si', 'dado', 'suponiendo', 'asumiendo', 'considerando', 'en caso',
    'if', 'given', 'assuming', 'provided', 'suppose', 'suppose that',
    'whenever', 'unless',
])

# Subordinate/nesting conjunctions (depth proxy)
_NESTING = frozenset([
    'que', 'porque', 'aunque', 'mientras', 'cuando', 'donde', 'como',
    'that', 'because', 'although', 'while', 'when', 'where', 'since',
    'however', 'therefore', 'thus',
])

# Retrievable / factual patterns (algebraic reducibility)
_RETRIEVABLE = frozenset([
    'qué es', 'qué son', 'define', 'definición', 'concepto', 'significa',
    'what is', 'what are', 'define', 'definition', 'meaning', 'means',
    'list', 'lista', 'ejemplos', 'examples',
])

# Technical / specialist register markers (domain-agnostic complexity signal)
# These appear across fields: science, law, engineering, medicine, philosophy...
_TECHNICAL_MARKERS = frozenset([
    # Formal reasoning / logic
    'demostrar', 'demostración', 'probar', 'prueba', 'teorema', 'lema', 'corolario',
    'prove', 'proof', 'theorem', 'lemma', 'corollary', 'axiom', 'axioma',
    # Quantitative / mathematical
    'calcular', 'derivar', 'integral', 'ecuación', 'función', 'matriz', 'vector',
    'calculate', 'derive', 'equation', 'integral', 'function', 'matrix',
    # Scientific method
    'hipótesis', 'experimento', 'variable', 'correlación', 'causalidad',
    'hypothesis', 'experiment', 'variable', 'correlation', 'causality',
    # Legal / normative
    'normativa', 'contrato', 'litigio', 'jurisprudencia', 'regulación',
    'regulation', 'contract', 'litigation', 'statute', 'jurisdiction',
    # Medical / biological
    'diagnóstico', 'síntoma', 'patología', 'tratamiento', 'protocolo',
    'diagnosis', 'symptom', 'pathology', 'treatment', 'protocol',
    # Engineering / technical
    'especificación', 'arquitectura', 'optimizar', 'implementar', 'algoritmo',
    'specification', 'architecture', 'optimize', 'implement', 'algorithm',
    # Philosophical / epistemic
    'ontología', 'epistemología', 'hermenéutica', 'dialéctica',
    'ontology', 'epistemology', 'hermeneutics', 'dialectics',
])

# Falsifiability markers — queries that naturally invite verification/testing
# Signal that the user expects observable, testable results
_FALSIFIABILITY_MARKERS = frozenset([
    # Verification verbs (ES)
    'verificar', 'comprobar', 'validar', 'medir', 'probar', 'testear', 'evaluar',
    'comparar', 'observar', 'registrar', 'monitorear', 'auditar', 'contrastar',
    'reproducir', 'replicar', 'ejecutar', 'correr', 'corroborar',
    # Verification verbs (EN)
    'verify', 'check', 'validate', 'measure', 'test', 'evaluate', 'assess',
    'compare', 'observe', 'record', 'monitor', 'audit', 'contrast',
    'reproduce', 'replicate', 'execute', 'run', 'confirm',
    # Outcome markers
    'resultado', 'outcome', 'output', 'qué pasa si', 'qué ocurre',
    'what happens', 'what if', 'what would',
    # Criteria markers
    'criterio', 'criterios', 'condición', 'umbral', 'límite',
    'criteria', 'criterion', 'threshold', 'condition', 'metric',
])

# Cross-domain linking terms (multi-field complexity signal)
_MULTI_FIELD = frozenset([
    'relación entre', 'relación con', 'aplicado a', 'en el contexto de',
    'implicaciones de', 'impacto en', 'intersección',
    'relationship between', 'applied to', 'in the context of',
    'implications of', 'impact on', 'intersection', 'interplay',
    'compared to', 'vs', 'versus', 'trade-off', 'tradeoff',
])


def _sentences(text: str) -> List[str]:
    parts = [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]
    return parts or [text]


def _words(text: str) -> List[str]:
    return _WORD.findall(text.lower())


class GahenaxSignatureExtractor:
    """
    Extracts a geometric feature signature from a Gahenax inference query.
    Returns (features_dict, mode_tag).
    """

    def extract_spectral(self, text: str) -> Dict[str, float]:
        words = _words(text)
        sentences = _sentences(text)
        n_words = max(len(words), 1)
        n_sentences = max(len(sentences), 1)

        # complexity proxy: avg words per sentence, normalized by log
        avg_sentence_len = n_words / n_sentences
        spectral_complexity = round(
            math.log1p(avg_sentence_len) / math.log1p(50), 6
        )

        # concept_specificity: type/token ratio (unique vocabulary breadth)
        unique = len(set(words))
        concept_specificity = round(unique / n_words, 6)

        # structural_depth: nesting conjunctions density
        nesting_count = sum(1 for w in words if w in _NESTING)
        structural_depth = round(nesting_count / n_words, 6)

        return {
            "spectral_complexity_proxy": spectral_complexity,
            "concept_specificity": concept_specificity,
            "structural_depth_proxy": structural_depth,
        }

    def extract_thermo(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        words = _words(text)
        sentences = _sentences(text)
        n_words = max(len(words), 1)
        n_sentences = max(len(sentences), 1)

        # uncertainty: question markers density
        q_hits = sum(1 for w in words if w in _QUESTION_MARKERS)
        q_hits += text.count('?')
        thermo_uncertainty = round(min(1.0, q_hits / n_sentences), 6)

        # negation signal: instability / phase flip
        neg_count = sum(1 for w in words if w in _NEGATIONS)
        thermo_negation = round(neg_count / n_words, 6)

        # open assumption fraction (from context if available)
        open_frac = 0.5  # default: unknown phase
        if context:
            assumptions = context.get("assumptions", [])
            if assumptions:
                open_count = sum(
                    1 for a in assumptions
                    if isinstance(a, dict) and a.get("status", "open") == "open"
                )
                open_frac = round(open_count / len(assumptions), 6)

        return {
            "thermo_uncertainty_proxy": thermo_uncertainty,
            "thermo_negation_signal": thermo_negation,
            "thermo_open_assumption_frac": open_frac,
        }

    def extract_algebra(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        words = _words(text)
        sentences = _sentences(text)
        n_words = max(len(words), 1)
        n_sentences = max(len(sentences), 1)
        text_lower = text.lower()

        # retrievable / reducible proxy: direct factual patterns
        retrieval_hits = sum(1 for p in _RETRIEVABLE if p in text_lower)
        algebra_reducible = round(min(1.0, retrieval_hits / max(n_sentences, 1)), 6)

        # assumption density
        assumption_hits = sum(1 for w in words if w in _ASSUMPTION_MARKERS)
        algebra_assumption_density = round(assumption_hits / n_words, 6)

        # horn fraction: sentences with a single clear polarity (no negation, no conjunction)
        horn_count = 0
        for s in sentences:
            s_words = _words(s)
            neg = any(w in _NEGATIONS for w in s_words)
            nested = any(w in _NESTING for w in s_words)
            if not neg and not nested and len(s_words) >= 3:
                horn_count += 1
        algebra_horn_fraction = round(horn_count / n_sentences, 6)

        return {
            "algebra_reducible_proxy": algebra_reducible,
            "algebra_assumption_density": algebra_assumption_density,
            "algebra_horn_fraction": algebra_horn_fraction,
        }

    def extract_domain(self, text: str) -> Dict[str, float]:
        """
        Domain meta-features: detect technical register and cross-field signals.
        These make the atlas domain-agnostic — a legal query and a physics query
        can both score high on technical_density without sharing vocabulary.
        """
        words = _words(text)
        text_lower = text.lower()
        n_words = max(len(words), 1)

        # Technical density: fraction of words that are specialist markers
        tech_hits = sum(1 for w in words if w in _TECHNICAL_MARKERS)
        domain_technical_density = round(min(1.0, tech_hits / n_words), 6)

        # Multi-field signal: cross-domain linking phrases
        multi_hits = sum(1 for p in _MULTI_FIELD if p in text_lower)
        domain_multi_field_signal = round(min(1.0, multi_hits / max(len(words) / 5, 1)), 6)

        # Falsifiability signal: density of verification/test/measure markers
        # Uses both exact match and root-prefix matching to cover conjugated forms
        # (verifico, verifica, comprueba, mide, ejecuta, etc.)
        _FALSI_ROOTS = (
            'verif', 'comprob', 'valid', 'medic', 'midiendo', 'mid',
            'prob', 'test', 'eval', 'compar', 'observ', 'registr',
            'monitor', 'audit', 'contras', 'reprod', 'replica', 'ejecut',
            'measur', 'check', 'confir', 'run', 'launch',
        )
        false_hits = sum(
            1 for w in words
            if w in _FALSIFIABILITY_MARKERS or any(w.startswith(r) for r in _FALSI_ROOTS)
        )
        false_phrase_hits = sum(
            1 for p in _FALSIFIABILITY_MARKERS if len(p.split()) > 1 and p in text_lower
        )
        falsifiability_signal = round(
            min(1.0, (false_hits + false_phrase_hits * 2) / max(n_words / 3, 1)), 6
        )

        return {
            "domain_technical_density": domain_technical_density,
            "domain_multi_field_signal": domain_multi_field_signal,
            "falsifiability_signal": falsifiability_signal,
        }

    def extract_all(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, float], str]:
        """
        Returns (features, mode_tag).
        mode_tag is "GAHENAX_DEMO" (no external deps).
        Works for any domain — features are purely linguistic/structural.
        """
        features: Dict[str, float] = {}
        features.update(self.extract_spectral(text))
        features.update(self.extract_thermo(text, context))
        features.update(self.extract_algebra(text, context))
        features.update(self.extract_domain(text))
        return features, "GAHENAX_DEMO"
