"""
spy_agent.py — CLI del sistema Gahenax Spy Agents & Scrapers
Punto de entrada de alto nivel (v1.1 Cyber-Spy Hybrid).

USO:
  python spy_agent.py --url https://example.com
  python spy_agent.py --url https://example.com --mode tech
  python spy_agent.py --url https://example.com --mode cyber --implant
  python spy_agent.py --url https://example.com --implant --goal "Extraer precios"
  python spy_agent.py --url https://example.com --output report.json -v

MODOS:
  full        — Ejecuta agentes estándar + Cyber & UX Infiltration (default)
  cyber       — Solo CyberAgent (Puppeteer-Stealth)
  ux          — Solo UXAgent (Scrapling Engine)
  tech        — Solo TechFingerprinter
  structure   — Solo StructuralScraper
  competitor  — Solo CompetitorProfiler
  price       — Solo PriceWatcher
  map         — Solo SitemapCrawler

FLAGS:
  --implant      Habilita Modo Implante (Stealth profundo para GoDaddy/Hostinger)
  --tor          Usa Tor Proxy (socks5://127.0.0.1:9050) - CyberScraper-2077 style
  --ai-parse     Activa el cerebro de IA para análisis semántico profundo
  --goal "TEXT"  Objetivo semántico para autonomía Puppeteer e IA
  --emit-skill   Genera SKILL.md en .agent/skills/
  --watch N      Re-ejecuta cada N segundos
  --output PATH  Guarda el reporte JSON en PATH
  -v / --verbose Muestra logs detallados
"""

from __future__ import annotations

import argparse
import sys
import time

from gahenax_spy_system import MasterOrchestrator
from gahenax_spy_system.models import SpyMission


VALID_MODES = ("full", "tech", "structure", "competitor", "price", "map", "cyber", "ux")

BANNER = """

    GAHENAX SPY SYSTEM v1.3 (Cyber-Spy-UX-AI Hybrid) — CyberScraper-2077    
  5 Agents: TechFingerprinter · StructuralScraper · CompetitorProfiler      
            PriceWatcher · SitemapCrawler                                    
  Motor: Ouroboros-v2-Sigil | GSD Wave Protocol                             

"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="spy_agent",
        description="Gahenax Web Intelligence Agent — extrae inteligencia técnica y de negocio.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--url", "-u", required=True,
        help="URL objetivo (ej: https://stripe.com)"
    )
    parser.add_argument(
        "--mode", "-m", default="full", choices=VALID_MODES,
        help=(
            "Modo de operación:\n"
            "  full        → 5 agentes (default)\n"
            "  tech        → TechFingerprinter\n"
            "  structure   → StructuralScraper\n"
            "  competitor  → CompetitorProfiler\n"
            "  price       → PriceWatcher\n"
            "  map         → SitemapCrawler\n"
            "  cyber       → CyberAgent (Stealth Engine)"
        )
    )
    parser.add_argument(
        "--emit-skill", action="store_true",
        help="Genera SKILL.md en .agent/skills/ con el patrón descubierto"
    )
    parser.add_argument(
        "--watch", type=int, default=0, metavar="SECONDS",
        help="Re-ejecuta la misión cada N segundos (0 = sin watch)"
    )
    parser.add_argument(
        "--output", "-o", default="",
        help="Guarda el reporte JSON en esta ruta"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Muestra logs detallados"
    )
    parser.add_argument(
        "--depth", type=int, default=2,
        help="Profundidad del SitemapCrawler (default: 2)"
    )
    parser.add_argument(
        "--delay", type=float, default=1.2,
        help="Delay entre requests HTTP en segundos (default: 1.2)"
    )
    parser.add_argument(
        "--timeout", type=int, default=15,
        help="Timeout HTTP por request (default: 15)"
    )
    parser.add_argument(
        "--implant", action="store_true",
        help="Habilitar modo infiltración profunda (Puppeteer Stealth + Inyectores)"
    )
    parser.add_argument(
        "--goal", type=str, default=None,
        help="Misión semántica para el agente de IA"
    )
    parser.add_argument(
        "--tor", action="store_true",
        help="Usa Tor Proxy (CyberScraper-2077 style)"
    )
    parser.add_argument(
        "--ai-parse", action="store_true",
        help="Activa el cerebro de IA para análisis semántico"
    )
    return parser.parse_args()


def run_once(mission: SpyMission, orchestrator: MasterOrchestrator) -> None:
    """Ejecuta una misión y muestra el reporte."""
    report = orchestrator.run_mission(mission)
    print()
    print(report.to_report())
    if report.errors:
        print("\n  Errors:")
        for e in report.errors:
            print(f"   {e}")


def main() -> None:
    print(BANNER)
    args = parse_args()

    # Validate URL
    if not args.url.startswith(("http://", "https://")):
        print(f" URL invalida: '{args.url}'. Debe empezar con http:// o https://")
        sys.exit(1)

    mission = SpyMission(
        url            = args.url,
        mode           = args.mode,
        max_depth      = args.depth,
        timeout        = args.timeout,
        delay          = args.delay,
        emit_skill     = args.emit_skill,
        watch_interval = args.watch,
        output_path    = args.output,
        verbose        = args.verbose,
        goal           = args.goal,
        implant        = args.implant,
        use_tor        = args.tor,
        ai_parse       = args.ai_parse,
    )

    orchestrator = MasterOrchestrator()

    if args.watch > 0:
        print(f"  Watch mode - re-ejecutando cada {args.watch}s (Ctrl+C para detener)")
        execution = 0
        while True:
            execution += 1
            print(f"\n   Ejecucion #{execution} ")
            run_once(mission, orchestrator)
            print(f"\n   Esperando {args.watch}s...")
            try:
                time.sleep(args.watch)
            except KeyboardInterrupt:
                print("\n   Watch mode detenido.")
                break
    else:
        run_once(mission, orchestrator)


if __name__ == "__main__":
    main()
