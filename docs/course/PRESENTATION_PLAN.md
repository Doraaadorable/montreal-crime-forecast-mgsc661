# Presentation plan, 25 November

8 to 10 minutes of talk, 2 to 4 minutes of questions, 12 minutes at most. Title and abstract
due 23 November, slides 24 November.

**One line:** forecasts are useful one month ahead until the series changes; residual checks
cannot see that coming, but forecast errors can.

| # | Slide | Time | Content | Figure or table |
|---|---|---|---|---|
| 1 | Question and PoC recap | 0:45 | Who would use monthly forecasts and for what. PoC: Bilan data 2023–2026, OLS trend + month, one holdout, hypothesis that stable seasonal crime gains most | One line per item |
| 2 | How the project changed | 1:00 | Two PoC limits: 44 months, DW = 1.02. Switch to the incident file from 2015 (fewer categories, not official statistics, checked against them). Tried and dropped: conformal recalibration, short training windows, pooled LightGBM, PDQ clustering | Table from EVOLUTION.md, shortened |
| 3 | Data and workflow | 0:45 | Five categories, 142 months, 77 rolling origins, 1–6 months ahead, same for every model | Rolling-origin diagram |
| 4 | From regression to ETS and ARIMA | 1:45 | OLS residuals are autocorrelated (DW 1.07–1.63) and its 80% intervals cover 56%. What ETS and ARIMA actually chose; Holt-Winters in 20% of fits; seasonal differencing for break and enter | `figures/course/ols_residual_acf.png`, `figures/course/differencing_acf.png`, a short structure table |
| 5 | Accuracy by horizon | 1:00 | ETS 40% better than the benchmark one month ahead, 8% at six months; OLS worse than the benchmark | `figures/fig2_mase_by_horizon.png` with OLS added, or `results/course/ols_summary_by_horizon.csv` |
| 6 | The vehicle theft surge | 1:30 | Before 2020: no trend, no seasonality, residual checks pass. 2021: forecasts and intervals fail (40% coverage). CUSUM alarms in April and July 2021 | `figures/fig4_vehicle_theft.png`, `figures/course/residuals_vehicle_theft.png` (one panel) |
| 7 | Planning example or demo | 1:00 | Plan at the 90th percentile one month ahead: short in 14.5% of months instead of 10% | `results/planning_one_month_ahead.csv`, interactive page |
| 8 | Recommendations, limits, next steps | 0:45 | Trust one-month forecasts for stable categories; at longer horizons use the benchmark as a check; on an alarm, review by hand. Limits: police records, five categories, revisions | Three bullets |

Total about 8:30, leaving room within 10 minutes.

**Out of the main talk, kept as backup slides for questions:** district pooling and
reconciliation; Theta and the forecast average; conformal details; the bootstrap table;
the Bilan cross-check; why not K-fold.

**Questions to prepare for**

- Why not K-fold cross-validation? (Random folds train on the future.)
- Why change the data after the PoC? (Length, and the surge.)
- Is ETS here Holt-Winters? (Only when it selects a trend and a seasonal term: 20% of fits.)
- Why trust a model whose residual check passed and which then failed? (We do not: that is
  the point of slide 6.)
- What would a police planner do differently? (Slide 8.)
