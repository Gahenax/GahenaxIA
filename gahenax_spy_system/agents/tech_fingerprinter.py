"""
gahenax_spy_system/agents/tech_fingerprinter.py
AGENT 1 — TechFingerprinter
Sigil: GATE — detecta el stack tecnológico pasivamente via headers + DOM.

Señales detectadas:
  • HTTP response headers (Server, X-Powered-By, CF-Ray, etc.)
  • HTML markers (__next_data__, ng-version, data-vue, data-reactroot)
  • JS/CSS asset patterns (chunk hashes, framework-specific bundles)
  • CDN, WAF, y proveedor de hosting
  • Analytics, chat widgets, y herramientas de pago
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from gahenax_spy_system.models import TechProfile, TechSignal
from gahenax_spy_system.utils import StealthHTTPClient


# 
#  DICCIONARIO DE SEÑALES (clave → {name, category, evidence_pattern})
#  Todos los patterns son búsquedas sobre el HTML + headers combinados.
# 

_HEADER_SIGNALS: list[tuple[str, str, str, float]] = [
    # (header_name, contains_value, tech_name, confidence)
    ("x-powered-by",    "next.js",          "Next.js",       0.99),
    ("x-powered-by",    "express",          "Express.js",    0.99),
    ("x-powered-by",    "php",              "PHP",           0.99),
    ("x-powered-by",    "asp.net",          "ASP.NET",       0.99),
    ("server",          "nginx",            "Nginx",         0.95),
    ("server",          "apache",           "Apache",        0.95),
    ("server",          "cloudflare",       "Cloudflare",    0.99),
    ("server",          "vercel",           "Vercel",        0.99),
    ("server",          "netlify",          "Netlify",       0.99),
    ("server",          "awselb",           "AWS ELB",       0.95),
    ("cf-ray",          "",                 "Cloudflare CDN",0.99),
    ("x-vercel-id",     "",                 "Vercel",        0.99),
    ("x-amz-cf-id",     "",                 "AWS CloudFront",0.99),
    ("x-cache",         "hit from cloudfront","AWS CloudFront",0.90),
    ("x-github-request-id","",              "GitHub Pages",  0.90),
    ("x-shopify-shop-api-call-limit","",    "Shopify",       0.99),
    ("cf-cache-status", "",                 "Cloudflare CDN",0.95),
]

_HTML_SIGNALS: list[tuple[str, str, str, str, float]] = [
    # (pattern_type, pattern, tech_name, category, confidence)
    # pattern_type: attr | id | class | data | script_src | meta | text
    ("data",   "__next_data__",        "Next.js",       "framework", 0.99),
    ("data",   "data-reactroot",       "React",         "framework", 0.95),
    ("data",   "data-gatsby",          "Gatsby",        "framework", 0.99),
    ("attr",   "ng-version",           "Angular",       "framework", 0.99),
    ("data",   "data-vue-app",         "Vue.js",        "framework", 0.95),
    ("data",   "data-svelte-h",        "Svelte",        "framework", 0.95),
    ("data",   "__nuxt",               "Nuxt.js",       "framework", 0.99),
    ("script_src", "wp-content",       "WordPress",     "cms",       0.99),
    ("script_src", "wp-includes",      "WordPress",     "cms",       0.99),
    ("meta",   "Shopify.theme",        "Shopify",       "cms",       0.99),
    ("script_src", "webflow.com",      "Webflow",       "cms",       0.99),
    ("script_src", "squarespace.com",  "Squarespace",   "cms",       0.99),
    ("script_src", "wixstatic.com",    "Wix",           "cms",       0.99),
    # Analytics
    ("script_src", "googletagmanager", "Google Analytics","analytics",0.99),
    ("script_src", "plausible.io",     "Plausible",     "analytics", 0.99),
    ("script_src", "hotjar.com",       "Hotjar",        "analytics", 0.99),
    ("script_src", "clarity.ms",       "MS Clarity",    "analytics", 0.99),
    ("script_src", "segment.com",      "Segment",       "analytics", 0.95),
    ("script_src", "mixpanel.com",     "Mixpanel",      "analytics", 0.95),
    # Payments
    ("script_src", "js.stripe.com",    "Stripe",        "payments",  0.99),
    ("script_src", "paypal.com",       "PayPal",        "payments",  0.99),
    ("script_src", "paddle.com",       "Paddle",        "payments",  0.99),
    # CSS Frameworks (via class patterns)
    ("class_pattern", r"\btw-\w|bg-\w+-\d{3}|text-\w+-\d{3}", "Tailwind CSS", "framework", 0.80),
    ("class_pattern", r"\bcol-md-|row\b|container-fluid", "Bootstrap",   "framework", 0.80),
    # WAF signals
    ("data",   "__cf_chl",             "Cloudflare WAF","waf",       0.99),
    ("script_src","challenges.cloudflare","Cloudflare WAF","waf",    0.99),
]


class TechFingerprinter:
    """
    Agente de detección de stack tecnológico.
    Analiza headers HTTP y el DOM HTML para construir un TechProfile.
    """

    def __init__(self, http: StealthHTTPClient | None = None):
        self._http = http or StealthHTTPClient()

    def run(self, url: str) -> TechProfile:
        profile = TechProfile(url=url)
        resp = self._http.get(url)

        if resp is None:
            return profile

        profile.has_https    = url.startswith("https://")
        profile.http_version = f"HTTP/{resp.http_version}" if hasattr(resp, "http_version") else ""
        profile.raw_headers  = dict(resp.headers)

        #  Header Analysis 
        headers_lower = {k.lower(): v.lower() for k, v in resp.headers.items()}
        self._analyze_headers(headers_lower, profile)

        #  HTML / DOM Analysis 
        if "text/html" in resp.headers.get("content-type", ""):
            soup = BeautifulSoup(resp.text, "lxml")
            self._analyze_html(soup, resp.text, profile)

        #  Compute summary fields 
        profile.frameworks = list({
            s.name for s in profile.signals
            if s.category in ("framework", "cms")
        })
        profile.analytics  = list({
            s.name for s in profile.signals if s.category == "analytics"
        })
        if profile.signals:
            profile.confidence_avg = round(
                sum(s.confidence for s in profile.signals) / len(profile.signals), 2
            )

        return profile

    #  Internal helpers 

    def _analyze_headers(self, headers: dict[str, str], profile: TechProfile) -> None:
        for header_name, contains, tech, confidence in _HEADER_SIGNALS:
            value = headers.get(header_name, "")
            if not value and header_name not in headers:
                continue
            if contains and contains not in value:
                continue

            # Deduplicate
            if any(s.name == tech for s in profile.signals):
                continue

            # Categorize
            category = self._categorize(tech)
            profile.signals.append(TechSignal(
                name=tech, category=category, confidence=confidence,
                evidence=f"Header '{header_name}': '{value[:60]}'"
            ))

            # Special: set top-level fields
            if "cloudflare" in tech.lower() and not profile.cdn:
                profile.cdn = "Cloudflare"
            elif "aws" in tech.lower() and not profile.cdn:
                profile.cdn = "AWS"
            if "vercel" in tech.lower():
                profile.cdn = profile.cdn or "Vercel"
            if "waf" in tech.lower() and not profile.waf:
                profile.waf = tech

        # Server & Powered-By
        profile.server     = headers.get("server", "")[:80]
        profile.powered_by = headers.get("x-powered-by", "")[:80]

    def _analyze_html(self, soup: BeautifulSoup, raw_html: str,
                      profile: TechProfile) -> None:
        # Pre-extract all script srcs (lowercase)
        script_srcs = [
            (s.get("src") or "").lower()
            for s in soup.find_all("script", src=True)
        ]
        # All classes in document (sample — first 5000 chars for performance)
        all_classes = " ".join(
            " ".join(el.get("class", []))
            for el in soup.find_all(class_=True)
        )

        for pattern_type, pattern, tech, category, confidence in _HTML_SIGNALS:
            if any(s.name == tech for s in profile.signals):
                continue  # Already detected

            hit   = False
            evid  = ""

            if pattern_type == "data":
                if pattern in raw_html:
                    hit  = True
                    evid = f"HTML marker: '{pattern}'"

            elif pattern_type == "attr":
                if soup.find(attrs={pattern: True}):
                    hit  = True
                    evid = f"DOM attribute: '{pattern}'"

            elif pattern_type == "script_src":
                matching = [s for s in script_srcs if pattern in s]
                if matching:
                    hit  = True
                    evid = f"Script src: '{matching[0][:80]}'"

            elif pattern_type == "class_pattern":
                if re.search(pattern, all_classes[:8000]):
                    hit  = True
                    evid = f"CSS class pattern: '{pattern}'"

            elif pattern_type == "meta":
                meta = soup.find("meta", attrs={"name": re.compile(pattern, re.I)})
                if meta:
                    hit  = True
                    evid = f"Meta tag: '{pattern}'"

            if hit:
                profile.signals.append(TechSignal(
                    name=tech, category=category,
                    confidence=confidence, evidence=evid
                ))
                if category == "cms" and not profile.cms:
                    profile.cms = tech

    @staticmethod
    def _categorize(tech: str) -> str:
        tech_l = tech.lower()
        if any(w in tech_l for w in ("waf", "shield")):          return "waf"
        if any(w in tech_l for w in ("cloudflare", "vercel", "netlify", "aws", "cdn")): return "cdn"
        if any(w in tech_l for w in ("stripe", "paypal", "paddle")): return "payments"
        if any(w in tech_l for w in ("analytics", "hotjar", "clarity",
                                      "plausible", "mixpanel", "segment")): return "analytics"
        if any(w in tech_l for w in ("wordpress", "shopify", "webflow",
                                      "squarespace", "wix")): return "cms"
        return "framework"
