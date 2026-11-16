# Contributions and AI use (draft: to complete and sign)

The course asks for a short AI use disclosure signed by all members, and evaluates teamwork.
This page records what can be checked from the files and leaves the rest for the group to
fill in. Do not fill a blank with anything that did not happen.

## Members

| Name | Student ID |
|---|---|
| Weiwei Xu | **check**: 261090107 on the pitch slides, 261098107 in the PoC report |
| Dora Zhuang | 261012351 |
| Eric Sun | 261320838 |
| Renkai Zhu | 261333162 |
| Vincent Wang | 261347738 |

## Where the work came from

| Work | Date | What the files show | Who did what (group to fill) |
|---|---|---|---|
| Pitch slides | 7 Oct 2026 | Group 6 pitch, all five names | |
| PoC report and notebook | 15 Oct 2026 | Group 6 report, all five names; the notebook's saved output was last run under a user folder named `changsun` | |
| Extended study (main branch of this repository) | 15–16 Nov 2026 | 19 commits from one GitHub account (Doraaadorable): data pipeline, rolling backtest, intervals, reconciliation, pooled model, planning, monitoring, summary page | |
| Course additions (branch `course/mgsc661`) | 16 Nov 2026 | Written by an AI coding assistant (Claude Code) at a member's request; commits authored "Claude" | Review and verification: |
| R cross-check, slides, final report | 17 Nov to 12 Dec 2026 | Not yet done | |

## Remaining work to assign

Each item has a concrete output that shows who did it.

| Task | Output | Assigned to |
|---|---|---|
| Run `course/r/check_first_origin.R` in R (fpp2) and compare with the Python structures | `course/r/r_first_origin_structures.csv`, a short note on any difference | |
| Rerun `python src/course_run_all.py` and `pytest` on your own machine; confirm the numbers | A line in this file with date and result | |
| Interpret the OLS results: month profile, trend, residual dependence, why it loses | Report section and slide 4 | |
| Interpret the ETS and ARIMA structures and residual checks | Report section and slide 4 | |
| Vehicle theft case: forecasts, intervals, CUSUM alarms | Slide 6 and report section | |
| Planning example or demo; recommendations and limits | Slides 7 and 8 | |
| Read the 18 November panel data slides; decide whether a panel model answers a question the project has (default: no) | A short note with the reason | |
| Title and abstract (23 Nov), slides (24 Nov), rehearsal to 10 minutes | Submitted files | |
| Final report (6 pages + appendix, 12 Dec): editing; every number checked against `results/` | Submitted report | |

Every member should be able to explain any slide, not only their own.

## AI use disclosure (draft)

| Tool | Used for | By whom | How the output was checked |
|---|---|---|---|
| Claude Code | Writing the course scripts (`src/course_*.py`, `tests/test_course.py`, `course/r/`), running them, drafting the documents in `docs/course/`, checking the open data sources | | Tests; refitted models reproduce the backtest forecasts exactly; numbers checked against output files; (add member checks) |
| (add other tools used for the PoC, the main branch, slides or report) | | | |

We used the tools above as described. We have read, checked and understood the submitted
work, and each of us can explain it.

| Name | Signature | Date |
|---|---|---|
| Weiwei Xu | | |
| Dora Zhuang | | |
| Eric Sun | | |
| Renkai Zhu | | |
| Vincent Wang | | |
