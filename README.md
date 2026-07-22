# TokenTicker

The authoritative cost-and-performance tracker for AI models — what each model
actually costs to do the job, measured (not borrowed).

*Chorus AI Systems · Daniel Wipert*

## Two rules that constrain everything

1. **Price comes from OpenRouter and nowhere else.** No other source touches a price field.
2. **No invented numbers.** A missing measurement shows as "awaiting measurement,"
   never a default or estimate.

## Layout

| Dir | Purpose |
| --- | --- |
| `schemas/` | Pydantic entities — the contract between modules |
| `ingestion/` | Price / capability / speed ingestion |
| `battery/` | The owned cost battery (tokens + cost via OpenRouter) |
| `generator/` | Procedural, seeded task generation |
| `grading/` | Deterministic graders + sandbox |
| `derive/` | Deterministic value, labels, snapshots (no LLM) |
| `site/` | Static site generation |
| `data/` | Immutable dated JSON snapshots |
| `docs/` | `DECISIONS.md` and methodology notes |
| `planning/` | Product spec, amendment, build plan |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then add your OPENROUTER_API_KEY
pytest
```

Current status: **Phase 0 — scaffolding.** See `planning/TokenTicker_Build_Plan_v2.md`.
