"""Export helpers for verified leads."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .models import Lead


def write_json(leads: list[Lead], path: Path) -> None:
    path.write_text(json.dumps([lead.model_dump(mode="json") for lead in leads], indent=2), encoding="utf-8")


def write_csv(leads: list[Lead], path: Path) -> None:
    fields = ["name", "category", "address", "phone", "website", "maps_url", "verification_score", "verification_status", "emails"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for lead in leads:
            writer.writerow(
                {
                    "name": lead.name,
                    "category": lead.category,
                    "address": lead.address,
                    "phone": lead.phone,
                    "website": lead.website or lead.contacts.website,
                    "maps_url": lead.maps_url,
                    "verification_score": lead.verification_score,
                    "verification_status": lead.verification_status,
                    "emails": ";".join(lead.contacts.emails),
                }
            )
