"""Configuration constants for gateway priority pipeline."""

from __future__ import annotations

import datetime as dt
import pathlib
from typing import List

METRICS: List[str] = ["offline_duration_sec", "disconnection_cnt", "reboot_cnt"]
SCORED_WEEKS: List[dt.date] = [dt.date(2026, 2, 2) + dt.timedelta(days=7 * i) for i in range(8)]

VISITS_PER_WEEK: int = 15
BASELINE_DAYS: int = 28
RECENT_DAYS: int = 7
SIGMA: float = 3.0

DEFAULT_DATA_DIR: pathlib.Path = pathlib.Path("data")
DEFAULT_OUTPUT_PATH: pathlib.Path = pathlib.Path("predictions.csv")
