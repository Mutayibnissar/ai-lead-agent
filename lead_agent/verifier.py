"""Lead verification and scoring."""

from __future__ import annotations

from urllib.parse import urlparse

from .models import Lead


def score_lead(lead: Lead) -> Lead:
    """Assign a conservative verification score to a lead in place."""

    score = 0
    sources = {item.source for item in lead.evidence}

    if "openstreetmap" in sources:
        score += 25
    if "search_engine" in sources:
        score += 15
    if "website" in sources and lead.contacts.website:
        score += 20
    if lead.phone or lead.contacts.phones:
        score += 10
    if lead.contacts.emails:
        score += 10
    if lead.rating and lead.review_count:
        score += min(10, int(lead.review_count / 10) + (3 if lead.rating >= 4 else 0))
    if _has_official_domain_match(lead):
        score += 10

    lead.verification_score = min(score, 100)
    if lead.verification_score >= 70:
        lead.verification_status = "verified"
    elif lead.verification_score >= 40:
        lead.verification_status = "needs_review"
    else:
        lead.verification_status = "unverified"
    return lead


def _has_official_domain_match(lead: Lead) -> bool:
    website = lead.website or lead.contacts.website
    if not website:
        return False
    domain = urlparse(website).netloc.lower().removeprefix("www.")
    if not domain:
        return False
    return any(domain in (evidence.url or "").lower() for evidence in lead.evidence)
