"""Integration unit tests for pipeline execution and determinism."""

from __future__ import annotations

import pathlib
import pytest
import pandas as pd

from gateway_priority.baseline import build_predictions, load_telemetry
from gateway_priority.pipeline import run_pipeline


def test_pipeline_determinism(tmp_path: pathlib.Path):
    # Load raw telemetry
    telemetry_df = load_telemetry("data")

    # Run predictions twice
    pred_1 = build_predictions(telemetry_df)
    pred_2 = build_predictions(telemetry_df)

    # Verify 100% identical DataFrames
    pd.testing.assert_frame_equal(pred_1, pred_2)


def test_run_pipeline_end_to_end(tmp_path: pathlib.Path):
    out_file = tmp_path / "test_predictions.csv"
    ret = run_pipeline(data_dir=pathlib.Path("data"), out_file=out_file)

    assert ret == 0
    assert out_file.exists()

    df = pd.read_csv(out_file)
    assert len(df) == 120
    assert list(df.columns) == ["week_start", "rank", "gateway_id", "score", "reason"]
