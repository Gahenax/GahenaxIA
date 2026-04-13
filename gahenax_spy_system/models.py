"""
gahenax_spy_system/models.py
Contratos de datos (Pydantic v2) para todo el sistema spy.
Sigil: SEAL — interfaces inmutables entre agentes.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# 
#  MISIÓN DE ENTRADA
# 

class SpyMission(BaseModel):
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


# 
#  PERFILES DE AGENTES
# 

class TechSignal(BaseModel):
    name:       str
    category:   str    # framework | language | cdn | waf | cms | analytics | payments
    confidence: float  # 0.0 - 1.0
    evidence:   str    # La señal concreta que activó la detección


class TechProfile(BaseModel):
    """Output del TechFingerprinter."""
    url:            str
    server:         str = ""
    powered_by:     str = ""
    cdn:            str = ""
    waf:            str = ""
    cms:            str = ""
    http_version:   str = ""
    has_https:      bool = False
    signals:        List[TechSignal] = Field(default_factory=list)
    frameworks:     List[str]        = Field(default_factory=list)
    analytics:      List[str]        = Field(default_factory=list)
    raw_headers:    Dict[str, Any]   = Field(default_factory=dict)
    confidence_avg: float = 0.0

    def top_frameworks(self, n: int = 5) -> List[str]:
        top = sorted(self.signals, key=lambda s: s.confidence, reverse=True)
        return [s.name for s in top if s.category == "framework"][:n]


class ColorToken(BaseModel):
    hex:  str
    hsl:  str
    role: str  # primary | secondary | background | text | accent


class StructuralProfile(BaseModel):
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
    colors:         List[ColorToken] = Field(default_factory=list)
    fonts:          List[str]        = Field(default_factory=list)
    section_count:  int  = 0
    component_tree: List[str]        = Field(default_factory=list)  # [nav, hero, features, pricing, footer]
    design_notes:   List[str]        = Field(default_factory=list)


class SEOSnapshot(BaseModel):
    title:       str = ""
    description: str = ""
    h1:          str = ""
    h_structure: Dict[str, int] = Field(default_factory=dict)  # {h1: 1, h2: 3, h3: 5}
    canonical:   str = ""
    og_image:    str = ""
    schema_types: List[str] = Field(default_factory=list)  # Schema.org types found


class CompetitorProfile(BaseModel):
    """Output del CompetitorProfiler."""
    url:           str
    seo:           SEOSnapshot      = Field(default_factory=SEOSnapshot)
    social_links:  List[str]        = Field(default_factory=list)
    third_party_tools: List[str]    = Field(default_factory=list)  # HotJar, Intercom, etc.
    trust_signals: List[str]        = Field(default_factory=list)  # Badges, certs, reviews
    contact_methods: List[str]      = Field(default_factory=list)
    has_blog:      bool = False
    has_pricing:   bool = False
    has_free_trial: bool = False
    language:      str  = ""
    word_count:    int  = 0


class PricePoint(BaseModel):
    label:    str
    amount:   str   # Raw text — puede ser "$29/mes", "Gratis", "Consultar"
    currency: str   = ""
    period:   str   = ""   # month | year | one-time | unknown
    features: List[str] = Field(default_factory=list)


class PriceReport(BaseModel):
    """Output del PriceWatcher."""
    url:          str
    plans:        List[PricePoint] = Field(default_factory=list)
    has_free_tier: bool = False
    has_trial:    bool  = False
    pricing_model: str  = ""  # saas-tiered | flat | usage | contact | unknown
    urgency_signals: List[str] = Field(default_factory=list)  # "Oferta termina en..."
    diff_from_last:  List[str] = Field(default_factory=list)  # Cambios vs ejecución anterior
    snapshot_ts:  str = ""


class SitePage(BaseModel):
    url:       str
    page_type: str   # landing | blog | product | docs | auth | about | legal | other
    depth:     int
    title:     str = ""
    lang:      str = ""


class SiteMap(BaseModel):
    """Output del SitemapCrawler."""
    root_url:   str
    pages:      List[SitePage] = Field(default_factory=list)
    total_urls: int = 0
    max_depth_reached: int = 0
    has_sitemap_xml: bool = False
    has_robots_txt:  bool = False
    sitemap_url:     str  = ""
    disallowed:      List[str] = Field(default_factory=list)
    languages:       List[str] = Field(default_factory=list)


class CyberProfile(BaseModel):
    """Output del CyberAgent (Puppeteer-based stealth scraper)."""
    url:            str
    status:         str = "Success"
    mode:           str = "standard"  # standard | implant
    identity:       str = ""          # User-Agent used
    timestamp:      str = ""
    assets_count:   int = 0
    bridge_data:    Dict[str, Any] = Field(default_factory=dict)  # Data from semantic_bridge.json
    reasoning_file: str = ""
    output_dir:     str = ""


class UXProfile(BaseModel):
    """Output del UXAgent (Scrapling-based adaptive scraper)."""
    url:            str
    status:         str = "Success"
    identity:       str = ""          # TLS Fingerprint / UA used
    has_cloudflare: bool = False
    load_time_ms:   int = 0
    navigation_tree: List[str] = Field(default_factory=list)
    interactive_elements: int = 0
    scrapling_stats: Dict[str, Any] = Field(default_factory=dict)


class LLMAnalysis(BaseModel):
    """Output del LLMAgent (CyberScraper-2077 Brain)."""
    summary:        str = ""
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    confidence:     float = 0.0
    raw_response:   str = ""


# 
#  TELEMETRÍA Y AUDITORÍA (V3)
# 

class MissionTelemetry(BaseModel):
    """Telemetría táctica volátil de la misión."""
    network_bytes_in:  int = 0
    network_bytes_out: int = 0
    latency_avg_ms:    int = 0
    identity_rotation_count: int = 0
    proxy_success:     bool = True
    evasion_score:     float = 1.0  # 1.0 = ghost, 0.0 = detected
    fingerprint_type:  str = "statistical"
    cpu_peak_percent:  float = 0.0
    memory_peak_mb:    float = 0.0
    container_id:      Optional[str] = None


# 
#  DISCOVERY / AMALGAM ENGINE
# 

class DiscoveryResult(BaseModel):
    """Un resultado individual de búsqueda (SerpApi o Soberano)."""
    url:            str
    title:          str = ""
    snippet:        str = ""
    rank:           int = 0
    source:         str = "sovereign"  # serpapi | sovereign | amalgam
    is_ad:          bool = False
    tactical_preview: List[str] = Field(default_factory=list)  # Tech detected from snippet
    metadata:       Dict[str, Any] = Field(default_factory=dict)


class DiscoverySearchReport(BaseModel):
    """Reporte de la Wave -1 (Discovery Amalgam)."""
    keyword:        str
    timestamp:      str
    results:        List[DiscoveryResult] = Field(default_factory=list)
    total_discovered: int = 0
    serpapi_used:   bool = False
    amalgam_notes:  List[str] = Field(default_factory=list)

    def top_urls(self, n: int = 10) -> List[str]:
        return [r.url for r in self.results[:n]]


# 
#  REPORTE FINAL
# 

class IntelReport(BaseModel):
    """Reporte de inteligencia completo — output del MasterOrchestrator."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    mission_id:   str
    timestamp:    str
    target_url:   str
    mode:         str

    discovery_origin: Optional[DiscoverySearchReport] = None  # Vinculación con Wave -1
    tech:         Optional[TechProfile]       = None
    structure:    Optional[StructuralProfile] = None
    competitor:   Optional[CompetitorProfile] = None
    pricing:      Optional[PriceReport]       = None
    sitemap:      Optional[SiteMap]           = None
    cyber:        Optional[CyberProfile]      = None
    ux:           Optional[UXProfile]         = None
    ai_synthesis: Optional[LLMAnalysis]       = None
    meta_audit:   Optional[Dict[str, Any]]    = None  # Results from MetaInformant
    telemetry:    Optional[MissionTelemetry]  = None

    errors:       List[str] = Field(default_factory=list)
    duration_ms:  int = 0

    def to_json(self, indent: int = 2) -> str:
        return self.model_dump_json(indent=indent)

    def to_report(self) -> str:
        """Genera un reporte Markdown ejecutivo."""
        lines = [
            f"#  Intel Report — {self.target_url}",
            f"**Mission ID:** `{self.mission_id}`  |  "
            f"**Timestamp:** {self.timestamp}  |  "
            f"**Duration:** {self.duration_ms}ms",
            "",
        ]

        if (tech := self.tech) is not None:
            lines += [
                "##  Tech Stack Detected",
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
                "##  Structural DNA",
                f"  - **Page Type:** `{struct.page_type}`  |  **Routing:** `{struct.routing_type}`",
                f"  - **Layout:** `{struct.layout_system}`  |  **Sections:** {struct.section_count}",
                f"  - **Fonts:** {', '.join(f'`{f}`' for f in struct.fonts) or 'N/A'}",
                f"  - **CTA:** `{struct.cta_text or 'N/A'}`",
            ]
            if struct.colors:
                colors_summary = ", ".join([c.hex for c in struct.colors[:3]])
                lines.append(f"  - **Colors:** {colors_summary}")
            if struct.component_tree:
                lines.append(f"  - **Components:** {' → '.join(struct.component_tree)}")
            lines.append("")

        if (comp := self.competitor) is not None:
            lines += [
                "##  Competitor Intel",
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
            lines += ["##  Pricing Intelligence"]
            for plan in pric.plans:
                lines.append(f"  - **{plan.label}:** {plan.amount}")
            if pric.diff_from_last:
                lines += ["  - **⚠️ Changes detected:**"]
                for d in pric.diff_from_last:
                    lines.append(f"    - {d}")
            lines.append("")

        if (smap := self.sitemap) is not None:
            lines += [
                "##  Site Architecture",
                f"  - **Pages found:** {smap.total_urls}  |  **Max depth:** {smap.max_depth_reached}",
                f"  - **sitemap.xml:** {'✅' if smap.has_sitemap_xml else '❌'}  |  "
                f"**robots.txt:** {'✅' if smap.has_robots_txt else '❌'}",
                f"  - **Languages:** {', '.join(smap.languages) or 'N/A'}",
                "",
            ]

        if (cyb := self.cyber) is not None:
            lines += [
                "##  Cyber Infiltration (Stealth Engine)",
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
                "##  UX Intelligence (Scrapling Engine)",
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
                "##  AI Synthesis (CyberScraper-2077 Brain)",
                f"  - **Summary:** {ai.summary[:100]}...",
                f"  - **Confidence:** {ai.confidence:.2f}",
                f"  - **Data points:** {len(ai.extracted_data)} keys extracted.",
            ]
            lines.append("")

        if (meta := self.meta_audit) is not None:
            lines += ["##  Meta-Text & Dev Audit"]
            if meta.get("comments"):
                lines.append(f"  - **Dev Comments:** Found {len(meta['comments'])} hidden notes.")
            if meta.get("webpack_manifests"):
                lines.append(f"  - **Webpack Engine:** {len(meta['webpack_manifests'])} manifests detected.")
            lines.append("")

        if (tel := self.telemetry) is not None:
            lines += [
                "##  Tactical Telemetry (SSC v3.0)",
                f"  - **Net Traffic:** Inbound {tel.network_bytes_in}b / Outbound {tel.network_bytes_out}b",
                f"  - **Identity Hub:** {tel.identity_rotation_count} rotations | Success: {'✅' if tel.proxy_success else '❌'}",
                f"  - **Evasion Score:** {tel.evasion_score:.2f} ({tel.fingerprint_type})",
                f"  - **Resource Peak:** CPU {tel.cpu_peak_percent}% | RAM {tel.memory_peak_mb}MB",
            ]
            if tel.container_id:
                lines.append(f"  - **Container:** `{tel.container_id[:12]}`")
            lines.append("")

        if self.errors:
            lines += ["##  Errors", *[f"  - {e}" for e in self.errors], ""]

        lines.append(f"---\n_Gahenax Spy System v3.0.amalg (Ghost-Container Hybrid) — Web Espionage Protocol_")
        return "\n".join(lines)
