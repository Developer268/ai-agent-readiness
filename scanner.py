"""
scanner.py — AI Agent Readiness Scanner
Fetches and analyses key agent-readiness signals from a given domain.
"""

import asyncio
import re
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass, field
from typing import Optional

import httpx
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "AIAgentReadinessBot/1.0 (+https://github.com/Developer268/ai-agent-readiness)"
}
TIMEOUT = 10.0


@dataclass
class ScanResult:
    domain: str
    robots_txt_present: bool = False
    robots_txt_allows_agents: bool = False
    sitemap_present: bool = False
    llms_txt_present: bool = False
    link_header_present: bool = False
    oauth_metadata_present: bool = False
    api_catalog_present: bool = False
    markdown_available: bool = False
    errors: list = field(default_factory=list)


def normalise_url(domain: str) -> str:
    """Ensure the domain has a scheme."""
    if not domain.startswith(("http://", "https://")):
        domain = "https://" + domain
    parsed = urlparse(domain)
    return f"{parsed.scheme}://{parsed.netloc}"


async def fetch(client: httpx.AsyncClient, url: str) -> Optional[httpx.Response]:
    """Safe GET with timeout; returns None on error."""
    try:
        resp = await client.get(url, timeout=TIMEOUT, follow_redirects=True)
        return resp
    except Exception as exc:
        return None


async def check_robots_txt(client: httpx.AsyncClient, base: str, result: ScanResult):
    resp = await fetch(client, urljoin(base, "/robots.txt"))
    if resp and resp.status_code == 200:
        result.robots_txt_present = True
        text = resp.text.lower()
        # Check if AI agents / all bots are allowed
        disallow_all = re.search(r"user-agent:\s*\*.*?disallow:\s*/", text, re.DOTALL)
        result.robots_txt_allows_agents = disallow_all is None


async def check_sitemap(client: httpx.AsyncClient, base: str, result: ScanResult):
    # Check sitemap.xml directly
    resp = await fetch(client, urljoin(base, "/sitemap.xml"))
    if resp and resp.status_code == 200:
        result.sitemap_present = True
        return
    # Also check robots.txt for Sitemap: directive
    resp2 = await fetch(client, urljoin(base, "/robots.txt"))
    if resp2 and "sitemap:" in resp2.text.lower():
        result.sitemap_present = True


async def check_llms_txt(client: httpx.AsyncClient, base: str, result: ScanResult):
    resp = await fetch(client, urljoin(base, "/llms.txt"))
    if resp and resp.status_code == 200 and len(resp.text) > 10:
        result.llms_txt_present = True


async def check_link_header(client: httpx.AsyncClient, base: str, result: ScanResult):
    resp = await fetch(client, base)
    if resp:
        link = resp.headers.get("link", "")
        if link:
            result.link_header_present = True


async def check_oauth_metadata(client: httpx.AsyncClient, base: str, result: ScanResult):
    # RFC 8414 — /.well-known/oauth-authorization-server
    urls = [
        urljoin(base, "/.well-known/oauth-authorization-server"),
        urljoin(base, "/.well-known/openid-configuration"),
    ]
    for url in urls:
        resp = await fetch(client, url)
        if resp and resp.status_code == 200:
            result.oauth_metadata_present = True
            return


async def check_api_catalog(client: httpx.AsyncClient, base: str, result: ScanResult):
    # RFC 9727 — /.well-known/api-catalog
    resp = await fetch(client, urljoin(base, "/.well-known/api-catalog"))
    if resp and resp.status_code == 200:
        result.api_catalog_present = True


async def check_markdown(client: httpx.AsyncClient, base: str, result: ScanResult):
    """Check if the server accepts text/markdown via Accept header."""
    try:
        resp = await client.get(
            base,
            headers={**HEADERS, "Accept": "text/markdown"},
            timeout=TIMEOUT,
            follow_redirects=True,
        )
        ct = resp.headers.get("content-type", "")
        if "markdown" in ct:
            result.markdown_available = True
    except Exception:
        pass


async def scan(domain: str) -> ScanResult:
    """Run all checks concurrently and return a ScanResult."""
    base = normalise_url(domain)
    result = ScanResult(domain=domain)

    async with httpx.AsyncClient(headers=HEADERS) as client:
        await asyncio.gather(
            check_robots_txt(client, base, result),
            check_sitemap(client, base, result),
            check_llms_txt(client, base, result),
            check_link_header(client, base, result),
            check_oauth_metadata(client, base, result),
            check_api_catalog(client, base, result),
            check_markdown(client, base, result),
        )

    return result
