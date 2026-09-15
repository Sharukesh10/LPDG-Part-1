"""Internal validation for gateway prioritization predictions."""

from __future__ import annotations

import re
from typing import Sequence

import numpy as np
import pandas as pd

from gateway_priority.config import SCORED_WEEKS, VISITS_PER_WEEK
from gateway_priority.ids import normalize_gateway_id

EXPECTED_COLUMNS = ["week_start", "rank", "gateway_id", "score", "reason"]
HEX_12_REGEX = re.compile(r"^[0-9A-Fa-f]{12}$")


def validate_predictions(
    df: pd.DataFrame,
    expected_weeks: Sequence[str] | None = None,
    rows_per_week: int = VISITS_PER_WEEK,
) -> bool:
    """Validates that a predictions DataFrame satisfies all output contract requirements.

    Contract:
    - Exact columns: ['week_start', 'rank', 'gateway_id', 'score', 'reason']
    - 8 required scoring weeks (120 total rows, 15 rows/week)
    - Ranks strictly 1..15 in contiguous order for each week
    - No duplicate gateway IDs within the same scoring week
    - Valid 12-character upper-case hexadecimal gateway IDs
    - Finite non-NaN numeric scores
    - Non-empty reasons with length <= 300 characters
    """
    if df.empty:
        raise ValueError("Predictions DataFrame is empty.")

    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Predictions DataFrame missing required columns: {missing_cols}")

    extra_cols = [c for c in df.columns if c not in EXPECTED_COLUMNS]
    if extra_cols:
        raise ValueError(f"Predictions DataFrame contains unexpected extra columns: {extra_cols}")

    if expected_weeks is None:
        expected_weeks_str = [w.isoformat() for w in SCORED_WEEKS]
    else:
        expected_weeks_str = list(expected_weeks)

    total_expected_rows = len(expected_weeks_str) * rows_per_week
    if len(df) != total_expected_rows:
        raise ValueError(
            f"Expected exactly {total_expected_rows} total rows, found {len(df)} rows."
        )

    for week in expected_weeks_str:
        week_df = pd.DataFrame(df[df["week_start"] == week]).sort_values("rank")

        if len(week_df) != rows_per_week:
            raise ValueError(
                f"Week {week} has {len(week_df)} rows, expected exactly {rows_per_week} rows."
            )

        ranks = week_df["rank"].tolist()
        expected_ranks = list(range(1, rows_per_week + 1))
        if ranks != expected_ranks:
            raise ValueError(
                f"Week {week} ranks are invalid: found {ranks}, expected {expected_ranks}."
            )

        gws = week_df["gateway_id"].tolist()
        if len(set(gws)) != len(gws):
            duplicates = [gw for gw in gws if gws.count(gw) > 1]
            raise ValueError(f"Week {week} contains duplicate gateway dispatches: {set(duplicates)}")

        for idx, row in week_df.iterrows():
            gw = str(row["gateway_id"])
            norm = normalize_gateway_id(gw)
            if norm is None or norm != gw:
                raise ValueError(
                    f"Row {idx} in week {week} has invalid gateway ID '{gw}'. Expected canonical 12-char hex string."
                )

            score = row["score"]
            if not isinstance(score, (int, float, np.number)) or not np.isfinite(score):
                raise ValueError(
                    f"Row {idx} in week {week} for gateway {gw} has non-finite score: {score}"
                )

            reason_val = row["reason"]
            reason = str(reason_val) if (reason_val is not None and not bool(pd.isna(reason_val))) else ""
            if not reason.strip():
                raise ValueError(f"Row {idx} in week {week} for gateway {gw} has empty reason string.")
            if len(reason) > 300:
                raise ValueError(
                    f"Row {idx} in week {week} for gateway {gw} reason string exceeds 300 characters ({len(reason)} chars)."
                )

    return True
