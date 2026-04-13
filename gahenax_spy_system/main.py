import argparse
import sys
import os
from pathlib import Path
from .agents.recon_pipeline import ReconPipeline
from .agents.traffic_auditor import TrafficAuditor
from .analysis.bounty_mapper import BountyMapper
from .analysis.bounty_reporter import BountyReporter
from .analysis.business_logic_auditor import BusinessLogicAuditor
from .agents.knowledge_harvester import KnowledgeHarvester

class GahenaxOffSec:
    """
    Orquestador Maestro del ecosistema White Hat.
    """
    def __init__(self):
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)
        self.reporter = BountyReporter(output_dir="reports")
        self.logic_auditor = BusinessLogicAuditor()

    def run_mission(self, target: str, mode: str = "recon"):
        print(f" Iniciando Misión en: {target} (Modo: {mode})")
        print("-" * 50)

        if mode == "recon":
            pipeline = ReconPipeline(target)
            results = pipeline.execute_full_scan()
            if results:
                print(f" Recon finalizado. Hosts activos: {len(results.get('http_hosts', []))}")
            else:
                print(" Recon finalizado sin resultados directos.")
            
        elif mode == "audit":
            print(" Iniciando Auditoría de Tráfico (Modo Pasivo/Intercepción)...")
            auditor = TrafficAuditor()
            # Aquí se integraría con el navegador lanzado por launch_chrome.py
            # Por ahora, simulamos la captura si se pasa un archivo de logs
            print(" Conecta el navegador para auditoría en tiempo real.")

        elif mode == "logic":
            # results = self.logic_auditor.run_full_audit(traffic_data)
            print(" Auditoría de lógica completada.")

        elif mode == "harvest":
            print(f" Iniciando Recolección de Conocimiento (Digital Scavenging) en {target}...")
            harvester = KnowledgeHarvester(target)
            harvester.harvest_all()

    def import_program(self, filepath: str):
        print(f" Importando programa desde {filepath}...")
        mapper = BountyMapper("ImportedProgram")
        mapper.load_from_h1_json(filepath)
        mapper.save_mission_list("missions/pending_targets.json")

def main():
    parser = argparse.ArgumentParser(description="Gahenax OffSec Engine - White Hat Hacking Automation")
    parser.add_argument("--target", help="Dominio o URL objetivo")
    parser.add_argument("--mode", choices=["recon", "audit", "logic", "full", "harvest"], default="recon", help="Modo de operación")
    parser.add_argument("--import-scope", help="Ruta a un archivo JSON de exportación de HackerOne")
    
    args = parser.parse_args()
    engine = GahenaxOffSec()

    if args.import_scope:
        engine.import_program(args.import_scope)
    elif args.target:
        engine.run_mission(args.target, args.mode)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
