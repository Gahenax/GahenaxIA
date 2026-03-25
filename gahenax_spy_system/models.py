"""
gahenax_spy_system/models.py
Contratos de datos (Pydantic v2 + dataclasses) para todo el sistema spy.
Sigil: SEAL — interfaces inmutables entre agentes.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional


# ══════════════════════════════════════════════════════════════════════════════
#  MISIÓN DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class SpyMission:
    """Define los parámetros de una misión de espionaje."""
    url:            str
    mode:           str   = "full"   # full | tech | structure | competitor | price | map
    max_depth:      int   = 2        # Profundidad máxima del crawler
    timeout:        int   = 15       # Segundos por request HTTP
    delay:          float = 1.2      # Segundos entre requests (rate limiting)
    emit_skill:     bool  = False    # Si True, genera SKILL.md en .agent/skills/
    watch_interval: int   = 0        # Segundos entre re-ejecuciones (0 = sin watch)
    output_path:    str   = ""       # Ruta donde guardar el JSON de reporte
    verbose:        bool  = False
    goal:           Optional[str] = None     # Misión semántica para el Cyber-Scraper
    implant:        bool  = False            # Habilita el modo Infiltration profundo
    use_tor:        bool  = False            # Enable Tor Proxy (CyberScraper-2077)
    ai_parse:       bool  = False            # Enable AI-powered extraction (CyberScraper-2077)


# ══════════════════════════════════════════════════════════════════════════════
#  PERFILES DE AGENTES
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class TechSignal:
    name:       str
    category:   str    # framework | language | cdn | waf | cms | analytics | payments
    confidence: float  # 0.0 - 1.0
    evidence:   str    # La señal concreta que activó la detección


@dataclass
class TechProfile:
    """Output del TechFingerprinter."""
    url:            str
    server:         str = ""
    powered_by:     str = ""
    cdn:            str = ""
    waf:            str = ""
    cms:            str = ""
    http_version:   str = ""
    has_https:      bool = False
    signals:        list[TechSignal] = field(default_factory=list)
    frameworks:     list[str]        = field(default_factory=list)
    analytics:      list[str]        = field(default_factory=list)
    raw_headers:    dict             = field(default_factory=dict)
    confidence_avg: float = 0.0

    def top_frameworks(self, n: int = 5) -> list[str]:
        top = sorted(self.signals, key=lambda s: s.confidence, reverse=True)
        return [s.name for s in top if s.category == "framework"][:n]


@dataclass
class ColorToken:
    hex:  str
    hsl:  str
    role: str  # primary | secondary | background | text | accent


@dataclass
class StructuralProfile:
    """Output del StructuralScraper."""
    url:            str
    title:          str = ""
    page_type:      str = ""   # landing | blog | product | docs | ecommerce | saas
    routing_type:   str = ""   # spa | mpa | ssr
    layout_system:  str = ""   # grid | flex | table | unknown
    has_sticky_nav: bool = False
    has_hero:       bool = False
    has_cta:        bool = False
    cta_text:       str  = ""
    colors:         list[ColorToken] = field(default_factory=list)
    fonts:          list[str]        = field(default_factory=list)
    section_count:  int  = 0
    component_tree: list[str]        = field(default_factory=list)  # [nav, hero, features, pricing, footer]
    design_notes:   list[str]        = field(default_factory=list)


@dataclass
class SEOSnapshot:
    title:       str = ""
    description: str = ""
    h1:          str = ""
    h_structure: dict = field(default_factory=dict)  # {h1: 1, h2: 3, h3: 5}
    canonical:   str = ""
    og_image:    str = ""
    schema_types: list[str] = field(default_factory=list)  # Schema.org types found


@dataclass
class CompetitorProfile:
    """Output del CompetitorProfiler."""
    url:           str
    seo:           SEOSnapshot      = field(default_factory=SEOSnapshot)
    social_links:  list[str]        = field(default_factory=list)
    third_party_tools: list[str]    = field(default_factory=list)  # HotJar, Intercom, etc.
    trust_signals: list[str]        = field(default_factory=list)  # Badges, certs, reviews
    contact_methods: list[str]      = field(default_factory=list)
    has_blog:      bool = False
    has_pricing:   bool = False
    has_free_trial: bool = False
    language:      str  = ""
    word_count:    int  = 0


@dataclass
class PricePoint:
    label:    str
    amount:   str   # Raw text — puede ser "$29/mes", "Gratis", "Consultar"
    currency: str   = ""
    period:   str   = ""   # month | year | one-time | unknown
    features: list[str] = field(default_factory=list)


@dataclass
class PriceReport:
    """Output del PriceWatcher."""
    url:          str
    plans:        list[PricePoint] = field(default_factory=list)
    has_free_tier: bool = False
    has_trial:    bool  = False
    pricing_model: str  = ""  # saas-tiered | flat | usage | contact | unknown
    urgency_signals: list[str] = field(default_factory=list)  # "Oferta termina en..."
    diff_from_last:  list[str] = field(default_factory=list)  # Cambios vs ejecución anterior
    snapshot_ts:  str = ""


@dataclass
class SitePage:
    url:       str
    page_type: str   # landing | blog | product | docs | auth | about | legal | other
    depth:     int
    title:     str = ""
    lang:      str = ""


@dataclass
class SiteMap:
    """Output del SitemapCrawler."""
    root_url:   str
    pages:      list[SitePage] = field(default_factory=list)
    total_urls: int = 0
    max_depth_reached: int = 0
    has_sitemap_xml: bool = False
    has_robots_txt:  bool = False
    sitemap_url:     str  = ""
    disallowed:      list[str] = field(default_factory=list)
    languages:       list[str] = field(default_factory=list)


@dataclass
class CyberProfile:
    """Output del CyberAgent (Puppeteer-based stealth scraper)."""
    url:            str
    status:         str = "Success"
    mode:           str = "standard"  # standard | implant
    identity:       str = ""          # User-Agent used
    timestamp:      str = ""
    assets_count:   int = 0
    bridge_data:    dict = field(default_factory=dict)  # Data from semantic_bridge.json
    reasoning_file: str = ""
    output_dir:     str = ""


@dataclass
class UXProfile:
    """Output del UXAgent (Scrapling-based adaptive scraper)."""
    url:            str
    status:         str = "Success"
    identity:       str = ""          # TLS Fingerprint / UA used
    has_cloudflare: bool = False
    load_time_ms:   int = 0
    navigation_tree: list[str] = field(default_factory=list)
    interactive_elements: int = 0
    scrapling_stats: dict = field(default_factory=dict)


@dataclass
class LLMAnalysis:
    """Output del LLMAgent (CyberScraper-2077 Brain)."""
    summary:        str = ""
    extracted_data: dict = field(default_factory=dict)
    confidence:     float = 0.0
    raw_response:   str = ""


# ══════════════════════════════════════════════════════════════════════════════
#  REPORTE FINAL
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class IntelReport:
    """Reporte de inteligencia completo — output del MasterOrchestrator."""
    mission_id:   str
    timestamp:    str
    target_url:   str
    mode:         str

    tech:         Optional[TechProfile]       = None
    structure:    Optional[StructuralProfile] = None
    competitor:   Optional[CompetitorProfile] = None
    pricing:      Optional[PriceReport]       = None
    sitemap:      Optional[SiteMap]           = None
    cyber:        Optional[CyberProfile]      = None
    ux:           Optional[UXProfile]         = None
    ai_synthesis: Optional[LLMAnalysis]       = None

    errors:       list[str] = field(default_factory=list)
    duration_ms:  int = 0

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(asdict(self), indent=indent, ensure_ascii=False)

    def to_report(self) -> str:
        """Genera un reporte Markdown ejecutivo."""
        lines = [
            f"# 🕵️ Intel Report — {self.target_url}",
            f"**Mission ID:** `{self.mission_id}`  |  "
            f"**Timestamp:** {self.timestamp}  |  "
            f"**Duration:** {self.duration_ms}ms",
            "",
        ]

        if (tech := self.tech) is not None:
            lines += [
                "## 🔍 Tech Stack Detected",
                f"  - **Server:** `{tech.server or 'N/A'}`",
                f"  - **CDN:** `{tech.cdn or 'N/A'}`",
                f"  - **WAF:** `{tech.waf or 'N/A'}`",
                f"  - **HTTPS:** {'✅' if tech.has_https else '❌'}",
                f"  - **Frameworks:** {', '.join(f'`{f}`' for f in tech.top_frameworks()) or 'N/A'}",
                f"  - **Analytics:** {', '.join(f'`{a}`' for a in tech.analytics) or 'N/A'}",
                "",
            ]

        if (struct := self.structure) is not None:
            lines += [
                "## 🎨 Structural DNA",
                f"  - **Page Type:** `{struct.page_type}`  |  **Routing:** `{struct.routing_type}`",
                f"  - **Layout:** `{struct.layout_system}`  |  **Sections:** {struct.section_count}",
                f"  - **Fonts:** {', '.join(f'`{f}`' for f in struct.fonts) or 'N/A'}",
                f"  - **CTA:** `{struct.cta_text or 'N/A'}`",
            ]
            if struct.colors:
                lines.append(f"  - **Colors:** {' '.join(c.hex for c in struct.colors[:5])}")
            if struct.component_tree:
                lines.append(f"  - **Components:** {' → '.join(struct.component_tree)}")
            lines.append("")

        if (comp := self.competitor) is not None:
            lines += [
                "## 📊 Competitor Intel",
                f"  - **Title:** {comp.seo.title[:80] if comp.seo.title else 'N/A'}",
                f"  - **Description:** {comp.seo.description[:120] if comp.seo.description else 'N/A'}",
                f"  - **H1:** {comp.seo.h1[:80] if comp.seo.h1 else 'N/A'}",
                f"  - **Tools:** {', '.join(f'`{t}`' for t in comp.third_party_tools) or 'N/A'}",
                f"  - **Features:** Blog={'✅' if comp.has_blog else '❌'}  "
                f"Pricing={'✅' if comp.has_pricing else '❌'}  "
                f"Free Trial={'✅' if comp.has_free_trial else '❌'}",
                "",
            ]

        if (pric := self.pricing) is not None and pric.plans:
            lines += ["## 💰 Pricing Intelligence"]
            for plan in pric.plans:
                lines.append(f"  - **{plan.label}:** {plan.amount}")
            if pric.diff_from_last:
                lines += ["  - **⚡ Changes detected:**"]
                for d in pric.diff_from_last:
                    lines.append(f"    - {d}")
            lines.append("")

        if (smap := self.sitemap) is not None:
            lines += [
                "## 🗺️ Site Architecture",
                f"  - **Pages found:** {smap.total_urls}  |  **Max depth:** {smap.max_depth_reached}",
                f"  - **sitemap.xml:** {'✅' if smap.has_sitemap_xml else '❌'}  |  "
                f"**robots.txt:** {'✅' if smap.has_robots_txt else '❌'}",
                f"  - **Languages:** {', '.join(smap.languages) or 'N/A'}",
                "",
            ]

        if (cyb := self.cyber) is not None:
            lines += [
                "## 🕵️ Cyber Infiltration (Stealth Engine)",
                f"  - **Status:** `{cyb.status}`  |  **Mode:** `{cyb.mode}`",
                f"  - **Identity (UA):** `{cyb.identity[:60]}...`" if cyb.identity else "  - **Identity:** N/A",
                f"  - **Assets Extracted:** {cyb.assets_count}",
                f"  - **Semantic Bridge:** {'✅ Connected' if cyb.bridge_data else '❌ Missing'}",
            ]
            if cyb.bridge_data and "links" in cyb.bridge_data:
                lines.append(f"  - **Links Discovered:** {len(cyb.bridge_data['links'])}")
            lines.append("")

        if (ux := self.ux) is not None:
            lines += [
                "## 🖱️ UX Intelligence (Scrapling Engine)",
                f"  - **Status:** `{ux.status}`  |  **Load Time:** {ux.load_time_ms}ms",
                f"  - **Identity (TLS):** `{ux.identity[:30]}...`" if ux.identity else "  - **Identity:** N/A",
                f"  - **Anti-bot Bypass:** {'✅' if ux.has_cloudflare else '❌'}",
                f"  - **Interactives Found:** {ux.interactive_elements}",
            ]
            if ux.navigation_tree:
                lines.append(f"  - **UX Path:** {' → '.join(ux.navigation_tree)}")
            lines.append("")

        if (ai := self.ai_synthesis) is not None:
            lines += [
                "## 🤖 AI Synthesis (CyberScraper-2077 Brain)",
                f"  - **Summary:** {ai.summary[:100]}...",
                f"  - **Confidence:** {ai.confidence:.2f}",
                f"  - **Data points:** {len(ai.extracted_data)} keys extracted.",
            ]
            lines.append("")

        if self.errors:
            lines += ["## ⚠️ Errors", *[f"  - {e}" for e in self.errors], ""]

        lines.append(f"---\n_Gahenax Spy System v1.1+.ux (Cyber-Spy-UX Hybrid) — Web Espionage Protocol_")
        return "\n".join(lines)
