import json
from dataclasses import asdict
from pathlib import Path
from .structural_scraper import StructuralScraper
from .tech_fingerprinter import TechFingerprinter
from .meta_informant import MetaInformant

class KnowledgeHarvester:
    def __init__(self, domain, output_dir="harvest_results"):
        self.domain = domain
        self.output_dir = Path(output_dir) / domain
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.scraper = StructuralScraper()
        self.fingerprinter = TechFingerprinter()
        self.informant = MetaInformant()

    def harvest_all(self):
        target_url = f"https://{self.domain}" if not self.domain.startswith("http") else self.domain
        print(f"[*] Iniciando Recolección de Conocimiento (Digital Scavenging) en {target_url}...")
        
        # 1. Tech Stack (ADN Infraestructura)
        tech_data = self.fingerprinter.run(target_url)
        self._save_json("tech_stack.json", asdict(tech_data))
        
        # 2. UI/UX Distillation (Diseño)
        structure = self.scraper.run(target_url)
        self._save_json("structural_dna.json", asdict(structure))
        
        # 3. Meta-Text & Dev Audit (Secretos de Arquitectura)
        meta_data = self.informant.analyze(target_url)
        self._save_json("meta_audit.json", meta_data)
        
        # 3. SEO & Content Strategy
        # Extraemos metadata relevante (headers, og tags, etc)
        seo_data = self._extract_seo_mock()
        self._save_json("seo_strategy.json", seo_data)

        print(f" Recolección completada. Activos guardados en {self.output_dir}")
        return {
            "domain": self.domain,
            "path": str(self.output_dir),
            "tech": tech_data,
            "structure": structure
        }

    def _save_json(self, filename, data):
        with open(self.output_dir / filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _extract_seo_mock(self):
        # Simulación de extracción de metadata estratégica
        return {
            "main_keywords": ["cybersecurity", "automation", "open-source"],
            "og_strategy": "Dynamic preview generation with custom branding",
            "hierarchy": "Semantic HTML5 with high accessibility scores"
        }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python knowledge_harvester.py <dominio>")
        sys.exit(1)
    
    target = sys.argv[1]
    harvester = KnowledgeHarvester(target)
    harvester.harvest_all()
