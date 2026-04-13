import re
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    import ollama
except ImportError:
    ollama = None

from gahenax_spy_system.models import DiscoveryResult, DiscoverySearchReport


class SerpParser:
    """
    Analizador de SERPs para el Gahenax Search Kernel v3.0.
    Implementa el 'Tactical Preview' y 'Self-Healing' con IA Local.
    """

    # Señales de tecnología presentes en snippets de Google
    _TECH_SIGNALS: List[tuple[str, str]] = [
        (r"Shopify", "Shopify (E-commerce)"),
        (r"WooCommerce|wordpress", "WordPress/WooCommerce"),
        (r"Stripe|Paypal", "Payments Detected"),
        (r"React|Next\.js", "Modern JS Framework"),
        (r"Wix|Squarespace", "Site Builder"),
        (r"Prestashop|Magento", "Enterprise E-commerce"),
        (r"Salesforce|Hubspot", "CRM/Marketing Ecosystem"),
    ]

    def is_blocked(self, html_content: Optional[str] = None) -> bool:
        """
        Detecta si la respuesta es un CAPTCHA o bloqueo de tráfico inusual.
        """
        if not html_content:
            return False
            
        block_signals = [
            "Nuestros sistemas han detectado tráfico inusual",
            "recaptcha",
            "g-recaptcha",
            "https://www.google.com/recaptcha",
            "detected unusual traffic",
            "unusual_traffic_explanation",
            "turnstile-widget",
            "solve the challenge below to continue",
            "nuestros sistemas han detectado tráfico inusual",
            "verificando si eres humano",
            "checking if the site connection is secure"
        ]
        
        content_lower = html_content.lower()
        return any(sig.lower() in content_lower for sig in block_signals)

    def parse_bridge(self, bridge_path: str, html_content: Optional[str] = None) -> List[DiscoveryResult]:
        """
        Parsea el JSON generado por el motor Node.js y enriquece con pre-recon.
        Implementa lógica de Autocuración si no hay resultados.
        """
        if html_content and self.is_blocked(html_content):
            print(" [SerpParser] BLOQUEO DETECTADO (CAPTCHA).")
            return []
            
        results = []
        path = Path(bridge_path)
        if not path.exists():
            return results

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                engine = data.get("engine", "google")
                entries = data.get("entries", [])
                
                # --- AUTO-HEALING (SSC v3.0) ---
                if not entries and html_content and not self.is_blocked(html_content):
                    print(f" [SerpParser] ⚠️ ESTRUCTURA DE {engine.upper()} CAMBIADA. Activando Autocuración...")
                    new_selectors = self.repair_selectors_with_ai(html_content, engine)
                    if new_selectors:
                        print(f" [SerpParser] ✨ Selectores actualizados dinámicamente: {new_selectors}")
                        # En una ejecución real, el Parser podría re-parsear el HTML con estos selectores.
                        # Por ahora, marcamos el fallo para que el Orquestador lo sepa.
                
                for entry in entries:
                    res = DiscoveryResult(
                        url=entry.get("url"),
                        title=entry.get("title"),
                        snippet=entry.get("snippet"),
                        rank=entry.get("rank", 0),
                        source=entry.get("source", f"ssc_{engine}")
                    )
                    
                    # Ejecutar Pre-Fingerprinting sobre el snippet y el título
                    text_to_scan = (res.title or "") + " " + (res.snippet or "")
                    res.tactical_preview = self._fingerprint_snippet(text_to_scan)
                    results.append(res)
        except Exception as e:
            print(f" [SerpParser] Error parsing bridge: {str(e)}")

        return results

    def repair_selectors_with_ai(self, html: str, engine: str) -> Optional[Dict[str, str]]:
        """
        Usa Ollama (Mistral/Llama) para encontrar los nuevos selectores CSS.
        """
        if not ollama:
            return None
            
        snippet = html[:5000] # Solo los primeros 5KB para no exceder contexto
        prompt = f"""
        Eres un experto en Web Infiltration. La estructura actual de {engine} ha cambiado.
        Analiza este fragmento de HTML y devuelve ÚNICAMENTE un JSON con los selectores CSS para:
        1. El contenedor del resultado (target_box)
        2. El título (title_link)
        3. El snippet de texto (description)

        HTML:
        {snippet}
        """
        
        try:
            response = ollama.generate(model='mistral', prompt=prompt)
            match = re.search(r'\{.*\}', response['response'], re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except Exception as e:
            print(f" [SerpParser] Error en Autocuración Ollama: {str(e)}")
        return None

    def _fingerprint_snippet(self, text: str) -> List[str]:
        """
        Detecta señales de tecnología sin visitar el sitio.
        """
        detected = []
        for pattern, label in self._TECH_SIGNALS:
            if re.search(pattern, text, re.I):
                detected.append(label)
        return list(set(detected))
