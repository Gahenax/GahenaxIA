"""
gahenax_spy_system/agents/competitor_profiler.py
AGENT 3 — CompetitorProfiler
Sigil: MIRROR — inteligencia de negocio: SEO, herramientas, social proof.

Extrae:
  • Complete SEO snapshot (title, description, H1, heading structure)
  • Schema.org JSON-LD (Organization, Product, Offer, Rating, etc.)
  • Herramientas de terceros (HotJar, Intercom, Drift, Zendesk, etc.)
  • Social proof (testimonios, ratings, menciones de prensa)
  • Links sociales (Twitter, LinkedIn, GitHub, YouTube)
  • Métodos de contacto (email, WhatsApp, Calendly, etc.)
  • Detección de Trial/Free tier / Pricing page
"""
from __future__ import annotations

import json
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from gahenax_spy_system.models import CompetitorProfile, SEOSnapshot
from gahenax_spy_system.utils import StealthHTTPClient


_THIRD_PARTY_SIGNALS: list[tuple[str, str]] = [
    # (url_pattern_in_script, tool_name)
    ("intercom.com",       "Intercom"),
    ("drift.com",          "Drift"),
    ("zendesk.com",        "Zendesk"),
    ("crisp.chat",         "Crisp"),
    ("hotjar.com",         "HotJar"),
    ("clarity.ms",         "Microsoft Clarity"),
    ("fullstory.com",      "FullStory"),
    ("mixpanel.com",       "Mixpanel"),
    ("segment.com",        "Segment"),
    ("hubspot.com",        "HubSpot"),
    ("salesforce.com",     "Salesforce"),
    ("freshdesk.com",      "Freshdesk"),
    ("zoho.com",           "Zoho"),
    ("mailchimp.com",      "Mailchimp"),
    ("convertkit.com",     "ConvertKit"),
    ("activecampaign.com", "ActiveCampaign"),
    ("stripe.com",         "Stripe"),
    ("paddle.com",         "Paddle"),
    ("lemon.squeezy",      "LemonSqueezy"),
    ("gumroad.com",        "Gumroad"),
    ("calendly.com",       "Calendly"),
    ("lemcal.com",         "Lemcal"),
    ("typeform.com",       "Typeform"),
    ("notion.so",          "Notion"),
    ("airtable.com",       "Airtable"),
    ("zapier.com",         "Zapier"),
    ("sentry.io",          "Sentry"),
    ("datadog-browser",    "Datadog RUM"),
    ("logrocket.com",      "LogRocket"),
    ("userflow.com",       "Userflow"),
    ("appcues.com",        "Appcues"),
]

_SOCIAL_PATTERNS: list[tuple[str, str]] = [
    ("twitter.com",   "Twitter/X"),
    ("x.com",         "Twitter/X"),
    ("linkedin.com",  "LinkedIn"),
    ("github.com",    "GitHub"),
    ("youtube.com",   "YouTube"),
    ("instagram.com", "Instagram"),
    ("facebook.com",  "Facebook"),
    ("discord.com",   "Discord"),
    ("discord.gg",    "Discord"),
    ("tiktok.com",    "TikTok"),
    ("producthunt.com","Product Hunt"),
]


class CompetitorProfiler:
    """
    Agente de inteligencia de negocio.
    Construye un perfil completo del competidor: SEO, herramientas, social proof.
    """

    def __init__(self, http: StealthHTTPClient | None = None):
        self._http = http or StealthHTTPClient()

    def run(self, url: str) -> CompetitorProfile:
        profile = CompetitorProfile(url=url)
        resp = self._http.get(url)
        if resp is None:
            return profile

        soup = BeautifulSoup(resp.text, "lxml")
        raw  = resp.text

        profile.seo              = self._extract_seo(soup)
        profile.third_party_tools = self._detect_third_party(raw)
        profile.social_links     = self._extract_social_links(soup, url)
        profile.trust_signals    = self._extract_trust_signals(soup, raw)
        profile.contact_methods  = self._detect_contact_methods(soup, raw)
        profile.language         = self._detect_language(soup)
        profile.word_count       = len(soup.get_text(" ", strip=True).split())
        profile.has_blog         = self._has_section(soup, raw, ["blog", "/posts", "/articles", "/news"])
        profile.has_pricing      = self._has_section(soup, raw, ["pricing", "/plans", "/upgrade",
                                                                   "get started", "per month"])
        profile.has_free_trial   = bool(re.search(
            r"free trial|try for free|start free|no credit card", raw, re.I
        ))

        return profile

    # ── SEO ──────────────────────────────────────────────────────────────────

    def _extract_seo(self, soup: BeautifulSoup) -> SEOSnapshot:
        seo = SEOSnapshot()
        # Title
        seo.title = (soup.title.string or "").strip()[:200] if soup.title else ""
        # Description
        desc_tag  = soup.find("meta", attrs={"name": "description"})
        seo.description = (desc_tag.get("content", "") if desc_tag else "")[:300]
        # H1
        h1 = soup.find("h1")
        seo.h1 = h1.get_text(strip=True)[:150] if h1 else ""
        # Heading structure
        for level in range(1, 7):
            count = len(soup.find_all(f"h{level}"))
            if count:
                seo.h_structure[f"h{level}"] = count
        # Canonical
        canonical = soup.find("link", rel="canonical")
        seo.canonical = canonical.get("href", "") if canonical else ""
        # OG Image
        og_img = soup.find("meta", attrs={"property": "og:image"})
        seo.og_image = og_img.get("content", "") if og_img else ""
        # Schema.org
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "{}")
                schema_type = data.get("@type", "")
                if schema_type and schema_type not in seo.schema_types:
                    seo.schema_types.append(str(schema_type))
            except Exception:
                pass
        return seo

    # ── Third-party tools ─────────────────────────────────────────────────────

    def _detect_third_party(self, raw: str) -> list[str]:
        detected = []
        raw_lower = raw.lower()
        for pattern, name in _THIRD_PARTY_SIGNALS:
            if pattern in raw_lower and name not in detected:
                detected.append(name)
        return sorted(detected)

    # ── Social links ──────────────────────────────────────────────────────────

    def _extract_social_links(self, soup: BeautifulSoup, base_url: str) -> list[str]:
        found: set[str] = set()
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            for pattern, name in _SOCIAL_PATTERNS:
                if pattern in href:
                    found.add(name)
        return sorted(found)

    # ── Trust signals ─────────────────────────────────────────────────────────

    def _extract_trust_signals(self, soup: BeautifulSoup, raw: str) -> list[str]:
        signals = []
        trust_patterns = [
            (r"g2\.com|capterra\.com|trustpilot", "Third-party review platform"),
            (r"rated\s+[\d.]+\s+(out of|\/)\s*5",  "Star rating visible"),
            (r"(\d[\d,]+)\s+(customer|user|client|compan)", "User count social proof"),
            (r"featured in|as seen on|press",        "Press mentions section"),
            (r"soc\s*2|gdpr|hipaa|iso\s*27001",     "Compliance certification"),
            (r"money.back|refund guarantee",          "Money-back guarantee"),
            (r"ssl|secure payment|encrypted",        "Security badge"),
        ]
        raw_lower = raw.lower()
        for pattern, label in trust_patterns:
            if re.search(pattern, raw_lower, re.I) and label not in signals:
                signals.append(label)
        return signals

    # ── Contact methods ───────────────────────────────────────────────────────

    def _detect_contact_methods(self, soup: BeautifulSoup, raw: str) -> list[str]:
        methods = []
        raw_lower = raw.lower()
        if re.search(r"mailto:|@[\w.-]+\.\w+", raw): methods.append("Email")
        if "whatsapp.com" in raw_lower or "wa.me" in raw_lower: methods.append("WhatsApp")
        if "calendly.com" in raw_lower: methods.append("Calendly")
        if "typeform.com" in raw_lower or soup.find("form"): methods.append("Contact Form")
        if "tel:" in raw_lower: methods.append("Phone")
        if any(p in raw_lower for p in ["crisp", "intercom", "drift", "zendesk"]):
            methods.append("Live Chat")
        return methods

    # ── Language ──────────────────────────────────────────────────────────────

    def _detect_language(self, soup: BeautifulSoup) -> str:
        html_tag = soup.find("html")
        if html_tag:
            return html_tag.get("lang", "")[:10]
        return ""

    # ── Section detection ─────────────────────────────────────────────────────

    def _has_section(self, soup: BeautifulSoup, raw: str, keywords: list[str]) -> bool:
        raw_lower = raw.lower()
        return any(kw in raw_lower for kw in keywords)
