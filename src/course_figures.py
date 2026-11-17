"""Figures for the course report and slides.

    figures/course/mase_by_horizon_with_ols.png   accuracy by horizon, the PoC regression added
    figures/course/rolling_origins.png            how the 77-origin rolling validation works

Usage:
    python src/course_figures.py     # needs results/course/ols_summary_by_horizon.csv
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle

import figures
from course_data import COURSE_FIGURES, COURSE_RESULTS

LABELS = {"AutoETS": "ETS", "AutoARIMA": "ARIMA", "SeasonalNaive": "Same month last year",
          "OLS": "OLS trend + month (PoC)"}
COLORS = {**figures.MODEL_COLORS, "OLS": "#7a5195"}


def save(fig: plt.Figure, name: str) -> None:
    COURSE_FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(COURSE_FIGURES / name, dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig_mase_with_ols() -> None:
    table = pd.read_csv(COURSE_RESULTS / "ols_summary_by_horizon.csv").pivot(
        index="horizon", columns="model", values="MASE")
    fig, ax = plt.subplots(figsize=(8, 4.6))
    for model in ["OLS", "SeasonalNaive", "AutoARIMA", "AutoETS"]:
        ax.plot(table.index, table[model], color=COLORS[model], lw=2, marker="o", ms=5,
                ls="--" if model == "OLS" else "-", label=LABELS[model])
    ax.set_xlabel("Months ahead")
    ax.set_ylabel("MASE (lower is better)")
    ax.set_title("ETS and ARIMA gain most one month ahead;\nthe regression has higher average "
                 "error than the benchmark at every horizon")
    ax.set_xticks(table.index)
    ax.grid(axis="x", visible=False)
    ax.legend(loc="center left", bbox_to_anchor=(1.0, 0.5))
    save(fig, "mase_by_horizon_with_ols.png")


def fig_rolling_origins() -> None:
    """Schematic: each row is one forecast origin; training grows, the forecast window moves."""
    fig, ax = plt.subplots(figsize=(9, 3.4))
    rows = [("Dec 2019 (origin 1)", 60), ("Jan 2020 (origin 2)", 61), ("Feb 2020 (origin 3)", 62),
            None, ("Apr 2026 (origin 77)", 136)]
    total = 142
    for i, row in enumerate(rows):
        y = len(rows) - 1 - i
        if row is None:
            ax.text(total / 2, y + 0.4, "...", ha="center", va="center", fontsize=14,
                    color=figures.MUTED)
            continue
        label, train = row
        ax.add_patch(Rectangle((0, y + 0.15), train, 0.5, color=figures.GRID))
        ax.add_patch(Rectangle((train, y + 0.15), 6, 0.5, color=figures.MODEL_COLORS["AutoETS"]))
        ax.text(-2, y + 0.4, label, ha="right", va="center", fontsize=9, color=figures.INK)
    ax.add_patch(Rectangle((0, -0.9), 6, 0.35, color=figures.GRID))
    ax.text(7, -0.72, "Training data: every month up to the origin", va="center", fontsize=9)
    ax.add_patch(Rectangle((62, -0.9), 6, 0.35, color=figures.MODEL_COLORS["AutoETS"]))
    ax.text(69, -0.72, "Forecasts 1 to 6 months ahead, scored against what happened",
            va="center", fontsize=9)
    ticks = {0: "Jan 2015", 60: "Jan 2020", 120: "Jan 2025", 141: "Oct 2026"}
    ax.set_xticks(list(ticks), list(ticks.values()))
    ax.set_yticks([])
    ax.set_xlim(-1, total + 1)
    ax.set_ylim(-1.1, len(rows))
    ax.grid(False)
    ax.spines["left"].set_visible(False)
    ax.set_title("Rolling validation: every model is refitted at 77 origins and forecasts the "
                 "next 6 months")
    save(fig, "rolling_origins.png")


def main() -> None:
    fig_mase_with_ols()
    fig_rolling_origins()
    print("Figures written to", COURSE_FIGURES)


if __name__ == "__main__":
    main()
