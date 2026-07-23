# TokenTicker Build Plan

**Companion to:** `TokenTicker_Product_Spec_v4` **+ `TokenTicker_Spec_Amendment_v4_2`**
**Status:** Phase 0 — not started
**Last updated:** 2026-07-22
**Supersedes:** Build Plan v1 (which tracked spec v4 + the v4.1 §6.3 amendment only, and predates v4.2)

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

> **⟳ Reading the `⟳` callouts.** Every block that changed from Build Plan v1 carries a `⟳ v4.2 · Ax` note naming the amendment that moved it. If you built anything against v1, these are the deltas to reconcile.

---

## What changed in this revision (v1 → v2)

Build Plan v1 was written against spec v4 + the v4.1 label fix. Amendment **v4.2** (14 items) landed afterward and reverses or hardens several v4 decisions. This revision folds them in. The load-bearing changes:

| # | Amendment | Effect on this plan |
| --- | --- | --- |
| A1 | Single unified view; dark "Analyst" theme removed | Phase 2 collapses from two view-blocks into one. `tokenticker_prototype_v3.html` is the reference (not v2). |
| A2 | Detail page + ±5 peer rule | Block 2.3 gains the peer set, teal/slate highlighting, empty-band case. |
| A3 | Rating engine reads unpublished axes | Reinforces Block 1.6; coding/reasoning live in the data model, not the columns. |
| A4 | Capability sourcing ~~still open~~ **RESOLVED** | Block 0.3: LMArena Elo + **Artificial Analysis Intelligence Index** (API, attributed, version-stamped). AA displayed but not redistributed → excluded from open export. |
| A5 | Owned battery is MVP-critical | Already true in v1; unchanged. |
| **A6** | **Deterministic grading at MVP** | **Reverses spec v4's "no grading at MVP."** Adds a grader module; no LLM in the MVP grading path. |
| A7 | Three MVP categories | Coding, extraction, reasoning. Summarization + long-context deferred. Headline = mean of **3**. |
| A8 | Procedural task generation | Block 0.4 builds a **generator + grading code**, not a fixed `tasks.yaml`. Fresh seeded instances per snapshot. |
| A9 | Repeat count `N` is calibration-derived | New Block 0.8 runs the calibration study to set `N` before the battery is automated. |
| A10 | Token accounting locked | Provider-reported usage only; two Python checks (cost recompute + output-token bound). |
| A11 | Measurement decoupled from pricing | `$/task` recomputes **daily** from cached tokens × fresh price. |
| A12 | Monthly cadence + snapshot pinning | Reframes Block 1.4a: monthly re-run = drift detection; roster addresses **pinned** identifiers, never aliases. |
| A13 | Listing criteria | Block 1.7 gains 5 hard gates + caps (max 3/provider, ~25 by Elo). |
| **A14** | **`success_rate` arrives at MVP** | **Reverses spec v4's `success_rate = None`.** cost-per-successful-task becomes available; publishing it is open item 2. |

---

## Phase 0: Validate before building

**Goal:** A spreadsheet of 25–50 real models with real OpenRouter prices, sourced capability, and hand-computed `$/task` **and `success_rate`** from a first real battery run — plus the tuned threshold values **and a measured repeat count `N`**. No pipeline yet. The point is to confirm the metric is meaningful *before* automating it.

> **Why Phase 0 exists:** the hero metric is the product. If `$/task` doesn't separate models in an interesting way on real data, everything downstream is wasted effort. Find that out with a spreadsheet, not a pipeline.

---

### Block 0.1: Scaffolding

Get the skeleton in place so every later step has somewhere to live. Target: an hour or two.

- [ ] Create the repo: `github.com/danielwipert/chorus-ai-tokenticker`
- [ ] Set up directory structure:
  - [ ] `schemas/`
  - [ ] `ingestion/`
  - [ ] `battery/`
  - [ ] `generator/` — the procedural task generator ⟳ *v4.2 · A8*
  - [ ] `grading/` — the deterministic graders + sandbox ⟳ *v4.2 · A6*
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
- [ ] Note whether a **pinned/versioned** model identifier is available distinct from any moving alias — you will need it for A12 ⟳ *v4.2 · A12*

**Done when:** raw JSON is on disk, and you can name the exact field path for input price, output price, context, and quantization.

*Don't skip the eyeballing.* Every later block assumes you know what these fields look like when they're missing, null, or weird.

---

### Block 0.3: Resolve the capability source (spec §8 open decision)

The one decision v4 deliberately left open, and v4.2 confirms is **still open** — a hard Phase 0 gate. Close it before it blocks Phase 1.

> **✅ RESOLVED 2026-07-22 — see `DECISIONS.md`. Status of the capability axes:**
>
> | Axis | Source | Status |
> | --- | --- | --- |
> | Chat Elo | LMArena | **Confirmed** — published openly |
> | Capability (overall) | **Artificial Analysis Intelligence Index** (API, attributed) | **Confirmed & publishable** |
> | Coding | Artificial Analysis (API, attributed) | **Confirmed & publishable** |
> | Reasoning | Artificial Analysis (API, attributed) | **Confirmed & publishable** |
> | Context window | Model cards | Confirmed |
>
> **Constraint (retained):** TokenTicker does **not** build its own blended capability index. AA's Intelligence Index is adopted **wholesale**, version-stamped — which satisfies this.
>
> **License terms that bind the build:** official AA **API only** (no website scraping); server-side cache; visible attribution footer linking to AA; every figure stamped with index version + retrieval date; and — load-bearing — **AA figures are displayed but never redistributed**, so they are excluded from the open data export (Block 2.4).

- [x] ~~Read Artificial Analysis's terms~~ → attributed, API-derived display **is** permitted; redistribution is not.
- [ ] Confirm LMArena's Elo access path (downloadable/queryable vs. scrape)
- [ ] **Confirm which AA API tier/subscription is required and its cost** — display rights ≠ free API access. Blocks Block 1.5 ingestion.
- [x] ~~Decision logged in `DECISIONS.md`~~
- [ ] Write each source's refresh cadence + known weakness for the methodology page (AA: composition drifts across major index versions → compare only within a version)

**Done when:** ~~`DECISIONS.md` names the primary capability source and its access method~~ ✅ — remaining: LMArena access path confirmed and AA API tier/cost confirmed.

---

### Block 0.4: Build the v0 task generator and deterministic grader

⟳ *v4.2 · A6, A7, A8* — **This block is substantially rewritten.** v1 hand-wrote a fixed `tasks.yaml`. v4.2 instead publishes a **task generator and grading code**; instances are generated fresh per snapshot from a published seed, so they can't leak into training data.

**MVP categories are three, not five** (A7): **coding, extraction, reasoning.** Summarization (needs a judge panel) and long-context Q&A (100K-token cost driver) are deferred.

- [ ] Write `generator/` — a seeded generator emitting, per category:

  | Category | Generator emits | Ground truth from |
  | --- | --- | --- |
  | Coding | Function spec from a template grammar — randomized data shapes, edge cases, constraints | Unit tests emitted by the same generator |
  | Extraction | Synthetic structured documents with planted field values | Generation parameters |
  | Reasoning | Multi-step problems with computed answers (constraint satisfaction, scheduling, arithmetic chains) | Solved by the generator |

- [ ] Enforce the **task admission rule**: a task that cannot be graded deterministically does not enter a deterministic category. Verifiability is a constraint on authoring, not discovered afterward.
- [ ] Hold instance **difficulty and token size approximately constant** across seeds via parameter bounds — randomize content, not scale (a 20-line vs. 200-line solution contaminates the variance measurement)
- [ ] Make it **seeded and byte-for-byte reproducible**: same seed → same instances
- [ ] Set `task_suite_version: v0` and record the generator version alongside it
- [ ] Confirm every generated prompt is answerable without tools or web access

> **No LLM in the MVP grading path** (A6). With summarization deferred, all three MVP graders are deterministic — unit-test exit code, exact match, verifiable final answer. Every published number is measured or computed by Python. The grader that *executes* model code is built and hardened in the calibration study (Block 0.8 → promoted in Block 1.4b); this block only needs the generator plus the non-executing graders (extraction exact-match, reasoning answer-match) to start.

**Done when:** running the generator twice with one seed produces identical instances across all three categories; the reference solution for each coding instance passes its own emitted unit tests; and five different seeds produce instances whose reference solutions fall in a narrow line-count band.

---

### Block 0.5: First battery run, three models, by hand

The riskiest technical assumption in the whole spec is that you can read real token consumption back out of OpenRouter. Prove it on three models before building anything around it.

- [ ] Write `battery/run_one.py` — takes a model id and a prompt, calls OpenRouter chat completions, and returns the response plus the generation id
- [ ] Extend it: after the call, fetch the generation record by id and print prompt tokens, completion tokens, reasoning tokens, and total cost
- [ ] Add a short wait/retry before fetching the generation record (it may not be immediately available)
- [ ] **Token accounting checks (A10)** ⟳ *v4.2 · A10*:
  - [ ] Take token counts from the **provider-reported usage** in the API response — never a local tokenizer for the count
  - [ ] Recompute cost as `tokens × published price`; **never** trust or display a provider-supplied cost field
  - [ ] Bound check: reported output tokens must not fall below a local tokenizer count of the visible text — a violation **flags the row**, it does not silently pass
- [ ] Run it against three models: one free, one cheap open-weight, one reasoning model
- [ ] Confirm the reasoning model reports a non-zero reasoning-token count
- [ ] **Grade each response** with the Block 0.4 deterministic grader and record pass/fail ⟳ *v4.2 · A6*
- [ ] Record the results by hand in a scratch file

**Done when:** you have real measured token counts, recomputed costs, **and a pass/fail** for 3 models on 1 task, and the reasoning model's reasoning tokens are visibly non-zero.

> **If reasoning tokens come back empty or null:** stop and assess. That field is the justification for the whole hero metric. Log what you found in `DECISIONS.md` before proceeding — it may change what `$/task` can honestly claim.

---

### Block 0.6: The Phase 0 spreadsheet

The gut check. Real data, hand-assembled, no pipeline.

- [ ] Pick 25–50 models spanning the range: frontier proprietary, mid-tier, small/cheap, open-weight, and at least 3 reasoning models
- [ ] Pull their OpenRouter prices into a CSV (script it if easier, but it's fine to be scrappy here)
- [ ] Add capability scores from the Block 0.3 source
- [ ] Run the full v0 battery (three categories) against every model — start with free models so a mistake costs nothing, then add paid ones
- [ ] Compute `$/task` per category and the **equal-weighted mean of the three categories** for the headline ⟳ *v4.2 · A7*
- [ ] Compute `success_rate` per model, and `cost-per-successful-task = $/task ÷ success_rate` ⟳ *v4.2 · A14*
- [ ] Put it all in one spreadsheet and sort by `$/task`

**Done when:** the spreadsheet exists, sorts sensibly, and you can point to at least one model whose per-token price and `$/task` rank disagree.

*That disagreement is the product.* If it doesn't appear on real data, stop and reassess the thesis before building the pipeline.

> **Watch for the perverse incentive (A14):** a model that fails fast burns few tokens and looks cheap on `$/task`. Check whether `cost-per-successful-task` re-ranks those rows sensibly — this is the argument for publishing it at MVP (open item 2).

---

### Block 0.7: Tune the thresholds against real data

The spec deliberately left these to be set once real numbers exist.

- [ ] Set the domination price margin (spec starting point: 10–15%)
- [ ] Set the capability noise band (v4.1 amendment starting point: 2 points) — check it against the actual spread of your capability source
- [ ] Set the Value log-compression anchors — fixed, version-stamped, *not* derived from the live table
- [ ] Set the label zone boundaries (top-capability, mid, low)
- [ ] Set the Specialist axis gap
- [ ] Set the peer-band width for the detail page (prototype uses ±5 capability points) ⟳ *v4.2 · A2*
- [ ] Write all of these into `config.yaml` with a comment explaining each
- [ ] Apply the label rules to the spreadsheet by hand and read every label
- [ ] Check the consistency assertion from §6.3: no model labeled Overpriced should carry a top Value score

**Done when:** `config.yaml` is committed, every model in the spreadsheet has a label, and you agree with every Overpriced call.

*Read the Overpriced rows most carefully.* Each one must name a specific model that is genuinely cheaper and at-least-as-capable **on every axis held in data — including the unpublished coding and reasoning axes** (A3). If any looks unfair, the thresholds are wrong — not the model.

---

### Block 0.8: Run the calibration study — set `N`

⟳ *v4.2 · A9* — **New block.** Fresh generated instances introduce run-to-run variance. The repeat count `N` is **not** set by fiat; it is measured. This block is a self-contained study with its own doc.

- [ ] Execute `TokenTicker_Calibration_Build_Plan_v1` end to end (generator → runner → sandbox grader → variance analysis), reusing the Block 0.4 generator
- [ ] Harden the executing sandbox grader here — it is the block most likely to eat a full day, and getting the isolation wrong is worse than getting it slow
- [ ] Separate **between-instance** variance (generator design) from **within-instance** variance (model nondeterminism) — they have different fixes and must not be conflated
- [ ] Decide whether the reasoning model needs its own `N`
- [ ] Write `N` (and any per-model `N`) into `config.yaml`; log the per-sweep cost you observed

**Done when:** this sentence is completed with measured numbers and committed to `DECISIONS.md` — *"At N = ___, cost per task is stable to within ___%, and success rate carries an interval of ±___ percentage points."* This closes amendment A9.

---

### ■ STOP AND ASSESS — end of Phase 0

Do not start Phase 1 until you can answer yes to all of these:

- [ ] Does `$/task` separate models in a way per-token price does not?
- [ ] Are reasoning tokens reliably measurable?
- [ ] Is the capability source settled and license-clean (or explicitly held data-only)?
- [ ] Do the labels read as fair on real data?
- [ ] Does the deterministic grader classify pass/fail correctly, and does the sandbox contain hostile code? ⟳ *v4.2 · A6*
- [ ] Is `N` set from measurement, with a known per-sweep cost? ⟳ *v4.2 · A9*
- [ ] Is the full battery run cost per refresh acceptable?

---

## Phase 1: The pipeline

**Goal:** A daily GitHub Action that writes a dated JSON snapshot of prices, capability, and speed — plus a battery runner that writes measured `$/task` **and `success_rate`** snapshots. No website yet. Data first.

> **⟳ v4.2 · A11 — the cost architecture that shapes this phase:** `$/task = cached measured tokens × current published price`. Tokens are a property of a pinned model snapshot and don't drift between runs; price changes often and is free to fetch. So token profiles are measured rarely and cached, prices refresh daily, and `$/task` recomputes daily at zero inference cost. Build the pipeline around that split.

---

### Block 1.1: Schemas

Pydantic schemas are the contract between every later module.

- [ ] Create `schemas/models.py` with the entities from spec §11:
  - [ ] `Model` — include the **pinned snapshot identifier** distinct from any alias ⟳ *v4.2 · A12*
  - [ ] `PriceSnapshot`
  - [ ] `CapabilityScore`
  - [ ] `Speed`
  - [ ] `TaskCost`
  - [ ] `Derived`
- [ ] Give every snapshot schema a `confidence` field and a `checked_at` / `observed_at` timestamp
- [ ] **`TaskCost.success_rate` is populated at MVP** — measured by the battery, not `None` ⟳ *v4.2 · A14*. Add `cost_per_successful_task` (derived) and a `published` flag on it (open item 2)
- [ ] Add the **grading result** fields to `TaskCost`: the pass/fail and the failure class from the taxonomy ⟳ *v4.2 · A6*:
  - `pass` · `fail_tests` · `fail_error` · `fail_syntax` · `fail_timeout` · `fail_extract` · `error_infra` (the last is a harness fault — **excluded** from success rate, never counted as a model failure)
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

- [ ] Write `battery/runner.py` — for each model, **generate fresh instances from the published seed** (A8), run each `N` times (A9), across the three MVP categories
- [ ] Support three run modes:
  - [ ] `--full` — every model (used on task-set or methodology changes)
  - [ ] `--model <id>` — one model (new entrant or version change)
  - [ ] `--canary` — 1–2 tasks across the roster, for drift detection
- [ ] Add `--dry-run` that estimates spend from current prices and stored token counts, and prints it *before* any call is made
- [ ] For each call: record prompt / completion / reasoning tokens and realized cost, taken from provider-reported usage, with both A10 checks applied ⟳ *v4.2 · A10*
- [ ] **Address models by their pinned snapshot identifier, never a moving alias** ⟳ *v4.2 · A12*
- [ ] Set sampling for reproducibility: temperature 0 and a fixed seed where the model supports it
- [ ] Disable prompt caching where the provider allows it — a cache hit understates real token cost and would corrupt the measurement
- [ ] **Grade every response** via the Block 1.4b grader and write `success_rate` alongside `$/task` ⟳ *v4.2 · A6, A14*
- [ ] Write results as `TaskCost` rows: one per category plus a blended roll-up (equal-weighted mean of the three categories)
- [ ] Add resumability — if a run dies partway, don't re-run models already measured
- [ ] Add a cost ceiling: abort the run if projected spend exceeds a configured limit
- [ ] Handle a model that errors or refuses: record it as unmeasured, never as zero
- [ ] Measure every listed model on the same cadence — no tier-based exemptions, so every `$/task` in the column is equally fresh and therefore comparable

**Done when:** a full battery run completes across the roster and writes `TaskCost` rows with token counts **and pass/fail**, and a deliberately interrupted run resumes without re-charging for completed models.

---

### Block 1.4b: The grading harness

⟳ *v4.2 · A6* — **New block.** Promote the calibration study's sandbox grader (calibration Block 3) into a reusable module. This is the block that runs code written by a language model, so isolation is the whole job.

- [ ] Write `grading/` with one grader per MVP category:
  - [ ] Coding → execute against the emitted unit tests, read the exit code
  - [ ] Extraction → exact match against planted ground truth
  - [ ] Reasoning → verifiable final-answer match
- [ ] For the coding grader, enforce real sandbox isolation:
  - [ ] Subprocess execution, never `exec()` / `eval()` in the host process
  - [ ] No network access
  - [ ] Filesystem jail — a scratch directory, nothing outside it
  - [ ] Hard wall-clock timeout
  - [ ] Memory ceiling
- [ ] Classify every outcome into the failure taxonomy from Block 1.1, keeping `error_infra` out of the success-rate denominator
- [ ] Write `tests/test_grading.py`: a known-good solution passes; a known-bad one fails with the *correct* class; an infinite loop times out cleanly; a solution attempting network or out-of-jail filesystem access is contained

**Done when:** all four grading-harness assertions pass, including containment of hostile code.

> **No LLM appears in this path at MVP.** Summarization's judge panel (three model families, majority vote) is specified but out of scope until summarization re-enters (open item 4).

---

### Block 1.4a: Battery cadence and drift detection

⟳ *v4.2 · A11, A12* — **Reframed.** v1 called the battery "event-driven, not scheduled." v4.2 keeps the event triggers **and adds a monthly re-run reframed as drift detection**: a pinned snapshot's numbers are *expected* not to move, and a move is itself a publishable finding.

**Run triggers:**

| Trigger | Scope |
| --- | --- |
| New model / new snapshot enters the roster | That model only (immediate) |
| Model version or serving fingerprint changes | That model only |
| Task set version bumps (v0 → v1) | Full sweep |
| Battery methodology changes | Full sweep |
| **Monthly scheduled re-run** | Every listed model — **drift detection**, not freshening |
| Canary detects drift between monthly runs | The drifted model only |

- [ ] Implement roster-change detection: compare today's roster against the last snapshot, and queue any new **pinned** model for measurement
- [ ] Implement version/fingerprint-change detection: on change, invalidate stored token counts and queue a re-measure
- [ ] Implement the monthly re-run and compare token counts against stored values; a divergence under a stable version id is a finding — log it, don't silently overwrite
- [ ] Set the drift threshold in `config.yaml` (starting point: re-measure if token count moves more than 15%)
- [ ] On drift detection from a canary, queue that model for a full re-measure — never patch the stored number from canary data alone
- [ ] Log every battery run to `data/battery_runs.jsonl`: date, mode, models touched, realized spend

**Done when:** adding a pinned model to the roster triggers a single-model run automatically, and a simulated token-count shift triggers a re-measure for that model only.

> **Why pinning matters (A12):** providers re-point aliases and change serving config — quantization, speculative decoding — without a version bump. Addressing pinned identifiers makes "a model is a model" true by construction. Catching a silent change under a stable id is exactly the class of event TokenTicker is positioned to catch and nobody else is watching for.

---

### Block 1.5: Capability and speed ingestion

- [ ] Write `ingestion/capability.py` against the Block 0.3 source, behind the same source abstraction as prices
- [ ] For any axis that is **data-only** (unconfirmed provenance), ingest it into the model record but mark it not-publishable so the view layer keeps it out of the columns while the rating engine still reads it ⟳ *v4.2 · A3, A4*
- [ ] Version-stamp every score with the index version and observation date
- [ ] Carry confidence intervals through where the source publishes them — never flatten a range to a point
- [ ] Capture speed (median tok/s, time to first token) from the battery runs where available
- [ ] Write `tests/test_capability.py` against a saved fixture

**Done when:** capability scores land as valid `CapabilityScore` objects with source, version, and date populated, and data-only axes are flagged as such.

---

### Block 1.6: Derived math

All deterministic Python. No LLM anywhere near these numbers.

- [ ] Write `derive/value.py` — log-compressed capability-per-dollar, scaled against the fixed anchors from `config.yaml`
- [ ] Write `derive/labels.py` implementing the **v4.1** domination rule:
  - [ ] Challenger must be at least as capable on **every axis held in the data model — published or not** (A3), within the noise band ⟳ *v4.2 · A3*
  - [ ] **and** meaningfully cheaper by the price margin
  - [ ] Record which model is the dominator, so the UI can name it
- [ ] Compute `cost_per_successful_task = $/task ÷ success_rate` ⟳ *v4.2 · A14*
- [ ] Implement the Specialist overlay as a separate boolean, not a primary label
- [ ] Implement confidence inheritance: a derived number takes the lowest confidence of its inputs
- [ ] Write `tests/test_labels.py` with hand-built cases:
  - [ ] a clearly dominated model → Overpriced, with the right dominator named
  - [ ] a specialist that is worse on overall but better on its axis → **not** Overpriced
  - [ ] a one-point axis difference → treated as a tie, not an escape
  - [ ] a challenger that ties on published axes but loses on an **unpublished** axis → **not** a dominator ⟳ *v4.2 · A3*
- [ ] Write the consistency assertion from §6.3 as a test: no Overpriced model holds a top Value score

**Done when:** all label tests pass, including the specialist case that motivated the v4.1 amendment and the unpublished-axis case that A3 protects.

> This block is where the trust wedge lives. Take the tests seriously — the specialist case is the one that was wrong in the prototype and would have shipped a false accusation.

---

### Block 1.7: Snapshot writer

- [ ] Write `data/` layout: one folder per date, JSON files per entity
- [ ] Write `derive/snapshot.py` — assembles prices + capability + speed + task costs + derived into one dated snapshot
- [ ] **Recompute `$/task` daily** from cached tokens × that day's fresh price, at zero inference cost ⟳ *v4.2 · A11*
- [ ] Make snapshots immutable: never overwrite a past date
- [ ] Implement the **listing criteria** (A13) ⟳ *v4.2 · A13* — roster membership by objective gates plus a bounded cap:
  - [ ] **Hard gates (all must pass):** callable through the configured route · a pinned snapshot identifier exists · public per-token pricing (no quote-gated models) · present on LMArena · currently served (not deprecated)
  - [ ] **Caps:** max **3 models per provider**; overall cap ~**25**, ranked by Elo
  - [ ] Price-only models that pass no capability gate wait in a holding set
- [ ] Implement the retirement rule: stale-flag past the per-field threshold, retire from the default table at ~90 days cold, never delete history
- [ ] Implement freshness thresholds per field from spec §10.2

**Done when:** two consecutive daily snapshots exist on disk, both valid, the second did not modify the first, and the roster respects the gates and caps.

> **Known hazard (A13):** ranking purely by Elo and truncating at ~25 yields an all-frontier roster with no commodity end — which flattens the frontier chart. The per-provider cap is expected to mitigate it (most providers ship a small model beside a large one). If it doesn't, reserve slots across capability bands (open item 5).

---

### Block 1.8: Automation

- [ ] Write `.github/workflows/daily.yml` — cron job running price + capability ingestion, then snapshot assembly (including the daily `$/task` recompute)
- [ ] Store `OPENROUTER_API_KEY` as a GitHub secret
- [ ] Make the job commit the new snapshot back to the repo
- [ ] Add a manually-triggered workflow for the battery run, exposing the `--full` / `--model` / `--canary` modes (it costs money — it must never run on the daily cron)
- [ ] Add a **monthly** scheduled workflow that runs the drift-detection sweep ⟳ *v4.2 · A12*
- [ ] Have the daily job open an issue (not auto-run) when it detects a new or version-changed pinned model, so a paid run is always a deliberate act
- [ ] Add failure notification so a silently-broken cron doesn't rot the data

**Done when:** the daily action runs unattended for three consecutive days and produces three valid snapshots, and the monthly drift sweep is wired but gated.

---

### ■ STOP AND ASSESS — end of Phase 1

- [ ] Do three consecutive snapshots look right?
- [ ] Does a price change between days show up correctly, and does `$/task` recompute daily against it? ⟳ *v4.2 · A11*
- [ ] Does the stale flag fire when a source goes cold?
- [ ] Do the labels stay stable day to day, or do they flicker? (Flickering means thresholds are too tight.)
- [ ] Does the monthly sweep flag a simulated drift rather than silently overwriting it? ⟳ *v4.2 · A12*

---

## Phase 2: The MVP site

**Goal:** The live site — a single unified table, model pages, methodology, open data download. Static generation to GitHub Pages.

> **⟳ v4.2 · A1 — the visual direction changed.** v1 planned two views (Manager = Briefing light, Analyst = Terminal dark, toggle swaps theme). **v4.2 removes the two-view split and the dark theme entirely: one unified view, the Manager visual language retained, every Tier A column sortable.** `tokenticker_prototype_v3.html` is the reference implementation — port from it rather than restyling from scratch.

---

### Block 2.1: Static site skeleton

- [ ] Write `site/build.py` — reads the latest snapshot, renders Jinja2 templates to `site/dist/`
- [ ] Port the prototype v3 CSS token system into `site/templates/base.html` — **the single light theme only; there is no `body.analyst` dark variant** ⟳ *v4.2 · A1*
- [ ] Set up the page shell: header, footer (no mode toggle) ⟳ *v4.2 · A1*
- [ ] Confirm the page renders from real snapshot data

**Done when:** `python site/build.py` produces a page in `dist/` that opens in a browser and renders from a real snapshot.

---

### Block 2.2: The unified view

⟳ *v4.2 · A1* — **Merges v1's Block 2.2 (Manager) and 2.3 (Analyst) into one.** Eight Tier A columns, every one sortable. Tier B moves to the detail page (not a column picker).

- [ ] Render the eight Tier A columns:

  | # | Column | Contents |
  | --- | --- | --- |
  | 1 | Model | Name, provider, ticker, OPEN badge, rating signal bar on the row edge |
  | 2 | Cost to run a task | Hero; blended `$/M` as subline; clay treatment when the sticker price inverts against run cost |
  | 3 | Capability | Score + bar |
  | 4 | Elo | Chat Elo |
  | 5 | Speed | tokens/sec |
  | 6 | Context | Context window |
  | 7 | Rating | Efficient / Premium / Commodity / Overpriced, plus dominated-by or specialist annotation |
  | 8 | Confidence · Updated | Confidence dot + data age |

- [ ] Keep coding/reasoning **out of the columns** but in the record (they drive Rating) ⟳ *v4.2 · A3*
- [ ] Implement the honest-blank state for unmeasured `$/task`, including its sort behavior (labeled group at the bottom, ordered by blended `$/M`)
- [ ] Render the summary strip (cheapest to run, best value, frontier leader, models flagged overpriced)
- [ ] Implement search and the open/proprietary filter chips
- [ ] Implement column sorting on all eight columns
- [ ] Apply the density spec: row padding ~13px, container ~1240px, secondary numerics in mono ⟳ *v4.2 · A1*
- [ ] Render the frontier chart (X = `$/task` log scale, Y = capability) behind its toggle

**Done when:** the unified view renders from a real snapshot, every column sorts, and every number traces back to a snapshot field.

> **Deferred:** the v3.1 Analyst preset tabs (Value / Market / Performance / Use case) lived inside the removed Analyst view. They are not part of the MVP single view — revisit in V1 if wanted.

---

### Block 2.3: Model detail pages

⟳ *v4.2 · A2* — gains the peer rule.

- [ ] Generate one page per active model
- [ ] Layout: observed facts up top, derived value separated below — the two-layer split must be visible
- [ ] Source trace on every number: what it came from, when it was checked
- [ ] Show the Tier B fields here (input/output `$/M`, TTFT, modality, license, full per-host spread with qualification status, source links, **coding and reasoning scores**) ⟳ *v4.2 · A1, A3*
- [ ] Battery run detail: tokens per category behind the `$/task` figure, plus `success_rate` and (if published) `cost_per_successful_task` ⟳ *v4.2 · A14*
- [ ] Implement the **peer set** (A2): models within **±5 capability points** of the subject, excluding it, sorted ascending by `$/task`
  - [ ] Highlight the subject row in slate; highlight any peer that is both cheaper **and** equal-or-better on capability in teal
  - [ ] Make peer rows navigable to their own detail pages
  - [ ] Render the frontier chart with the ±5 band as a shaded horizontal strip
  - [ ] **Empty-band case:** where no model falls within ±5, state that the model has no direct substitute at its quality level — never widen the band silently
- [ ] Where a model is Overpriced, name and link the dominating model

**Done when:** every model has a page, every number on it has a visible source, and the peer band renders correctly including the empty-band case.

---

### Block 2.4: Methodology, corrections, and open data

- [ ] Write the methodology page from spec §13 — in plain language, with a worked `$/task` example
- [ ] State the MVP caveats explicitly:
  - [ ] **Three categories, not five** — and never present a three-category mean as if it were five ⟳ *v4.2 · A7*
  - [ ] Which categories are in the current suite (disclosure requirement)
  - [ ] How tasks are **procedurally generated** and how any third party can reproduce a snapshot from the seed + generator + grading code ⟳ *v4.2 · A8*
  - [ ] How tokens are counted (provider-reported, with the two Python checks) ⟳ *v4.2 · A10*
  - [ ] The compute-platform exclusion
  - [ ] What "cheapest qualifying" means
  - [ ] If `cost-per-successful-task` is published, how it's computed; if not, why it's held ⟳ *v4.2 · A14*
- [ ] Add the correction link on every page (opens a GitHub issue with the field pre-filled)
- [ ] Add the CSV/JSON download of prices, measured costs, and pass rates
- [ ] **Exclude AA-derived capability figures from the export** — it is redistribution, which AA's attribution license does not cover. Export owned data only (OpenRouter prices + measured token/cost + derived); link out to AA rather than rehosting its values. *(Block 0.3 decision)*
- [ ] Add the AA attribution footer sitewide — *"Model benchmark, pricing, and performance data provided by Artificial Analysis"*, linking **Artificial Analysis** to their homepage; stamp each AA figure with index version + retrieval date
- [ ] Publish the generator + grading code, and make clear what is owned data vs. attributed capability data ⟳ *v4.2 · A8*

**Done when:** a stranger could read the methodology page and reproduce one model's `$/task` — including regenerating its task instances from the published seed.

---

### Block 2.5: Ship

- [ ] Enable GitHub Pages on the repo
- [ ] Extend the daily action to rebuild and publish the site after each snapshot
- [ ] Check responsive behavior down to mobile
- [ ] Check keyboard focus is visible and every sortable header + row is reachable
- [ ] Confirm reduced-motion is respected (any ticker/animation must stop)
- [ ] Final pass: click every Overpriced label and confirm the named dominator is genuinely cheaper and at-least-as-capable **on every axis, published or not**

**Done when:** the site is live, rebuilding daily, and the last check passes on every Overpriced row.

---

### ■ STOP AND ASSESS — MVP shipped

Before starting V1 work:

- [ ] Has a non-technical reader used the unified view and reached a decision without help?
- [ ] Has anyone submitted a correction? (If the data is public and nobody corrects it, either it's right or nobody's reading.)
- [ ] Is the daily job stable, and does the monthly drift sweep behave?
- [ ] What does the battery cost per refresh in practice, at the calibrated `N`?
- [ ] Did `cost-per-successful-task` earn its place, or is it noise? (Settles open item 2.) ⟳ *v4.2 · A14*

---

## Phase 3 (V1): after the MVP

Not scoped in detail — deliberately. Revisit after the MVP has run for a few weeks.

- **Summarization category** + the three-family judge panel (majority vote), re-entering the fourth category ⟳ *v4.2 · A6, A7*
- **Long-context Q&A** re-entry — the 100K-token cost driver — restoring the five-category headline mean ⟳ *v4.2 · A7*
- Axis-aware labels: labels recompute against the selected Value axis, so switching to "reasoning" re-ranks the board for reasoning work *(the natural extension of the v4.1 amendment)*
- Suite pass rate as an owned capability axis — likely needs difficulty-calibrated generation to avoid ceiling effects ⟳ *v4.2 · open item 3*
- Use-case calculator with user-supplied success and latency inputs
- Price history and the frontier-over-time slider
- Alerts, saved views, public read API; possibly the Analyst preset tabs
- A second capability source for cross-checking

---

## Open items carried into the build

| Item | Where it resolves |
| --- | --- |
| Capability source for overall / coding / reasoning + AA terms | Block 0.3 *(v4.2 open item 1)* |
| Whether reasoning tokens are reliably readable | Block 0.5 |
| v0 generator + deterministic graders (3 categories) | Block 0.4 |
| Domination margin, noise band, Value anchors, zone boundaries, peer-band width | Block 0.7 |
| Real cost of one full battery sweep | Block 0.6 / 0.8 — sets the drift threshold and cost ceiling |
| Repeat count `N` | Block 0.8 (calibration study) *(closes A9)* |
| Whether to publish `cost-per-successful-task` at MVP | Block 0.6 / MVP stop-assess *(v4.2 open item 2)* |
| Sandbox grading harness | Block 0.8 → Block 1.4b |
| Canary / monthly drift threshold | Block 1.4a |
| Capability-band slot reservation if the per-provider cap under-fills the commodity end | Block 1.7 *(v4.2 open item 5)* |

---

*Chorus AI Systems — Daniel Wipert — TokenTicker Build Plan v2 (reconciled to Spec v4 + Amendment v4.2) — July 2026*
