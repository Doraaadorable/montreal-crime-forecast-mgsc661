# MGSC 661 course version

MGSC 661 Multivariate Statistics, Group 6. This folder adapts the project for the course:
it adds the PoC's regression to the rolling backtest, explains which ETS and ARIMA models
were actually fitted, and checks the data against the SPVM's official monthly statistics.

- [How the project changed since the PoC](EVOLUTION.md)
- [Presentation plan (25 November)](PRESENTATION_PLAN.md)
- [Contributions and AI use: to complete and sign](CONTRIBUTIONS_AND_AI.md)

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

This file is not the SPVM's official statistics; the official monthly figures are the
**Bilan mensuel sur la criminalité**, which the PoC used. For January 2023 to October 2026,
the two agree closely on the categories they share (`results/course/bilan_crosscheck.csv`):

| Category | Incident file ÷ official | Monthly correlation |
|---|---|---|
| Vehicle theft | 0.98 | 0.999 |
| Break and enter | 0.99 | 0.993 |
| Mischief | 0.99 | 0.997 |
| Robbery | 0.64 | 0.765 |

Robbery differs because the official figures count crimes against the person by victim.

## Course results

**The PoC regression does not hold up in a longer, rolling test.** OLS with a linear trend
and month dummies, refitted at the same 77 origins, has a MASE of 1.46, against 1.25 for
"same month last year" and 1.01 for ETS. Its error is 17% above the benchmark overall
(95% interval 0.98 to 1.41) and 27% above at six months ahead (1.05 to 1.52). The fixed trend
is the problem: at the first origin, four of five categories had a significant downward
trend from 2015 to 2019, and extrapolating it went wrong once the series turned.

**Its residuals explain why.** At the first origin, Durbin–Watson is 1.07 to 1.63 and
Ljung–Box rejects independence for all five categories (lag 12, p < 0.025), as in the PoC
(DW 1.02). The OLS intervals assume independent errors, so they are too narrow: the 80%
interval covered 56% of outcomes. This is the reason to move to ETS and ARIMA, which model
the dependence.

**What ETS and ARIMA chose.** Across 77 origins × 5 categories:

- ETS included a trend in 20% of fits and seasonality in 66%. Only fits with both a trend
  and a seasonal term, such as ETS(A,A,A), are Holt-Winters: 20% of fits, all in break and
  enter, mischief and theft from vehicle. The most common fit is ETS(A,N,A) (34%): seasonal
  smoothing without a trend.
- ARIMA was seasonal in 87% of fits. Break and enter and mischief nearly always used a
  seasonal difference (D = 1).
- Vehicle theft is the exception. ETS was ETS(M,N,N) or ETS(A,N,N) at 76 of 77 origins: no
  trend, no seasonality, α between 0.39 and 0.97. ARIMA was most often a random walk,
  ARIMA(0,1,0). Both models forecast "about the current level".
- Structures change from origin to origin (3 to 13 distinct structures per category), so
  "the model" is a selection rule refitted each month, not one fixed equation.

**Diagnostics passed before the vehicle theft surge.** At the first origin (data to December
2019), vehicle theft had no trend and no month effect in the OLS fit (trend p = 0.20, no month
coefficient significant). The ETS and ARIMA residuals showed no autocorrelation (Ljung–Box
p = 0.23 and 0.58 at lag 12). The models were a fair description of the past; the 2021–2023
surge had no precedent in it. In-sample diagnostics cannot warn of that kind of change; the
CUSUM on forecast errors raised alarms in April and July 2021. Robbery is the opposite case:
both models failed Ljung–Box (p = 0.003 and 0.002) yet forecast it reasonably well.

The other results (accuracy by horizon, interval coverage by year, planning, monitoring)
are in the [main findings](../FINDINGS.md).

## Workflow

```
data/snapshots/2026-11-15.csv.gz ─┬─> backtest.py ──> results/backtest_forecasts.parquet
(frozen monthly counts)           │      (Naive, same month last year, ETS, ARIMA, Theta)
                                  ├─> course_ols.py ──> OLS in the same 77-origin backtest
                                  ├─> course_structure.py ──> fitted structures, residual checks
data/bilan/ (official statistics) ┴─> course_bilan_check.py ──> cross-check
course/r/check_first_origin.R ──> the same first-origin fits in R (fpp2), as in Lab 10
```

| Script | Output |
|---|---|
| `src/course_data.py` | Citywide series from the frozen snapshot; the 77 origins |
| `src/course_ols.py` | `results/course/ols_*`, `figures/course/ols_residual_acf.png` |
| `src/course_structure.py` | `results/course/model_structures.csv`, `structure_frequency.csv`, `structure_selected_origins.csv`, `residual_checks_first_origin.csv`, `figures/course/differencing_acf.png`, `figures/course/residuals_vehicle_theft.png` |
| `src/course_bilan_check.py` | `results/course/bilan_crosscheck.csv` |
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

To reproduce the R cross-check, install `fpp2` and run `Rscript course/r/check_first_origin.R`
from the repository root.
