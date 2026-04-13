"""
gahenax_spy_system/agents/price_watcher.py
AGENT 4 — PriceWatcher
Sigil: SWORD — extrae y monitorea precios, planes y señales de urgencia.

Detecta:
  • Estructuras de pricing (tiers, planes, freemium)
  • Precios individuales y sus períodos (mes/año/único)
  • Señales de urgencia (countdown, "últimas plazas", "oferta termina")
  • Anchoring de precios (tachados, comparaciones)
  • Cambios vs. ejecución anterior (diff mode)
  • Modelo de pricing: saas-tiered | flat | usage | contact | unknown
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from gahenax_spy_system.models import PricePoint, PriceReport
from gahenax_spy_system.utils import StealthHTTPClient

# Carpeta donde se guardan snapshots anteriores para el diff
_SNAPSHOT_DIR = Path(".spy_cache/price_snapshots")


class PriceWatcher:
    """
    Agente de monitoreo de precios.
    Parsea la estructura de pricing del sitio y detecta cambios entre ejecuciones.
    """

    def __init__(self, http: StealthHTTPClient | None = None):
        self._http = http or StealthHTTPClient()

    def run(self, url: str, save_snapshot: bool = True) -> PriceReport:
        report = PriceReport(
            url=url,
            snapshot_ts=datetime.now(timezone.utc).isoformat()
        )
        resp = self._http.get(url)
        if resp is None:
            return report

        soup = BeautifulSoup(resp.text, "lxml")
        raw  = resp.text

        report.plans         = self._extract_plans(soup, raw)
        report.has_free_tier = self._detect_free_tier(soup, raw)
        report.has_trial     = self._detect_trial(raw)
        report.pricing_model = self._classify_model(report.plans, raw)
        report.urgency_signals = self._detect_urgency(soup, raw)
        report.diff_from_last  = self._compute_diff(url, report.plans, save_snapshot)

        return report

    #  Plan extraction 

    def _extract_plans(self, soup: BeautifulSoup, raw: str) -> list[PricePoint]:
        plans: list[PricePoint] = []

        # Strategy 1: Structured pricing cards
        # Look for containers that likely hold pricing info
        card_selectors = [
            "pricing-card", "plan-card", "price-card", "tier", "plan",
            "pricing__plan", "card", "package"
        ]
        pricing_containers = []
        for selector in card_selectors:
            found = soup.find_all(class_=re.compile(selector, re.I))
            if found:
                pricing_containers.extend(found)
                if len(pricing_containers) >= 2:
                    break

        for container in pricing_containers[:6]:  # Max 6 plans
            plan = self._extract_plan_from_container(container)
            if plan and plan.label:
                # Deduplicate
                if not any(p.label == plan.label for p in plans):
                    plans.append(plan)

        # Strategy 2: Regex over raw text if no structured cards found
        if not plans:
            plans = self._regex_extract_prices(raw)

        return plans[:6]

    def _extract_plan_from_container(self, container) -> PricePoint | None:
        try:
            # Plan label (name)
            label = ""
            for tag in ["h2", "h3", "h4", ".plan-name", ".tier-name"]:
                el = container.find(tag)
                if el:
                    label = el.get_text(strip=True)[:60]
                    break

            # Price
            amount = ""
            price_patterns = [
                re.compile(r"\$[\d,]+(?:\.\d{2})?"),
                re.compile(r"€[\d,]+(?:\.\d{2})?"),
                re.compile(r"[\d,]+(?:\.\d{2})?\s*(?:USD|EUR|GBP)"),
                re.compile(r"Free|Gratis|Gratuito", re.I),
                re.compile(r"Contact|Contactar|Custom", re.I),
            ]
            text = container.get_text(" ", strip=True)
            for pp in price_patterns:
                m = pp.search(text)
                if m:
                    amount = m.group(0)[:30]
                    break

            # Period
            period = "unknown"
            if re.search(r"/mo|per month|mensual|monthly|month", text, re.I):
                period = "month"
            elif re.search(r"/yr|per year|anual|yearly|annual|year", text, re.I):
                period = "year"
            elif re.search(r"one.time|pago.único|lifetime", text, re.I):
                period = "one-time"
            elif re.search(r"free|gratis", text, re.I):
                period = "free"

            # Features (bullet points)
            features = [
                li.get_text(strip=True)[:80]
                for li in container.find_all("li")
            ][:5]

            if not label and not amount:
                return None

            return PricePoint(
                label=label or "Unknown",
                amount=amount or "?",
                period=period,
                features=features,
            )
        except Exception:
            return None

    def _regex_extract_prices(self, raw: str) -> list[PricePoint]:
        """Fallback: regex scan sobre el HTML crudo para detectar precios."""
        plans = []
        # Find price + context patterns
        price_re = re.compile(
            r"(?:plan|tier|(\w+))\s*[:\-]?\s*\$?(\d[\d,.]+)\s*/?\s*(mo|month|yr|year|año|mes)?",
            re.I
        )
        for m in price_re.finditer(raw[:30_000]):
            label  = m.group(1) or "Plan"
            amount = f"${m.group(2)}"
            period = {"mo": "month", "month": "month",
                      "yr": "year", "year": "year",
                      "año": "year", "mes": "month"}.get(
                (m.group(3) or "").lower(), "unknown"
            )
            if not any(p.amount == amount for p in plans):
                plans.append(PricePoint(label=label.capitalize(), amount=amount, period=period))
        return plans[:5]

    #  Tier detection 

    def _detect_free_tier(self, soup: BeautifulSoup, raw: str) -> bool:
        return bool(re.search(r"free tier|free plan|free forever|freemium|\$0", raw, re.I))

    def _detect_trial(self, raw: str) -> bool:
        return bool(re.search(
            r"free trial|try for free|(\d+).day trial|no credit card", raw, re.I
        ))

    def _classify_model(self, plans: list[PricePoint], raw: str) -> str:
        if not plans:
            return "unknown"
        if any(p.amount.lower() in ("contact", "contactar", "custom") for p in plans):
            return "contact"
        if len(plans) == 1:
            return "flat"
        if re.search(r"per seat|per user|per api call|usage", raw, re.I):
            return "usage"
        return "saas-tiered"

    #  Urgency 

    def _detect_urgency(self, soup: BeautifulSoup, raw: str) -> list[str]:
        signals = []
        urgency_patterns = [
            (r"offer ends|oferta termina|limited time|tiempo limitado", "Time-limited offer"),
            (r"only \d+ left|últimas \d+ plazas",                       "Scarcity signal"),
            (r"countdown|timer|expires in",                             "Countdown timer"),
            (r"\d+%\s*off|descuento de \d+",                           "Percentage discount"),
            (r"save \$[\d,]+|ahorra \$[\d,]+",                         "Dollar savings highlight"),
        ]
        raw_lower = raw.lower()
        for pattern, label in urgency_patterns:
            if re.search(pattern, raw_lower, re.I) and label not in signals:
                signals.append(label)
        return signals

    #  Diff vs previous snapshot 

    def _compute_diff(self, url: str, plans: list[PricePoint],
                      save: bool) -> list[str]:
        """Compara con el snapshot anterior. Retorna lista de cambios detectados."""
        cache_key = hashlib.md5(url.encode()).hexdigest()[:12]
        _SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        snap_path = _SNAPSHOT_DIR / f"{cache_key}.json"

        current = {p.label: p.amount for p in plans}
        diff = []

        if snap_path.exists():
            try:
                previous = json.loads(snap_path.read_text(encoding="utf-8"))
                for label, amount in current.items():
                    prev_amount = previous.get(label)
                    if prev_amount is None:
                        diff.append(f"NEW plan detected: '{label}' @ {amount}")
                    elif prev_amount != amount:
                        diff.append(f"PRICE CHANGE: '{label}' was {prev_amount} → now {amount}")
                for label in previous:
                    if label not in current:
                        diff.append(f"REMOVED plan: '{label}'")
            except Exception:
                pass

        if save:
            snap_path.write_text(
                json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8"
            )

        return diff
