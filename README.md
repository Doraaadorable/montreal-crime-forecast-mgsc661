# When can Montréal's monthly incident forecasts be trusted for planning?

**MGSC 661 Multivariate Statistics, Group 6** (Fall 2026): Weiwei Xu, Dora Zhuang, Eric Sun,
Renkai Zhu, Vincent Wang.

This is the course version of the project. It builds on Dora Zhuang's study
[montreal-crime-forecast](https://github.com/Doraaadorable/montreal-crime-forecast)
([its README](docs/ORIGINAL_STUDY.md)).

## Start here

| | |
|---|---|
| [Course analysis](docs/course/README.md) | Question, data, methods, results and workflow |
| [From the PoC to the final project](docs/course/EVOLUTION.md) | What changed since the 15 October PoC, and why |
| [Presentation plan](docs/course/PRESENTATION_PLAN.md) | 25 November presentation |
| [Contributions](docs/course/CONTRIBUTIONS.md) | Draft, to be completed by the group |
| [Original study findings](docs/FINDINGS.md) | Full results of the underlying study |
| [Interactive summary](https://doraaadorable.github.io/montreal-crime-forecast/) | Demo page of the original study |

## Question

1. Do the models beat "same month last year"?
2. How do forecasts and their uncertainty fail when the series changes, as with the
   vehicle theft surge?
3. What happens when plans are built on these forecasts?

## Data and methods in brief

- **Data.** SPVM incident records (Actes criminels, Montréal open data), downloaded
  15 November 2026 and frozen: five categories, January 2015 to October 2026. The PoC used
  the official monthly statistics (Bilan mensuel), which cover all offences but start in 2023;
  the change is explained in the [evolution note](docs/course/EVOLUTION.md).
- **Validation.** 77 rolling forecast origins, 1 to 6 months ahead, the same for every model.
- **Models.** "Same month last year" (benchmark), the PoC's OLS with trend and month dummies,
  ETS and ARIMA. Theta, a forecast average and a pooled LightGBM model are in the original
  study.
- **Diagnostics.** OLS residual dependence with HAC standard errors; the ETS and ARIMA
  structures actually selected at each origin; residual ACF and Ljung–Box tests.
- **Use.** Interval coverage, an error monitor (CUSUM) and a one-month-ahead planning example.

## Reproduce the course results

```bash
pip install -r requirements.txt pytest
python src/course_run_all.py   # about 4 minutes; reads the frozen snapshot, no download
pytest -q
```

The course scripts read `data/snapshots/2026-11-15.csv.gz` and the committed backtest results
in `results/`, so they give the same numbers on any machine. Rerunning the full original
pipeline (`python src/run_all.py`) downloads the current data, which the city updates daily,
and so gives slightly different numbers; see the [original README](docs/ORIGINAL_STUDY.md).

## Data and license

Data: [Actes criminels](https://donnees.montreal.ca/dataset/actes-criminels) and
[Bilan mensuel sur la criminalité](https://donnees.montreal.ca/dataset/bilan-mensuel-criminalite),
Service de police de la Ville de Montréal, Ville de Montréal open data portal,
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Code: [MIT](LICENSE).
