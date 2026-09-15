# Part 1 — Final Acceptance Review

**Phase:** 1.6 — Final Acceptance Review  
**Date:** 2026-09-16  
**Reviewed against:** LPDG Innovation Hub Selection Challenge 2026 Brief

---

## Requirement Checklist

### Requirement 1 — One-Command Execution
**Status: PASS**

- `make run` executes the full pipeline, runs internal validation, writes `predictions.csv`, and checks it with the official validator.
- Data is read from `./data` by default. Alternate path supported via `--data /other/path`.
- No hardcoded user-specific paths in source, scripts, or tests.
- Dependencies documented in `requirements.txt` and `README.md`.
- Installation documented in `README.md` (Quick Start section).
- Output: `predictions.csv: OK — 15 ranked gateways for each of 8 weeks, 2026-02-02 to 2026-03-23`

---

### Requirement 2 — predictions.csv
**Status: PASS**

| Property | Expected | Actual |
| :--- | :--- | :--- |
| Columns | `week_start, rank, gateway_id, score, reason` | ✅ Exact match |
| Total rows | 120 | ✅ 120 |
| Weeks | 8 (2026-02-02 to 2026-03-23) | ✅ All 8 present |
| Rows per week | 15 | ✅ 15 every week |
| Ranks per week | 1–15, no gaps | ✅ Verified |
| Duplicate gateway per week | 0 | ✅ 0 |
| Score | Numeric, finite, no missing | ✅ `float64`, range 15–43 |
| Reason | Non-empty string, ≤ 300 chars | ✅ Max 120 chars |
| Official validator | PASS | ✅ PASS |
| Baseline parity | 120/120 | ✅ 100.00% exact rows |
| Deterministic MD5 | Consistent | ✅ `fbd532fe4364809a9cae5c218f0f8841` |

---

### Requirement 3 — DECISIONS.md
**Status: PASS**

Five decisions present, each with chosen approach, alternative considered, and reason for rejection:

| # | Decision |
| :--- | :--- |
| 1 | Reproduce supplied baseline exactly for Part 1 |
| 2 | Treat overlapping windows as modelling limitation, not future-data leakage |
| 3 | Preserve exact duplicate telemetry rather than deduplicate |
| 4 | Preserve supplied tie-breaking behaviour in Part 1 |
| 5 | **Part 2 area: Data Science** — defines "needs a visit," builds cost simulator, evaluates threshold policy |

Decision 5 explicitly states Part 2 area = **Data Science** and explains why Machine Learning was not chosen.

---

### Requirement 4 — What It Cannot Do
**Status: PASS**

`LIMITATIONS.md` contains:

**"What It Cannot Do"** — 8 evidence-backed limitations:
1. Does not prove a gateway requires a visit
2. Does not optimise €380/€600 operational cost
3. Silent telemetry gaps not in score
4. Rank-cutoff ties ambiguous (7/8 weeks)
5. Reference/detection windows overlap (self-normalisation)
6. Historical field visits are selection-biased
7. Engineer review temporally limited (2026-02-15)
8. Rankings without calibrated uncertainty

**"What Another Two Weeks Would Fix"** — 14-day plan with specific milestones.

No unsupported accuracy, cost-saving, or ROI claims present.

---

### Requirement 5 — AI-USAGE.md
**Status: PASS**

- 7 categories of AI tool usage documented.
- Verification methods described (tests, validator, parity, audit, type-checking, manual review).
- **Genuine AI error documented:** AI characterised overlapping reference/detection windows as "target leakage." Human review corrected this — all observations are before scoring Monday T, making this reference-window overlap / self-normalisation, not future-data leakage. Correction matters because misidentifying the problem would justify an unjustified algorithm change.

---

### Requirement 6 — Normal Commit History
**Status: PASS**

6 logical, incremental commits — no squashing, no single giant final commit:

```
dc5a1a8  docs: document Part 1 decisions, limitations, and AI usage
cfe8a99  docs: Phase 1.4 — freeze final Part 1 predictions
666a041  test: add prediction parity and validation checks
aaa2fe0  feat: add modular baseline prediction pipeline
f34a083  test: add gateway data audit and safety checks
4d0c387  chore: initialise reproducible challenge environment
```

- No raw challenge data tracked (`data/` in `.gitignore`).
- No credentials, tokens, or `.env` files present.
- No machine-specific absolute paths.
- No files over 1 MB tracked.

---

### Requirement 7 — 6–8 Minute Screen Recording
**Status: PENDING HUMAN ACTION**

The recording cannot be completed by automated tooling. See `RECORDING_PLAN.md` for the structured 7-minute script with segment timings and talking points.

**Selected row for demonstration in recording:**
```
week_start:  2026-02-02
rank:        1
gateway_id:  0A2778A31BE3
score:       43.0
reason:      43 hour(s) beyond 3 sigma of this gateway's own 28-day baseline
             in the last 7 days; first breach on disconnection_cnt
```

Plain-language explanation: This gateway had 43 hours in the last 7 days where its disconnection count exceeded its own 28-day historical mean by more than 3 standard deviations. The system is prioritising it for inspection — it is not claiming confirmed failure.

---

## Technical Regression Results

| Check | Result |
| :--- | :--- |
| `make run` | PASS |
| Official validator | PASS |
| `pytest` | 33/33 PASS |
| `pyright` | 0 errors, 0 warnings |
| Frozen predictions MD5 | `fbd532fe4364809a9cae5c218f0f8841` (unchanged) |

---

## Repository Safety

| Check | Status |
| :--- | :--- |
| Raw challenge data tracked | No (`data/` excluded by `.gitignore`) |
| `.env` / credentials / tokens | None found |
| Hardcoded machine-specific paths | None found |
| Files > 1 MB tracked | None |

---

## Public Repository Readiness

The repository contains all required code and documentation and does not contain the supplied raw challenge data. It is structurally ready for publication. **Do not publish until the screen recording is complete and the submission deadline actions are confirmed.**

---

## Overall Status

> **PART 1 — TECHNICAL REQUIREMENTS: PASS**  
> **PART 1 — FULL COMPLETION: PENDING** (Requirement 7 — screen recording requires human action)

Part 1 is not marked complete while the recording is outstanding.
