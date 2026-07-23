"""Block 0.5 — the thesis probe.

The riskiest assumption in the whole spec: that we can read real token
consumption — including hidden reasoning tokens — back out of OpenRouter.
Prove it on one model before building anything around it.

Flow:
  1. POST a prompt to chat/completions (temperature 0, usage included).
  2. Read usage straight off the response.
  3. Fetch the generation record by id (with backoff) and read the
     native token counts + realized cost.

Usage:
    python battery/run_one.py <model_id> ["prompt"]
"""

import json
import os
import sys
import time

import httpx
from dotenv import load_dotenv

CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
GEN_URL = "https://openrouter.ai/api/v1/generation"

# A prompt that forces multi-step reasoning, so a reasoning model actually
# spends reasoning tokens rather than answering in one shot.
DEFAULT_PROMPT = (
    "A rope ladder hangs over the side of a ship. The rungs are 30 cm apart. "
    "At low tide, 10 rungs are above the water. The tide rises 15 cm per hour. "
    "After 3 hours, how many rungs are above the water? Explain your reasoning."
)


def key() -> str:
    load_dotenv()
    k = os.environ.get("OPENROUTER_API_KEY", "")
    if not k:
        sys.exit("OPENROUTER_API_KEY not set in .env")
    return k


def run(model_id: str, prompt: str) -> None:
    headers = {"Authorization": f"Bearer {key()}", "Content-Type": "application/json"}
    body = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "usage": {"include": True},
    }
    resp = httpx.post(CHAT_URL, headers=headers, json=body, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    gen_id = data.get("id")
    msg = data["choices"][0]["message"]
    answer = msg.get("content", "")
    reasoning_text = msg.get("reasoning") or ""
    usage = data.get("usage", {})

    print(f"model: {model_id}")
    print(f"generation id: {gen_id}")
    print("\n--- usage from the completion response ---")
    print(json.dumps(usage, indent=2))
    print(f"\nreasoning text present in response: {bool(reasoning_text)} "
          f"({len(reasoning_text)} chars)")
    print(f"answer (first 200 chars): {answer[:200]!r}")

    # Now the generation record — the spec's canonical source.
    print("\n--- generation record (polled with backoff) ---")
    gen = fetch_generation(gen_id, headers)
    if gen is None:
        print("generation record did not become available")
        return
    print(json.dumps(gen, indent=2))

    r = gen
    print("\n--- headline token counts ---")
    for field in (
        "native_tokens_prompt",
        "native_tokens_completion",
        "native_tokens_reasoning",
        "tokens_prompt",
        "tokens_completion",
        "total_cost",
    ):
        print(f"  {field:28} = {r.get(field)}")


def fetch_generation(gen_id: str, headers: dict) -> dict | None:
    for attempt in range(6):
        time.sleep(1.5 * (attempt + 1))  # simple backoff; record may lag
        try:
            g = httpx.get(GEN_URL, headers=headers, params={"id": gen_id}, timeout=30)
            if g.status_code == 404:
                continue
            g.raise_for_status()
            return g.json().get("data", g.json())
        except httpx.HTTPError:
            continue
    return None


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "nvidia/nemotron-3-super-120b-a12b:free"
    text = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_PROMPT
    run(model, text)
