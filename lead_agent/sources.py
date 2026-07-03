"""Free collectors for OpenStreetMap, DuckDuckGo, and public website signals."""

from __future__ import annotations

import re
from html import unescape
from urllib.parse import urljoin, urlparse

import httpx

from .config import Settings
from .models import ContactSignal, Evidence, Lead

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
PHONE_RE = re.compile(r"(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}")
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
DESCRIPTION_RE = re.compile(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)', re.IGNORECASE)


class OpenStreetMapSource:
    """No-key business discovery using OpenStreetMap Nominatim search."""

    endpoint = "https://nominatim.openstreetmap.org/search"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def search(self, query: str, location: str, limit: int) -> list[Lead]:
        headers = {"User-Agent": self.settings.user_agent}
        params = {
            "q": f"{query} {location}",
            "format": "jsonv2",
            "addressdetails": 1,
            "extratags": 1,
            "namedetails": 1,
            "limit": limit,
        }
        with httpx.Client(timeout=self.settings.request_timeout_seconds, headers=headers) as client:
            response = client.get(self.endpoint, params=params)
            response.raise_for_status()
            results = response.json()[:limit]

        leads: list[Lead] = []
        for item in results:
            extratags = item.get("extratags", {}) or {}
            address = item.get("address", {}) or {}
            name = item.get("namedetails", {}).get("name") or item.get("name") or item.get("display_name", "Unknown business").split(",")[0]
            osm_type = item.get("osm_type")
            osm_id = item.get("osm_id")
            osm_url = f"https://www.openstreetmap.org/{osm_type}/{osm_id}" if osm_type and osm_id else None
            lead = Lead(
                name=name,
                category=item.get("type") or item.get("class"),
                address=item.get("display_name"),
                locality=address.get("city") or address.get("town") or address.get("village") or address.get("county"),
                phone=extratags.get("phone") or extratags.get("contact:phone"),
                website=extratags.get("website") or extratags.get("contact:website"),
                maps_url=osm_url,
            )
            lead.add_evidence(
                Evidence(
                    source="openstreetmap",
                    url=osm_url,
                    label="OpenStreetMap Nominatim result",
                    details={"osm_type": osm_type, "osm_id": osm_id, "class": item.get("class"), "type": item.get("type")},
                )
            )
            leads.append(lead)
        return leads


class SearchEngineSource:
    """No-key search discovery using DuckDuckGo's lightweight HTML endpoint."""

    endpoint = "https://duckduckgo.com/html/"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def evidence_for(self, lead: Lead, location: str, max_results: int = 5) -> list[Evidence]:
        headers = {"User-Agent": self.settings.user_agent}
        params = {"q": f'"{lead.name}" "{location}" official website contact'}
        with httpx.Client(timeout=self.settings.request_timeout_seconds, headers=headers, follow_redirects=True) as client:
            response = client.get(self.endpoint, params=params)
            response.raise_for_status()
        return self._parse_results(response.text, max_results)

    @staticmethod
    def _parse_results(html: str, max_results: int) -> list[Evidence]:
        results: list[Evidence] = []
        blocks = re.findall(r'<div[^>]+class=["\'][^"\']*result[^"\']*["\'][^>]*>(.*?)</div>\s*</div>', html, re.IGNORECASE | re.DOTALL)
        if not blocks:
            blocks = html.split('class="result"')
        for block in blocks:
            link_match = re.search(r'<a[^>]+class=["\'][^"\']*result__a[^"\']*["\'][^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', block, re.IGNORECASE | re.DOTALL)
            if not link_match:
                continue
            snippet_match = re.search(r'<a[^>]+class=["\'][^"\']*result__snippet[^"\']*["\'][^>]*>(.*?)</a>|<div[^>]+class=["\'][^"\']*result__snippet[^"\']*["\'][^>]*>(.*?)</div>', block, re.IGNORECASE | re.DOTALL)
            label = SearchEngineSource._clean_html(link_match.group(2)) or "DuckDuckGo result"
            snippet_html = next((group for group in (snippet_match.groups() if snippet_match else ()) if group), None)
            results.append(
                Evidence(
                    source="search_engine",
                    url=unescape(link_match.group(1)),
                    label=label,
                    details={"snippet": SearchEngineSource._clean_html(snippet_html) if snippet_html else None},
                )
            )
            if len(results) >= max_results:
                break
        return results

    @staticmethod
    def _clean_html(value: str | None) -> str | None:
        if not value:
            return None
        text = re.sub(r"<[^>]+>", " ", value)
        return re.sub(r"\s+", " ", unescape(text)).strip()


class WebsiteSource:
    """Fetches public website metadata and contact signals without paid services."""

    contact_paths = ("/contact", "/contact-us", "/about", "/about-us")

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def inspect(self, url: str | None) -> tuple[ContactSignal, Evidence | None]:
        if not url:
            return ContactSignal(), None

        normalized = self._normalize_url(url)
        headers = {"User-Agent": self.settings.user_agent}
        try:
            with httpx.Client(timeout=self.settings.request_timeout_seconds, follow_redirects=True, headers=headers) as client:
                response = client.get(normalized)
                response.raise_for_status()
                html_parts = [response.text[:250_000]]
                for path in self.contact_paths:
                    contact_url = urljoin(str(response.url), path)
                    try:
                        contact_response = client.get(contact_url)
                        if contact_response.status_code < 400:
                            html_parts.append(contact_response.text[:100_000])
                    except httpx.HTTPError:
                        continue
        except httpx.HTTPError as exc:
            return ContactSignal(website=normalized), Evidence(
                source="website",
                url=normalized,
                label="Website unavailable or blocked",
                details={"error": str(exc)},
            )

        html = "\n".join(html_parts)
        title = self._first_match(TITLE_RE, html)
        description = self._first_match(DESCRIPTION_RE, html)
        emails = sorted(set(EMAIL_RE.findall(html)))[:10]
        phones = sorted(set(PHONE_RE.findall(html)))[:10]
        evidence = Evidence(
            source="website",
            url=str(response.url),
            label="Public website metadata and contact signals",
            details={"title": title, "description": description, "domain": urlparse(str(response.url)).netloc},
        )
        return ContactSignal(emails=emails, phones=phones, website=str(response.url)), evidence

    @staticmethod
    def _normalize_url(url: str) -> str:
        return url if url.startswith(("http://", "https://")) else f"https://{url}"

    @staticmethod
    def _first_match(pattern: re.Pattern[str], text: str) -> str | None:
        match = pattern.search(text)
        return re.sub(r"\s+", " ", match.group(1)).strip() if match else None
