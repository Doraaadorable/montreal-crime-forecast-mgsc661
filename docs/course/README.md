# MGSC 661 course version

MGSC 661 Multivariate Statistics, Group 6. This folder adapts the project for the course:
it adds the PoC's regression to the rolling backtest, explains which ETS and ARIMA models
were actually fitted, and compares the data with the SPVM's official monthly statistics.

- [How the project changed since the PoC](EVOLUTION.md)
- [Presentation plan (25 November)](PRESENTATION_PLAN.md)
- [Contributions: to complete](CONTRIBUTIONS.md)

## Question

When can Montréal's monthly incident forecasts be trusted for planning?

1. Do the models beat "same month last year"?
2. How do forecasts and their uncertainty fail when the series changes, as with the
   vehicle theft surge?
3. What happens when plans are built on these forecasts?

## Data

**Actes criminels** (SPVM incident records, Montréal open data, CC BY 4.0), as downloaded on
15 November 2026: 365,404 incidents, January 2015 to 13 November 2026. The analysis uses the
complete months January 2015 to October 2026 in five categories: break and enter, theft from
vehicle, vehicle theft, mischief and robbery.

The portal replaces this file every day and keeps no old versions. The course scripts
therefore read the committed snapshot `data/snapshots/2026-11-15.csv.gz`, which rebuilds
the backtest data exactly. The 16 November update changed three complete months by 3 incidents
in total (October +2, April −1), so the analysis is not rerun on later downloads.

This file is not the SPVM's official statistics; the portal points to the
**Bilan mensuel sur la criminalité**, which the PoC used, for the official monthly picture.
The two are not interchangeable. As a consistency check, not an independent validation (both
come from the same police records system), we compared the categories they share for January
2023 to October 2026 (`results/course/bilan_consistency.csv`):

| Category | Incident file ÷ official | Monthly correlation |
|---|---|---|
| Vehicle theft | 0.98 | 0.999 |
| Break and enter | 0.99 | 0.993 |
| Mischief | 0.99 | 0.997 |
| Robbery | 0.64 | 0.765 |

Three categories line up closely, though not exactly. Robbery does not. One documented
difference is the counting unit: the official file counts crimes against the person, robbery
included, by victim, while the incident file has one row per event. We have not confirmed
that this explains a gap of this size; category definitions and geographic coverage could
also differ. The final analysis does not depend on robbery matching.

## Course results

**The PoC regression does not hold up in a longer, rolling test.** OLS with a linear trend
and month dummies, refitted at the same 77 origins, has a MASE of 1.46, against 1.25 for
"same month last year" and 1.01 for ETS. Overall it is not clearly different from the benchmark (error ratio
1.17, 95% interval 0.98 to 1.41); six months ahead it is clearly worse (1.27, 1.05 to 1.52).
A likely reason is the fixed linear trend: at the first origin, four of five categories had
a significant downward trend from 2015 to 2019 (p < 0.002 with Newey–West standard errors,
which allow for the autocorrelated residuals), and the error grows with the horizon, as it
would if extrapolating that trend went wrong once the series turned.

**Its residuals are autocorrelated.** At the first origin, Durbin–Watson is 1.07 to 1.63 and
Ljung–Box detects residual autocorrelation in all five categories (lag 12, p < 0.025), as in the PoC
(DW 1.02). The usual OLS intervals assume independent errors around a correct trend; here
neither holds, and the 80% interval covered 56% of outcomes. ETS and ARIMA model the
dependence directly, which is the reason to move to them. For the same reason, the
coefficient tables report Newey–West (HAC) standard errors next to the usual ones (lag 3,
fixed in advance by the standard rule; lag 12 as a check).

**What ETS and ARIMA chose.** Across 77 origins × 5 categories:

- ETS included a trend in 20% of fits and seasonality in 66%. Only fits with both a trend
  and a seasonal term, such as ETS(A,A,A), are Holt-Winters: 20% of fits, all in break and
  enter, mischief and theft from vehicle. The most common fit is ETS(A,N,A) (34%): seasonal
  smoothing without a trend.
- ARIMA was seasonal in 87% of fits. Break and enter and mischief nearly always used a
  seasonal difference (D = 1).
- Vehicle theft is the exception. ETS was ETS(M,N,N) or ETS(A,N,N) at 76 of 77 origins: no
  trend, no seasonality, α between 0.39 and 0.97, so its forecasts stay flat at the latest
  smoothed level. ARIMA was most often ARIMA(0,1,0) without drift (29 origins), a random walk
  whose forecasts stay at the last value, or ARIMA(1,0,0) with a mean (21 origins), whose
  forecasts move back toward the training average.
- Structures change from origin to origin (3 to 13 distinct structures per category), so
  "the model" is a selection rule refitted each month, not one fixed equation.

**Residual checks did not flag the coming surge.** At the first origin (data to December
2019), vehicle theft was flat: 4,170 to 4,732 incidents a year from 2015 to 2019, no
significant trend or month effect in the OLS fit (trend p = 0.26, HAC). The ARIMA(1,0,0) residuals
showed no evidence of autocorrelation (Ljung–Box p = 0.78 at lag 12, all 60 residuals,
1 degree of freedom removed): no residual autocorrelation was detected at the tested lags.
That does not mean the model could forecast the sustained rise that followed. The forecast errors did flag it: the CUSUM raised
alarms in April and July 2021. (The ETS check, p = 0.23, removes no degrees of freedom and is
only indicative; see `src/course_structure.py`.)

The diagnostics reported here are for the statsforecast models that produced the backtest
forecasts. The R script repeats the first origin with the course's `ets()`, `auto.arima()`
and `checkresiduals()` as an independent check of the method; if R selects a different
structure, the difference is reported and explained, not substituted.

**What goes where.** The presentation uses representative structures and the vehicle theft
residual checks. The full structure frequency, the per-origin parameter table and the data
consistency table are appendix material.

The other results (accuracy by horizon, interval coverage by year, planning, monitoring)
are in the [main findings](../FINDINGS.md).

## Workflow

```
Original study (already run; outputs committed)
  data/raw/actes_criminels.csv (15 Nov download, not in the repository)
    └─> backtest.py ──> results/backtest_forecasts.parquet
                         (Naive, same month last year, ETS, ARIMA, Theta at 77 origins)

Course additions (python src/course_run_all.py)
  data/snapshots/2026-11-15.csv.gz (monthly counts from the same download, committed)
    ├─> course_ols.py ─────────┐   OLS at the same 77 origins; compared with the
    │                          ├── committed backtest results above
    ├─> course_structure.py ───┘   refits ETS and ARIMA; checks they match the backtest
    └─> course_bilan_check.py <── data/bilan/ (official monthly statistics)
  course/r/check_first_origin.R    first-origin fits in R (fpp2), independent check
```

| Script | Output |
|---|---|
| `src/course_data.py` | Citywide series from the frozen snapshot; the 77 origins |
| `src/course_ols.py` | `results/course/ols_*`, `figures/course/ols_residual_acf.png` |
| `src/course_structure.py` | `results/course/model_structures.csv`, `structure_frequency.csv`, `structure_selected_origins.csv`, `residual_checks_first_origin.csv`, `figures/course/differencing_acf.png`, `figures/course/residuals_vehicle_theft.png` |
| `src/course_bilan_check.py` | `results/course/bilan_consistency.csv` |
| `course/r/check_first_origin.R` | `course/r/r_first_origin_structures.csv` (not yet run) |

Choices fixed before looking at results: the OLS specification (identical to the PoC), the
77 origins and 1 to 6 month horizons of the main backtest, and three origins for the
structure tables (first, December 2022, last).

## Reproduce

```bash
pip install -r requirements.txt pytest
python src/course_run_all.py      # about 4 minutes, no download needed
pytest -q
```

To run the R check, install `fpp2` and run `Rscript course/r/check_first_origin.R`
from the repository root.
