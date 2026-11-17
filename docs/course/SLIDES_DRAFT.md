# Slide draft, 25 November

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
benchmark "same month last year"; one six-month holdout; hypothesis: largest gains where
seasonality is strong and stable.

**Notes:** Planners who prepare monthly workload need to know how many incidents to expect
next month. A forecast helps only if they also know when to trust it. In our PoC, we used the
SPVM's official monthly statistics from 2023 to 2026 and fitted a regression with a time trend
and month effects, compared with simply using the same month last year. We expected the
largest gains for stable, seasonal crime such as property crime. Today we show how that idea
held up.

### 2. Two PoC limits changed the plan (1:00)

**On slide:** PoC limits: 44 months (one holdout, too short for seasonal models);
Durbin–Watson 1.02 (autocorrelated residuals) · Change of data, a trade-off: official
statistics (all offences, from 2023) vs incident records (5 categories, from 2015), long
enough to test the years before, during and after the vehicle theft surge · Tried and
dropped: recalibrated intervals (conformal); training on the last 2–3 years (errors 25–45%
higher elsewhere); pooled machine-learning model; district clustering.

**Notes:** The PoC raised two problems. First, 44 months allowed only one test and was too
short to estimate seasonal models reliably. Second, the regression's residuals were
autocorrelated, so its errors were not independent. We therefore switched to the city's
incident records, which go back to 2015. This was a trade-off: we gave up coverage of all
offences and kept five categories, but gained enough history to test many forecast dates and
the years before, during and after the vehicle theft surge. We also tried some things that
did not work. Recalibrating the intervals did not beat the model's own intervals, and
training only on recent years made errors worse elsewhere.

### 3. Data and rolling validation (0:45)

**On slide:** 365,404 incidents, frozen 15 Nov 2026 · 142 months · 5 categories · 77
forecast dates, each 1–6 months ahead · rolling-origin diagram · every model refitted at
every date; scored by MASE and 80% interval coverage; shared categories within 2% of the
official statistics.

**Figure:** `figures/course/rolling_origins.png` (drawn natively in the PPTX).

**Notes:** Our data are 365,000 incidents recorded by Montréal police, frozen on 15 November
so results are reproducible. For three shared categories, the totals agree with the official
statistics within 2%. To evaluate fairly, we pretend to stand at 77 different months, fit
every model using only the past, and forecast the next one to six months. Every model gets
exactly the same test.

### 4. From regression to ETS and ARIMA (1:45)

**On slide:** OLS residual ACF for break and enter, 2015–2019 · autocorrelated residuals in
all 5 categories (DW 1.07–1.63; Ljung–Box p < 0.025) · 80% intervals covered only 56% ·
most common structure in 77 refits:

| Category | ETS | ARIMA |
|---|---|---|
| Break and enter | ETS(M,Ad,A) | (0,1,1)(0,1,1)[12] |
| Mischief | ETS(A,N,A) | (0,1,2)(0,1,1)[12] |
| Theft from vehicle | ETS(A,N,A) | (0,1,2)(2,0,0)[12] |
| Robbery | ETS(A,N,A) | (0,1,1)(2,0,0)[12] |
| Vehicle theft | ETS(M,N,N) | (0,1,0) |

Holt-Winters in 20% of ETS fits · seasonal ARIMA in 87% · vehicle theft before the surge: no
trend, no seasonality.

**Notes:** We first put the PoC regression into the same rolling test. Its residuals are
autocorrelated in every category: this month's error predicts next month's. The regression
ignores this, so its intervals are too narrow, covering only 56% of outcomes instead of 80%.
ETS and ARIMA model this dependence directly. We recorded the structure each one selected at
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

**On slide:** vehicle thefts per month with the ETS forecast 3 months ahead and its 80%
interval, Mar 2020 – Jul 2026 · 40% of 2021 outcomes inside the 80% interval · 2.6× the usual
error scale in 2021 · CUSUM alarms in April and July 2021, two years before the August 2023
peak · caption: 2015–2019 flat at 4,200–4,700 a year; no residual autocorrelation detected
(ARIMA, Ljung–Box p = 0.78).

**Notes:** Vehicle theft was flat from 2015 to 2019, then more than doubled by 2023, peaking
at 1,205 in August 2023, and has since fallen 43%. Before the surge, no residual
autocorrelation was detected. That did not mean the models could forecast the rise. In 2021,
errors were 2.6 times their usual size, and the 80% interval contained only 40% of outcomes.
Training only on recent years did not fix it. What did work was watching the forecast
errors: a standard monitor, CUSUM, raised alarms in April and July 2021, when thefts had
reached 652 a month, against 392 a month in 2020. Residual checks look at the past; error
monitoring looks at what is happening now.

### 7. Plans fall short more often than intended (1:00)

**On slide:** share of months a 90th-percentile plan fell short, one month ahead: vehicle
theft 20.8%, theft from vehicle 18.2%, break and enter 13.0%, mischief 10.4%, robbery 10.4%,
average 14.5%, against a 10% target · half the cost of "last year + 20%", with shortfalls
weighted 9:1 · demo: interactive summary page.

**Notes:** Suppose a planner sets capacity at the 90th percentile of next month's forecast,
aiming to fall short only one month in ten. In our test, plans fell short in 14.5% of months:
more often than intended, and twice as often for vehicle theft. Even so, if a shortfall costs
nine times as much as spare capacity, these plans cost half as much as the simple rule "last
year plus 20%". The forecasts are useful, but their stated uncertainty is too optimistic when
a series changes.

### 8. When to rely on the forecasts (0:45)

**On slide:** Rely on one-month-ahead forecasts; at 3–6 months, check them against "same
month last year" · Monitor the forecast errors; after an alarm, review by hand and widen the
plan · Do not use for total crime, for causes, or to rate the risk of places or people ·
Limits: police records reflect reporting and policing, not only crime; five categories, not
total crime; not the official statistics; recent months can be revised · Next steps: test
these rules on new monthly releases; keep the error monitor running.

**Notes:** Our recommendations: use the one-month forecasts; at longer horizons, treat them as
roughly as good as last year's count. Watch the errors, and when the monitor raises an alarm,
have someone review the forecast and widen the plan. These data are police records, so they
reflect reporting and policing as well as crime. They cover five categories, not total
crime, and they say nothing about causes or about which places are risky. The next step is to
check these rules on new months as the city publishes them. Thank you.

## Backup slides

1. Which differences are real: block-bootstrap error ratios (`results/significance.csv`)
2. Data consistency and why not K-fold cross-validation (`results/course/bilan_consistency.csv`)
3. Why ARIMA differences break and enter: ACF of the counts, the seasonal difference, and both
   differences, with bounds for each series length

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
