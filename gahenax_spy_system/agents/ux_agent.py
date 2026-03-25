"""
ux_agent.py — Agente de Inteligencia UX basado en Scrapling.
Especializado en capturar patrones de interacción, velocidad y evasión de anti-bots.
"""

import time
from typing import Optional

try:
    from scrapling import Fetcher
except ImportError:
    # Fallback if scrapling is not installed in the environment
    Fetcher = None

from gahenax_spy_system.models import UXProfile, SpyMission


class UXAgent:
    """
    UXAgent: Analiza la experiencia de usuario y accesibilidad técnica.
    Utiliza Scrapling para una navegación ultrarrápida y sigilosa.
    """

    def run(self, mission: SpyMission) -> UXProfile:
        if Fetcher is None:
            return UXProfile(
                url=mission.url,
                status="Error: Scrapling not installed (pip install scrapling)"
            )

        start_time = time.time()
        try:
            # Fetcher from scrapling handles Cloudflare/Turnstile by default
            page = Fetcher().get(mission.url)
            load_time = int((time.time() - start_time) * 1000)

            # Extraer navegación (UX Tree)
            nav_items = page.css('nav a::text, .menu a::text, [role="navigation"] a::text').getall()
            # Limpiar y deduplicar
            nav_tree = list(dict.fromkeys([n.strip() for n in nav_items if n.strip()]))[:10]

            # Contar elementos interactivos
            buttons = len(page.css('button, input[type="submit"], .btn, .button').getall())
            inputs = len(page.css('input:not([type="hidden"]), select, textarea').getall())

            return UXProfile(
                url=mission.url,
                status="Success",
                identity=getattr(page, 'user_agent', "Scrapling/Stealth"),
                has_cloudflare="cloudflare" in (page.text.lower() if page.text else ""),
                load_time_ms=load_time,
                navigation_tree=nav_tree,
                interactive_elements=buttons + inputs,
                scrapling_stats={
                    "status_code": page.status,
                    "encoding": page.encoding,
                }
            )

        except Exception as e:
            return UXProfile(
                url=mission.url,
                status=f"Error: {str(e)}"
            )
