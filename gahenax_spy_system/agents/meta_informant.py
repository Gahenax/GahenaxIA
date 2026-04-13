import re
import json
from bs4 import BeautifulSoup, Comment
from ..utils import StealthHTTPClient

class MetaInformant:
    """
    Agente para extraer meta-texto, comentarios de dev y estructura interna de Webpack.
    """
    def __init__(self, http=None):
        self._http = http or StealthHTTPClient()
        self.meta_patterns = {
            "webpack": r"webpackJsonp|webpackChunk|__webpack_require__|__webpack_public_path__",
            "dev_comments": r"TODO|FIXME|TEMP|DEBUG|TEST",
            "versioning": r"v\d+\.\d+\.\d+|version:\s*['\"]\d+\.\d+\.\d+['\"]"
        }

    def top_frameworks(self, n: int = 5) -> list[str]:
        # Usamos un slice más explícito para el linter
        all_f = [s.name for s in self.signals if s.category == "framework"]
        return all_f[:n]

    def analyze(self, url, html_content=None):
        results = {
            "url": url,
            "comments": [],
            "webpack_manifests": [],
            "meta_tags": {},
            "hidden_fields": []
        }
        
        if html_content:
            raw_text = html_content
        else:
            resp = self._http.get(url)
            if not resp: return results
            raw_text = resp.text
        
        soup = BeautifulSoup(raw_text, "lxml")
        
        # 1. Comentarios de desarrollador (HTML)
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        results["comments"] = [str(c).strip() for c in comments if len(str(c)) > 5]
        
        # 2. Meta tags con contenido atípico
        for meta in soup.find_all("meta"):
            name = meta.get("name") or meta.get("property")
            if name:
                results["meta_tags"][name] = meta.get("content")
        
        # 3. Scripts buscando rastro de Webpack o código inyectado
        for script in soup.find_all("script"):
            content = script.string or ""
            if re.search(self.meta_patterns["webpack"], content):
                results["webpack_manifests"].append({
                    "src": script.get("src", "inline"),
                    "hints": self._extract_webpack_hints(content)
                })
        
        return results

    def _extract_webpack_hints(self, content):
        # Intenta extraer IDs de chunks o rutas de carga
        match = re.search(r"\.p\+\s*['\"]([^'\"]+)['\"]", content)
        p_path = match.group(1) if match else "/"
        
        # Buscar el mapeo de chunks si está disponible
        chunks = re.findall(r"(\d+):\s*['\"]([a-f0-9]{8})['\"]", content)
        return {
            "public_path": p_path,
            "chunks_found": len(chunks),
            "sample_chunks": dict(chunks[:5])
        }

if __name__ == "__main__":
    inf = MetaInformant()
    print(json.dumps(inf.analyze("https://faucetpay.io/advanced-dice?type=script"), indent=2))
