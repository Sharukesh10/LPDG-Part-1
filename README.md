# LPDG Innovation Hub Selection Challenge 2026 — Gateway Prioritisation

Modular, reproducible, and point-in-time correct implementation of the 3-sigma baseline gateway prioritisation pipeline.

## System Architecture

The pipeline processes hourly gateway telemetry partitions, evaluates 28-day baseline reference statistics against 7-day recent detection windows, ranks gateways by anomaly severity, and outputs point-in-time prioritized gateway dispatches for each required scoring Monday.

```
data/
  └── telemetry/
        ↓
src/gateway_priority/
  ├── config.py       (Constants & scoring schedule)
  ├── ids.py          (Gateway ID normalisation & validation)
  ├── data.py         (Safe data loading & point-in-time filtering)
  ├── baseline.py     (3-sigma anomaly ranking engine)
  ├── validation.py   (Internal output contract validator)
  └── pipeline.py     (CLI pipeline runner)
        ↓
predictions.csv
        ↓
validate_submission.py
        ↓
PASS
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Running the Pipeline

To run the complete pipeline, perform internal validation, export `predictions.csv`, and execute official submission validation:

```bash
make run
```

### Alternative CLI Commands

Run the pipeline manually:

```bash
python -m gateway_priority.pipeline --data data --out predictions.csv
```

Run official validation independently:

```bash
python validate_submission.py predictions.csv
```

Run test suite:

```bash
pytest
```
