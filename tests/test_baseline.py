"""Unit tests for baseline 3-sigma anomaly ranking and point-in-time isolation."""

from __future__ import annotations

import datetime as dt
import pathlib
import pytest
import pandas as pd

from gateway_priority.baseline import build_predictions, load_telemetry, rank_week
from gateway_priority.config import SCORED_WEEKS


def test_strict_point_in_time_isolation():
    monday = dt.date(2026, 2, 2)
    end = pd.Timestamp(monday, tz="UTC")

    # Allowed historical data: T - 1h
    t_allow_1 = end - dt.timedelta(hours=1)
    t_allow_2 = end - dt.timedelta(days=2)

    # Excluded data: exactly T, and T + 1h
    t_exact_T = end
    t_future = end + dt.timedelta(hours=1)

    df_base = pd.DataFrame(
        [
            {"gateway_id": "0639EA5602C1", "ts": t_allow_1, "offline_duration_sec": 3600, "disconnection_cnt": 10, "reboot_cnt": 2},
            {"gateway_id": "0639EA5602C1", "ts": t_allow_2, "offline_duration_sec": 0, "disconnection_cnt": 0, "reboot_cnt": 0},
            {"gateway_id": "0A56038B20D0", "ts": t_allow_1, "offline_duration_sec": 0, "disconnection_cnt": 0, "reboot_cnt": 0},
            {"gateway_id": "0A56038B20D0", "ts": t_allow_2, "offline_duration_sec": 0, "disconnection_cnt": 0, "reboot_cnt": 0},
        ]
    )

    df_with_future = pd.concat(
        [
            df_base,
            pd.DataFrame(
                [
                    {"gateway_id": "0A56038B20D0", "ts": t_exact_T, "offline_duration_sec": 3600, "disconnection_cnt": 50, "reboot_cnt": 10},
                    {"gateway_id": "0A56038B20D0", "ts": t_future, "offline_duration_sec": 3600, "disconnection_cnt": 50, "reboot_cnt": 10},
                ]
            ),
        ],
        ignore_index=True,
    )

    res_base = rank_week(df_base, monday)
    res_with_future = rank_week(df_with_future, monday)

    # Data at T or > T must have ZERO impact on ranking
    pd.testing.assert_frame_equal(res_base, res_with_future)


def test_load_telemetry_missing_columns(tmp_path: pathlib.Path):
    telem_dir = tmp_path / "telemetry"
    telem_dir.mkdir()
    bad_parquet = telem_dir / "bad.parquet"
    df = pd.DataFrame({"gateway_id": ["GW1"], "ts_utc": ["2026-01-01T00:00:00Z"]})
    df.to_parquet(bad_parquet)

    with pytest.raises(ValueError, match="missing required columns"):
        load_telemetry(tmp_path)


def test_build_predictions_insufficient_gateways():
    monday = dt.date(2026, 2, 2)
    end = pd.Timestamp(monday, tz="UTC")
    # Only 5 gateways available, expected 15
    rows = []
    for i in range(5):
        gw_id = f"0639EA5602C{i}"
        rows.append({"gateway_id": gw_id, "ts": end - dt.timedelta(days=1), "offline_duration_sec": 10, "disconnection_cnt": 1, "reboot_cnt": 0})
    df = pd.DataFrame(rows)

    with pytest.raises(ValueError, match="expected at least 15"):
        build_predictions(df, weeks=[monday], top_n=15)
