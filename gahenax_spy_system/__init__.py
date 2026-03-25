"""
Gahenax Spy System — Motor de Inteligencia Web
Motor: Ouroboros-v2-Sigil | Web Espionage Protocol v1.0

Agentes disponibles:
    TechFingerprinter   — detecta el stack tecnológico (GATE)
    StructuralScraper   — extrae DNA visual y layout (MAP)
    CompetitorProfiler  — inteligencia de negocio + SEO (MIRROR)
    PriceWatcher        — monitorea precios y cambios (SWORD)
    SitemapCrawler      — mapea la arquitectura de información (CHAIN)

Uso rápido:
    from gahenax_spy_system import MasterOrchestrator
    report = MasterOrchestrator().run("https://example.com")
    print(report.to_json())
"""

from gahenax_spy_system.orchestrator import MasterOrchestrator
from gahenax_spy_system.models import SpyMission, IntelReport

__all__ = ["MasterOrchestrator", "SpyMission", "IntelReport"]
__version__ = "1.0.0"
