# AI Lead Agent

AI Lead Agent is a free, no-paid-API-key lead-generation assistant that gathers and verifies business leads using OpenStreetMap, DuckDuckGo search results, public website signals, and optional local open-source model enrichment through Ollama.

The project is designed for responsible B2B prospecting: it avoids spam automation, keeps every lead traceable to source URLs, and produces a verification score instead of blindly exporting unqualified contacts.

## Capabilities

- **Free map discovery**: queries OpenStreetMap Nominatim for business names, categories, locations, websites, phones, and map URLs.
- **Free search discovery**: uses DuckDuckGo's lightweight HTML results to find official websites, company pages, directories, and public references without search API keys.
- **Open-source verification**: checks website availability and extracts lightweight public metadata such as page title, description, email addresses, and phone numbers.
- **Free enrichment**: uses a local Ollama model when available, otherwise falls back to deterministic offline heuristics.
- **Lead scoring**: assigns a transparent verification score based on source agreement, contact completeness, website health, and public-source corroboration.
- **Auditable exports**: writes JSON or CSV output with source evidence attached to every lead.

## Responsible-use guardrails

Use this tool only for lawful B2B prospecting and comply with applicable privacy, anti-spam, platform, and data-protection rules. The agent is built to prioritize official/public sources and evidence trails. Do not use it to collect sensitive personal data, evade website restrictions, or send unsolicited bulk messages.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

No paid API keys are required. Optional local-model enrichment can use Ollama:

```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
LEAD_AGENT_CONTACT_EMAIL=you@example.com
```

Run a lead search:

```bash
python -m lead_agent.cli \
  --query "dentists" \
  --location "Austin, TX" \
  --limit 10 \
  --output leads.json
```

CSV export:

```bash
python -m lead_agent.cli --query "roofing companies" --location "Denver, CO" --format csv --output leads.csv
```

## How verification works

Each lead receives a score from 0 to 100:

- OpenStreetMap identity and contact signals.
- Website availability and official-domain evidence.
- Public emails/phones found on official pages.
- Search-result corroboration from independent public sources.
- Optional local model or heuristic enrichment based only on collected evidence.

Scores are intentionally conservative. Review leads manually before outreach.

## Project structure

```text
lead_agent/
  cli.py          Command-line interface
  config.py       Environment and runtime settings
  models.py       Lead and evidence data models
  sources.py      OpenStreetMap, search engine, and website collectors
  verifier.py     Verification and scoring logic
  enrich.py       Free local/heuristic enrichment
  export.py       JSON/CSV exporters
```

## Notes

- OpenStreetMap/Nominatim and DuckDuckGo are free public services; use modest query volume and respect their usage policies.
- Add `LEAD_AGENT_CONTACT_EMAIL` so public services can identify responsible usage.
- Ollama enrichment is optional; without it, the agent still collects, verifies, scores, and heuristically enriches leads.
