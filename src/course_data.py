"""Citywide monthly series for the MGSC 661 course analyses, read from the frozen snapshot.

The open data file is replaced every day and old versions cannot be downloaded again.
The course work therefore uses the committed snapshot of the 15 November 2026 download
(data/snapshots/2026-11-15.csv.gz, raw file sha256 in data/manifest.json). It holds counts
by month, category and district, so the citywide series can be rebuilt without the raw file.
The result equals monthly_by_category() in data.py on that download: every value of y
in results/backtest_forecasts.parquet matches (checked in tests/test_course.py).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from data import CATEGORY_LABELS, EXCLUDED_FROM_FORECASTS

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data" / "snapshots" / "2026-11-15.csv.gz"
COURSE_RESULTS = ROOT / "results" / "course"
COURSE_FIGURES = ROOT / "figures" / "course"

HORIZON = 6
SEASON = 12
MIN_TRAIN_MONTHS = 60


def citywide_series(path: Path = SNAPSHOT) -> pd.DataFrame:
    """Long format (unique_id, ds, y), last (partial) month dropped, as in data.py."""
    snap = pd.read_csv(path)
    snap["category"] = snap["category"].map(CATEGORY_LABELS)
    if snap["category"].isna().any():
        raise ValueError("Unmapped category in snapshot")
    wide = (snap.assign(ds=pd.to_datetime(snap["month"]))
            .groupby(["ds", "category"])["count"].sum().unstack(fill_value=0)
            .asfreq("MS", fill_value=0))
    wide = wide.iloc[:-1].drop(columns=EXCLUDED_FROM_FORECASTS)
    long = wide.stack().rename("y").reset_index()
    long.columns = ["ds", "unique_id", "y"]
    return long[["unique_id", "ds", "y"]].sort_values(["unique_id", "ds"]).reset_index(drop=True)


def origins(series: pd.DataFrame) -> pd.DatetimeIndex:
    """The 77 forecast origins of backtest.py: first after 60 months, last with 6 months left."""
    months = pd.DatetimeIndex(sorted(series["ds"].unique()))
    return months[MIN_TRAIN_MONTHS - 1: len(months) - HORIZON]


def mase_scale(y: pd.Series, cutoff: pd.Timestamp) -> float:
    """In-sample seasonal-naive MAE up to the origin, the MASE denominator in backtest.py."""
    return float((y - y.shift(SEASON)).abs().loc[:cutoff].mean())
