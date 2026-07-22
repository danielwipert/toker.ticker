"""Block 0.2 — per-host endpoints for one model.

For open-weight models, price and quantization vary by host. This is the feed
the cheapest-qualifying filter (Block 1.3) will read. Dumps raw JSON and prints
each host's price + serving variant.

Usage:
    python ingestion/fetch_endpoints.py deepseek/deepseek-v3.2
"""

import datetime as dt
import json
import os
import pathlib
import sys

import httpx
from dotenv import load_dotenv

RAW_DIR = pathlib.Path(__file__).resolve().parent.parent / "data" / "raw"


def fetch_endpoints(model_id: str) -> dict:
    load_dotenv()
    key = os.environ.get("OPENROUTER_API_KEY", "")
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    url = f"https://openrouter.ai/api/v1/models/{model_id}/endpoints"
    resp = httpx.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    model_id = sys.argv[1] if len(sys.argv) > 1 else "deepseek/deepseek-v3.2"
    payload = fetch_endpoints(model_id)
    data = payload.get("data", payload)
    endpoints = data.get("endpoints", []) if isinstance(data, dict) else []

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    slug = model_id.replace("/", "__")
    out = RAW_DIR / f"endpoints_{slug}_{today}.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"model: {model_id}")
    print(f"hosts returned: {len(endpoints)}")
    print(f"raw JSON written to: {out}")
    print("\n--- per-host: provider | quantization | ctx | prompt$/tok | completion$/tok ---")
    for e in endpoints:
        pr = e.get("pricing", {})
        print(
            f"  {e.get('provider_name'):24} | quant={str(e.get('quantization')):8} "
            f"| ctx={e.get('context_length')} "
            f"| in={pr.get('prompt')} out={pr.get('completion')}"
        )
    print("\n--- one full endpoint record ---")
    if endpoints:
        print(json.dumps(endpoints[0], indent=2))


if __name__ == "__main__":
    main()
