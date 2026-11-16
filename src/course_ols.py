"""The PoC regression in the same rolling backtest as the time-series models.

Model, fixed in advance and identical to the PoC (crime_poc_analysis.ipynb, Step 4):

    y_t = b0 + b1 * t + month dummies (January = reference) + e_t,   fitted by OLS

Differences from the PoC are the data and the evaluation, not the model: the PoC used the
Bilan mensuel file (Jan 2023 to Aug 2026) and one six-month holdout; here the model is
refitted at the same 77 origins as backtest.py and forecasts 1 to 6 months ahead, with 80%
and 95% prediction intervals from the usual OLS formula.

Outputs (results/course/):
    ols_forecasts.parquet          every OLS forecast, same columns as backtest_forecasts
    ols_summary_by_horizon.csv     MASE and coverage for OLS, same month last year, ETS, ARIMA
    ols_summary_by_category.csv
    ols_comparisons.csv            error ratios with 95% block-bootstrap intervals
    ols_first_origin_coefficients.csv   coefficients at the first origin (Dec 2019)
    ols_first_origin_diagnostics.csv    R2, Durbin-Watson, Breusch-Pagan, Ljung-Box
and figures/course/ols_residual_acf.png

Usage:
    python src/course_ols.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.diagnostic import acorr_ljungbox, het_breuschpagan
from statsmodels.stats.stattools import durbin_watson

from backtest import summarize
from course_data import COURSE_FIGURES, COURSE_RESULTS, HORIZON, ROOT, citywide_series, \
    mase_scale, origins
from significance import block_bootstrap_ratio

LEVELS = [80, 95]
COMPARED = ["OLS", "SeasonalNaive", "AutoETS", "AutoARIMA"]


def design(ds: pd.DatetimeIndex, start: pd.Timestamp) -> pd.DataFrame:
    """Intercept, linear trend (months since the first month) and 11 month dummies."""
    X = pd.DataFrame({"const": 1.0,
                      "trend": (ds.year - start.year) * 12 + (ds.month - start.month)},
                     index=ds)
    for m in range(2, 13):
        X[f"m{m:02d}"] = (ds.month == m).astype(float)
    return X


def fit(y: pd.Series):
    return sm.OLS(y.astype(float), design(y.index, y.index[0])).fit()


def forecast(y: pd.Series, h: int = HORIZON) -> pd.DataFrame:
    """Point forecasts and prediction intervals for the h months after y ends."""
    model = fit(y)
    future = pd.date_range(y.index[-1] + pd.offsets.MonthBegin(), periods=h, freq="MS")
    pred = model.get_prediction(design(future, y.index[0]))
    out = pd.DataFrame({"ds": future, "horizon": np.arange(1, h + 1),
                        "forecast": pred.predicted_mean})
    for lv in LEVELS:
        band = pred.conf_int(obs=True, alpha=1 - lv / 100)
        out[f"lo{lv}"], out[f"hi{lv}"] = band[:, 0], band[:, 1]
    return out


def score(df: pd.DataFrame) -> pd.DataFrame:
    """Same error and interval measures as backtest.to_long()."""
    df["abs_scaled_error"] = (df["y"] - df["forecast"]).abs() / df["scale"]
    for lv in LEVELS:
        alpha = 1 - lv / 100
        df[f"covered{lv}"] = df["y"].between(df[f"lo{lv}"], df[f"hi{lv}"])
        below = (df[f"lo{lv}"] - df["y"]).clip(lower=0)
        above = (df["y"] - df[f"hi{lv}"]).clip(lower=0)
        width = df[f"hi{lv}"] - df[f"lo{lv}"]
        df[f"interval_score{lv}"] = (width + 2 / alpha * (below + above)) / df["scale"]
    return df


def rolling_backtest(series: pd.DataFrame) -> pd.DataFrame:
    wide = series.pivot(index="ds", columns="unique_id", values="y")
    rows = []
    for uid in wide.columns:
        y = wide[uid]
        for cutoff in origins(series):
            f = forecast(y.loc[:cutoff])
            f["unique_id"], f["cutoff"] = uid, cutoff
            f["y"] = y.reindex(f["ds"]).to_numpy()
            f["scale"] = mase_scale(y, cutoff)
            rows.append(f)
    out = pd.concat(rows, ignore_index=True)
    out["model"] = "OLS"
    return score(out)


def comparisons(long: pd.DataFrame) -> pd.DataFrame:
    by = {m: g for m, g in long.groupby("model")}

    def per_origin(m: str, mask) -> np.ndarray:
        g = by[m][mask(by[m])]
        return g.groupby("cutoff")["abs_scaled_error"].sum().sort_index().to_numpy()

    pairs = [("OLS", "SeasonalNaive"), ("OLS", "AutoETS"), ("AutoETS", "SeasonalNaive")]
    cuts = [("all horizons", lambda d: d["horizon"] > 0),
            ("1 month ahead", lambda d: d["horizon"] == 1),
            ("6 months ahead", lambda d: d["horizon"] == 6)]
    rows = []
    for a, b in pairs:
        for label, mask in cuts:
            ratio, lo, hi = block_bootstrap_ratio(per_origin(a, mask), per_origin(b, mask))
            rows.append({"A": a, "B": b, "horizons": label, "error_ratio": round(ratio, 3),
                         "ci_low": round(lo, 3), "ci_high": round(hi, 3)})
    return pd.DataFrame(rows)


def first_origin_diagnostics(series: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    cutoff = origins(series)[0]
    wide = series.pivot(index="ds", columns="unique_id", values="y").loc[:cutoff]
    coefs, diags, resids = [], [], {}
    for uid in wide.columns:
        m = fit(wide[uid])
        ci = m.conf_int()
        coefs.append(pd.DataFrame({"unique_id": uid, "term": m.params.index,
                                   "estimate": m.params.round(2), "std_error": m.bse.round(2),
                                   "p_value": m.pvalues.round(4),
                                   "ci_low": ci[0].round(2), "ci_high": ci[1].round(2)}))
        lb = acorr_ljungbox(m.resid, lags=[12, 24])
        diags.append({"unique_id": uid, "origin": f"{cutoff:%Y-%m}", "n_months": int(m.nobs),
                      "r_squared": round(m.rsquared, 3),
                      "durbin_watson": round(durbin_watson(m.resid), 2),
                      "breusch_pagan_p": round(het_breuschpagan(m.resid, m.model.exog)[1], 3),
                      "ljung_box_p_lag12": round(lb["lb_pvalue"].iloc[0], 4),
                      "ljung_box_p_lag24": round(lb["lb_pvalue"].iloc[1], 4),
                      "lag1_autocorrelation": round(m.resid.autocorr(1), 2)})
        resids[uid] = m.resid
    return pd.concat(coefs, ignore_index=True), pd.DataFrame(diags), resids


def fig_residual_acf(resids: dict, origin: str) -> None:
    import matplotlib.pyplot as plt
    from statsmodels.tsa.stattools import acf

    import figures  # noqa: F401  (shared plot style)

    fig, axes = plt.subplots(1, len(resids), figsize=(13, 2.8), sharey=True)
    for ax, (uid, r) in zip(axes, resids.items()):
        vals = acf(r, nlags=24)[1:]
        bound = 1.96 / np.sqrt(len(r))
        ax.bar(np.arange(1, 25), vals, color=figures.MODEL_COLORS["AutoETS"], width=0.7)
        ax.axhspan(-bound, bound, color=figures.GRID, alpha=0.7, lw=0, zorder=0)
        ax.set_title(uid, fontsize=10)
        ax.set_xticks([1, 6, 12, 18, 24])
        ax.set_xlabel("Lag (months)")
    axes[0].set_ylabel("Residual ACF")
    fig.suptitle(f"OLS (trend + month) residuals, fitted on Jan 2015 to {origin}; "
                 "shaded band = approximate 95% bounds", x=0.01, ha="left", fontsize=11,
                 fontweight="bold")
    fig.tight_layout()
    COURSE_FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(COURSE_FIGURES / "ols_residual_acf.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    COURSE_RESULTS.mkdir(parents=True, exist_ok=True)
    series = citywide_series()
    ols = rolling_backtest(series)
    ols.to_parquet(COURSE_RESULTS / "ols_forecasts.parquet", index=False)

    base = pd.read_parquet(ROOT / "results" / "backtest_forecasts.parquet")
    long = pd.concat([base, ols[base.columns]], ignore_index=True)
    long = long[long["model"].isin(COMPARED)]
    assert long.groupby("model").size().nunique() == 1, "OLS must cover the same forecasts"

    by_h = summarize(long, ["model", "horizon"])
    by_c = summarize(long, ["unique_id", "model"])
    by_h.to_csv(COURSE_RESULTS / "ols_summary_by_horizon.csv")
    by_c.to_csv(COURSE_RESULTS / "ols_summary_by_category.csv")
    comp = comparisons(long)
    comp.to_csv(COURSE_RESULTS / "ols_comparisons.csv", index=False)

    coefs, diags, resids = first_origin_diagnostics(series)
    coefs.to_csv(COURSE_RESULTS / "ols_first_origin_coefficients.csv", index=False)
    diags.to_csv(COURSE_RESULTS / "ols_first_origin_diagnostics.csv", index=False)
    fig_residual_acf(resids, f"{origins(series)[0]:%b %Y}")

    pd.set_option("display.width", 200)
    print("Overall:\n", summarize(long, ["model"]).sort_values("MASE"))
    print("\nMASE by horizon:\n", by_h["MASE"].unstack())
    print("\nMASE by category:\n", by_c["MASE"].unstack())
    print("\n", comp.to_string(index=False))
    print("\n", diags.to_string(index=False))
    print("\nTrend coefficients at the first origin:\n",
          coefs[coefs["term"] == "trend"].to_string(index=False))


if __name__ == "__main__":
    main()
