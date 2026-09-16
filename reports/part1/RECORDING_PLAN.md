# Part 1 — Screen Recording Plan

**Target duration:** ~7 minutes  
**Format:** Screen capture with voice narration — terminal + editor + CSV  
**Goal:** Show the project runs, produces valid output, and demonstrate understanding of the decisions made.

---

## Segment 1 — Problem and Objective (0:00–0:35)

**Show:** `README.txt` or brief summary slide.

**Talking points:**
- LPDG runs ~320 radio gateways on rooftops and in basements.
- When a gateway fails, meters behind it stop reporting — nobody notices immediately. Weeks later it becomes a wrong bill or a manual meter read.
- The operations team can send **15 site visits per week**. Today: spreadsheet and gut feel.
- Every visit costs **€380**. A broken gateway left alone for a week costs **€600** — and it repeats every week it stays broken.
- The task: take historical telemetry and output a ranked list of 15 gateways to visit for each of 8 scoring Mondays.

---

## Segment 2 — Repository Structure (0:35–1:15)

**Show:** Project root in terminal (`ls`), then the `src/gateway_priority/` directory.

**Talking points:**
- Standard Python src-layout package: six focused modules.
- `config.py` — scoring schedule and algorithm constants.
- `data.py` — safe loading with point-in-time filtering (no future data leaks in).
- `baseline.py` — the 3-sigma ranking engine.
- `validation.py` — output contract enforced before writing.
- `pipeline.py` — CLI entry point; `--data` and `--out` flags, no hardcoded paths.
- One command to run everything: `make run`. Reads `./data` by default; accepts `--data /anywhere`.

---

## Segment 3 — Run make run (1:15–2:00)

**Show:** Run `make run` live in terminal. Let it complete. Point to validator output.

**Talking points:**
- Loads 1,433,387 telemetry rows from Parquet files.
- Runs internal schema validation before writing output.
- Official validator confirms: **15 gateways for each of 8 weeks, 2026-02-02 to 2026-03-23.**
- Output is deterministic — running it again produces the byte-identical file (MD5 `fbd532fe...`).
- 120/120 exact row parity against the supplied `predictions_baseline.csv`.

---

## Segment 4 — Show predictions.csv and Explain One Result (2:00–2:50)

**Show:** Open `predictions.csv`. Scroll to the first row.

**Selected row:**
```
week_start:  2026-02-02
rank:        1
gateway_id:  0A2778A31BE3
score:       43.0
reason:      43 hour(s) beyond 3 sigma of this gateway's own 28-day baseline
             in the last 7 days; first breach on disconnection_cnt
```

**Talking points:**
- Score = **43** means this gateway had 43 individual hours in the last 7 days where `disconnection_cnt` exceeded its own 28-day historical mean by more than 3 standard deviations.
- The maximum possible score is 168 (7 × 24). A score of 43 is the highest that week.
- The system is prioritising this gateway for inspection. It is **not** claiming confirmed failure — it is flagging unusual behaviour relative to the gateway's own history.
- The field team decides what to do when they get there.

---

## Segment 5 — Explain the 3-Sigma Baseline (2:50–3:40)

**Show:** Open `src/gateway_priority/baseline.py`. Point to the core ranking logic.

**Talking points:**
- For each scoring Monday T, take 28 days of telemetry **strictly before T** — point-in-time safe.
- Compute mean (μ) and standard deviation (σ) per gateway across three metrics: `offline_duration_sec`, `disconnection_cnt`, `reboot_cnt`.
- Look at the most recent 7 days. For each hour: flag it if `value > μ + 3σ`.
- Gateways with σ = 0 (perfectly consistent behaviour) produce no flags.
- Sum flagged hours → **score**. Sort descending. Top 15 dispatched.
- This is the supplied baseline. Part 1 reproduces it exactly. Part 2 will evaluate whether improvements to this logic reduce the €380/€600 operational cost.

---

## Segment 6 — One Data Audit Finding (3:40–4:30)

**Show:** Open `reports/data_audit/DATA_AUDIT.md`. Scroll to Section 4 (Duplicates) then Section 5 (Windows).

**Talking points (duplicates):**
- Audit found **6,547 duplicate `(gateway_id, timestamp)` key groups** across 8 months of telemetry — 13,094 total rows.
- Every single one is an **exact duplicate**: same values, zero conflicting groups.
- Materiality experiment: remove duplicates, rerun baseline → **zero score changes, zero rank changes, zero top-15 swaps** across all 8 weeks.
- Decision: preserve baseline input semantics for Part 1. A production pipeline would handle deduplication idempotently.

**Talking points (window overlap):**
- The 28-day reference window contains the 7-day detection window.
- This is **not future-data leakage** — all observations are before Monday T.
- It is **self-normalisation**: recent abnormal values inflate the baseline statistics, reducing anomaly sensitivity. That is a modelling trade-off for Part 2 to evaluate.

---

## Segment 7 — DECISIONS.md and Part 2 Choice (4:30–5:15)

**Show:** Open `DECISIONS.md`. Scroll through the five decision headings.

**Talking points:**
- Five decisions, each with: what was chosen, what alternative was considered, and why the alternative was rejected.
- Decision 1: reproduce the baseline exactly — gives a controlled reference before changing anything.
- Decision 2: overlapping windows are a modelling limitation, not leakage — the terminology matters because misidentifying the problem leads to unjustified changes.
- Decision 5: **Part 2 = Data Science.**
- Why Data Science over Machine Learning: the brief explicitly refuses to define "needs a visit" — that definition is the core problem. Historical field visits are selection-biased. ML would add complexity before the evaluation framework is defensible. Data Science builds the honest cost framework first.

---

## Segment 8 — LIMITATIONS.md (5:15–5:55)

**Show:** Open `LIMITATIONS.md`. Scroll through "What It Cannot Do."

**Talking points:**
- The **anomaly score is not a failure probability** — it measures unusual telemetry relative to the gateway's own history.
- Part 1 does **not optimise the €380/€600 cost** — that is Part 2.
- Silent gateways — those that stop emitting entirely — **score zero** and are invisible to this approach.
- Rank-15 ties in **7 of 8 weeks** — the 15th slot currently depends on arbitrary DataFrame ordering.
- The two-week plan is realistic: define outcome, build cost simulator, test improvements, produce operations-manager charts.
- No fake accuracy, precision, or ROI claims anywhere.

---

## Segment 9 — AI-USAGE.md and Mistake Caught (5:55–6:25)

**Show:** Open `AI-USAGE.md`. Highlight "What AI Got Wrong."

**Talking points:**
- AI was used for: planning phases, reviewing structure, drafting tests, debugging packaging, suggesting audit checks, and structuring documentation.
- **Genuine mistake:** AI initially called the overlapping reference/detection windows "target leakage."
- Human review corrected it: all telemetry in both windows is strictly before Monday T — no future data involved. The correct term is **reference-window overlap / self-normalisation**.
- This matters because calling it leakage implies it must be fixed immediately. Calling it self-normalisation frames it correctly as a trade-off to evaluate.
- All AI suggestions verified through: tests, official validator, baseline parity comparison, data audit, type checking, and manual review.

---

## Segment 10 — Reproducibility Summary (6:25–7:00)

**Show:** Show `pytest` output (33 passed), `git log --oneline`.

**Talking points:**
- **33 tests** covering ID normalisation, point-in-time filtering, score calculation, validation schema, and end-to-end pipeline.
- **7 incremental commits** — normal development history.
- pyright: **0 errors, 0 warnings**.
- `make run` twice → byte-identical output every time.
- The pipeline accepts `--data` and `--out` — ready to run on unseen data live.
- Part 2 will define "needs a visit," build a rolling cost backtest using €380/€600, and produce charts for the operations manager.
