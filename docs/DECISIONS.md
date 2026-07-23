# Decisions Log

Append-only. Every decision from Phase 0 onward gets one line with a date.
Newest at the bottom.

---

- **2026-07-22** — Repo scaffolded (Block 0.1). Directory layout, `requirements.txt`,
  `.env` template, root `conftest.py` to anchor imports, and the `test_import.py`
  smoke test in place.
- **2026-07-22** — Build plan reconciled to Spec v4 + Amendment v4.2
  (`planning/TokenTicker_Build_Plan_v2.md`). Building against v4.2: deterministic
  grading and `success_rate` at MVP (A6/A14), three MVP categories (A7), procedural
  task generation (A8), `N` set by calibration study (A9), single unified view (A1).
- **2026-07-22** — Remote set to `github.com/danielwipert/toker.ticker`.
- **2026-07-22** — Block 0.2 done. OpenRouter feed inspected (342 models, 152
  open-weight). Field paths confirmed from real data:

  **Models list** — `GET /api/v1/models`, array under `data[]`:
  | Need | Field path | Note |
  |---|---|---|
  | Input price | `pricing.prompt` | USD **per token**, as a string. ×1e6 for $/M. |
  | Output price | `pricing.completion` | same units |
  | Cache-read price | `pricing.input_cache_read` | relevant to A6 cache-disable discipline |
  | Context | `context_length` (also `top_provider.context_length`) | |
  | Max output | `top_provider.max_completion_tokens` | |
  | Alias id | `id` (e.g. `deepseek/deepseek-v3.2`) | the moving handle |
  | **Pinned id (A12)** | `canonical_slug` (e.g. `…-20251201`) | date-stamped; this is the roster key |
  | Open-weight signal | `hugging_face_id` present | 152/342 have it |
  | Modality | `architecture.modality`, `architecture.input_modalities` | |
  | Reasoning-capable | `supported_parameters` contains `reasoning`/`include_reasoning`; `reasoning{mandatory,default_enabled}` | tells us which models can emit reasoning tokens (Block 0.5) |

  **Endpoints (per host)** — `GET /api/v1/models/{id}/endpoints`, `data.endpoints[]`:
  | Need | Field path | Note |
  |---|---|---|
  | Per-host in/out price | `pricing.prompt` / `pricing.completion` | |
  | **Quantization** | `quantization` | `fp8` / `fp4` / `unknown` — "unknown" is common; the reference-spec guard (Block 1.3) must decide how to treat it |
  | Context served | `context_length` | varies per host (32K–164K on DeepSeek V3.2) |
  | Host name | `provider_name` | |
  | Pinned slug per host | `name` (e.g. `StreamLake \| deepseek/deepseek-v3.2-20251201`) | |
  | Speed (bonus) | `throughput_last_30m.p50` (tok/s), `latency_last_30m.p50` (ms) | per-host speed is in the feed — a first-pass speed source before our own battery |
  | Caching | `supports_implicit_caching`, `pricing.input_cache_read` | |

  **Flags for later blocks:**
  - Prices are per-token strings — parse as Decimal, ×1e6 for $/M display.
  - A `pricing.discount` field appears on some hosts (StreamLake 0.25) — decide
    whether blended price uses pre- or post-discount. (Open, Block 1.2.)
  - Per-host speed/uptime is available now, so Block 1.5 can source speed from
    the endpoints feed rather than waiting on battery runs.
- **2026-07-22** — **Block 0.5 done — the thesis holds.** `battery/run_one.py`
  proves reasoning-token consumption is readable from OpenRouter's generation
  endpoint. Probed three models on one reasoning prompt (~$0.0002 total):

  | Model | Kind | `native_tokens_reasoning` | `total_cost` |
  |---|---|---|---|
  | `nvidia/nemotron-3-super-120b-a12b:free` | free reasoning | 455 | $0 |
  | `poolside/laguna-xs-2.1` | paid reasoning | 949 | $0.00014598 |
  | `qwen/qwen3-coder-30b-a3b-instruct` | non-reasoning | 0 | $0.00008867 |

  **Locked findings (feed into schemas + battery runner):**
  - **Use `native_tokens_*`, not `tokens_*`.** `native_*` are the provider's
    actually-billed counts; `tokens_*` are OpenRouter's normalized GPT-tokenizer
    counts and differ (e.g. native prompt 79 vs normalized 55). $/task must use
    native.
  - **Reasoning tokens are a subset of completion, not additive.** 949 reasoning
    of 1178 completion. So `cost = (prompt + completion) × price` already includes
    reasoning burn — do not double-count.
  - **A10 recompute reconciles exactly.** `(77·$0.06 + 1178·$0.12)/1e6 =
    $0.00014598` == reported `total_cost`, to the cent. The "recompute, never
    trust the provider cost field" check works against live data.
  - **`native_tokens_reasoning` is always present** — integer `0` on
    non-reasoning models, never null. No missing-field handling needed.
  - The generation record also carries `model_permaslug` (pinned, date-stamped)
    and per-provider detail — more A12 confirmation.
  - Set `usage:{include:true}` on the completion request to also get usage inline;
    the generation record needs a short backoff (available within a few seconds).
- **2026-07-22** — **Block 0.3 resolved — capability sourcing settled. Closes §8 / A4.**

  **Decision:**
  | Axis | Source | Access |
  |---|---|---|
  | Chat Elo | LMArena | Published openly |
  | Overall / Coding / Reasoning | **Artificial Analysis Intelligence Index** (adopted wholesale, version-stamped) | **Official API only** — never website scraping |
  | Context, modality, license | Model cards / OpenRouter metadata | — |

  AA use **is permitted with attribution** for selected, API-derived figures
  (benchmark, pricing, performance) displayed in products/charts. It is adopted
  wholesale as a pre-composed index — consistent with the "no homemade blended
  capability index" constraint (A4). So overall/coding/reasoning are now
  **confirmed-and-publishable**, not data-only.

  **Rules that come with the license (all mandatory):**
  1. **Official API, cached server-side.** No scraping AA's website — permission is
     tied to API use.
  2. **Attribution:** a visible footer/byline — *"Model benchmark, pricing, and
     performance data provided by Artificial Analysis"* — with **Artificial
     Analysis** linked to their homepage.
  3. **Precise metric identity on every figure:** index name + version + retrieval
     date, e.g. `Artificial Analysis Intelligence Index v4.1: 42 · retrieved
     2026-07-22`. AA changes benchmark composition between major versions; scores
     are only comparable within a major version (this is why CapabilityScore
     carries `index_version` + `observed_at`).
  4. **⚠ No redistribution.** Republishing the AA dataset, a competing live
     leaderboard, or bulk redistribution is **not** covered by attribution —
     requires a written redistribution agreement.

  **Design consequence (load-bearing):** TokenTicker's open CSV/JSON export is
  redistribution. Therefore the export carries **owned data only** — OpenRouter
  prices + our measured token/cost + our derived numbers — and **excludes AA-derived
  capability figures**, linking out to AA instead of rehosting the values. Displaying
  AA numbers on the site (attributed) is fine; putting them in the downloadable file
  is not. Enforced in Block 2.4.

  **Residual to confirm (procurement, not design):** display rights ≠ free API
  access. Confirm which AA API tier/subscription is needed to pull the index and its
  cost, before Block 1.5 wires the ingestion. Logged as an open item.
