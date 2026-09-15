"""CLI pipeline entry point for gateway priority predictions."""

from __future__ import annotations

import argparse
import pathlib
import sys
from typing import Sequence

from gateway_priority.baseline import build_predictions, load_telemetry
from gateway_priority.config import DEFAULT_DATA_DIR, DEFAULT_OUTPUT_PATH
from gateway_priority.validation import validate_predictions


def run_pipeline(
    data_dir: pathlib.Path = DEFAULT_DATA_DIR,
    out_file: pathlib.Path = DEFAULT_OUTPUT_PATH,
) -> int:
    """Executes the complete baseline prediction pipeline with validation and export."""
    print(f"Loading telemetry from {data_dir}...")
    telemetry_df = load_telemetry(data_dir)
    print(f"Loaded {len(telemetry_df):,} telemetry rows.")

    print("Generating 3-sigma baseline predictions...")
    predictions_df = build_predictions(telemetry_df)

    print("Executing internal prediction validation...")
    validate_predictions(predictions_df)
    print("Internal validation PASSED.")

    out_file.parent.mkdir(parents=True, exist_ok=True)
    predictions_df.to_csv(out_file, index=False)
    print(f"Wrote {out_file} — {len(predictions_df)} rows over {predictions_df['week_start'].nunique()} weeks.")

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run Part 1 Gateway Priority Baseline Prediction Pipeline."
    )
    parser.add_argument(
        "--data",
        type=pathlib.Path,
        default=DEFAULT_DATA_DIR,
        help="Path to input data directory (default: ./data)",
    )
    parser.add_argument(
        "--out",
        type=pathlib.Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path to output predictions CSV file (default: predictions.csv)",
    )

    args = parser.parse_args(argv)

    try:
        return run_pipeline(data_dir=args.data, out_file=args.out)
    except Exception as exc:
        print(f"PIPELINE ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
