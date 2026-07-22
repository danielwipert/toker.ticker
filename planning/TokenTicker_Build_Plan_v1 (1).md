# TokenTicker Build Plan

**Companion to:** `TokenTicker_Product_Spec_v4.docx` (+ §6.3 amendment, v4.1)
**Status:** Phase 0 — not started
**Last updated:** 2026-07-21

---

## How to use this doc

This is the operational work plan for building TokenTicker. The spec is the architectural contract; this file is the sequence of moves that gets it built.

Rules of engagement:

- Work through blocks in order. Each block has a **Done when** criterion — don't move on until it's met.
- Check boxes as you go. Commit the checked-off version so the repo history shows progress.
- If you revise the plan mid-build (e.g., a block needs to split in two), that's fine — edit this file. This doc is expected to evolve. The spec is not.
- Stop-and-assess checkpoints between phases are mandatory, not optional.
- Every block is small on purpose. If a block is taking more than a session, it was too big — split it.

**Two rules carried from the spec that constrain every block:**

1. **Price comes from OpenRouter and nowhere else.** No other source touches a price field.
2. **No invented numbers.** A missing measurement shows as "awaiting measurement," never as a default or an estimate. This is the trust wedge; it is not negotiable for convenience.

---

## Phase 0: Validate before building

**Goal:** A spreadsheet of 25–50 real models with real OpenRouter prices, sourced capability, and hand-computed `$/task` from a first real battery run — plus the tuned threshold values. No pipeline yet. The point is to confirm the metric is meaningful *before* automating it.

> **Why Phase 0 exists:** the hero metric is the product. If `$/task` doesn't separate models in an interesting way on real data, everything downstream is wasted effort. Find that out with a spreadsheet, not a pipeline.

---

### Block 0.1: Scaffolding

Get the skeleton in place so every later step has somewhere to live. Target: an hour or two.

- [ ] Create the repo: `github.com/danielwipert/chorus-ai-tokenticker`
- [ ] Set up directory structure:
  - [ ] `schemas/`
  - [ ] `ingestion/`
  - [ ] `battery/`
  - [ ] `derive/`
  - [ ] `site/`
  - [ ] `data/`
  - [ ] `tests/`
  - [ ] `docs/`
- [ ] Write `requirements.txt`: `httpx`, `pydantic`, `pandas`, `jinja2`, `python-dotenv`, `pyyaml`, `pytest`
- [ ] Create `.env` with `OPENROUTER_API_KEY`; add `.env` to `.gitignore`
- [ ] Create `docs/DECISIONS.md` — an append-only log; every decision from here gets one line with a date
- [ ] Write `tests/test_import.py` — imports the package and asserts it loads
- [ ] Commit and push

**Done when:** `pytest tests/test_import.py` passes and the repo is pushed.

---

### Block 0.2: First look at the OpenRouter feed

Before writing any ingestion logic, look at the actual data with your own eyes.

- [ ] Write `ingestion/fetch_models.py` — a ~20 line script that GETs the OpenRouter models endpoint and writes the raw JSON to `data/raw/models_YYYY-MM-DD.json`
- [ ] Run it. Print: how many models came back, and one full record pretty-printed
- [ ] Read that one record field by field. Write down in `docs/DECISIONS.md` which fields map to: input price, output price, context length, and provider
- [ ] Repeat for the endpoints/providers data for one open-weight model — confirm you can see per-host prices and quantization

**Done when:** raw JSON is on disk, and you can name the exact field path for input price, output price, context, and quantization.

*Don't skip the eyeballing.* Every later block assumes you know what these fields look like when they're missing, null, or weird.

---

### Block 0.3: Resolve the capability source (spec §8 open decision)

The one decision v4 deliberately left open. Close it before it blocks Phase 1.

- [ ] Read Artificial Analysis's terms of use — determine whether attributed, linked citation of individual figures on a public site is permitted
- [ ] Check LMArena's leaderboard for access: is there a downloadable/queryable source, or does it need scraping?
- [ ] Identify one open coding/reasoning leaderboard as a second axis source
- [ ] Log the decision in `docs/DECISIONS.md`: which source is primary, which are complementary, whether AA appears at all
- [ ] For whichever sources are chosen, write down their refresh cadence and known weakness (needed for the methodology page later)

**Done when:** `DECISIONS.md` names the primary capability source and its access method, with the AA question answered yes or no.

---

### Block 0.4: Write the v0 task set

The battery's content. Small on purpose — this is the launch-blocking deliverable created by moving the battery onto the MVP path.

- [ ] Create `battery/tasks.yaml`
- [ ] Write 1–2 tasks per category (5–10 total): coding, reasoning, extraction, summarization, long-context Q&A
- [ ] Each task needs: `task_id`, `category`, `prompt`, and a short note on what it's meant to exercise
- [ ] Deliberately vary the token profile — at least one short-input/long-reasoning task, and at least one large-input/short-output task
- [ ] Keep the large-input task as small as it can be while still testing long context — prompt tokens dominate battery cost, so this one task drives the bill on every model
- [ ] Set `task_suite_version: v0` at the top of the file
- [ ] Read every prompt back and check it's answerable without tools or web access

**Done when:** `tasks.yaml` exists with 5–10 tasks, each tagged to a category, and the file loads with `yaml.safe_load`.

---

### Block 0.5: First battery run, three models, by hand

The riskiest technical assumption in the whole spec is that you can read real token consumption back out of OpenRouter. Prove it on three models before building anything around it.

- [ ] Write `battery/run_one.py` — takes a model id and a prompt, calls OpenRouter chat completions, and returns the response plus the generation id
- [ ] Extend it: after the call, fetch the generation record by id and print prompt tokens, completion tokens, reasoning tokens, and total cost
- [ ] Add a short wait/retry before fetching the generation record (it may not be immediately available)
- [ ] Run it against three models: one free, one cheap open-weight, one reasoning model
- [ ] Confirm the reasoning model reports a non-zero reasoning-token count
- [ ] Record the three results by hand in a scratch file

**Done when:** you have real measured token counts and costs for 3 models on 1 task, and the reasoning model's reasoning tokens are visibly non-zero.

> **If reasoning tokens come back empty or null:** stop and assess. That field is the justification for the whole hero metric. Log what you found in `DECISIONS.md` before proceeding — it may change what `$/task` can honestly claim.

---

### Block 0.6: The Phase 0 spreadsheet

The gut check. Real data, hand-assembled, no pipeline.

- [ ] Pick 25–50 models spanning the range: frontier proprietary, mid-tier, small/cheap, open-weight, and at least 3 reasoning models
- [ ] Pull their OpenRouter prices into a CSV (script it if easier, but it's fine to be scrappy here)
- [ ] Add capability scores from the Block 0.3 source
- [ ] Run the full v0 battery against every model — start with free models so a mistake costs nothing, then add paid ones
- [ ] Compute `$/task` per category and the equal-weighted headline
- [ ] Put it all in one spreadsheet and sort by `$/task`

**Done when:** the spreadsheet exists, sorts sensibly, and you can point to at least one model whose per-token price and `$/task` rank disagree.

*That disagreement is the product.* If it doesn't appear on real data, stop and reassess the thesis before building the pipeline.

---

### Block 0.7: Tune the thresholds against real data

The spec deliberately left these to be set once real numbers exist.

- [ ] Set the domination price margin (spec starting point: 10–15%)
- [ ] Set the capability noise band (v4.1 amendment starting point: 2 points) — check it against the actual spread of your capability source
- [ ] Set the Value log-compression anchors — fixed, version-stamped, *not* derived from the live table
- [ ] Set the label zone boundaries (top-capability, mid, low)
- [ ] Set the Specialist axis gap
- [ ] Write all of these into `config.yaml` with a comment explaining each
- [ ] Apply the label rules to the spreadsheet by hand and read every label
- [ ] Check the consistency assertion from §6.3: no model labeled Overpriced should carry a top Value score

**Done when:** `config.yaml` is committed, every model in the spreadsheet has a label, and you agree with every Overpriced call.

*Read the Overpriced rows most carefully.* Each one must name a specific model that is genuinely cheaper and at-least-as-capable on every axis. If any looks unfair, the thresholds are wrong — not the model.

---

### ■ STOP AND ASSESS — end of Phase 0

Do not start Phase 1 until you can answer yes to all of these:

- [ ] Does `$/task` separate models in a way per-token price does not?
- [ ] Are reasoning tokens reliably measurable?
- [ ] Is the capability source settled and license-clean?
- [ ] Do the labels read as fair on real data?
- [ ] Is the full battery run cost per refresh acceptable?

---

## Phase 1: The pipeline

**Goal:** A daily GitHub Action that writes a dated JSON snapshot of prices, capability, and speed — plus a battery runner that writes measured `$/task` snapshots. No website yet. Data first.

---

### Block 1.1: Schemas

Pydantic schemas are the contract between every later module.

- [ ] Create `schemas/models.py` with the entities from spec §11:
  - [ ] `Model`
  - [ ] `PriceSnapshot`
  - [ ] `CapabilityScore`
  - [ ] `Speed`
  - [ ] `TaskCost`
  - [ ] `Derived`
- [ ] Give every snapshot schema a `confidence` field and a `checked_at` / `observed_at` timestamp
- [ ] Make `TaskCost.success_rate` optional and default to `None` (V2 fills it; MVP leaves it empty)
- [ ] Write `tests/test_schemas.py` — construct one valid instance of each and assert one invalid instance raises

**Done when:** `pytest tests/test_schemas.py` passes.

---

### Block 1.2: Price ingestion

- [ ] Write `ingestion/prices.py` behind a source abstraction (one class, one `fetch()` method) so a second source could be added later without touching callers
- [ ] Parse the OpenRouter feed into `PriceSnapshot` objects
- [ ] Compute blended price at the default 70/30 input/output weighting, with the weights read from `config.yaml`
- [ ] Handle the failure path: on fetch error, keep last-known values and mark them stale rather than writing nothing
- [ ] Write `tests/test_prices.py` using a saved fixture of the raw JSON from Block 0.2

**Done when:** running the module produces valid `PriceSnapshot` objects for every model, and the test passes against the fixture.

---

### Block 1.3: Cheapest-qualifying host filter

Open-weight models have many hosts at different prices and quality. This picks one honestly.

- [ ] Define the reference serving spec in `config.yaml`: minimum quantization and minimum context served
- [ ] Write the filter: among hosts for a model, keep only those meeting the reference spec, then take the cheapest
- [ ] Record which host was chosen on the snapshot, and keep the full per-host spread for the detail page later
- [ ] Add the outlier guard: flag (don't drop) a price suspiciously far below the field for manual review
- [ ] Set confidence to Medium for cheapest-qualifying prices, High for first-party — per spec §10.1

**Done when:** for one multi-host open model, the filter picks a host you agree with, and the full spread is retained in the snapshot.

---

### Block 1.4: Battery runner

Promote Block 0.5's script into a real module.

- [ ] Write `battery/runner.py` — loops the task set × the model roster
- [ ] Support three run modes:
  - [ ] `--full` — every model (used on task-set or methodology changes)
  - [ ] `--model <id>` — one model (new entrant or version change)
  - [ ] `--canary` — 1–2 tasks across the roster, for drift detection
- [ ] Add `--dry-run` that estimates spend from current prices and stored token counts, and prints it *before* any call is made
- [ ] For each call: record prompt / completion / reasoning tokens and realized cost from the generation record
- [ ] Set sampling for reproducibility: temperature 0 and a fixed seed where the model supports it
- [ ] Disable prompt caching where the provider allows it — a cache hit understates real token cost and would corrupt the measurement
- [ ] Write results as `TaskCost` rows: one per category plus a blended roll-up
- [ ] Add resumability — if a run dies partway, don't re-run models already measured
- [ ] Add a cost ceiling: abort the run if projected spend exceeds a configured limit
- [ ] Handle a model that errors or refuses: record it as unmeasured, never as zero
- [ ] Measure every tier on the same cadence — no tier-based exemptions, so every `$/task` in the column is equally fresh and therefore comparable

**Done when:** a full battery run completes across the roster and writes `TaskCost` rows, and a deliberately interrupted run resumes without re-charging for completed models.

---

### Block 1.4a: Battery cadence and drift detection

The battery is the only part of the system that costs money to run. It is deliberately **event-driven, not scheduled** — token consumption only changes when the model changes, so there is nothing to re-measure on a clock.

**Run triggers:**

| Trigger | Scope |
| --- | --- |
| New model enters the roster | That model only |
| Model version changes | That model only |
| Task set version bumps (v0 → v1) | Full sweep |
| Battery methodology changes | Full sweep |
| Canary detects drift | The drifted model only |

- [ ] Implement roster-change detection: compare today's roster against the last snapshot, and queue any new model for measurement
- [ ] Implement version-change detection: if a model's version or serving fingerprint changes, invalidate its stored token counts and queue a re-measure
- [ ] Implement the monthly canary: re-run 1–2 tasks across the roster and compare token counts against stored values
- [ ] Set the drift threshold in `config.yaml` (starting point: re-measure if token count moves more than 15%)
- [ ] On drift detection, queue that model for a full re-measure — never patch the stored number from canary data alone
- [ ] Log every battery run to `data/battery_runs.jsonl`: date, mode, models touched, realized spend

**Done when:** adding a model to the roster triggers a single-model run automatically, and a simulated token-count shift triggers a re-measure for that model only.

> **Why a canary and not a periodic full sweep:** providers silently requantize, change serving configs, or push new weights under the same name. Without a detector, stored token counts go quietly wrong with no event to catch them. The canary is a cheap sensor that triggers an expensive correction only when one is warranted — roughly a dollar a month instead of a standing sweep cost.

---

### Block 1.5: Capability and speed ingestion

- [ ] Write `ingestion/capability.py` against the Block 0.3 source, behind the same source abstraction as prices
- [ ] Version-stamp every score with the index version and observation date
- [ ] Carry confidence intervals through where the source publishes them — never flatten a range to a point
- [ ] Capture speed (median tok/s, time to first token) from the battery runs where available
- [ ] Write `tests/test_capability.py` against a saved fixture

**Done when:** capability scores land as valid `CapabilityScore` objects with source, version, and date populated.

---

### Block 1.6: Derived math

All deterministic Python. No LLM anywhere near these numbers.

- [ ] Write `derive/value.py` — log-compressed capability-per-dollar, scaled against the fixed anchors from `config.yaml`
- [ ] Write `derive/labels.py` implementing the **v4.1** domination rule:
  - [ ] Challenger must be at least as capable on **every** published axis, within the noise band
  - [ ] **and** meaningfully cheaper by the price margin
  - [ ] Record which model is the dominator, so the UI can name it
- [ ] Implement the Specialist overlay as a separate boolean, not a primary label
- [ ] Implement confidence inheritance: a derived number takes the lowest confidence of its inputs
- [ ] Write `tests/test_labels.py` with hand-built cases:
  - [ ] a clearly dominated model → Overpriced, with the right dominator named
  - [ ] a specialist that is worse on overall but better on its axis → **not** Overpriced
  - [ ] a one-point axis difference → treated as a tie, not an escape
- [ ] Write the consistency assertion from §6.3 as a test: no Overpriced model holds a top Value score

**Done when:** all label tests pass, including the specialist case that motivated the v4.1 amendment.

> This block is where the trust wedge lives. Take the tests seriously — the specialist case is the one that was wrong in the prototype and would have shipped a false accusation.

---

### Block 1.7: Snapshot writer

- [ ] Write `data/` layout: one folder per date, JSON files per entity
- [ ] Write `derive/snapshot.py` — assembles prices + capability + speed + task costs + derived into one dated snapshot
- [ ] Make snapshots immutable: never overwrite a past date
- [ ] Implement the roster rule: a model needs an OpenRouter price **and** at least one capability score to earn a row; price-only models go to a holding set
- [ ] Implement the retirement rule: stale-flag past the per-field threshold, retire from the default table at ~90 days cold, never delete history
- [ ] Implement freshness thresholds per field from spec §10.2

**Done when:** two consecutive daily snapshots exist on disk, both valid, and the second did not modify the first.

---

### Block 1.8: Automation

- [ ] Write `.github/workflows/daily.yml` — cron job running price + capability ingestion, then snapshot assembly
- [ ] Store `OPENROUTER_API_KEY` as a GitHub secret
- [ ] Make the job commit the new snapshot back to the repo
- [ ] Add a manually-triggered workflow for the battery run, exposing the `--full` / `--model` / `--canary` modes (it costs money — it must never run on the daily cron)
- [ ] Add a monthly scheduled workflow that runs `--canary` only
- [ ] Have the daily job open an issue (not auto-run) when it detects a new or version-changed model, so a paid run is always a deliberate act
- [ ] Add failure notification so a silently-broken cron doesn't rot the data

**Done when:** the daily action runs unattended for three consecutive days and produces three valid snapshots.

---

### ■ STOP AND ASSESS — end of Phase 1

- [ ] Do three consecutive snapshots look right?
- [ ] Does a price change between days show up correctly?
- [ ] Does the stale flag fire when a source goes cold?
- [ ] Do the labels stay stable day to day, or do they flicker? (Flickering means thresholds are too tight.)

---

## Phase 2: The MVP site

**Goal:** The live site — simple-first Manager view, Analyst view, model pages, methodology, open data download. Static generation to GitHub Pages.

> The visual direction is settled: **Manager view = Briefing (light)**, **Analyst view = Terminal (dark)**, with the mode toggle swapping the whole theme. `tokenticker_prototype_v2.html` is the reference implementation — port from it rather than restyling from scratch.

---

### Block 2.1: Static site skeleton

- [ ] Write `site/build.py` — reads the latest snapshot, renders Jinja2 templates to `site/dist/`
- [ ] Port the prototype's CSS token system into `site/templates/base.html` (the `:root` / `body.analyst` variable pair)
- [ ] Set up the page shell: header, mode toggle, footer
- [ ] Confirm the theme swap works from real data

**Done when:** `python site/build.py` produces a page in `dist/` that opens in a browser with both themes toggling.

---

### Block 2.2: Manager view

- [ ] Render the five columns: Model, `$/task` (+ subordinate blended `$/M`), Capability, Rating, Confidence · Updated
- [ ] Render the per-token inversion flag where a cheaper sticker hides a higher run cost
- [ ] Render the summary strip (cheapest to run, best value, frontier leader, models tracked)
- [ ] Implement the honest-blank state for unmeasured `$/task`, including its sort behavior (labeled group at the bottom)
- [ ] Implement search and the open/proprietary filter chips
- [ ] Implement column sorting

**Done when:** the Manager view renders from a real snapshot and every number traces back to a snapshot field.

---

### Block 2.3: Analyst view

- [ ] Render the banded screener: Model / Cost / Performance / Speed / Context / Trust
- [ ] Port the Terminal theme, including the per-row rating signal bar
- [ ] Render the frontier chart (X = `$/task` log scale, Y = capability) behind its toggle
- [ ] Add the preset tabs: Value (default), Market, Performance, Use case

**Done when:** toggling to Analyst view shows every band with real data, and the frontier chart plots correctly.

---

### Block 2.4: Model detail pages

- [ ] Generate one page per active model
- [ ] Layout: observed facts up top, derived value separated below — the two-layer split must be visible
- [ ] Source trace on every number: what it came from, when it was checked
- [ ] Full per-host price spread
- [ ] Battery run detail: tokens per category behind the `$/task` figure
- [ ] Where a model is Overpriced, name and link the dominating model

**Done when:** every model has a page and every number on it has a visible source.

---

### Block 2.5: Methodology, corrections, and open data

- [ ] Write the methodology page from spec §13 — in plain language, with a worked `$/task` example
- [ ] State the MVP caveats explicitly: no grading yet, the compute-platform exclusion, what "cheapest qualifying" means
- [ ] Add the correction link on every page (opens a GitHub issue with the field pre-filled)
- [ ] Add the CSV/JSON download of prices and measured costs
- [ ] Make clear in the export what is owned data vs. attributed capability data

**Done when:** a stranger could read the methodology page and reproduce one model's `$/task` by hand.

---

### Block 2.6: Ship

- [ ] Enable GitHub Pages on the repo
- [ ] Extend the daily action to rebuild and publish the site after each snapshot
- [ ] Check responsive behavior down to mobile
- [ ] Check keyboard focus is visible and the mode toggle is reachable
- [ ] Confirm reduced-motion is respected (the ticker rail must stop)
- [ ] Final pass: click every Overpriced label and confirm the named dominator is genuinely cheaper and at-least-as-capable

**Done when:** the site is live, rebuilding daily, and the last check passes on every Overpriced row.

---

### ■ STOP AND ASSESS — MVP shipped

Before starting V1 work:

- [ ] Has a non-technical reader used the Manager view and reached a decision without help?
- [ ] Has anyone submitted a correction? (If the data is public and nobody corrects it, either it's right or nobody's reading.)
- [ ] Is the daily job stable?
- [ ] What does the battery cost per refresh in practice?

---

## Phase 3 (V1): after the MVP

Not scoped in detail — deliberately. Revisit after the MVP has run for a few weeks.

- Battery **grading** (generator-verifier) → `success_rate` and real cost-per-successful-task
- Axis-aware labels: labels recompute against the selected Value axis, so switching to "reasoning" re-ranks the board for reasoning work *(the natural extension of the v4.1 amendment)*
- Use-case calculator with user-supplied success and latency inputs
- Price history and the frontier-over-time slider
- Alerts, saved views, public read API
- A second capability source for cross-checking

---

## Open items carried into the build

| Item | Where it resolves |
| --- | --- |
| Capability source + AA terms | Block 0.3 |
| Whether reasoning tokens are reliably readable | Block 0.5 |
| v0 task set content | Block 0.4 |
| Domination margin, noise band, Value anchors, zone boundaries | Block 0.7 |
| Real cost of one full battery sweep | Block 0.6 — record it; it sets the drift threshold and cost ceiling |
| Canary drift threshold | Block 1.4a |

---

*Chorus AI Systems — Daniel Wipert — TokenTicker Build Plan v1 — July 2026*
