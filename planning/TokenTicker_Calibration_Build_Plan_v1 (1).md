# TokenTicker — Calibration Study Build Plan v1

**Chorus AI Systems · July 2026**

Prerequisite for the owned task battery. Determines the repeat count `N` left unlocked by spec amendment A9.

---

## Purpose

The battery generates fresh task instances each snapshot (A8). Fresh instances introduce run-to-run variance. Before locking a repeat count, measure how much variance actually exists.

**Two quantities to measure:**

1. **Token consumption spread** across procedurally generated instances of equivalent difficulty — this drives cost per task, the hero metric
2. **Pass rate spread** across the same instances — this drives success rate

**Output:** a defensible value for `N`, plus the interval that success rate carries at that `N`.

---

## Scope

Deliberately narrow. One category, four models.

| Parameter | Value | Why |
|---|---|---|
| Category | Coding | Deterministically graded by construction; certain to be in the final suite; real token variance |
| Instances | 5 | Enough to separate instance variance from run variance |
| Models | 4 | Must include at least one reasoning model — that is where token variance lives |
| Repeats | 10 per task per model | Enough to estimate spread |
| **Total calls** | **200** | |

**Estimated cost: under $5.** Coding tasks are small in both directions. The reasoning model dominates the bill and still costs cents per call.

**Model selection:** one reasoning model, one frontier non-reasoning model, one mid-tier, one small. Four distinct families per Chorus reference stack discipline.

---

## Block 1 — Task generator

Produce coding task instances from a template grammar with a published seed.

**Each instance emits three artifacts:**
- Problem statement (the prompt sent to the model)
- Reference solution (for sanity-checking the generator, not for grading)
- Unit test suite (the grader)

**Design constraint:** instances from the same template must be comparable in difficulty *and* in expected token size. Randomize content — data shapes, edge cases, identifiers, constraint values — not scale. If one instance needs a 20-line solution and another 200, the variance measurement is contaminated by difficulty rather than measuring instance noise.

**Seeded and reproducible:** the same seed produces the same five instances, byte for byte.

**Done when:** running the generator twice with one seed produces identical instances; running with five different seeds produces five instances whose reference solutions fall within a narrow line-count band.

---

## Block 2 — Runner

Call each model against each instance, N times, recording everything.

**Records per call:**
- Model identifier — **pinned snapshot**, never an alias (A12)
- Instance seed and identifier
- Repeat index
- Prompt tokens, completion tokens, reasoning tokens where reported
- Wall-clock latency and time to first token
- Raw response text
- Timestamp
- Error class where the call failed

**Requirements:**
- Provider-reported usage taken from the API response (A10)
- Survives errors without losing the run — record the failure, continue, never retry silently in a way that hides it
- Rate-limit backoff
- Every record written to disk as it completes, not batched at the end

**Done when:** a full 200-call sweep completes and produces 200 records, with any failures explicitly recorded as failures rather than missing.

---

## Block 3 — Grader

Execute model-produced code against the generated unit tests. Return pass/fail.

**This block runs code written by a language model. It needs a real sandbox.**

Minimum isolation:
- Subprocess execution, never `exec()` or `eval()` in the host process
- No network access
- Filesystem jail — a scratch directory, nothing outside it
- Hard wall-clock timeout
- Memory ceiling

**Failure taxonomy — a task can fail in distinguishable ways, and collapsing them loses information:**

| Outcome | Meaning |
|---|---|
| `pass` | All tests passed |
| `fail_tests` | Code ran, tests failed |
| `fail_error` | Code raised at runtime |
| `fail_syntax` | Code did not parse |
| `fail_timeout` | Exceeded wall-clock limit |
| `fail_extract` | No code block could be recovered from the response |
| `error_infra` | Sandbox or harness fault — **not the model's failure**, excluded from pass rate |

**Done when:** a known-good reference solution passes, a known-bad solution fails with the correct classification, an infinite loop times out cleanly, and a solution attempting network or filesystem access outside the jail is contained.

**Time note:** this is the block most likely to consume a full day. It is a solved problem but not a one-liner, and getting the isolation wrong is worse than getting it slow.

---

## Block 4 — Variance analysis

Compute the numbers the study exists to produce.

**Per model, per instance, across repeats:**
- Mean, median, standard deviation, coefficient of variation of total tokens
- Same for cost, computed as `tokens × published price` (A10 — never a provider cost field)
- Pass rate and its spread

**Per model, across instances:**
- How much of total token variance is between-instance versus within-instance. Between-instance variance is generator design; within-instance is model nondeterminism. **They have different fixes and must not be conflated.**

**The deliverable:**
- Smallest `N` at which mean cost per task falls inside a stated tolerance — propose ±5%
- The confidence interval success rate carries at that `N`
- Whether the reasoning model behaves differently enough to warrant a per-model `N`

**Done when:** the following sentence can be completed with measured numbers — *"At N = ___, cost per task is stable to within ___%, and success rate carries an interval of ±___ percentage points."*

---

## Sequence

```
Block 1 (generator)  ──┐
                       ├──►  Block 2 (runner)  ──►  Block 3 (grader)  ──►  Block 4 (analysis)
Model selection      ──┘
```

Blocks 1 and 3 can be built in parallel with a stubbed interface between them — the grader needs only a code string and a test file, so it can be developed against handwritten samples before the generator is finished.

---

## What this study does not decide

- Task content for extraction and reasoning categories
- Total suite size
- Whether cost-per-successful-task publishes at MVP (open item 2)
- Anything about capability sourcing (open item 1 — independent track)

---

## Exit criteria

The calibration study is complete when `N` is set from measurement and spec amendment A9 can be closed with a number.

At that point the full battery build plan can be written against known variance, known per-sweep cost, and a known grading harness.
