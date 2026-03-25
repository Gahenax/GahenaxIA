"""
gahenax_spy_system/utils/http_client.py
Cliente HTTP stealth para el sistema spy.
Sigil: GATE — controla y valida todo el acceso de red.
"""
from __future__ import annotations

import random
import time
import urllib.robotparser
from typing import Optional
from urllib.parse import urlparse, urljoin

import httpx

# Pool de User-Agents realistas (rotación)
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]

_BASE_HEADERS = {
    "Accept":           "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language":  "en-US,en;q=0.9,es;q=0.8",
    "Accept-Encoding":  "gzip, deflate, br",
    "Cache-Control":    "no-cache",
    "Sec-Fetch-Dest":   "document",
    "Sec-Fetch-Mode":   "navigate",
    "Sec-Fetch-Site":   "none",
    "Sec-Fetch-User":   "?1",
    "Upgrade-Insecure-Requests": "1",
}


class StealthHTTPClient:
    """
    Cliente HTTP con comportamiento de browser real.
    - Rotación de User-Agents
    - Headers de navegador legítimos
    - Retry con backoff exponencial (3 intentos)
    - Rate limiting integrado (delay configurable)
    - Respeta robots.txt
    """

    def __init__(self, timeout: int = 15, delay: float = 1.2, verbose: bool = False, proxy: Optional[str] = None, ignore_robots: bool = False):
        self.timeout  = timeout
        self.delay    = delay
        self.verbose  = verbose
        self.proxy    = proxy
        self.ignore_robots = ignore_robots
        self._last_request: float = 0.0
        self._robots_cache: dict[str, urllib.robotparser.RobotFileParser] = {}

    def _get_headers(self) -> dict:
        h = dict(_BASE_HEADERS)
        h["User-Agent"] = random.choice(_USER_AGENTS)
        if self.proxy and "127.0.0.1" in self.proxy: # Probable Tor
             h["Accept-Language"] = "en-US,en;q=0.5" # Tor browser typical
        return h

    def _rate_limit(self) -> None:
        elapsed = time.time() - self._last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed + random.uniform(0.1, 0.4))
        self._last_request = time.time()

    def _can_fetch(self, url: str) -> bool:
        """Verifica robots.txt antes de hacer fetch."""
        if self.ignore_robots:
            return True
            
        # Si es .onion o Tor, a veces robots.txt no es accesible o deseado
        if ".onion" in url.lower():
            return True
        parsed = urlparse(url)
        base   = f"{parsed.scheme}://{parsed.netloc}"
        if base not in self._robots_cache:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(urljoin(base, "/robots.txt"))
            try:
                rp.read()
            except Exception:
                pass
            self._robots_cache[base] = rp
        return self._robots_cache[base].can_fetch("*", url)

    def get(self, url: str, retries: int = 3,
            follow_redirects: bool = True) -> httpx.Response | None:
        """
        GET con retry exponencial. Respeta robots.txt y rate limit.
        Retorna None si la URL está bloqueada o todos los intentos fallan.
        """
        if not self._can_fetch(url):
            if self.verbose:
                print(f"  [robots.txt BLOCK] {url}")
            return None

        for attempt in range(retries):
            self._rate_limit()
            try:
                # Configure proxies if available
                proxies = None
                if self.proxy:
                    # httpx expects a dict for proxies or a single string for all
                    proxies = {"all://": self.proxy}

                with httpx.Client(
                    timeout=self.timeout,
                    follow_redirects=follow_redirects,
                    verify=False,        # Ignora SSL inválido en targets legacy
                    proxy=self.proxy,   # Simplified proxy pass
                ) as client:
                    resp = client.get(url, headers=self._get_headers())
                    if self.verbose:
                        print(f"  [{resp.status_code}] {url}")
                    return resp
            except (httpx.TimeoutException, httpx.ConnectError, httpx.RemoteProtocolError) as e:
                wait = (2 ** attempt) + random.uniform(0, 1)
                if self.verbose:
                    print(f"  [retry {attempt+1}/{retries}] {url} — {e} — wait {wait:.1f}s")
                if attempt < retries - 1:
                    time.sleep(wait)
        return None

    def get_robots(self, base_url: str) -> tuple[bool, list[str]]:
        """Descarga y parsea robots.txt. Retorna (existe, disallowed_paths)."""
        parsed   = urlparse(base_url)
        base     = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = urljoin(base, "/robots.txt")
        resp = self.get(robots_url, retries=1)
        if not resp or resp.status_code != 200:
            return False, []
        disallowed = [
            line.split(":", 1)[1].strip()
            for line in resp.text.splitlines()
            if line.lower().startswith("disallow:")
        ]
        return True, disallowed
