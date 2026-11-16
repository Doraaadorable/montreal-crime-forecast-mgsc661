# From the PoC to the final project

Sources: the submitted PoC report (15 October 2026), the pitch slides (7 October), the PoC
notebook `crime_poc_analysis.ipynb`, and the 13 anonymous peer responses to the pitch.
The instructor confirmed that the final project need not match the PoC.

## The PoC

- **Question.** Can a trend and calendar-month model forecast monthly recorded offence counts
  in Montréal more accurately than the same month last year? Does accuracy differ across
  offence groups?
- **Initial hypothesis.** The largest gains over the benchmark would come where seasonal
  patterns are strong and stable, such as property crime.
- **Data.** Bilan mensuel sur la criminalité (official SPVM monthly statistics), January 2023
  to August 2026: 44 months, 29 PDQs, five offence groups, 31 subgroups. Six series: the
  citywide total and each group.
- **Method.** OLS with an intercept, a linear trend and 11 month dummies. Trained on 38
  months, tested on March to August 2026. Seasonal naive benchmark. MAE, MAPE and RMSE.
- **Results.** Citywide MAPE 3.99% for OLS against 5.09% for the benchmark. Durbin–Watson
  1.02: residuals positively autocorrelated. Exploratory K-means on PDQ offence shares.
- **Next steps it named.** Several forecast origins; prediction intervals with empirical
  coverage; a seasonal time-series model, kept only if out-of-sample evidence supports it.

## What changed and why

| PoC | Final | Why |
|---|---|---|
| Bilan mensuel, 44 months from 2023 | Actes criminels, 142 months from 2015 | 44 months (about 3.5 seasonal cycles) is too short for many forecast origins or for estimating seasonal models. The Bilan also starts after the vehicle theft surge began, so it cannot show how forecasts fail through it. |
| All recorded offences, five broad groups | Five categories: break and enter, theft from vehicle, vehicle theft, mischief, robbery | The longer file covers only these. The final results do not describe total crime. |
| OLS trend + month | OLS kept as a baseline; ETS and ARIMA added | The PoC's Durbin–Watson of 1.02 showed dependent residuals, which OLS ignores and ETS and ARIMA model. |
| One six-month holdout | 77 rolling origins, 1 to 6 months ahead, same for every model | Named in the PoC's next steps. One holdout of six spring and summer months cannot separate methods. |
| No intervals | 80% and 95% intervals, coverage by year | Named in the PoC's next steps; also asked for in peer feedback. |
| MAE, MAPE, RMSE | MASE and interval score | The PoC noted MAPE is unstable for small counts. MASE compares categories of different size. |
| K-means on PDQ offence shares | Dropped | It described offence mix but did not help answer the forecasting question. |

The PoC's OLS result (3.99% against 5.09%) is not comparable with the final results: it
comes from a different file, different series and one holdout. In the final rolling test,
the same OLS model is worse than the benchmark (see [README](README.md)).

**The initial hypothesis, tested: partly supported.** The stable seasonal series were
forecast most accurately (ETS MASE 0.85 for break and enter, 0.93 for mischief) and vehicle
theft, also property crime, least accurately (1.46). But the gain over the benchmark was not
largest for the stable series: on vehicle theft, "same month last year" did even worse (2.09),
because copying last year fails most when the level shifts. Whether a series was stable
mattered more than the type of crime.

## Main difficulties

- **Series length against relevance.** The official monthly file is the better measure of
  crime but too short; the longer incident file covers fewer categories and is not the
  official statistics. The overlap check shows the two agree on vehicle theft, break and enter
  and mischief (within 2%), but not on robbery, which the official file counts by victim.
- **Data that changes daily.** Both files are revised after publication, and the incident
  file keeps no old versions. The analysis is frozen on the 15 November download.
- **A structural break.** Vehicle theft more than doubled from 2020 to 2023. No method tested
  anticipated it, which turned the project from "which model is best" to "when can forecasts
  be trusted".

## Tried and dropped

| Tried | Result |
|---|---|
| Recalibrating intervals (split and adaptive conformal) | Did not fix coverage in the years it failed; the model's own intervals scored better |
| Fitting ETS on only the last 2 or 3 years, to react faster to the surge | Did not help vehicle theft and raised errors on the other categories by 25% to 45% |
| A pooled LightGBM model across districts | No clear gain over splitting the city forecast by district share |
| PDQ clustering (PoC) | Not needed for the forecasting question |

## Response to peer feedback

Feedback came from classmates; only suggestions that improve the analysis were acted on.

| Suggestion | Response |
|---|---|
| Handle low or irregular counts (#2) | Poisson and negative binomial intervals for small district series |
| Explain how errors affect planning decisions (#2, #3) | Planning example: how often a plan set at the 90th percentile falls short |
| Add prediction ranges (#9) | 80% and 95% intervals, coverage checked by year |
| More visuals (#5) | Presentation |
| K-fold cross-validation (#11) | Not used: random folds would train on the future. Rolling origins are the time-series equivalent. |
| Time of day and day of week (#13) | Not used: the target is a monthly count |
| Unreported crime, socioeconomic factors, profiling (#7, #8, #10) | Stated as limits: the data are police records, which reflect reporting and policing; no information on people; the project does not explain causes or rate places by risk |
| "Y is not predictable" (#12) | This is the research question: the results show when it is and when it is not |
