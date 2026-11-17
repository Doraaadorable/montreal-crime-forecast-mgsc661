# Slide draft, 25 November

The slides are in [MGSC661_Group6_Final_Presentation.pptx](MGSC661_Group6_Final_Presentation.pptx),
with the speaker notes in each slide's notes. From now on the PPTX is the version to edit;
this page is a text copy for reading and review, and may fall behind it.

Draft text for the title, abstract and slides, with speaker notes. Timings follow the
[presentation plan](PRESENTATION_PLAN.md); together about 8:30. Every number comes from
`results/` or `results/course/`.

## Title and abstract (due 23 November)

**When Can Montréal's Monthly Crime Forecasts Be Trusted for Planning?**

Police planners need estimates of next month's workload, but a forecast is only useful if
they know when to rely on it. Our proof of concept fitted a trend-and-month regression to 44
months of official SPVM statistics. Its residuals were autocorrelated and the series was too
short for repeated testing, so we moved to 142 months of police-recorded incidents (2015 to
2026) in five categories. We compare the regression, exponential smoothing (ETS) and ARIMA
with a same-month-last-year benchmark at 77 rolling forecast origins, 1 to 6 months ahead, and
examine the model structures selected, their residuals and their prediction intervals. ETS
cut the benchmark's error by 40% one month ahead but only 8% six months ahead. The regression
did not beat the benchmark, and its 80% intervals covered 56% of outcomes. When vehicle thefts
more than doubled between 2020 and 2023, no method anticipated the rise, although residual
checks before it detected no autocorrelation. A monitor on forecast errors raised alarms in
2021. We show what these errors mean for capacity plans and propose rules for when to rely on
forecasts and when to review them. (186 words)

## Slides

### 1. The question, and where we started (0:45)

**On slide:** When can monthly crime forecasts be trusted for planning? · Users: public safety
planners preparing monthly workload and capacity · PoC card: official SPVM monthly
statistics, Jan 2023 – Aug 2026 (44 months); OLS with a linear trend and 11 month dummies;
benchmark "same month last year"; one six-month holdout, plus a short one-month-ahead check; hypothesis: largest gains where
seasonality is strong and stable.

**Notes:** Planners who prepare monthly workload need to know how many incidents to expect
next month. A forecast helps only if they also know when to trust it. In our PoC, we used the
SPVM's official monthly statistics from 2023 to 2026 and fitted a regression with a time trend
and month effects, compared with simply using the same month last year. We expected the
largest gains for stable, seasonal crime such as property crime. Today we show how that idea
held up.

### 2. Two PoC limits changed the plan (1:00)

**On slide:** PoC limits: 44 months (limited history for fitting seasonal models and testing across
different periods);
Durbin–Watson 1.02 (autocorrelated residuals) · Change of data, a trade-off: official
statistics (all offences, from 2023) vs incident records (5 categories, from 2015), long
enough to test the years before, during and after the vehicle theft surge · Tried and
dropped: recalibrated intervals (conformal); training on the last 2–3 years (errors 25–45%
higher elsewhere); pooled machine-learning model; district clustering.

**Notes:** The PoC raised two problems. First, our PoC relied on one six-month holdout. With
only 44 months, we had limited history for fitting seasonal models and for testing across
different periods. Second, the regression's residuals were
autocorrelated, so its errors were not independent. We therefore switched to the city's
incident records, which go back to 2015. This was a trade-off: we gave up coverage of all
offences and kept five categories, but gained enough history to test many forecast dates and
the years before, during and after the vehicle theft surge. We also tried some things that
did not work. Recalibrating the intervals did not beat the model's own intervals, and
training only on recent years made errors worse elsewhere.

### 3. Data and rolling validation (0:45)

**On slide:** 365,404 incidents, frozen 15 Nov 2026 · 142 months · 5 categories · 77
forecast dates, each 1–6 months ahead · rolling-origin diagram · every model refitted at
every date; scored by MASE and 80% interval coverage; three shared categories within 2% of
the official statistics; robbery differs.

**Figure:** `figures/course/rolling_origins.png` (drawn natively in the PPTX).

**Notes:** Our data are 365,000 incidents recorded by Montréal police, frozen on 15 November
so results are reproducible. For three shared categories, the totals agree with the official
statistics within 2%; robbery does not, which we discuss in the backup slides. To evaluate fairly, we pretend to stand at 77 different months, fit
every model using only the past, and forecast the next one to six months. Every model gets
exactly the same test.

### 4. From regression to ETS and ARIMA (1:45)

**On slide:** OLS residual ACF for break and enter, 2015–2019 · autocorrelated residuals in
all 5 categories (DW 1.07–1.63; Ljung–Box p < 0.025) · 80% intervals covered only 56% ·
what the two models do: ETS updates its estimated level, trend and seasonality as each month
arrives; ARIMA models dependence over time, differencing where needed · most common
structure in 77 refits (three categories; all five in the backup slides):

| Category | ETS | ARIMA |
|---|---|---|
| Break and enter | ETS(M,Ad,A) | (0,1,1)(0,1,1)[12] |
| Theft from vehicle | ETS(A,N,A) | (0,1,2)(2,0,0)[12] |
| Vehicle theft | ETS(M,N,N) | (0,1,0) |

Footnote: ETS(error, trend, season): N none, A additive, Ad damped, M multiplicative.
Holt-Winters (trend + season) in 20% of ETS fits; seasonal ARIMA in 87%.

**Notes:** We first put the PoC regression into the same rolling test. Its residuals are
autocorrelated in every category: this month's error predicts next month's. The conventional OLS
intervals covered only 56% of outcomes instead of 80%; residual dependence and a fixed trend
both limit this specification. ETS updates its level, trend and seasonality as each month
arrives, and ARIMA models the dependence directly, differencing where needed. We recorded the structure each one selected at
every forecast date. Most ETS fits have a seasonal term but no trend; only 20% are
Holt-Winters. Most ARIMA fits are seasonal, and break and enter needs a seasonal difference.
Vehicle theft is different: before the surge it had no trend and no seasonality, so both
models essentially forecast the current level. The structure also changes from one forecast
date to the next, so "the model" is really a selection rule that is refitted each month.

### 5. Large gains one month ahead, small at six (1:00)

**On slide:** MASE by months ahead for OLS, same month last year, ARIMA and ETS · error ratio
vs the benchmark: ETS 1 month ahead 0.60 (0.51–0.66); ETS 6 months ahead 0.92 (0.81–0.99);
OLS 6 months ahead 1.27 (1.05–1.52).

**Figure:** `figures/course/mase_by_horizon_with_ols.png` (native chart in the PPTX).

**Notes:** One month ahead, ETS cuts the benchmark's error by 40%, and every category
improves. Six months ahead the gain shrinks to 8%, and since 2023 it is no longer clear. ETS
and ARIMA are statistically indistinguishable: error ratio 1.00. The regression is not
clearly different from the benchmark overall (1.17, interval 0.98 to 1.41), and is clearly
worse six months ahead: extrapolating a fixed trend goes wrong once the series turns. So the
value of these models is mainly in the short run.

### 6. Vehicle theft: a surge no method anticipated (1:30)

**On slide:** vehicle thefts per month, Mar 2020 – Jul 2026, with the ETS forecast made 3
months earlier, its 80% interval (shaded) and the upward CUSUM alarms (Apr 2021, Jul 2021,
May 2022; legend: "CUSUM alarm, based on 1-month-ahead errors") · 40% of 2021 outcomes inside the 80% interval (1–6
months ahead) · MASE 2.63 in 2021 (1–6 months ahead); same month last year 3.26 · first
upward alarm April 2021, two years before the August 2023 peak · caption: 2015–2019 flat at
4,200–4,700 a year; no residual autocorrelation detected (ARIMA, Ljung–Box p = 0.78).

**Notes:** Vehicle theft was flat from 2015 to 2019, then more than doubled by 2023 before
falling back. Before the surge, the residual checks detected no autocorrelation, but that did
not mean the models could forecast the rise. The blue line is the forecast made three months
earlier, with its 80% interval shaded. During the surge, forecasts and intervals both missed:
across 2021, the MASE was 2.63 and only 40% of outcomes fell inside the 80% interval. What did
help was watching the one-month-ahead errors: a CUSUM monitor raised its first upward alarm in
April 2021, and another in July, when thefts had reached 652 a month.

*If asked:* MASE 2.63 means the average error was 2.6 times the in-sample error of the
same-month-last-year forecast, which itself scored 3.26 in 2021. The 40% and 2.63 pool all
2021 forecasts, 1 to 6 months ahead. The monitor also flagged a downward miss in February
2021. Training only on recent years did not help.

### 7. Plans fall short more often than intended (1:00)

**On slide:** share of months a 90th-percentile plan fell short, one month ahead: vehicle
theft 20.8%, theft from vehicle 18.2%, break and enter 13.0%, mischief 10.4%, robbery 10.4%,
average shortfall rate across the five categories 14.5%, against a 10% target · half the
loss of "last year + 20%" in a simulation weighting shortfalls 9:1 · demo: interactive
summary page.

**Notes:** Suppose a planner sets capacity at the 90th percentile of next month's forecast,
aiming to fall short only one month in ten. In our test, averaged over the five categories,
plans fell short in 14.5% of months: more often than intended, and twice as often for vehicle
theft. Even so, in a simulation where a shortfall counts nine times as much as spare
capacity, these plans had half the loss of the simple rule "last year plus 20%". This is a
simulated loss under that weighting, not a budget saving. The forecasts are useful, but their stated uncertainty is too optimistic when
a series changes.

### 8. When to rely on the forecasts (0:45)

**On slide:** Rely on one-month-ahead forecasts; at 3–6 months, check them against "same
month last year" · Monitor the forecast errors; after an alarm, review the forecast and
reassess the capacity margin · Do not use for total crime, for causes, or to rate the risk of places or people ·
Limits: police records reflect reporting and policing, not only crime; five categories, not
total crime; not the official statistics; recent months can be revised · Next steps: test
these rules on new monthly releases; keep the error monitor running.

**Notes:** Our recommendations: use the one-month forecasts; at longer horizons, treat them as
roughly as good as last year's count. Watch the errors, and when the monitor raises an alarm,
have someone review the forecast and reassess the capacity margin. These data are police records, so they
reflect reporting and policing as well as crime. They cover five categories, not total
crime, and they say nothing about causes or about which places are risky. The next step is to
check these rules on new months as the city publishes them. Thank you.

## Backup slides

1. Which differences are real: models and horizons, including the OLS comparisons
   (`results/significance.csv`, `results/course/ols_comparisons.csv`)
2. Which differences are real: categories and districts
3. Data consistency and why not K-fold cross-validation (`results/course/bilan_consistency.csv`)
4. Model structures for all five categories (`results/course/structure_frequency.csv`)
5. Why ARIMA differences break and enter: ACF of the counts, the seasonal difference, and both
   differences, with bounds for each series length. After seasonal and first differencing, the
   ACF shows prominent spikes at lags 1 and 12, consistent with the selected MA terms.
   AutoARIMA chooses d and D with KPSS and seasonal-strength tests; the plots illustrate the
   result, they do not decide it.

## Questions to prepare for

- Why not K-fold cross-validation? Random folds would train on the future; rolling origins
  are the time-series equivalent.
- Why change the data after the PoC? A trade-off: all-offence coverage for a history long
  enough to test many origins and the years around the surge.
- Is ETS here Holt-Winters? Only when it selects a trend and a seasonal term: 20% of fits.
- The residual check found nothing, yet the model failed. Why? A residual check describes the
  fit to past data; it cannot test a change that has not happened yet.
- Do the two datasets agree? Closely for three categories, not for robbery; the reason is not
  fully established.

## Still open

- Slide 2 and slide 8: one line on the panel model after the 18 November lecture.
