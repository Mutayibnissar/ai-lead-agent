"""Free lead enrichment using either local Ollama or offline heuristics."""

from __future__ import annotations

import json

import httpx

from .config import Settings
from .models import Lead


class FreeEnricher:
    """Enrich leads without paid API keys.

    If `OLLAMA_BASE_URL` is configured and reachable, the class asks a local
    open-source model for a concise JSON enrichment. Otherwise it falls back to
    deterministic heuristics so the agent remains fully usable offline.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def enrich(self, lead: Lead, target_customer: str | None = None) -> Lead:
        if self.settings.ollama_base_url:
            enriched = self._try_ollama(lead, target_customer)
            if enriched:
                lead.enrichment = enriched
                return lead

        lead.enrichment = self._heuristic_enrichment(lead, target_customer)
        return lead

    def _try_ollama(self, lead: Lead, target_customer: str | None) -> dict[str, str] | None:
        evidence = [
            {"source": item.source, "url": item.url, "label": item.label, "details": item.details}
            for item in lead.evidence
        ]
        payload = {
            "model": self.settings.ollama_model,
            "stream": False,
            "prompt": (
                "You enrich B2B leads only from provided evidence. Do not invent facts. "
                "Return compact JSON with keys summary, likely_fit, outreach_angle, missing_verification.\n"
                + json.dumps({"lead": lead.model_dump(exclude={"evidence", "enrichment"}), "target_customer": target_customer, "evidence": evidence}, default=str)
            ),
        }
        try:
            with httpx.Client(timeout=self.settings.request_timeout_seconds) as client:
                response = client.post(f"{self.settings.ollama_base_url.rstrip('/')}/api/generate", json=payload)
                response.raise_for_status()
        except httpx.HTTPError:
            return None

        text = response.json().get("response", "").strip()
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return {"summary": text, "likely_fit": "needs_review", "outreach_angle": "Review sourced evidence before outreach.", "missing_verification": "Local model returned non-JSON text."}
        return {str(key): str(value) for key, value in parsed.items()}

    @staticmethod
    def _heuristic_enrichment(lead: Lead, target_customer: str | None) -> dict[str, str]:
        contact_bits = []
        if lead.contacts.emails:
            contact_bits.append("public email")
        if lead.phone or lead.contacts.phones:
            contact_bits.append("phone")
        if lead.website or lead.contacts.website:
            contact_bits.append("website")
        contacts = ", ".join(contact_bits) if contact_bits else "limited public contact data"
        fit = "good" if lead.verification_score >= 70 else "needs_review" if lead.verification_score >= 40 else "low"
        target = f" for {target_customer}" if target_customer else ""
        return {
            "summary": f"{lead.name} appears to be a {lead.category or 'business'} in {lead.locality or lead.address or 'the target area'} with {contacts}.",
            "likely_fit": fit,
            "outreach_angle": f"Reference the verified public business context{target} and keep outreach specific and compliant.",
            "missing_verification": "Manually confirm decision-maker identity and consent requirements before outreach.",
        }
