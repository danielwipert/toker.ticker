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
