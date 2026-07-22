"""Block 0.2 — first look at the OpenRouter feed.

GET the models endpoint, dump raw JSON to data/raw/, and print enough to
eyeball one record. No parsing logic yet: the point of this block is to see
the real shape of the data before writing ingestion against it.

Usage:
    python ingestion/fetch_models.py
"""

import datetime as dt
import json
import os
import pathlib

import httpx
from dotenv import load_dotenv

MODELS_URL = "https://openrouter.ai/api/v1/models"
RAW_DIR = pathlib.Path(__file__).resolve().parent.parent / "data" / "raw"


def fetch_models() -> dict:
    load_dotenv()
    key = os.environ.get("OPENROUTER_API_KEY", "")
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    resp = httpx.get(MODELS_URL, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    payload = fetch_models()
    models = payload.get("data", payload)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    out = RAW_DIR / f"models_{today}.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"models returned: {len(models)}")
    print(f"raw JSON written to: {out}")
    print("\n--- one full record, pretty-printed ---")
    print(json.dumps(models[0], indent=2))


if __name__ == "__main__":
    main()
