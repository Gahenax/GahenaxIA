"""
gahenax_spy_system/spy.py
CLI Maestro para el Gahenax Spy System & Amalgam Discovery Engine.
"""
import argparse
import sys
import os
from pathlib import Path

# Asegurar que el path incluya el directorio raíz para imports relativos
sys.path.append(str(Path(__file__).parent.parent))

from gahenax_spy_system.orchestrator import MasterOrchestrator
from gahenax_spy_system.models import SpyMission

def main():
    parser = argparse.ArgumentParser(description="Gahenax Spy System - Intelligence & Amalgam Discovery")
    
    # Modo Discovery (Wave -1)
    parser.add_argument("--keyword", help="Palabra clave para iniciar el descubrimiento de competidores (Wave -1)")
    
    # Modo Infiltración Directa (Misión clásica)
    parser.add_argument("--url", help="URL objetivo para infiltración directa")
    
    # Opciones de configuración
    parser.add_argument("--mode", choices=["full", "tech", "structure", "competitor", "price", "map"], 
                        default="full", help="Modo de infiltración")
    parser.add_argument("--implant", action="store_true", help="Habilitar modo implante (Infiltración profunda)")
    parser.add_argument("--use-tor", action="store_true", help="Usar proxies Tor para evasión")
    parser.add_argument("--output", help="Ruta de salida para el reporte JSON")
    parser.add_argument("--emit-skill", action="store_true", help="Generar SKILL.md a partir del patrón detectado")

    args = parser.parse_args()
    orchestrator = MasterOrchestrator()

    if args.keyword:
        # Iniciando Amalgama de descubrimiento
        reports = orchestrator.run_discovery(
            keyword=args.keyword,
            mode=args.mode,
            implant=args.implant,
            use_tor=args.use_tor,
            output_path=args.output,
            emit_skill=args.emit_skill
        )
        print(f"\n [Spy] Ciclo de descubrimiento finalizado. {len(reports)} misiones ejecutadas.")
        
    elif args.url:
        # Misión directa
        report = orchestrator.run(
            url=args.url,
            mode=args.mode,
            implant=args.implant,
            use_tor=args.use_tor,
            output_path=args.output,
            emit_skill=args.emit_skill
        )
        print(f"\n [Spy] Misión finalizada para {args.url}")
        print(report.to_report())
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
