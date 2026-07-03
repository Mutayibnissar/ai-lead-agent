"""Runtime configuration for the free lead-generation agent."""

from __future__ import annotations

import os
from dataclasses import dataclass



@dataclass(frozen=True)
class Settings:
    """Environment-backed settings that do not require paid API keys."""

    ollama_base_url: str | None
    ollama_model: str
    contact_email: str | None
    request_timeout_seconds: float = 20.0

    @property
    def user_agent(self) -> str:
        suffix = f" ({self.contact_email})" if self.contact_email else ""
        return f"AILeadAgent/0.2 free-open-source-prospecting{suffix}"

    @classmethod
    def from_env(cls) -> "Settings":
        _load_dotenv()
        return cls(
            ollama_base_url=os.getenv("OLLAMA_BASE_URL") or None,
            ollama_model=os.getenv("OLLAMA_MODEL") or "llama3.1:8b",
            contact_email=os.getenv("LEAD_AGENT_CONTACT_EMAIL") or None,
        )


def _load_dotenv(path: str = ".env") -> None:
    """Load simple KEY=VALUE pairs without requiring python-dotenv."""

    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("'\""))
