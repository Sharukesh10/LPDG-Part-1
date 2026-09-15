# Part 1 — Screen Recording Plan

**Target duration:** 6–8 minutes (aim for ~7 minutes)  
**Format:** Screen capture with voice narration. Show terminal, editor, and CSV output.  
**Goal:** Demonstrate that Part 1 runs, produces valid output, and that you understand the choices made.

---

## Segment 1 — Problem and Objective (0:00–0:35)

**Show:** The challenge README.txt or brief summary.

**Talking points:**
- LPDG runs a radio network of ~320 gateways on rooftops and in basements.
- When a gateway fails, meters behind it stop reporting — nobody notices immediately.
- The operations team can send 15 site visits per week. Today they choose from a spreadsheet.
- The task: take historical telemetry data and produce a ranked list of 15 gateways to visit each week, for 8 scoring Mondays.
- Every visit costs €380. A broken gateway left alone costs €600/week. That trade-off drives everything.

---

## Segment 2 — Repository Structure and One-Command Run (0:35–1:15)

**Show:** Project root in terminal (`ls`) and then the Makefile.

**Talking points:**
- The project uses a standard Python src-layout package: `src/gateway_priority/`.
- Six modules: config, ids, data, baseline, validation, pipeline.
- One command to run everything: `make run`.
- Data is read from `./data` by default; accepts `--data /other/path`.
- No hardcoded paths — runs on any machine that has the data folder.

---

## Segment 3 — Run make run and Show Validator PASS (1:15–2:00)

**Show:** Run `make run` in terminal live. Let it complete. Show the validator output.

**Talking points:**
- Pipeline loads 1,433,387 telemetry rows from Parquet files.
- Runs internal schema validation before writing output.
- Official validator confirms: 15 gateways for each of 8 weeks, 2026-02-02 to 2026-03-23.
- Output is deterministic — running it again produces the byte-identical file.

---

## Segment 4 — Show predictions.csv and Explain One Row (2:00–2:50)

**Show:** Open `predictions.csv` in the editor or terminal. Scroll to week 2026-02-02. Point to rank-1 row.

**Selected row:**
```
week_start:  2026-02-02
rank:        1
gateway_id:  0A2778A31BE3
score:       43.0
reason:      43 hour(s) beyond 3 sigma of this gateway's own 28-day baseline in the last 7 days; first breach on disconnection_cnt
```

**Talking points:**
- Score = 43 means this gateway had 43 individual hours in the last 7 days where its disconnection count exceeded its own 28-day mean by more than 3 standard deviations.
- The maximum possible score is 168 (7 × 24). No gateway comes close to that here.
- This gateway ranks first that week — the system is prioritising it for inspection.
- Importantly: the system is **not** claiming this gateway is definitely broken. It is flagging unusual behaviour relative to its own history. Human judgement and the site visit itself determine whether action is needed.
- 120 rows total. 100% exact parity with the supplied baseline.

---

## Segment 5 — Explain the 3-Sigma Baseline (2:50–3:40)

**Show:** Open `baseline_3sigma.py` briefly, or `src/gateway_priority/baseline.py`.

**Talking points:**
- For each scoring Monday T, take 28 days of telemetry strictly before T.
- Compute mean and standard deviation per gateway across three metrics: `offline_duration_sec`, `disconnection_cnt`, `reboot_cnt`.
- Look at the most recent 7 days. For each hour, flag it if the value exceeds mean + 3×std.
- Sum flagged hours → score. Sort descending. Top 15 are dispatched.
- Zero-std gateways (perfectly consistent behaviour) are excluded — their flagged hours default to zero.
- This is the supplied baseline. Part 1 reproduces it exactly. Part 2 will evaluate whether improvements to this approach reduce the €380/€600 cost.

---

## Segment 6 — One Important Data Audit Finding (3:40–4:30)

**Show:** Open `reports/data_audit/DATA_AUDIT.md`, scroll to Section 4 (Duplicate Telemetry).

**Talking points:**
- The data audit found 6,547 duplicate `(gateway_id, timestamp)` key groups in the telemetry Parquet files — 13,094 total rows involved.
- Every single one is an **exact** duplicate: same gateway, same timestamp, same metric values. Zero conflicting duplicates.
- We ran a materiality experiment: remove duplicates, rerun baseline. Result: zero score changes, zero rank changes, zero top-15 membership swaps across all 8 weeks.
- Decision: preserve baseline input semantics for Part 1. A production pipeline would handle deduplication idempotently.
- Alternatively, show the reference-window overlap finding in Section 5: the 7-day detection window sits inside the 28-day reference window, which reduces anomaly sensitivity through self-normalisation. This is not future-data leakage — all observations are before Monday T. It's a modelling trade-off for Part 2 to evaluate.

---

## Segment 7 — DECISIONS.md and Part 2 Area (4:30–5:15)

**Show:** Open `DECISIONS.md`. Scroll through headings.

**Talking points:**
- Five decisions, each with an alternative considered and why it was rejected.
- Decision 1: reproduce the baseline exactly — gives a controlled reference; changing it before understanding it would be speculation.
- Decision 2: overlapping windows are a modelling limitation, not future leakage — the terminology matters because calling it leakage implies it must be fixed immediately.
- Decision 5 is the required Part 2 area: **Data Science**.
- Why Data Science over Machine Learning: the brief explicitly refuses to define "needs a visit." That definition is the core problem. ML would add complexity before the evaluation framework is defensible. The historical field visits are selection-biased — not a random sample. Data Science builds the honest evaluation framework first; ML can follow from that foundation if justified.

---

## Segment 8 — LIMITATIONS.md (5:15–5:55)

**Show:** Open `LIMITATIONS.md`. Scroll through the "What It Cannot Do" section.

**Talking points:**
- Eight limitations, all evidence-backed.
- The score is not a calibrated failure probability — it measures unusual telemetry, not confirmed faults.
- Silent gateways — those that stop emitting entirely — score zero and are invisible to this approach.
- No cost optimisation yet. The €380/€600 trade-off is not in the ranking logic.
- Rank-15 ties in 7 of 8 weeks: three or four gateways share the exact cutoff score, so the 15th slot depends on arbitrary DataFrame ordering.
- No fake accuracy or cost-saving claims anywhere in the documentation.
- The two-week plan is realistic: define the outcome variable, build the cost simulator, test candidate improvements, produce operations-manager charts.

---

## Segment 9 — AI-USAGE.md and Mistake Caught (5:55–6:25)

**Show:** Open `AI-USAGE.md`. Highlight the "What AI Got Wrong" section.

**Talking points:**
- AI was used for planning phases, drafting tests, debugging the packaging issue, and structuring documentation.
- The genuine mistake: AI initially described the overlapping reference/detection windows as "target leakage."
- Human review caught this. All telemetry in both windows is strictly before Monday T — no future data is used. The correct term is reference-window overlap or self-normalisation.
- This matters because calling it leakage implies the algorithm must be changed. Calling it self-normalisation correctly frames it as a trade-off to evaluate under operational cost — which is the Part 2 plan.
- All AI suggestions were verified through: tests, official validator, baseline parity comparison, data audit, static type checking, and manual review.

---

## Segment 10 — Reproducibility Summary and What Comes Next (6:25–7:00)

**Show:** Run `pytest` briefly, or show the test count. Show `git log --oneline`.

**Talking points:**
- 33 tests, all passing. Covers ID normalisation, point-in-time filtering, score calculation, validation schema, and end-to-end pipeline.
- Six incremental commits — normal development history, not one big commit at the end.
- pyright: 0 errors, 0 warnings.
- Predictions are deterministic: running `make run` twice produces the byte-identical file.
- The code accepts `--data` for any path and `--out` for any output location — ready to run on unseen data in a live session.
- Part 2 will focus on Data Science: defining "needs a visit," building a rolling cost backtest, and producing charts for the operations manager.
