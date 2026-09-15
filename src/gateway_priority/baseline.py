"""Baseline 3-sigma anomaly scoring implementation for gateway prioritization."""

from __future__ import annotations

import datetime as dt
import pathlib
from typing import Any, Dict, List, Sequence, Union, cast

import numpy as np
import pandas as pd

from gateway_priority.config import BASELINE_DAYS, METRICS, RECENT_DAYS, SCORED_WEEKS, SIGMA, VISITS_PER_WEEK
from gateway_priority.ids import canonicalize_gateway_id_series


def load_telemetry(data_dir: Union[str, pathlib.Path] = "data") -> pd.DataFrame:
    """Loads and validates telemetry parquet partitions from the supplied data directory.

    Supports either data_dir / 'telemetry' or data_dir directly.
    Canonicalises gateway IDs and parses timestamps safely.
    """
    path = pathlib.Path(data_dir)
    telemetry_dir = path / "telemetry" if (path / "telemetry").exists() else path

    if not telemetry_dir.exists():
        raise FileNotFoundError(f"Telemetry directory not found at: {telemetry_dir.resolve()}")

    parquet_files = sorted(list(telemetry_dir.glob("**/*.parquet")))
    if not parquet_files:
        raise FileNotFoundError(f"No parquet files found under telemetry directory: {telemetry_dir.resolve()}")

    frames: List[pd.DataFrame] = []
    required_cols = ["gateway_id", "ts_utc", *METRICS]

    for pfile in parquet_files:
        df = pd.read_parquet(pfile)
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Parquet partition {pfile.name} is missing required columns: {missing}")

        p_df = df[required_cols].copy()
        p_df["ts"] = pd.to_datetime(p_df["ts_utc"], utc=True)
        p_df["gateway_id"] = canonicalize_gateway_id_series(p_df["gateway_id"], "telemetry.gateway_id")
        frames.append(cast(pd.DataFrame, p_df.drop(columns=["ts_utc"])))

    combined = pd.concat(frames, ignore_index=True)
    return combined


def rank_week(frame: pd.DataFrame, monday: dt.date) -> pd.DataFrame:
    """Ranks gateways for a single scoring Monday using the 3-sigma baseline methodology."""
    end = pd.Timestamp(monday, tz="UTC")
    window = pd.DataFrame(frame[(frame["ts"] >= end - dt.timedelta(days=BASELINE_DAYS)) & (frame["ts"] < end)])

    if window.empty:
        return pd.DataFrame(columns=cast(Any, ["gateway_id", "flagged_hours", "worst_metric"]))

    stats = window.groupby("gateway_id")[METRICS].agg(["mean", "std"])
    recent = pd.DataFrame(window[window["ts"] >= end - dt.timedelta(days=RECENT_DAYS)]).copy()

    flags = pd.Series(0, index=recent.index, dtype=int)
    worst = pd.Series("", index=recent.index, dtype=object)

    rec_gw = pd.Series(recent["gateway_id"])

    for metric in METRICS:
        mean_map = dict(stats[(metric, "mean")])
        std_map = dict(stats[(metric, "std")])

        mean_s = pd.Series(rec_gw.map(lambda x: mean_map.get(x, 0.0)), index=recent.index)
        std_raw = pd.Series(rec_gw.map(lambda x: std_map.get(x, np.nan)), index=recent.index)
        std_s = std_raw.replace(0, np.nan)

        val_s = pd.Series(recent[metric])
        exceeded_s = pd.Series((val_s - mean_s) > (SIGMA * std_s), index=recent.index).fillna(False)

        flags = flags + exceeded_s.astype(int)
        worst = worst.where(~exceeded_s | (worst != ""), metric)

    recent["flagged"] = flags
    recent["worst_metric"] = worst

    grouped = pd.DataFrame(
        recent.groupby("gateway_id").agg(
            flagged_hours=("flagged", "sum"),
            worst_metric=("worst_metric", lambda s: next((v for v in s if v), "")),
        )
    )

    ranked = grouped.sort_values("flagged_hours", ascending=False).reset_index()
    return ranked


def build_predictions(
    frame: pd.DataFrame,
    weeks: Sequence[dt.date] = SCORED_WEEKS,
    top_n: int = VISITS_PER_WEEK,
) -> pd.DataFrame:
    """Generates baseline predictions for all specified scoring weeks."""
    rows: List[Dict[str, Any]] = []

    for monday in weeks:
        ranked = rank_week(frame, monday)

        if len(ranked) < top_n:
            raise ValueError(f"Only {len(ranked)} gateways available before {monday}, expected at least {top_n}")

        top_df = ranked.head(top_n)
        for rank, row in enumerate(top_df.itertuples(index=False), 1):
            row_gw = str(getattr(row, "gateway_id"))
            flagged_h = int(getattr(row, "flagged_hours"))
            worst_m = str(getattr(row, "worst_metric"))

            metric_reason = worst_m if worst_m else "no metric over 3 sigma"
            reason_str = (
                f"{flagged_h} hour(s) beyond 3 sigma of this gateway's own "
                f"28-day baseline in the last 7 days; first breach on {metric_reason}"
            )

            rows.append(
                {
                    "week_start": monday.isoformat(),
                    "rank": rank,
                    "gateway_id": row_gw,
                    "score": float(flagged_h),
                    "reason": reason_str,
                }
            )

    return pd.DataFrame(rows)

