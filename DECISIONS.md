# Decisions

Five key decisions made during Part 1, and for each: what else we could have done and why we did not.

---

## Decision 1 — Reproduce the Supplied Baseline Exactly for Part 1

**Chosen:** Modularly reimplement the supplied 3-sigma baseline (`baseline_3sigma.py`) as a clean Python package (`gateway_priority`), preserving its exact semantics.

**Alternative considered:** Immediately redesign the anomaly detection algorithm — for example, separate the reference/detection windows, add telemetry gap features, or incorporate meter-read data.

**Why we rejected the alternative:** Part 1 rewards a *working* prioritisation system, and the supplied baseline is explicitly acceptable ("You are welcome to use it exactly as it is and never train anything"). Exact reproduction provides a controlled, verified reference point. Any scoring improvement is meaningless without first proving the baseline works and understanding what it does. Premature changes risk introducing unvalidated behaviour.

**Evidence:** 120/120 exact row parity between our `predictions.csv` and the supplied `predictions_baseline.csv` (verified in Phase 1.4). Score range 15–43 flagged hours, deterministic output across repeated runs (MD5 `fbd532fe4364809a9cae5c218f0f8841`).

**Trade-off:** We defer potential ranking improvements to Part 2. Part 1 scores match the baseline, which the brief states is acceptable for non-ML areas.

---

## Decision 2 — Treat Overlapping Windows as a Modelling Limitation, Not Future-Data Leakage

**Chosen:** Preserve the baseline's overlapping window construction — reference window [T−28 days, T) contains the detection window [T−7 days, T) — and document the resulting self-normalisation effect.

**Alternative considered:** Immediately separate the windows into a non-overlapping reference period [T−28 days, T−7 days) and detection period [T−7 days, T).

**Why we rejected the alternative:** Both windows contain only observations *before* scoring Monday T, so this is not future-data leakage. The overlap is a modelling design choice that reduces anomaly sensitivity (recent abnormal values inflate the baseline mean and standard deviation). Our audit showed that separating the windows changes top-15 gateway membership by 4–7 gateways per week, but that alone does not prove the separated window produces lower operational cost. Making this change without an honest cost evaluation would be speculation.

**Evidence:** Phase 1.2A audit confirmed the overlap is present in all 8 scoring weeks and quantified the 4–7 gateway membership difference. All telemetry used in both windows is strictly before T.

**Trade-off:** We retain a known sensitivity reduction. Part 2 will evaluate whether window separation reduces the combined €380 wasted-visit and €600/week missed-broken-gateway cost.

---

## Decision 3 — Preserve Exact Duplicate Telemetry Rather Than Deduplicate

**Chosen:** Detect and audit all duplicate telemetry records but preserve the baseline's input data as-is for Part 1 scoring.

**Alternative considered:** Automatically deduplicate telemetry by removing exact duplicate rows before scoring.

**Why we rejected the alternative:** All 6,547 duplicate key groups (13,094 total rows) are exact duplicates — zero conflicting groups exist. Removing them produced zero score changes, zero rank changes, and zero top-15 membership swaps across all 8 scoring weeks. Deduplication would add a processing step with no demonstrated prediction benefit and would break exact parity with the supplied baseline.

**Evidence:** Phase 1.2 audit: 6,547 duplicate `(gateway_id, ts_utc)` groups, all exact, 0 conflicting. Materiality experiment: 0/120 scores changed, 0/120 ranks changed, 0 top-15 swaps.

**Trade-off:** A production data pipeline should normally handle deduplication explicitly and idempotently. This remains appropriate for Part 2 data engineering work.

---

## Decision 4 — Preserve Supplied Tie-Breaking Behaviour in Part 1

**Chosen:** Retain the baseline's implicit stable-sort tie-breaking at the rank-15 cutoff boundary.

**Alternative considered:** Introduce a deterministic business-informed tie-breaker — for example, using meter-read success rate, recent field visit history, or telemetry gap duration as secondary sort criteria.

**Why we rejected the alternative:** Rank-15 score ties occur in 7 out of 8 scoring weeks, with 3–4 gateways sharing the exact cutoff score. However, no evidence yet exists that any specific tie-breaker reduces operational cost. Introducing one without cost evaluation would be an arbitrary choice disguised as an improvement. The baseline's stable-sort behaviour is the controlled reference.

**Evidence:** Phase 1.2 audit confirmed ties in weeks 2026-02-09 through 2026-03-23 (7/8 weeks). The only tie-free week is 2026-02-02.

**Trade-off:** Tied gateways at the rank-15 boundary are selected by pandas DataFrame insertion order, which is data-dependent rather than operationally meaningful. Part 2 will evaluate candidate tie-breakers under cost simulation.

---

## Decision 5 — Part 2 Area: Data Science

**Chosen area:** D — Data Science.

**What this means:** Part 2 will focus on answering the question the brief explicitly refuses to answer: *what does "needs a visit" mean?* Specifically:

- Define a defensible outcome variable using field visits, telemetry patterns, and meter-read evidence, with strict point-in-time rules.
- Build a rolling backtest with the €380 wasted-visit and €600/week missed-broken-gateway costs as the evaluation metric — not accuracy, precision, or recall in isolation.
- Evaluate threshold and top-k policies: where to draw the line, and what moving it costs in each direction.
- Produce uncertainty ranges rather than a single unsupported number: how much the result moves depending on which gateways and weeks are tested on.
- Create charts aimed at the operations manager showing cost trade-offs, not technical model diagnostics.

**Alternative considered:** E — Machine Learning.

**Why we rejected the alternative:** The immediate challenge is *decision quality and honest evaluation*, not model complexity. The supplied 3-sigma baseline provides a strong controlled starting point. Historical field visit labels are selection-biased (the team only visited gateways they already suspected), so training a supervised model on them without careful outcome definition risks learning the current selection policy rather than improving it. ML would add implementation complexity before the target variable and evaluation framework are defensible. This does not mean ML is inappropriate — it means the foundation for responsible ML use needs to be built first, and that foundation is data science.

**Trade-off:** We forgo potential gains from a learned model in exchange for a rigorous evaluation framework that could later support ML if justified by cost evidence.
