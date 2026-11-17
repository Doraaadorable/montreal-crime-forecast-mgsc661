"""Which ETS and ARIMA structures the backtest actually used, and how their residuals look.

backtest.py refits AutoETS and AutoARIMA at each of the 77 origins but keeps only the
forecasts. This script refits the same models on the same data at every origin and records
the selected structure and parameters. It checks that the one-month-ahead forecasts equal
those in results/backtest_forecasts.parquet, so the structures belong to the reported results.

ETS(E,T,S): error, trend, seasonality; N = none, A = additive, Ad = additive damped,
M = multiplicative. Additive Holt-Winters is ETS(A,A,A) and multiplicative Holt-Winters is
ETS(M,A,M); ETS(.,N,.) has no trend term. ARIMA(p,d,q)(P,D,Q)[12]; a fit is seasonal (SARIMA)
only if P, D or Q is above zero.

Residual checks follow the course's checkresiduals(): residual plot, residual ACF and a
Ljung-Box test. For ETS the residuals are innovation residuals (relative errors when the
error is multiplicative), as in R. Ljung-Box degrees of freedom are reduced by p+q+P+Q for
ARIMA and not reduced for ETS: with 60 months, ETS models with seasonal initial states have
more parameters than lags, so a reduced test is not defined; treat the ETS p-values as
indicative. These are the reported diagnostics, since these models produced the forecasts.
The R script in course/r/ repeats the first origin with the course's checkresiduals() as an
independent check of the method, not a replacement.

Outputs (results/course/):
    model_structures.csv            one row per series, origin and model
    structure_frequency.csv         share of the 77 origins with trend, seasonality, D = 1 ...
    structure_selected_origins.csv  structures at three origins fixed in advance
    residual_checks_first_origin.csv
and figures/course/differencing_acf.png, figures/course/residuals_vehicle_theft.png

Usage:
    python src/course_structure.py     # about 5 minutes on 4 cores
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from statsforecast import StatsForecast
from statsforecast.arima import arima_string
from statsforecast.models import AutoARIMA, AutoETS
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import acf

from course_data import COURSE_FIGURES, COURSE_RESULTS, HORIZON, ROOT, SEASON, \
    citywide_series, origins

# Fixed before looking at the structures: first origin, the end of the surge's first full
# year, and the last origin.
SELECTED_ORIGINS = ["2019-12-01", "2022-12-01", "2026-04-01"]
FEATURED = "Vehicle theft"
DIFFERENCING_EXAMPLE = "Break and enter"


def ets_row(model: dict) -> dict:
    alpha, beta, gamma, phi = (model["par"][:4].tolist() + [np.nan] * 4)[:4]
    comp = model["components"]  # e.g. "MAdM" + damped flag; method string is clearer
    method = model["method"]
    trend = method.split(",")[1]
    season = method.split(",")[2].rstrip(")")
    return {"structure": method, "error": method[4], "trend": trend, "season": season,
            "alpha": alpha, "beta": beta, "gamma": gamma, "phi": phi,
            "holt_winters": trend in {"A", "Ad"} and season in {"A", "M"},
            "aicc": model["aicc"], "components": comp}


def arima_row(model: dict) -> dict:
    p, q, P, Q, m, d, D = model["arma"]
    return {"structure": arima_string(model).strip(), "p": p, "d": d, "q": q, "P": P, "D": D,
            "Q": Q, "seasonal": (P + D + Q) > 0, "aicc": model["aicc"],
            "drift_or_mean": any(k in model["coef"] for k in ("drift", "intercept"))}


def fit_all(series: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    rows, first = [], {}
    for cutoff in origins(series):
        train = series[series["ds"] <= cutoff]
        sf = StatsForecast(models=[AutoETS(season_length=SEASON),
                                   AutoARIMA(season_length=SEASON)], freq="MS", n_jobs=-1)
        sf.fit(train)
        fc = sf.predict(h=HORIZON)
        fc = fc.reset_index() if "unique_id" not in fc.columns else fc
        fc1 = fc[fc["ds"] == cutoff + pd.offsets.MonthBegin()].set_index("unique_id")
        for i, uid in enumerate(sf.uids):
            for j, (name, rowfn) in enumerate([("AutoETS", ets_row), ("AutoARIMA", arima_row)]):
                model = sf.fitted_[i, j].model_
                rows.append({"unique_id": uid, "cutoff": cutoff, "model": name,
                             "forecast_h1": float(fc1.loc[uid, name]), **rowfn(model)})
                if cutoff == origins(series)[0]:
                    first[(uid, name)] = model
    return pd.DataFrame(rows), first


def check_against_backtest(structures: pd.DataFrame) -> float:
    bt = pd.read_parquet(ROOT / "results" / "backtest_forecasts.parquet")
    bt = bt[(bt["horizon"] == 1) & bt["model"].isin(["AutoETS", "AutoARIMA"])]
    m = structures.merge(bt[["unique_id", "cutoff", "model", "forecast"]],
                         on=["unique_id", "cutoff", "model"])
    assert len(m) == len(structures), "every refit must match a backtest forecast"
    return float((m["forecast_h1"] - m["forecast"]).abs().max())


def frequency(structures: pd.DataFrame) -> pd.DataFrame:
    ets = structures[structures["model"] == "AutoETS"]
    ari = structures[structures["model"] == "AutoARIMA"]
    rows = []
    for uid in sorted(structures["unique_id"].unique()):
        e, a = ets[ets["unique_id"] == uid], ari[ari["unique_id"] == uid]
        rows.append({
            "unique_id": uid,
            "ets_has_trend": (e["trend"] != "N").mean(),
            "ets_damped_trend": (e["trend"] == "Ad").mean(),
            "ets_has_season": (e["season"] != "N").mean(),
            "ets_holt_winters": e["holt_winters"].mean(),
            "ets_most_common": e["structure"].mode().iloc[0],
            "ets_distinct_structures": e["structure"].nunique(),
            "arima_seasonal": a["seasonal"].mean(),
            "arima_D1": (a["D"] == 1).mean(),
            "arima_d1": (a["d"] == 1).mean(),
            "arima_most_common": a["structure"].mode().iloc[0],
            "arima_distinct_structures": a["structure"].nunique(),
        })
    return pd.DataFrame(rows).round(2)


def residual_checks(first: dict) -> pd.DataFrame:
    rows = []
    for (uid, name), model in first.items():
        r = np.asarray(model["residuals"], dtype=float)
        if name == "AutoARIMA":
            p, q, P, Q, *_ = model["arma"]
            df, structure = p + q + P + Q, arima_string(model).strip()
            r = r[SEASON + 1:]  # drop start-up residuals from differencing
        else:
            df, structure = 0, model["method"]
        lb = acorr_ljungbox(r, lags=[12, 24], model_df=df)
        rows.append({"unique_id": uid, "model": name, "structure": structure,
                     "ljung_box_df_reduction": df,
                     "ljung_box_p_lag12": round(lb["lb_pvalue"].iloc[0], 3),
                     "ljung_box_p_lag24": round(lb["lb_pvalue"].iloc[1], 3),
                     "residual_lag1_acf": round(acf(r, nlags=1)[1], 2),
                     "residual_lag12_acf": round(acf(r, nlags=12)[12], 2)})
    return pd.DataFrame(rows).sort_values(["unique_id", "model"])


def fig_differencing(series: pd.DataFrame, cutoff: pd.Timestamp) -> None:
    import matplotlib.pyplot as plt

    import figures

    y = series[(series["unique_id"] == DIFFERENCING_EXAMPLE) & (series["ds"] <= cutoff)]
    y = y.set_index("ds")["y"]
    panels = [("Recorded counts", y),
              ("Seasonal difference (y_t - y_t-12)", y.diff(SEASON)),
              ("Seasonal and first difference", y.diff(SEASON).diff())]
    fig, axes = plt.subplots(1, 3, figsize=(13, 2.8), sharey=True)
    for ax, (title, s) in zip(axes, panels):
        s = s.dropna()
        ax.bar(np.arange(1, 25), acf(s, nlags=24)[1:], color=figures.MODEL_COLORS["AutoARIMA"],
               width=0.7)
        bound = 1.96 / np.sqrt(len(s))
        ax.axhspan(-bound, bound, color=figures.GRID, alpha=0.7, lw=0, zorder=0)
        ax.set_title(title, fontsize=10)
        ax.set_xticks([1, 6, 12, 18, 24])
        ax.set_xlabel("Lag (months)")
    axes[0].set_ylabel("ACF")
    fig.suptitle(f"{DIFFERENCING_EXAMPLE}, Jan 2015 to {cutoff:%b %Y}: why ARIMA differences",
                 x=0.01, ha="left", fontsize=11, fontweight="bold")
    fig.tight_layout()
    fig.savefig(COURSE_FIGURES / "differencing_acf.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_residuals(series: pd.DataFrame, first: dict, cutoff: pd.Timestamp) -> None:
    import matplotlib.pyplot as plt

    import figures

    ds = series[(series["unique_id"] == FEATURED) & (series["ds"] <= cutoff)]["ds"].to_numpy()
    fig, axes = plt.subplots(2, 2, figsize=(12, 5.2))
    for row, name in enumerate(["AutoETS", "AutoARIMA"]):
        model = first[(FEATURED, name)]
        r = np.asarray(model["residuals"], dtype=float)
        label = model["method"] if name == "AutoETS" else arima_string(model).strip()
        color = figures.MODEL_COLORS[name]
        axes[row, 0].plot(ds, r, color=color, lw=1.4)
        axes[row, 0].axhline(0, color=figures.MUTED, lw=0.8)
        unit = " (relative error)" if name == "AutoETS" and model["method"][4] == "M" else ""
        axes[row, 0].set_title(f"{label}: residuals{unit}", fontsize=10)
        rr = r[SEASON + 1:] if name == "AutoARIMA" else r
        axes[row, 1].bar(np.arange(1, 25), acf(rr, nlags=24)[1:], color=color, width=0.7)
        bound = 1.96 / np.sqrt(len(rr))
        axes[row, 1].axhspan(-bound, bound, color=figures.GRID, alpha=0.7, lw=0, zorder=0)
        axes[row, 1].set_xticks([1, 6, 12, 18, 24])
        axes[row, 1].set_title(f"{label}: residual ACF", fontsize=10)
    axes[1, 1].set_xlabel("Lag (months)")
    fig.suptitle(f"{FEATURED}, models fitted on Jan 2015 to {cutoff:%b %Y}", x=0.01, ha="left",
                 fontsize=11, fontweight="bold")
    fig.tight_layout()
    fig.savefig(COURSE_FIGURES / "residuals_vehicle_theft.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    COURSE_RESULTS.mkdir(parents=True, exist_ok=True)
    COURSE_FIGURES.mkdir(parents=True, exist_ok=True)
    series = citywide_series()
    structures, first = fit_all(series)
    gap = check_against_backtest(structures)
    print(f"Largest gap to the backtest's one-month forecasts: {gap:.2e}")
    assert gap < 1e-6, "refits do not reproduce the backtest"

    keep = ["unique_id", "cutoff", "model", "structure", "alpha", "beta", "gamma", "phi",
            "p", "d", "q", "P", "D", "Q", "aicc"]
    out = structures[keep].copy()
    out[["alpha", "beta", "gamma", "phi", "aicc"]] = out[["alpha", "beta", "gamma", "phi",
                                                          "aicc"]].round(3)
    out.to_csv(COURSE_RESULTS / "model_structures.csv", index=False)
    freq = frequency(structures)
    freq.to_csv(COURSE_RESULTS / "structure_frequency.csv", index=False)
    sel = out[out["cutoff"].isin(pd.to_datetime(SELECTED_ORIGINS))]
    sel = sel.pivot_table(index=["unique_id", "cutoff"], columns="model", values="structure",
                          aggfunc="first").reset_index()
    sel.to_csv(COURSE_RESULTS / "structure_selected_origins.csv", index=False)
    checks = residual_checks(first)
    checks.to_csv(COURSE_RESULTS / "residual_checks_first_origin.csv", index=False)

    cutoff = origins(series)[0]
    fig_differencing(series, cutoff)
    fig_residuals(series, first, cutoff)

    pd.set_option("display.width", 220)
    print("\n", freq.to_string(index=False))
    print("\n", sel.to_string(index=False))
    print("\n", checks.to_string(index=False))
    fv = out[(out["unique_id"] == FEATURED) & (out["model"] == "AutoETS")]
    print("\nVehicle theft ETS at selected origins:\n",
          fv[fv["cutoff"].isin(pd.to_datetime(SELECTED_ORIGINS))].to_string(index=False))


if __name__ == "__main__":
    np.seterr(all="ignore")
    main()
