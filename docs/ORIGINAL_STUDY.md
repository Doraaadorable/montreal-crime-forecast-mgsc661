# Original study: when can monthly crime forecasts be trusted?

This is the README of Dora Zhuang's study
[montreal-crime-forecast](https://github.com/Doraaadorable/montreal-crime-forecast),
which the MGSC 661 course version builds on. Paths are relative to this file.

Between 2020 and 2023, vehicle thefts in Montréal more than doubled, then fell 43% in two
years. None of the seven methods tested caught either turn. This project replays six years of
forecasts on 365,000 police-recorded incidents to find where forecasts hold up and where they
break.

**Dora Zhuang** ·
[Interactive summary](https://doraaadorable.github.io/montreal-crime-forecast/) ·
[Full findings](FINDINGS.md)

## Findings

Every model is refit at 77 points in time and forecasts 1 to 6 months ahead from the months
before that point.

**1. Models beat "same month last year" by 19%, mostly in the short run.**
One month ahead, ETS cuts the benchmark's error by 40%. Six months ahead the gain is 8%, and
since 2023 it is no longer clear.

**2. A structural break defeats every method tested.**
On 2021 forecast months, ETS errors on vehicle theft were 2.6 times the benchmark scale, and
only 40% of outcomes fell inside its 80% interval. Fitting on only the last two or three years
did not help, and raised errors on the other four categories by 25% to 45%.

![Vehicle theft forecasts](../figures/fig4_vehicle_theft.png)

**3. The errors signalled the break long before the peak.**
A standard monitor on the forecast errors raised alarms in April and July 2021. By July thefts
had reached 652 a month, up from 392 in 2020. The peak of 1,205 came in August 2023.

**4. Uncertainty ranges fail when they matter.**
80% intervals covered 50% of outcomes in 2020 and 61% in 2021, then 78% to 81% from 2023 on.
Recalibration did not fix this. The standard method overcorrects to 91%. The adaptive one
averages 81% by swinging from 92% in 2022 to 73% in 2026, and the model's own interval scored
better in every year.

![Coverage by year](../figures/fig3_coverage_by_year.png)

**5. For small districts, pooling beats separate models.**
A typical district series has 14 incidents a month. Splitting the citywide forecast by each
district's share of the last year beats a model per district by 5%. With the model and its
inputs held fixed, training on all 145 series at once cuts error by 7% against training each
alone.

**6. Plans built on these forecasts fall short more often than intended.**
A plan set at the 90th percentile, one month ahead, should be short in 10% of months. It was
short in 14.5%: 21% for vehicle theft, 10% for robbery and mischief. With shortfalls weighted
nine to one against spare capacity, it still costs half as much as planning on "last year plus
20%".

## Which differences are real

Error ratios with 95% intervals from a block bootstrap over the 77 forecast origins. Below 1
favours the first method.

| Comparison | Error ratio | 95% interval |
|---|---|---|
| Citywide: ETS vs same month last year | 0.81 | 0.71 to 0.86 |
| Same, 1 month ahead | 0.60 | 0.51 to 0.66 |
| Same, 6 months ahead | 0.92 | 0.81 to 0.99 |
| Citywide: ARIMA vs ETS | 1.00 | 0.95 to 1.09 |
| Citywide: average of ETS, ARIMA, Theta vs ETS | 0.97 | 0.95 to 1.00 |
| District: top-down split vs separate ETS | 0.95 | 0.93 to 0.97 |
| District: pooled vs separate training, same model | 0.93 | 0.91 to 0.95 |
| District: pooled model vs top-down split | 0.99 | 0.98 to 1.00 |

The choice between ETS and ARIMA, or between a pooled model and the top-down split, makes no
clear difference. How far ahead the forecast is, and whether the series is stable, matter more.

All but the pooled-versus-separate test were rerun with other block lengths and on each half of
the test period. Three
readings are sensitive to those choices: the six-month gain, the forecast average against ETS,
and the pooled model against the top-down split.

## Method

- **Data.** 365,404 incidents recorded by the Service de police de la Ville de Montréal (SPVM),
  January 2015 to October 2026, in five categories and 29 police districts.
- **Backtest.** 77 rolling origins, horizons of 1 to 6 months, 80% and 95% intervals.
- **Models.** ETS, ARIMA, Theta, their average, a pooled LightGBM model with a Poisson loss,
  and two naive benchmarks. Hyperparameters were fixed in advance.
- **Uncertainty.** Coverage and interval scores; split and adaptive conformal calibration;
  Poisson and negative binomial intervals for small counts.
- **Hierarchy.** City, category, district and category by district (180 series), reconciled
  bottom-up, top-down, and by OLS and WLS projection, written out in `src/hierarchy.py`.
- **Significance.** Moving-block bootstrap on error ratios, in blocks of 12 origins.
- **Monitoring.** CUSUM on one-month-ahead errors with textbook settings.

The counts are incidents recorded by police, so they reflect reporting and recording practice
as well as crime. The backtest uses the data as published on 15 November 2026; earlier
versions of recent months may have differed.

## Reproduce

```bash
pip install -r requirements.txt
python src/run_all.py                   # downloads today's data, then runs every step
pytest                                  # method checks, no data needed
```

The source is updated daily, so a new download shifts the numbers slightly. To reproduce the
committed results exactly, place the data version recorded in `data/manifest.json` at
`data/raw/actes_criminels.csv`, then:

```bash
python src/run_all.py --skip-download   # about 22 minutes on 4 cores
python src/verify_outputs.py            # checks every committed output against recorded hashes
```

With the package versions in `requirements.txt`, a fresh clone reproduces every committed
result, figure and the summary page byte for byte.

## Data and license

Data: [Actes criminels](https://donnees.montreal.ca/dataset/actes-criminels), Service de police
de la Ville de Montréal, Ville de Montréal open data portal,
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Code: [MIT](../LICENSE).
