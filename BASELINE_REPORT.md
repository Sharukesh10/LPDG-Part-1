# Baseline Reproduction Report (Phase 1)

## Executive Summary
- **Phase 1 Status**: **PASS**
- **Execution Date**: 2026-09-15
- **Validator Result**: **PASS (OK)** — 15 ranked gateways for each of 8 weeks (120 predictions total).

---

## 1. Environment Information
- **Operating System**: macOS (Darwin arm64)
- **Python Version**: Python 3.9.6
- **Virtual Environment**: `.venv` (created via `python3 -m venv .venv`)
- **Key Installed Dependencies**:
  - `pandas` == 2.3.3
  - `numpy` == 2.0.2
  - `pyarrow` == 21.0.0
  - `openpyxl` == 3.1.5

---

## 2. Dependencies (`requirements.txt`)
The baseline script `baseline_3sigma.py` and validator script `validate_submission.py` require the following core dependencies:
```text
numpy>=2.0.0
pandas>=2.2.0
pyarrow>=15.0.0
```

---

## 3. Commands Executed & Outputs

### Step E: Baseline Execution Command
```bash
.venv/bin/python baseline_3sigma.py --data data --out predictions_baseline.csv
```
**Output**:
```text
wrote predictions_baseline.csv — 120 rows over 8 weeks
```

### Step F: Validation Command
```bash
.venv/bin/python validate_submission.py predictions_baseline.csv
```
**Output**:
```text
predictions_baseline.csv: OK
  15 ranked gateways for each of 8 weeks, 2026-02-02 to 2026-03-23
```

---

## 4. Verification of `predictions_baseline.csv`
- **Total Row Count**: Exactly 120 rows (15 rows/week × 8 weeks).
- **Scored Weeks Count**: Exactly 8 weeks (`2026-02-02`, `2026-02-09`, `2026-02-16`, `2026-02-23`, `2026-03-02`, `2026-03-09`, `2026-03-16`, `2026-03-23`).
- **Rows per Week**: Exactly 15 rows for every week.
- **Ranks**: 1 to 15 for every week without gaps or duplicates.
- **Gateway Uniqueness**: No duplicate gateway within any single week.
- **Scores**: Numeric float values (`float64`, min score 15.0, max score 43.0), no missing or NaN values.
- **Reasons**: 100% populated non-empty strings, all under the 300 character limit.
- **Columns Present**: `['week_start', 'rank', 'gateway_id', 'score', 'reason']` (exact match to required schema).

---

## 5. Explanation of Baseline Algorithm (`baseline_3sigma.py`)
For each Monday in the 8 scored weeks (`2026-02-02` through `2026-03-23`):
1. **Trailing Window Selection**: Extracts a 28-day window of hourly telemetry strictly prior to the target Monday (`[Monday - 28 days, Monday)`).
2. **Baseline Statistics Computation**: Computes the mean ($\mu$) and standard deviation ($\sigma$) per gateway across three hourly metrics: `offline_duration_sec`, `disconnection_cnt`, and `reboot_cnt`.
3. **Anomaly Thresholding**: Filters for the trailing 7 days (`[Monday - 7 days, Monday)`). For each metric, an hour is flagged if $\text{value} - \mu > 3.0 \times \sigma$. (Gateways with $\sigma = 0$ return `NaN` and are ignored).
4. **Aggregation & Ranking**: Counts total flagged hours per gateway across the 7 days (`score = flagged_hours`). Gateways are sorted in descending order by `flagged_hours`, taking the top 15 gateways for each week.
5. **Reason Generation**: Formats a text explanation specifying the total flagged hours and the first metric that breached the 3-sigma threshold in iteration order.

---

## 6. Baseline Observations & Suspicious Behaviors
1. **In-Sample Target Leakage in Baseline**: The 7-day recent evaluation window is a sub-window of the 28-day baseline window. Large spikes during the recent 7 days inflate the baseline $\mu$ and $\sigma$ for that same gateway, reducing sensitivity to persistent or recent anomalies.
2. **Zero Standard Deviation Suppression ($\sigma = 0$)**: If a gateway had zero disconnects/reboots across the entire 28 days, its $\sigma = 0$. `baseline_3sigma.py` replaces $\sigma=0$ with `NaN`, causing any sudden breach during the trailing 7 days to be completely ignored (`fillna(False)`).
3. **Implicit Arbitrary Tie-Breaking**: Multiple gateways frequently share identical `flagged_hours` scores (e.g., ties at 19 hours or 15 hours). The algorithm relies on pandas implicit DataFrame ordering for tie-breaking rather than business-driven criteria (e.g., impact, field visit history, or severity).
4. **First Breach Metric Over-Simplification**: The generated reason string selects the metric of the "first breach" based on arbitrary row/iteration order, ignoring which metric had the most severe anomaly or highest business impact.
5. **Ignore Meter Reads & Field Visits**: The baseline solely uses 3 raw telemetry metrics and completely ignores meter reading failure rates, historic field visit outcomes, and engineer review feedback.

---

## 7. Blockers & Errors
- None. Execution and validation passed with zero errors.
