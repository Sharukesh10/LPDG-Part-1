"""Unit tests for safe data loading and handling primitives."""

from __future__ import annotations

import datetime as dt
import pathlib
from typing import cast
import pytest
import pandas as pd

from gateway_priority.data import (
    load_gateway_master,
    filter_point_in_time,
    is_engineer_review_available,
    is_gateway_active,
    compute_telemetry_gaps,
    classify_telemetry_duplicates,
)


def test_load_gateway_master_success(tmp_path: pathlib.Path):
    csv_file = tmp_path / "gateway_master.csv"
    # Content with German character 'Außenmast' in Latin-1
    content = (
        "gateway_id,tenant,site_type,installed_on,decommissioned_on\n"
        "06:39:EA:56:02:C1,tenant_a,Außenmast,2024-01-01,2026-05-01\n"
        "0A56038B20D0,tenant_b,Innenmast,2025-06-15,\n"
    )
    csv_file.write_bytes(content.encode("latin1"))

    df = load_gateway_master(csv_file, encoding="latin1")

    assert len(df) == 2
    # Verify original raw gateway_id preserved
    assert df.loc[0, "gateway_id"] == "06:39:EA:56:02:C1"
    # Verify canonical gateway ID added separately
    assert df.loc[0, "gateway_id_canonical"] == "0639EA5602C1"
    assert df.loc[1, "gateway_id_canonical"] == "0A56038B20D0"
    # Verify site_type German character parsed properly
    assert df.loc[0, "site_type"] == "Außenmast"


def test_load_gateway_master_missing_file():
    with pytest.raises(FileNotFoundError, match="Gateway master file not found"):
        load_gateway_master("non_existent_file.csv")


def test_load_gateway_master_missing_columns(tmp_path: pathlib.Path):
    csv_file = tmp_path / "bad_master.csv"
    content = "gateway_id,tenant\n06:39:EA:56:02:C1,tenant_a\n"
    csv_file.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match="missing required columns"):
        load_gateway_master(csv_file, encoding="utf-8")


def test_point_in_time_cutoff():
    cutoff = pd.Timestamp("2026-02-02 00:00:00", tz="UTC")
    timestamps = [
        pd.Timestamp("2026-02-01 23:59:59", tz="UTC"),  # T - 1s -> allowed
        pd.Timestamp("2026-02-01 23:00:00", tz="UTC"),  # T - 1h -> allowed
        pd.Timestamp("2026-02-02 00:00:00", tz="UTC"),  # T -> rejected
        pd.Timestamp("2026-02-02 00:00:01", tz="UTC"),  # T + 1s -> rejected
    ]
    df = pd.DataFrame({"ts_utc": timestamps, "val": [1, 2, 3, 4]})

    filtered = filter_point_in_time(df, "ts_utc", cast(pd.Timestamp, cutoff))

    assert len(filtered) == 2
    assert set(filtered["val"].tolist()) == {1, 2}


def test_engineer_review_availability():
    # Engineer review date is 2026-02-15
    assert not is_engineer_review_available("2026-02-02")
    assert not is_engineer_review_available("2026-02-09")
    assert is_engineer_review_available("2026-02-16")
    assert is_engineer_review_available("2026-02-23")
    assert is_engineer_review_available("2026-03-02")
    assert is_engineer_review_available("2026-03-09")
    assert is_engineer_review_available("2026-03-16")
    assert is_engineer_review_available("2026-03-23")


def test_is_gateway_active():
    row = {
        "installed_on": "2025-01-15",
        "decommissioned_on": "2026-02-10",
    }
    # Before installation
    assert not bool(is_gateway_active(row, "2025-01-14"))
    # On installation date
    assert bool(is_gateway_active(row, "2025-01-15"))
    # Active period
    assert bool(is_gateway_active(row, "2025-06-01"))
    # On decommission date -> False
    assert not bool(is_gateway_active(row, "2026-02-10"))
    # After decommission date
    assert not bool(is_gateway_active(row, "2026-02-15"))

    # Gateway with no decommission date
    row_no_decomm = {"installed_on": "2025-01-15", "decommissioned_on": None}
    assert bool(is_gateway_active(row_no_decomm, "2026-03-01"))


def test_compute_telemetry_gaps_synthetic():
    start = "2026-02-01 00:00:00"
    end = "2026-02-01 10:00:00"  # 10 expected hourly slots
    # Observed slots: 0, 1, 2, 6, 7 (missing 3, 4, 5 -> 3h gap; missing 8, 9 -> 2h gap)
    obs_ts = [
        "2026-02-01 00:00:00",
        "2026-02-01 01:00:00",
        "2026-02-01 02:00:00",
        "2026-02-01 06:00:00",
        "2026-02-01 07:00:00",
    ]
    df = pd.DataFrame({"gateway_id": ["GW1"] * 5, "ts_utc": obs_ts})

    res = compute_telemetry_gaps(df, "GW1", start, end)

    assert res["expected_timestamps"] == 10
    assert res["observed_timestamps"] == 5
    assert res["missing_timestamps"] == 5
    assert res["longest_gap_hours"] == 3.0


def test_compute_telemetry_gaps_no_gaps():
    start = "2026-02-01 00:00:00"
    end = "2026-02-01 05:00:00"
    obs_ts = [f"2026-02-01 0{i}:00:00" for i in range(5)]
    df = pd.DataFrame({"gateway_id": ["GW1"] * 5, "ts_utc": obs_ts})

    res = compute_telemetry_gaps(df, "GW1", start, end)

    assert res["expected_timestamps"] == 5
    assert res["observed_timestamps"] == 5
    assert res["missing_timestamps"] == 0
    assert res["longest_gap_hours"] == 0.0


def test_compute_telemetry_gaps_with_duplicates():
    start = "2026-02-01 00:00:00"
    end = "2026-02-01 03:00:00"
    # Duplicate rows for 00:00:00
    obs_ts = [
        "2026-02-01 00:00:00",
        "2026-02-01 00:00:00",
        "2026-02-01 01:00:00",
        "2026-02-01 02:00:00",
    ]
    df = pd.DataFrame({"gateway_id": ["GW1"] * 4, "ts_utc": obs_ts})

    res = compute_telemetry_gaps(df, "GW1", start, end)

    assert res["expected_timestamps"] == 3
    assert res["observed_timestamps"] == 3
    assert res["missing_timestamps"] == 0
    assert res["longest_gap_hours"] == 0.0


def test_classify_telemetry_duplicates():
    df = pd.DataFrame(
        [
            # Exact duplicate pair
            {"norm_id": "GW1", "ts_utc": "2026-01-01 00:00:00", "offline_duration_sec": 0, "disconnection_cnt": 0, "reboot_cnt": 0},
            {"norm_id": "GW1", "ts_utc": "2026-01-01 00:00:00", "offline_duration_sec": 0, "disconnection_cnt": 0, "reboot_cnt": 0},
            # Conflicting duplicate pair
            {"norm_id": "GW2", "ts_utc": "2026-01-01 01:00:00", "offline_duration_sec": 100, "disconnection_cnt": 1, "reboot_cnt": 0},
            {"norm_id": "GW2", "ts_utc": "2026-01-01 01:00:00", "offline_duration_sec": 200, "disconnection_cnt": 1, "reboot_cnt": 0},
            # Non-duplicate row
            {"norm_id": "GW3", "ts_utc": "2026-01-01 02:00:00", "offline_duration_sec": 0, "disconnection_cnt": 0, "reboot_cnt": 0},
        ]
    )

    res = classify_telemetry_duplicates(df)

    assert res["duplicate_groups"] == 2
    assert res["rows_involved"] == 4
    assert res["excess_rows"] == 2
    assert res["exact_duplicate_groups"] == 1
    assert res["conflicting_duplicate_groups"] == 1
    assert res["exact_duplicate_rows"] == 2
    assert res["conflicting_duplicate_rows"] == 2
    assert res["affected_gateways"] == 2
    assert "offline_duration_sec" in res["differing_metrics"]
