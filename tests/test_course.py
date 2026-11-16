"""Checks on the MGSC 661 course additions."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from course_data import citywide_series, origins
from course_ols import design, forecast
from course_structure import ets_row

ROOT = Path(__file__).resolve().parents[1]


def toy_series(n: int = 60) -> pd.Series:
    rng = np.random.default_rng(0)
    ds = pd.date_range("2015-01-01", periods=n, freq="MS")
    y = 500 - 2 * np.arange(n) + 40 * np.sin(2 * np.pi * ds.month / 12) + rng.normal(0, 10, n)
    return pd.Series(y, index=ds)


def test_design_has_trend_and_eleven_month_dummies():
    X = design(pd.date_range("2015-01-01", periods=24, freq="MS"), pd.Timestamp("2015-01-01"))
    assert list(X.columns) == ["const", "trend"] + [f"m{m:02d}" for m in range(2, 13)]
    assert X["trend"].tolist() == list(range(24))
    assert X.loc["2015-01-01", [f"m{m:02d}" for m in range(2, 13)]].sum() == 0  # reference
    assert (X.iloc[:, 2:].sum(axis=1) <= 1).all()


def test_ols_forecast_matches_least_squares_and_intervals_nest():
    y = toy_series()
    out = forecast(y, h=6)
    X = design(y.index, y.index[0]).to_numpy()
    beta = np.linalg.lstsq(X, y.to_numpy(), rcond=None)[0]
    future = pd.date_range("2020-01-01", periods=6, freq="MS")
    expected = design(future, y.index[0]).to_numpy() @ beta
    assert np.allclose(out["forecast"], expected)
    assert (out["lo95"] < out["lo80"]).all() and (out["hi80"] < out["hi95"]).all()
    assert out["horizon"].tolist() == [1, 2, 3, 4, 5, 6]


def test_holt_winters_label_needs_trend_and_season():
    base = {"par": np.array([0.5, np.nan, np.nan, np.nan]), "aicc": 1.0, "components": ""}
    assert ets_row({**base, "method": "ETS(A,A,A)"})["holt_winters"]
    assert ets_row({**base, "method": "ETS(M,Ad,M)"})["holt_winters"]
    assert not ets_row({**base, "method": "ETS(A,N,A)"})["holt_winters"]
    assert not ets_row({**base, "method": "ETS(M,A,N)"})["holt_winters"]


@pytest.mark.skipif(not (ROOT / "results" / "backtest_forecasts.parquet").exists(),
                    reason="needs committed backtest results")
def test_snapshot_rebuilds_the_backtest_data():
    series = citywide_series()
    cut = origins(series)
    assert len(cut) == 77 and cut[0] == pd.Timestamp("2019-12-01")
    bt = pd.read_parquet(ROOT / "results" / "backtest_forecasts.parquet")
    bt = bt[["unique_id", "ds", "y"]].drop_duplicates()
    merged = bt.merge(series, on=["unique_id", "ds"], suffixes=("_bt", ""))
    assert len(merged) == len(bt)
    assert (merged["y_bt"] == merged["y"]).all()
