# AI Usage

How AI tools were used during this project, and what they got wrong.

---

## How AI Was Used

AI assistance (large language model) was used during development for:

1. **Planning implementation phases** — structuring the project into reproducible phases (baseline reproduction → data audit → pipeline build → freeze → documentation) to avoid ad-hoc development.

2. **Reviewing project structure** — suggesting the standard setuptools src-layout packaging for `gateway_priority` and organising modules (config, ids, data, baseline, validation, pipeline).

3. **Generating and refining tests** — drafting unit tests for gateway ID normalisation, point-in-time filtering, validation schema enforcement, and end-to-end pipeline integration. Tests were reviewed, adjusted, and verified by hand.

4. **Debugging Python packaging and import configuration** — diagnosing a `pyright` / Pylance import resolution issue caused by the `src/` layout. The fix involved correcting `pyproject.toml` package discovery, adding `pyrightconfig.json`, and verifying that both runtime imports and static analysis resolved correctly.

5. **Suggesting audit checks** — proposing specific data quality investigations (duplicate telemetry keys, cross-dataset gateway reconciliation, point-in-time filtering validation, zero-standard-deviation behaviour, rank-15 tie analysis).

6. **Helping structure documentation** — drafting report outlines, table formats, and section structures for phase reports.

7. **Reviewing terminology and assumptions** — discussing the distinction between future-data leakage and reference-window contamination (see below).

---

## What AI Got Wrong

**AI initially described the overlapping baseline windows as "target leakage."**

During the Phase 1.2 data audit, the AI characterised the overlap between the 28-day reference window [T−28d, T) and the 7-day detection window [T−7d, T) as "target leakage" and "future-data leakage."

**Why this was wrong:** All telemetry in both windows occurs strictly before scoring Monday T. No data from the future is used. The term "target leakage" implies that information from the prediction target has contaminated the training features — but there is no supervised target here, and no temporal boundary violation. Using the term "leakage" incorrectly could have led to an unjustified algorithm change: separating the windows to "fix" a problem that does not exist in the way described.

**How we caught it:** During human review of the audit report, the temporal semantics were re-examined. The reference window is computed from data available before T; the detection window is also computed from data available before T. The issue is not leakage but *self-normalisation*: recent abnormal values inflate the reference statistics against which they are then evaluated, reducing anomaly sensitivity.

**What we corrected it to:** The behaviour is now described as "reference-window contamination," "reference-window overlap," or "self-normalisation" throughout all project documentation. The term "future-data leakage" is reserved strictly for situations where data from after Monday T would be used (e.g., using the engineer review from 2026-02-15 for scoring weeks before that date).

**Why this matters:** Terminology drives decisions. Calling something "leakage" implies it must be fixed. Calling it "self-normalisation" correctly frames it as a modelling trade-off to be evaluated under operational cost — which is the approach taken in Part 2.

---

## Verification of AI-Generated Suggestions

All AI-generated code and suggestions were verified through:

- **Automated tests** — pytest suite (33/33 passing) covering ID normalisation, data loading, point-in-time filtering, score calculation, validation schema, and end-to-end pipeline.
- **Supplied validator** — `validate_submission.py` confirms `predictions.csv` format and constraints.
- **Baseline parity comparison** — 120/120 exact row match against `predictions_baseline.csv`.
- **Data audit** — empirical verification of duplicate counts, cross-dataset reconciliation, window overlap effects, and tie-break behaviour.
- **Static type checking** — pyright with zero errors and zero warnings across all source, script, and test files.
- **Manual review** — human review of all documentation claims, terminology, and quantitative assertions against verified project output.
