"""
gahenax_spy_system/agents/structural_scraper.py
AGENT 2 — StructuralScraper
Sigil: MAP — extrae el DNA visual y arquitectura de componentes del sitio.

Extrae:
  • Paleta de colores dominantes (hex → HSL)
  • Tipografías (Google Fonts, sistema, custom)
  • Sistema de layout (grid / flex / table)
  • Árbol de componentes (nav, hero, sections, footer)
  • Tipo de routing (SPA vs MPA)
  • Tipo de página (landing | saas | ecommerce | docs | blog)
  • CTA principal y su copy
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from gahenax_spy_system.models import ColorToken, StructuralProfile
from gahenax_spy_system.utils import StealthHTTPClient


# 
#  Utilidades de color
# 

def _hex_to_hsl(hex_color: str) -> str:
    """Convierte color hex a HSL string. Retorna '' si falla."""
    try:
        h = hex_color.lstrip("#")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        r, g, b = int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255
        mx, mn = max(r, g, b), min(r, g, b)
        l = (mx + mn) / 2
        if mx == mn:
            return f"hsl(0, 0%, {round(l*100)}%)"
        d = mx - mn
        s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
        if mx == r:
            hue = (g - b) / d + (6 if g < b else 0)
        elif mx == g:
            hue = (b - r) / d + 2
        else:
            hue = (r - g) / d + 4
        hue = round(hue * 60)
        return f"hsl({hue}, {round(s*100)}%, {round(l*100)}%)"
    except Exception:
        return ""


# 
#  PAGE TYPE HEURISTICS
# 

_PAGE_TYPE_SIGNALS: list[tuple[str, list[str]]] = [
    ("saas",       ["pricing", "free trial", "get started", "sign up", "dashboard", "api"]),
    ("ecommerce",  ["add to cart", "buy now", "checkout", "product", "shop", "price"]),
    ("blog",       ["published", "author", "tags", "categories", "read more", "article"]),
    ("docs",       ["documentation", "api reference", "getting started", "changelog", "sdk"]),
    ("landing",    ["hero", "cta", "features", "testimonials", "contact"]),
]


class StructuralScraper:
    """
    Agente de extracción de estructura visual.
    Construye el 'DNA' de diseño del sitio objetivo.
    """

    def __init__(self, http: StealthHTTPClient | None = None):
        self._http = http or StealthHTTPClient()

    def run(self, url: str) -> StructuralProfile:
        profile = StructuralProfile(url=url)
        resp = self._http.get(url)
        if resp is None:
            return profile

        soup = BeautifulSoup(resp.text, "lxml")
        text_content = soup.get_text(" ", strip=True).lower()

        profile.title     = (soup.title.string or "").strip()[:200] if soup.title else ""
        profile.page_type = self._detect_page_type(text_content)
        profile.routing_type = self._detect_routing(soup, resp.text)
        profile.layout_system = self._detect_layout(soup, resp.text)
        profile.fonts         = self._extract_fonts(soup, resp.text)
        profile.colors        = self._extract_colors(soup, resp.text)
        profile.component_tree = self._build_component_tree(soup)
        profile.section_count  = len(soup.find_all("section"))
        profile.has_sticky_nav = self._has_sticky_nav(soup, resp.text)
        profile.has_hero       = self._has_hero(soup)
        profile.has_cta, profile.cta_text = self._find_cta(soup)
        profile.design_notes   = self._generate_design_notes(profile, soup, resp.text)

        return profile

    #  Routing detection 

    def _detect_routing(self, soup: BeautifulSoup, raw: str) -> str:
        spa_markers = [
            "__next_data__", "data-reactroot", "data-vue-app",
            "ng-version", "svelte-h", "__nuxt"
        ]
        if any(m in raw for m in spa_markers):
            return "spa"
        # Check if most links use href="#" or JS click handlers
        links = soup.find_all("a", href=True)
        js_links = sum(1 for a in links if a["href"].startswith(("#", "javascript:")))
        if links and js_links / len(links) > 0.5:
            return "spa"
        return "mpa"

    #  Layout detection 

    def _detect_layout(self, soup: BeautifulSoup, raw: str) -> str:
        text = raw.lower()
        grid_score = text.count("display:grid") + text.count("display: grid") + \
                     text.count("grid-template") + text.count("grid-cols-")
        flex_score = text.count("display:flex") + text.count("display: flex") + \
                     text.count("flex-wrap") + text.count("flex-col") + text.count("flex-row")
        if grid_score > flex_score:
            return "grid"
        if flex_score > 0:
            return "flex"
        if soup.find("table"):
            return "table"
        return "unknown"

    #  Font extraction 

    def _extract_fonts(self, soup: BeautifulSoup, raw: str) -> list[str]:
        fonts: set[str] = set()

        # Google Fonts via link tag
        for link in soup.find_all("link", rel="stylesheet"):
            href = link.get("href", "")
            if "fonts.googleapis.com" in href:
                # Extract family names
                matches = re.findall(r"family=([A-Za-z+]+)", href)
                for m in matches:
                    fonts.add(m.replace("+", " "))

        # @import in style tags
        for style in soup.find_all("style"):
            css = style.string or ""
            matches = re.findall(r"font-family:\s*['\"]?([^;,'\"]+)", css)
            for m in matches[:5]:
                clean = m.strip().split(",")[0].strip("'\"")
                if clean and clean.lower() not in ("inherit", "unset", "revert"):
                    fonts.add(clean)

        # CSS-in-JS / Tailwind font hint in raw
        google_names = re.findall(r"fonts\.googleapis\.com/css.*?family=([A-Za-z+]+)", raw)
        for gn in google_names:
            fonts.add(gn.replace("+", " "))

        return sorted(fonts)[:8]

    #  Color extraction 

    def _extract_colors(self, soup: BeautifulSoup, raw: str) -> list[ColorToken]:
        hex_pat = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
        found   = hex_pat.findall(raw[:40_000])

        # Count frequency
        count: dict[str, int] = {}
        for h in found:
            norm = h.lower() if len(h) == 6 else "".join(c*2 for c in h.lower())
            count[norm] = count.get(norm, 0) + 1

        # Exclude near-white and near-black (noise)
        def is_interesting(h: str) -> bool:
            try:
                r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
                lum = (r + g + b) / 3
                return 15 < lum < 240 and not (abs(r-g)<10 and abs(g-b)<10 and abs(r-b)<10)
            except Exception:
                return False

        top = sorted(
            [(cnt, h) for h, cnt in count.items() if is_interesting(h)],
            reverse=True
        )[:6]

        tokens = []
        roles  = ["primary", "secondary", "accent", "background", "text", "neutral"]
        for i, (cnt, h) in enumerate(top):
            tokens.append(ColorToken(
                hex  = f"#{h}",
                hsl  = _hex_to_hsl(h),
                role = roles[i] if i < len(roles) else "other",
            ))
        return tokens

    #  Component tree 

    def _build_component_tree(self, soup: BeautifulSoup) -> list[str]:
        tree = []
        # Navigation
        if soup.find(["nav", "header"]):
            tree.append("nav")
        # Hero
        if soup.find(class_=re.compile(r"hero|banner|jumbotron", re.I)):
            tree.append("hero")
        elif soup.find("h1"):
            tree.append("hero")
        # Features
        if soup.find(class_=re.compile(r"feature|benefit|advantage|service", re.I)):
            tree.append("features")
        # Pricing
        if soup.find(class_=re.compile(r"pric|plan|tier", re.I)):
            tree.append("pricing")
        # Testimonials
        if soup.find(class_=re.compile(r"testimonial|review|quote|social-proof", re.I)):
            tree.append("testimonials")
        # FAQ
        if soup.find(class_=re.compile(r"faq|accordion|question", re.I)):
            tree.append("faq")
        # Footer
        if soup.find("footer"):
            tree.append("footer")
        return tree

    #  CTA detection 

    def _find_cta(self, soup: BeautifulSoup) -> tuple[bool, str]:
        cta_patterns = re.compile(
            r"get started|sign up|start free|try for free|start now|book a demo|"
            r"request demo|contact us|learn more|get access|subscribe|join now",
            re.I
        )
        # Check buttons first, then links
        for tag in ["button", "a"]:
            for el in soup.find_all(tag):
                text = el.get_text(strip=True)
                if cta_patterns.search(text):
                    return True, text[:80]
        return False, ""

    #  Sticky nav 

    def _has_sticky_nav(self, soup: BeautifulSoup, raw: str) -> bool:
        raw_l = raw.lower()
        return (
            "position:sticky" in raw_l or
            "position: sticky" in raw_l or
            "fixed top-0" in raw_l or
            soup.find(attrs={"class": re.compile(r"sticky|fixed.*nav|navbar-fixed", re.I)}) is not None
        )

    #  Hero detection 

    def _has_hero(self, soup: BeautifulSoup) -> bool:
        return bool(
            soup.find(class_=re.compile(r"hero|banner|jumbotron|splash|masthead", re.I)) or
            soup.find("h1")
        )

    #  Page type 

    def _detect_page_type(self, text: str) -> str:
        scores: dict[str, int] = {}
        for page_type, keywords in _PAGE_TYPE_SIGNALS:
            scores[page_type] = sum(1 for kw in keywords if kw in text)
        if not any(scores.values()):
            return "unknown"
        return max(scores, key=scores.get)

    #  Design notes 

    def _generate_design_notes(self, profile: StructuralProfile,
                                soup: BeautifulSoup, raw: str) -> list[str]:
        notes = []
        if profile.has_sticky_nav:
            notes.append("Sticky navigation detected — premium UX pattern")
        if len(profile.colors) >= 4:
            notes.append(f"Rich color palette ({len(profile.colors)} distinct tones)")
        if len(profile.fonts) > 1:
            notes.append(f"Multi-font system: {', '.join(profile.fonts[:3])}")
        if profile.routing_type == "spa":
            notes.append("SPA routing — likely React/Vue/Svelte with client-side navigation")
        if profile.layout_system == "grid":
            notes.append("CSS Grid dominant layout — modern, 2D control")
        if "tailwind" in raw.lower() or "tw-" in raw.lower():
            notes.append("Tailwind CSS utility classes detected")
        return notes
