# LPDG Innovation Hub Selection Challenge 2026 — Gateway Prioritisation

Modular, reproducible, and point-in-time correct implementation of the 3-sigma baseline gateway prioritisation pipeline.

**Part 2 area selected:** D — Data Science (see [DECISIONS.md](DECISIONS.md), Decision 5).

---

## What It Does

Takes 8 months of hourly gateway telemetry and produces a ranked list of 15 gateways to visit each week, for 8 scoring weeks (2 February – 23 March 2026). Each gateway receives a score (count of anomalous hours in the trailing 7 days, measured against a 28-day baseline) and a text reason.

Output: `predictions.csv` — 120 rows, 5 columns (`week_start`, `rank`, `gateway_id`, `score`, `reason`).

---

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### Run

```bash
make run
```

This executes the pipeline, runs internal validation, writes `predictions.csv`, and checks it with the official validator.

### Alternative Commands

```bash
# Pipeline only
python -m gateway_priority.pipeline --data data --out predictions.csv

# Official validator
python validate_submission.py predictions.csv

# Tests and type checking
pytest
pyright src/ scripts/ tests/
```

### Custom Data Path

```bash
python -m gateway_priority.pipeline --data /path/to/data --out predictions.csv
```

---

## Project Structure

```
├── DECISIONS.md                  Five key decisions and trade-offs
├── LIMITATIONS.md                What it cannot do + two-week improvement plan
├── AI-USAGE.md                   AI tool usage and one mistake caught
├── Makefile                      One-command execution
├── predictions.csv               Final Part 1 output (120 rows, validated)
├── predictions_baseline.csv      Supplied baseline reference output
├── baseline_3sigma.py            Supplied baseline script (unchanged)
├── validate_submission.py        Supplied validator (unchanged)
├── data/                         Raw challenge data (not tracked in Git)
├── src/gateway_priority/
│   ├── __init__.py               Package exports
│   ├── config.py                 Constants and scoring schedule
│   ├── ids.py                    Gateway ID normalisation
│   ├── data.py                   Data loading and point-in-time filtering
│   ├── baseline.py               3-sigma anomaly ranking engine
│   ├── validation.py             Output contract validator
│   └── pipeline.py               CLI entry point
├── scripts/
│   └── audit_data.py             Data quality audit script
├── tests/                        33 unit and integration tests
└── reports/
    ├── data_audit/               Audit findings and CSV summaries
    └── part1/                    Phase reports (1.3, 1.4, 1.5)
```

---

## Verification Summary

| Check | Result |
| :--- | :--- |
| Official validator | PASS |
| Baseline parity (120/120 rows) | 100% |
| Score range | 15–43 flagged hours |
| Deterministic output | Yes (MD5 verified) |
| pytest | 33/33 |
| pyright | 0 errors, 0 warnings |

---

## Key Documentation

- [DECISIONS.md](DECISIONS.md) — Five decisions with alternatives and evidence
- [LIMITATIONS.md](LIMITATIONS.md) — What it cannot do and what two more weeks would fix
- [AI-USAGE.md](AI-USAGE.md) — AI tool usage and one error caught during review
