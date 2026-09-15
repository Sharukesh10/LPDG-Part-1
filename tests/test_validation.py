"""Unit tests for internal predictions validator."""

from __future__ import annotations

import pytest
import pandas as pd
import numpy as np

from gateway_priority.config import SCORED_WEEKS
from gateway_priority.validation import validate_predictions


def _make_valid_predictions_df() -> pd.DataFrame:
    rows = []
    for week in SCORED_WEEKS:
        w_str = week.isoformat()
        for r in range(1, 16):
            # Create valid 12-char hex string
            gw_id = f"0639EA56{r:04X}"
            rows.append(
                {
                    "week_start": w_str,
                    "rank": r,
                    "gateway_id": gw_id,
                    "score": float(20 - r),
                    "reason": f"{20 - r} hour(s) beyond 3 sigma on offline_duration_sec",
                }
            )
    return pd.DataFrame(rows)


def test_validate_predictions_success():
    df = _make_valid_predictions_df()
    assert validate_predictions(df) is True


def test_validate_predictions_missing_column():
    df = _make_valid_predictions_df().drop(columns=["reason"])
    with pytest.raises(ValueError, match="missing required columns"):
        validate_predictions(df)


def test_validate_predictions_invalid_row_count():
    df = _make_valid_predictions_df().iloc[:-1]  # 119 rows
    with pytest.raises(ValueError, match="Expected exactly 120 total rows"):
        validate_predictions(df)


def test_validate_predictions_duplicate_gateway_in_week():
    df = _make_valid_predictions_df()
    # Replace rank 2 gateway with rank 1 gateway in week 1
    df.loc[1, "gateway_id"] = df.loc[0, "gateway_id"]
    with pytest.raises(ValueError, match="duplicate gateway dispatches"):
        validate_predictions(df)


def test_validate_predictions_invalid_gateway_id():
    df = _make_valid_predictions_df()
    df.loc[0, "gateway_id"] = "INVALID_ID_123"
    with pytest.raises(ValueError, match="invalid gateway ID"):
        validate_predictions(df)


def test_validate_predictions_non_finite_score():
    df = _make_valid_predictions_df()
    df.loc[0, "score"] = np.nan
    with pytest.raises(ValueError, match="non-finite score"):
        validate_predictions(df)


def test_validate_predictions_empty_reason():
    df = _make_valid_predictions_df()
    df.loc[0, "reason"] = ""
    with pytest.raises(ValueError, match="empty reason string"):
        validate_predictions(df)


def test_validate_predictions_reason_too_long():
    df = _make_valid_predictions_df()
    df.loc[0, "reason"] = "A" * 301
    with pytest.raises(ValueError, match="exceeds 300 characters"):
        validate_predictions(df)
