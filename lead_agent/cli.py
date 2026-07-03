"""Command-line entry point for AI Lead Agent."""

from __future__ import annotations

import argparse
from pathlib import Path

from .config import Settings
from .enrich import FreeEnricher
from .export import write_csv, write_json
from .models import Lead
from .sources import OpenStreetMapSource, SearchEngineSource, WebsiteSource
from .verifier import score_lead


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate verified B2B leads from free open sources and optional local-model enrichment.")
    parser.add_argument("--query", required=True, help="Business category or search phrase, e.g. 'dentists'.")
    parser.add_argument("--location", required=True, help="Target city/region, e.g. 'Austin, TX'.")
    parser.add_argument("--limit", type=int, default=10, help="Maximum OpenStreetMap leads to collect.")
    parser.add_argument("--target-customer", help="Optional ICP context for free local/heuristic enrichment.")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Export format.")
    parser.add_argument("--output", type=Path, default=Path("leads.json"), help="Output file path.")
    return parser


def generate_leads(query: str, location: str, limit: int, target_customer: str | None = None) -> list[Lead]:
    settings = Settings.from_env()
    places = OpenStreetMapSource(settings)
    search = SearchEngineSource(settings)
    websites = WebsiteSource(settings)
    enricher = FreeEnricher(settings)

    leads = places.search(query=query, location=location, limit=limit)
    if not leads:
        raise SystemExit("No OpenStreetMap leads collected. Try a broader query/location or verify network access.")

    for lead in leads:
        for evidence in search.evidence_for(lead, location):
            lead.add_evidence(evidence)
            if not lead.website and evidence.url:
                lead.website = evidence.url

        contacts, website_evidence = websites.inspect(lead.website)
        lead.contacts = contacts
        if contacts.website and not lead.website:
            lead.website = contacts.website
        if website_evidence:
            lead.add_evidence(website_evidence)

        score_lead(lead)
        enricher.enrich(lead, target_customer=target_customer)

    return sorted(leads, key=lambda item: item.verification_score, reverse=True)


def main() -> None:
    args = build_parser().parse_args()
    leads = generate_leads(args.query, args.location, args.limit, args.target_customer)
    if args.format == "csv":
        write_csv(leads, args.output)
    else:
        write_json(leads, args.output)
    print(f"Wrote {len(leads)} leads to {args.output}")


if __name__ == "__main__":
    main()
