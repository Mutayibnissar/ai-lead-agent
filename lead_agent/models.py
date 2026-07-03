"""Shared data models for collected and verified leads."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """A public source used to support a lead field or score."""

    source: str
    url: str | None = None
    label: str
    details: dict[str, Any] = Field(default_factory=dict)
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ContactSignal(BaseModel):
    """Public contact details discovered for a business."""

    emails: list[str] = Field(default_factory=list)
    phones: list[str] = Field(default_factory=list)
    website: str | None = None


class Lead(BaseModel):
    """A business lead with traceable evidence and verification metadata."""

    name: str
    category: str | None = None
    address: str | None = None
    locality: str | None = None
    phone: str | None = None
    website: str | None = None
    maps_url: str | None = None
    rating: float | None = None
    review_count: int | None = None
    contacts: ContactSignal = Field(default_factory=ContactSignal)
    evidence: list[Evidence] = Field(default_factory=list)
    verification_score: int = 0
    verification_status: Literal["unverified", "needs_review", "verified"] = "unverified"
    enrichment: dict[str, Any] = Field(default_factory=dict)

    def add_evidence(self, evidence: Evidence) -> None:
        self.evidence.append(evidence)
