"""
gahenax_spy_system/orchestrator.py
MasterOrchestrator — coordina los 5 agentes con GSD Wave Protocol.
Sigil: CHAIN → SWORD → MIRROR

WAVE 1 (independiente):  TechFingerprinter + SitemapCrawler
WAVE 2 (depende de W1):  StructuralScraper + CompetitorProfiler
WAVE 3 (secuencial):     PriceWatcher + síntesis + emit_skill opcional

Además, puede emitir una SKILL.md nueva en .agent/skills/ con el patrón
arquitectónico descubierto — implementando el web-espionage-protocol.
"""
from __future__ import annotations

import concurrent.futures
import json
import re
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from gahenax_spy_system.agents import (
    TechFingerprinter,
    StructuralScraper,
    CompetitorProfiler,
    PriceWatcher,
    SitemapCrawler,
    CyberAgent,
    UXAgent,
    LLMAgent,
)
from gahenax_spy_system.models import IntelReport, SpyMission
from gahenax_spy_system.utils import StealthHTTPClient


class MasterOrchestrator:
    """
    Orquestador principal del sistema de espionaje.

    Uso básico:
        engine = MasterOrchestrator()
        report = engine.run("https://stripe.com")
        print(report.to_report())

    Con misión personalizada:
        mission = SpyMission(url="https://stripe.com", mode="tech", verbose=True)
        report = engine.run_mission(mission)
    """

    def __init__(self, rules_dir: str = ".agent/skills"):
        self._rules_dir  = Path(rules_dir)
        self._http_pool  = {}  # Shared HTTP clients per delay config

    def run(self, url: str, mode: str = "full", **kwargs) -> IntelReport:
        """Shortcut: crea una SpyMission y la ejecuta."""
        mission = SpyMission(url=url, mode=mode, **kwargs)
        return self.run_mission(mission)

    def run_mission(self, mission: SpyMission) -> IntelReport:
        """Ejecuta la misión completa con el ciclo de waves GSD."""
        t_start = time.time()
        mission_id = str(uuid.uuid4())[:8]

        report = IntelReport(
            mission_id = mission_id,
            timestamp  = datetime.now(timezone.utc).isoformat(),
            target_url = mission.url,
            mode       = mission.mode,
        )

        # Configuración de Tor si se solicita (SOCKS5 local Tor)
        proxy = "socks5://127.0.0.1:9050" if mission.use_tor else None
        http = StealthHTTPClient(
            timeout=mission.timeout,
            delay=mission.delay,
            verbose=mission.verbose,
            proxy=proxy,
            ignore_robots=mission.implant
        )

        print(f"\n  🕵️  GAHENAX SPY — Mission {mission_id}")
        print(f"  Target : {mission.url}")
        print(f"  Mode   : {mission.mode}")
        if mission.implant:
            print("  Stealth: IMPLANT MODE ENABLED (HackerOne Level)")
        print(f"  {'─'*50}")

        try:
            # ── WAVE 0: Cyber-Infiltration (Infiltración profunda) ────────────
            if mission.mode in ("full", "cyber") or mission.implant:
                print("  🌊 Wave 0 → Cyber-Infiltration (Puppeteer-Stealth Engine)")
                # Crear directorio de salida para los assets si no existe
                output_base = Path("spy_data") / mission_id
                output_base.mkdir(parents=True, exist_ok=True)
                
                try:
                    report.cyber = CyberAgent().run(
                        url=mission.url, 
                        output_dir=str(output_base),
                        implant=mission.implant,
                        goal=mission.goal,
                        use_tor=mission.use_tor
                    )
                    if report.cyber.status == "Success":
                        print(f"      Cyber: Success | Identity: {report.cyber.identity[:30]}...")
                        # Si tenemos bridge data, podemos enriquecer otros campos preventivamente
                        if report.cyber.bridge_data:
                            print(f"      Bridge: {len(report.cyber.bridge_data.get('links', []))} semantic links captured.")
                except Exception as e:
                    report.errors.append(f"Wave0/cyber: {str(e)[:120]}")

            # ── WAVE 0.5: UX-Infiltration (Scrapling Engine) ──────────────────
            if mission.mode in ("full", "cyber", "ux"):
                print("  🌊 Wave 0.5 → UX-Infiltration (Scrapling Engine)")
                try:
                    report.ux = UXAgent().run(mission)
                    if report.ux.status == "Success":
                        interactives = report.ux.interactive_elements
                        print(f"      UX: Success | Interactives: {interactives} | Load: {report.ux.load_time_ms}ms")
                    else:
                        print(f"      UX: {report.ux.status}")
                except Exception as e:
                    report.errors.append(f"Wave0.5/ux: {str(e)[:120]}")

            # ── WAVE 1: TechFingerprinter + SitemapCrawler (paralelo) ─────────
            if mission.mode in ("full", "tech", "map"):
                print("  🌊 Wave 1 → TechFingerprinter + SitemapCrawler (paralelo)")
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    futures = {}
                    if mission.mode in ("full", "tech"):
                        futures["tech"]    = executor.submit(
                            TechFingerprinter(http).run, mission.url
                        )
                    if mission.mode in ("full", "map"):
                        futures["sitemap"] = executor.submit(
                            SitemapCrawler(http, mission.max_depth).run, mission.url
                        )

                    for key, future in futures.items():
                        try:
                            result = future.result(timeout=mission.timeout + 10)
                            if key == "tech":    report.tech    = result
                            if key == "sitemap": report.sitemap = result
                        except Exception as e:
                            report.errors.append(f"Wave1/{key}: {str(e)[:120]}")

                if report.tech:
                    fw = ", ".join(report.tech.frameworks[:4]) or "unknown"
                    print(f"      Tech: {fw} | CDN: {report.tech.cdn or 'N/A'}")
                if report.sitemap:
                    print(f"      Sitemap: {report.sitemap.total_urls} URLs")

            # ── WAVE 4: AI Synthesis (CyberScraper-2077 Brain) ────────────────
            if mission.ai_parse:
                print("  🌊 Wave 4 → AI Synthesis (CyberScraper-2077 Brain)")
                try:
                    report.ai_synthesis = LLMAgent().run(mission, report)
                    if report.ai_synthesis.confidence > 0:
                        print(f"      AI: {report.ai_synthesis.summary[:60]}...")
                except Exception as e:
                    report.errors.append(f"Wave4/ai: {str(e)[:120]}")

            # ── WAVE 3: StructuralScraper + CompetitorProfiler (paralelo) ────
            if mission.mode in ("full", "structure", "competitor"):
                print("  🌊 Wave 2 → StructuralScraper + CompetitorProfiler (paralelo)")
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    futures2 = {}
                    if mission.mode in ("full", "structure"):
                        futures2["structure"]   = executor.submit(
                            StructuralScraper(http).run, mission.url
                        )
                    if mission.mode in ("full", "competitor"):
                        futures2["competitor"]  = executor.submit(
                            CompetitorProfiler(http).run, mission.url
                        )

                    for key, future in futures2.items():
                        try:
                            result = future.result(timeout=mission.timeout + 10)
                            if key == "structure":  report.structure  = result
                            if key == "competitor": report.competitor = result
                        except Exception as e:
                            report.errors.append(f"Wave2/{key}: {str(e)[:120]}")

                if report.structure:
                    print(f"      Blueprint: {report.structure.page_type} | "
                          f"Routing: {report.structure.routing_type} | "
                          f"Colors: {len(report.structure.colors)}")
                if report.competitor:
                    tools = len(report.competitor.third_party_tools)
                    print(f"      Competitor: Tools={tools} | "
                          f"Pricing={'✅' if report.competitor.has_pricing else '❌'}")

            # ── WAVE 3: PriceWatcher (secuencial) ────────────────────────────
            if mission.mode in ("full", "price"):
                print("  🌊 Wave 3 → PriceWatcher")
                try:
                    report.pricing = PriceWatcher(http).run(mission.url)
                    model  = report.pricing.pricing_model
                    plans  = len(report.pricing.plans)
                    changes= len(report.pricing.diff_from_last)
                    print(f"      Pricing: model={model} | plans={plans} | changes={changes}")
                except Exception as e:
                    report.errors.append(f"Wave3/price: {str(e)[:120]}")

        except Exception as outer_e:
            report.errors.append(f"Orchestrator fatal: {str(outer_e)[:200]}")

        report.duration_ms = int((time.time() - t_start) * 1000)
        print(f"\n  ✅ Mission complete in {report.duration_ms}ms")

        # ── Emit Skill (web-espionage-protocol) ───────────────────────────────
        if mission.emit_skill:
            skill_path = self._emit_skill(mission, report)
            if skill_path:
                print(f"  📖 New Skill → {skill_path}")

        # ── Save output ───────────────────────────────────────────────────────
        if mission.output_path:
            Path(mission.output_path).write_text(
                report.to_json(), encoding="utf-8"
            )
            print(f"  💾 Report saved → {mission.output_path}")

        return report

    # ── Skill Emitter (web-espionage-protocol) ────────────────────────────────

    def _emit_skill(self, mission: SpyMission, report: IntelReport) -> str | None:
        """
        Genera un SKILL.md en .agent/skills/ con el patrón arquitectónico
        descubierto. Implementa el protocolo web-espionage-protocol.
        """
        try:
            parsed       = urlparse(mission.url)
            domain_clean = re.sub(r"[^a-z0-9]+", "-", parsed.netloc.lower()).strip("-")
            skill_name   = f"architectural-pattern-{domain_clean}"
            skill_dir    = self._rules_dir / skill_name
            skill_dir.mkdir(parents=True, exist_ok=True)
            skill_path   = skill_dir / "SKILL.md"

            # Collect data
            fw_list   = report.tech.frameworks[:5] if report.tech else []
            cdn       = report.tech.cdn if report.tech else ""
            colors    = [c.hsl for c in report.structure.colors[:3]] if report.structure else []
            fonts_str = ", ".join(f"`{f}`" for f in (report.structure.fonts[:3] if report.structure else []))
            page_type = report.structure.page_type if report.structure else "unknown"
            routing   = report.structure.routing_type if report.structure else "unknown"
            layout    = report.structure.layout_system if report.structure else "unknown"
            components= report.structure.component_tree if report.structure else []
            tools     = report.competitor.third_party_tools[:5] if report.competitor else []
            title     = report.competitor.seo.title[:80] if report.competitor else ""

            skill_content = f"""---
name: "{skill_name}"
description: "Activa esta skill CUANDO necesites replicar o inspirarte en el patrón arquitectónico obtenido del espionaje de {parsed.netloc}. Cargado via web-espionage-protocol desde {mission.url}."
version: "1.0.0"
source_url: "{mission.url}"
scanned_at: "{report.timestamp}"
---

# Architectural Pattern — {parsed.netloc}

Patrón extraído mediante el **Gahenax Web Espionage Protocol** aplicado a `{mission.url}`.

## Tech Stack detectado

| Componente | Valor |
|-----------|-------|
| Frameworks | {', '.join(f'`{f}`' for f in fw_list) or 'No detectado'} |
| CDN        | `{cdn or 'N/A'}` |
| Page Type  | `{page_type}` |
| Routing    | `{routing}` |
| Layout     | `{layout}` |
| Tools      | {', '.join(f'`{t}`' for t in tools) or 'N/A'} |

## Design DNA

### Paleta de Colores (Top 3)
{chr(10).join(f"- `{c}`" for c in colors) or "- No detectada"}

### Tipografía
{fonts_str or "No detectada"}

### Árbol de Componentes
```
{" → ".join(components) if components else "No detectado"}
```

## SEO Snapshot

- **Title:** {title}
- **H1:** {report.competitor.seo.h1[:80] if report.competitor else 'N/A'}

## Cómo Replicar Este Patrón

1. **Stack:** Usa {fw_list[0] if fw_list else 'el framework del objetivo'} como base.
2. **Layout:** Implementa `{layout}` como sistema principal.
3. **Colores:** Adapta la paleta HSL a tu identidad de marca.
4. **Componentes:** Sigue la secuencia `{" → ".join(components)}`.
5. **Routing:** {"Client-side routing (React Router / Next.js App Router)" if routing == "spa" else "Server-side rendering con full reloads"}.

## Invariantes Ontológicas (Gahenax)

- Si detectaste Stripe/PayPal → implementar GATE (validación) antes de SWORD (pago)
- Si el sitio tiene mensajería (CHAIN) → agregar MIRROR (OpenTelemetry) obligatorio
- PK en MySQL → ULIDv7 o INT auto-increment, NUNCA UUIDv4

---
_Generado por Gahenax Spy System v1.0 | web-espionage-protocol_
"""
            skill_path.write_text(skill_content, encoding="utf-8")
            return str(skill_path)
        except Exception as e:
            return None
