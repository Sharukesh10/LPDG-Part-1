"""Data loading and safe data-handling primitives for gateway prioritization."""

from __future__ import annotations

import datetime as dt
import pathlib
from typing import Any, Dict, List, Sequence, Union, cast

import numpy as np
import pandas as pd

from gateway_priority.ids import canonicalize_gateway_id_series

REQUIRED_MASTER_COLUMNS = ["gateway_id", "installed_on", "decommissioned_on"]


def load_gateway_master(
    filepath: Union[str, pathlib.Path] = "data/gateway_master.csv",
    encoding: str = "latin1",
) -> pd.DataFrame:
    """Safely loads gateway_master.csv using explicit encoding and canonical ID validation.

    Requirements:
    - Explicit encoding (defaults to ISO-8859-1 / Latin-1 for German characters like 'Außenmast')
    - Useful error if file missing
    - Required-column validation
    - Preserves original raw gateway_id values
    - Adds canonical gateway ID in 'gateway_id_canonical'
    - Does not mutate the source file
    """
    path = pathlib.Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Gateway master file not found at path: {path.resolve()}")

    df = pd.read_csv(path, encoding=encoding)

    missing_cols = [c for c in REQUIRED_MASTER_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Gateway master file {path} is missing required columns: {missing_cols}"
        )

    # Preserve original raw values in gateway_id, add canonical gateway ID
    df["gateway_id_canonical"] = canonicalize_gateway_id_series(
        df["gateway_id"], column_name="gateway_id"
    )

    # Convert timestamps while preserving raw strings
    df["installed_dt"] = pd.to_datetime(df["installed_on"], errors="coerce")
    df["decommissioned_dt"] = pd.to_datetime(df["decommissioned_on"], errors="coerce")

    return df


def filter_point_in_time(
    df: pd.DataFrame,
    timestamp_col: str,
    cutoff_t: Union[str, dt.datetime, pd.Timestamp],
) -> pd.DataFrame:
    """Filters dataframe to enforce strict point-in-time cutoff: timestamp < cutoff_t.

    Rules:
    - timestamp < T -> allowed
    - timestamp >= T -> rejected/excluded
    """
    if timestamp_col not in df.columns:
        raise ValueError(f"Column '{timestamp_col}' not found in DataFrame.")

    ts_series = pd.to_datetime(df[timestamp_col])
    cutoff_ts = pd.to_datetime(cutoff_t)

    # Align timezone awareness
    if ts_series.dt.tz is not None and cutoff_ts.tz is None:
        cutoff_ts = cutoff_ts.tz_localize("UTC")
    elif ts_series.dt.tz is None and cutoff_ts.tz is not None:
        cutoff_ts = cutoff_ts.tz_convert(None)

    mask = ts_series < cutoff_ts
    return pd.DataFrame(df[mask]).copy()


def is_engineer_review_available(
    prediction_monday_t: Union[str, dt.date, dt.datetime, pd.Timestamp],
) -> bool:
    """Checks if engineer review dataset (dated 2026-02-15) is point-in-time available at prediction Monday T.

    The review was performed on 2026-02-15 (Sunday).
    Rule: timestamp < prediction_monday_t.
    Since 2026-02-15 is before 2026-02-16 00:00:00 UTC, the review is available for Mondays on or after 2026-02-16.
    """
    t_date = pd.to_datetime(prediction_monday_t).date()
    review_date = dt.date(2026, 2, 15)
    return review_date < t_date


def is_gateway_active(
    gateway_row_or_df: Union[pd.Series, Dict[str, Any], pd.DataFrame],
    timestamp: Union[str, dt.date, dt.datetime, pd.Timestamp],
) -> Union[bool, pd.Series]:
    """Evaluates whether a gateway is active at a given timestamp.

    Fields used:
    - 'installed_on' or 'installed_dt'
    - 'decommissioned_on' or 'decommissioned_dt'

    Semantics:
    - Active if installed_on <= timestamp AND (decommissioned_on is NaT/NaN/None OR decommissioned_on > timestamp)
    - If timestamp == decommissioned_on, the gateway is considered decommissioned/inactive.
    """
    ts = pd.to_datetime(timestamp)

    if isinstance(gateway_row_or_df, pd.DataFrame):
        inst = (
            gateway_row_or_df["installed_dt"]
            if "installed_dt" in gateway_row_or_df.columns
            else pd.to_datetime(gateway_row_or_df["installed_on"])
        )
        decomm = (
            gateway_row_or_df["decommissioned_dt"]
            if "decommissioned_dt" in gateway_row_or_df.columns
            else pd.to_datetime(gateway_row_or_df["decommissioned_on"])
        )

        is_installed = inst <= ts
        not_decommissioned = decomm.isna() | (decomm > ts)
        return pd.Series(is_installed & not_decommissioned)

    if isinstance(gateway_row_or_df, pd.Series):
        inst_val = gateway_row_or_df.get("installed_dt", gateway_row_or_df.get("installed_on"))
        decomm_val = gateway_row_or_df.get("decommissioned_dt", gateway_row_or_df.get("decommissioned_on"))
    elif isinstance(gateway_row_or_df, dict):
        inst_val = gateway_row_or_df.get("installed_dt", gateway_row_or_df.get("installed_on"))
        decomm_val = gateway_row_or_df.get("decommissioned_dt", gateway_row_or_df.get("decommissioned_on"))
    else:
        return False

    if inst_val is None or pd.isna(inst_val):
        return False

    inst_dt = pd.to_datetime(inst_val)
    if bool(inst_dt > ts):
        return False

    if decomm_val is not None and not pd.isna(decomm_val):
        decomm_dt = pd.to_datetime(decomm_val)
        if bool(decomm_dt <= ts):
            return False

    return True


def compute_telemetry_gaps(
    df: pd.DataFrame,
    gateway_id: str,
    start_time: Union[str, dt.datetime, pd.Timestamp],
    end_time_cutoff: Union[str, dt.datetime, pd.Timestamp],
    timestamp_col: str = "ts_utc",
    gateway_id_col: str = "gateway_id",
) -> Dict[str, Any]:
    """Diagnostic function computing gateway telemetry gaps before cutoff T without imputation.

    Returns:
    - expected_count
    - observed_count
    - missing_count
    - longest_gap_hours
    - gap_buckets ({'1h': c, '2-3h': c, '4-24h': c, '>24h': c})
    """
    start_ts = pd.to_datetime(start_time)
    end_ts = pd.to_datetime(end_time_cutoff)

    # Filter for gateway
    gw_mask = df[gateway_id_col] == gateway_id
    gw_df = pd.DataFrame(df[gw_mask]).copy()

    if gw_df.empty:
        expected_range = pd.date_range(start_ts, end_ts, freq="1h", inclusive="left")
        exp_cnt = len(expected_range)
        return {
            "gateway_id": gateway_id,
            "expected_timestamps": exp_cnt,
            "observed_timestamps": 0,
            "missing_timestamps": exp_cnt,
            "longest_gap_hours": float(exp_cnt) if exp_cnt > 0 else 0.0,
            "gap_buckets": {
                "1h": 0,
                "2-3h": 0,
                "4-24h": 0,
                ">24h": 1 if exp_cnt > 24 else (1 if exp_cnt > 0 else 0),
            },
        }

    ts_series = pd.Series(pd.to_datetime(gw_df[timestamp_col]))
    if ts_series.dt.tz is not None and start_ts.tz is None:
        start_ts = start_ts.tz_localize("UTC")
        end_ts = end_ts.tz_localize("UTC")
    elif ts_series.dt.tz is None and start_ts.tz is not None:
        ts_series = ts_series.dt.tz_localize("UTC")

    # Filter within interval [start_ts, end_ts)
    filtered_ts = pd.Series(ts_series[(ts_series >= start_ts) & (ts_series < end_ts)])
    window_ts = pd.Series(filtered_ts.sort_values().drop_duplicates())

    expected_range = pd.date_range(start_ts, end_ts, freq="1h", inclusive="left")
    expected_set = set(expected_range)
    observed_set = set(window_ts)
    missing_set = expected_set - observed_set

    # Compute continuous gaps
    sorted_obs = sorted(list(observed_set))

    gaps: List[float] = []
    if window_ts.empty:
        gaps.append((end_ts - start_ts).total_seconds() / 3600.0)
    else:
        # Check start gap
        if sorted_obs[0] > start_ts:
            gaps.append((sorted_obs[0] - start_ts).total_seconds() / 3600.0)
        # Check internal gaps
        for i in range(len(sorted_obs) - 1):
            diff_h = (sorted_obs[i + 1] - sorted_obs[i]).total_seconds() / 3600.0
            if diff_h > 1.0:
                gaps.append(diff_h - 1.0)
        # Check end gap
        if sorted_obs[-1] < end_ts - pd.Timedelta(hours=1):
            gaps.append((end_ts - sorted_obs[-1]).total_seconds() / 3600.0 - 1.0)

    gap_buckets = {"1h": 0, "2-3h": 0, "4-24h": 0, ">24h": 0}
    for g in gaps:
        if g <= 1.0:
            gap_buckets["1h"] += 1
        elif g <= 3.0:
            gap_buckets["2-3h"] += 1
        elif g <= 24.0:
            gap_buckets["4-24h"] += 1
        else:
            gap_buckets[">24h"] += 1

    return {
        "gateway_id": gateway_id,
        "expected_timestamps": len(expected_range),
        "observed_timestamps": len(window_ts),
        "missing_timestamps": len(missing_set),
        "longest_gap_hours": max(gaps) if gaps else 0.0,
        "gap_buckets": gap_buckets,
    }


def classify_telemetry_duplicates(
    telemetry_df: pd.DataFrame,
    gateway_id_col: str = "norm_id",
    timestamp_col: str = "ts_utc",
    metric_cols: Sequence[str] = ("offline_duration_sec", "disconnection_cnt", "reboot_cnt"),
) -> Dict[str, Any]:
    """Categorises duplicate telemetry keys (gateway_id, ts_utc) into exact vs conflicting duplicates.

    Definitions:
    - Exact duplicate rows: Same gateway, timestamp, and ALL metric values match across duplicate rows.
    - Conflicting duplicate rows: Same gateway, timestamp, but one or more metric values differ.
    """
    key_cols = [gateway_id_col, timestamp_col]

    dup_mask = telemetry_df.duplicated(subset=key_cols, keep=False)
    dup_rows = pd.DataFrame(telemetry_df[dup_mask]).copy()

    if dup_rows.empty:
        return {
            "duplicate_groups": 0,
            "rows_involved": 0,
            "excess_rows": 0,
            "exact_duplicate_groups": 0,
            "conflicting_duplicate_groups": 0,
            "exact_duplicate_rows": 0,
            "conflicting_duplicate_rows": 0,
            "affected_gateways": 0,
            "affected_months": [],
            "differing_metrics": [],
        }

    grouped = dup_rows.groupby(key_cols)
    num_groups = len(grouped)
    total_rows = len(dup_rows)
    excess_rows = total_rows - num_groups

    exact_dup_groups = 0
    conflicting_dup_groups = 0
    exact_dup_rows = 0
    conflicting_dup_rows = 0
    affected_gws: set[str] = set()
    differing_metrics_set: set[str] = set()
    affected_months_set: set[str] = set()

    for group_key, group_df in grouped:
        gw_id, ts_val = cast(Any, group_key)
        group = pd.DataFrame(cast(Any, group_df))
        affected_gws.add(str(gw_id))
        ts_str = str(ts_val)
        if len(ts_str) >= 7:
            affected_months_set.add(ts_str[:7])

        is_exact = True
        for m in metric_cols:
            if m in group.columns:
                if pd.Series(group[m]).nunique(dropna=False) > 1:
                    is_exact = False
                    differing_metrics_set.add(m)

        if is_exact:
            exact_dup_groups += 1
            exact_dup_rows += len(group)
        else:
            conflicting_dup_groups += 1
            conflicting_dup_rows += len(group)

    return {
        "duplicate_groups": num_groups,
        "rows_involved": total_rows,
        "excess_rows": excess_rows,
        "exact_duplicate_groups": exact_dup_groups,
        "conflicting_duplicate_groups": conflicting_dup_groups,
        "exact_duplicate_rows": exact_dup_rows,
        "conflicting_duplicate_rows": conflicting_dup_rows,
        "affected_gateways": len(affected_gws),
        "affected_months": sorted(list(affected_months_set)),
        "differing_metrics": sorted(list(differing_metrics_set)),
    }
