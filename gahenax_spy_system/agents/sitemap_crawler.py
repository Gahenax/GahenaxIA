"""
gahenax_spy_system/agents/sitemap_crawler.py
AGENT 5 — SitemapCrawler
Sigil: CHAIN — mapea la arquitectura de información del sitio.

Estrategias (en orden):
  1. sitemap.xml — descarga y parsea todos los <loc> entries
  2. robots.txt  — extrae Sitemap: directivas y Disallow paths
  3. BFS link crawling — si no hay sitemap.xml, rastrea links desde la home
     (máximo depth=2, máximo 50 URLs)

Clasifica cada URL en tipos de página:
  landing | blog | product | docs | auth | about | legal | other
"""
from __future__ import annotations

import re
from collections import deque
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from gahenax_spy_system.models import SiteMap, SitePage
from gahenax_spy_system.utils import StealthHTTPClient


_PAGE_TYPE_RULES: list[tuple[str, str]] = [
    # (url_pattern, page_type)
    (r"/blog|/posts|/articles|/news", "blog"),
    (r"/docs|/documentation|/api|/reference|/sdk|/guides", "docs"),
    (r"/pricing|/plans|/upgrade|/subscribe", "pricing"),
    (r"/login|/signin|/signup|/register|/auth|/oauth", "auth"),
    (r"/about|/team|/company|/mission|/story", "about"),
    (r"/privacy|/terms|/legal|/cookies|/gdpr", "legal"),
    (r"/product|/features|/solutions|/platform", "product"),
    (r"/contact|/support|/help|/faq", "support"),
]


class SitemapCrawler:
    """
    Agente de mapeo de arquitectura de información.
    Combina sitemap.xml + robots.txt + BFS crawling.
    """

    def __init__(self, http: StealthHTTPClient | None = None, max_depth: int = 2):
        self._http      = http or StealthHTTPClient()
        self._max_depth = max_depth

    def run(self, url: str) -> SiteMap:
        parsed   = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        sitemap  = SiteMap(root_url=url)

        # Step 1: robots.txt
        has_robots, disallowed = self._http.get_robots(base_url)
        sitemap.has_robots_txt = has_robots
        sitemap.disallowed = disallowed[:20]

        # Step 2: Attempt sitemap.xml
        sitemap_urls = self._discover_sitemap_urls(base_url, disallowed)
        if sitemap_urls:
            sitemap.has_sitemap_xml = True
            pages = self._parse_sitemap_xml(sitemap_urls[:3], base_url)
        else:
            # Step 3: BFS crawl fallback
            pages = self._bfs_crawl(url, base_url)

        sitemap.pages            = pages[:80]
        sitemap.total_urls       = len(sitemap.pages)
        sitemap.max_depth_reached = max((p.depth for p in sitemap.pages), default=0)
        sitemap.languages        = self._detect_languages(sitemap.pages)

        return sitemap

    #  Sitemap XML 

    def _discover_sitemap_urls(self, base_url: str, disallowed: list[str]) -> list[str]:
        candidates = [
            f"{base_url}/sitemap.xml",
            f"{base_url}/sitemap_index.xml",
            f"{base_url}/sitemap-index.xml",
            f"{base_url}/sitemaps/sitemap.xml",
        ]
        # Check robots.txt for Sitemap: directive
        resp_robots = self._http.get(f"{base_url}/robots.txt", retries=1)
        if resp_robots and resp_robots.status_code == 200:
            for line in resp_robots.text.splitlines():
                if line.lower().startswith("sitemap:"):
                    sm_url = line.split(":", 1)[1].strip()
                    if sm_url not in candidates:
                        candidates.insert(0, sm_url)

        valid = []
        for url in candidates:
            resp = self._http.get(url, retries=1)
            if resp and resp.status_code == 200 and "xml" in resp.headers.get("content-type", ""):
                valid.append(url)
                break  # Use first valid sitemap
        return valid

    def _parse_sitemap_xml(self, sitemap_urls: list[str], base: str) -> list[SitePage]:
        pages: list[SitePage] = []
        for sm_url in sitemap_urls:
            resp = self._http.get(sm_url)
            if not resp:
                continue
            soup = BeautifulSoup(resp.text, "lxml-xml")
            # sitemap index — recurse into sub-sitemaps
            sitemapindex = soup.find_all("sitemap")
            if sitemapindex:
                sub_locs = [s.find("loc").text for s in sitemapindex[:5] if s.find("loc")]
                pages.extend(self._parse_sitemap_xml(sub_locs, base))
                continue
            # Regular sitemap
            for url_el in soup.find_all("url")[:60]:
                loc = url_el.find("loc")
                if loc:
                    loc_text = loc.text.strip()
                    pages.append(SitePage(
                        url       = loc_text,
                        page_type = self._classify_url(loc_text),
                        depth     = 1,
                    ))
        return pages

    #  BFS Crawl 

    def _bfs_crawl(self, start_url: str, base_url: str) -> list[SitePage]:
        visited: set[str] = set()
        queue   = deque([(start_url, 0)])
        pages:  list[SitePage] = []

        while queue and len(pages) < 50:
            url, depth = queue.popleft()
            if url in visited or depth > self._max_depth:
                continue
            visited.add(url)

            resp = self._http.get(url)
            if not resp or resp.status_code != 200:
                continue
            if "text/html" not in resp.headers.get("content-type", ""):
                continue

            soup  = BeautifulSoup(resp.text, "lxml")
            title = (soup.title.string or "").strip()[:100] if soup.title else ""
            lang  = soup.find("html").get("lang", "") if soup.find("html") else ""

            pages.append(SitePage(
                url=url, depth=depth, title=title, lang=lang,
                page_type=self._classify_url(url),
            ))

            # Enqueue child links (same domain only)
            if depth < self._max_depth:
                for a in soup.find_all("a", href=True):
                    href = self._normalize_url(a["href"], base_url, url)
                    if href and href.startswith(base_url) and href not in visited:
                        queue.append((href, depth + 1))

        return pages

    #  Helpers 

    def _classify_url(self, url: str) -> str:
        url_lower = url.lower()
        for pattern, page_type in _PAGE_TYPE_RULES:
            if re.search(pattern, url_lower):
                return page_type
        return "landing" if url.rstrip("/").count("/") <= 1 else "other"

    def _normalize_url(self, href: str, base_url: str, current: str) -> str | None:
        try:
            if href.startswith(("#", "javascript:", "mailto:", "tel:")):
                return None
            full = urljoin(current, href)
            parsed = urlparse(full)
            # Strip fragments and query strings for deduplication
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/") or None
        except Exception:
            return None

    def _detect_languages(self, pages: list[SitePage]) -> list[str]:
        langs = set()
        for p in pages:
            if p.lang:
                langs.add(p.lang[:5])
            # URL pattern: /es/, /en/, /fr/
            m = re.search(r"/([a-z]{2})(?:/|$)", p.url)
            if m:
                langs.add(m.group(1))
        return sorted(langs)
