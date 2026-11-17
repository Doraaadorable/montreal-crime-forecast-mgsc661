"""Run the MGSC 661 course analyses. About 4 minutes on 4 cores; no download needed.

They read the frozen snapshot (data/snapshots/2026-11-15.csv.gz) and the committed
backtest results, so they give the same numbers on any machine with requirements.txt.

Usage:
    python src/course_run_all.py
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

SRC = Path(__file__).resolve().parent
STEPS = [
    "course_ols.py",          # PoC regression in the 77-origin backtest, OLS diagnostics
    "course_structure.py",    # ETS / ARIMA structures at every origin, residual checks
    "course_bilan_check.py",  # consistency with official monthly statistics
]

if __name__ == "__main__":
    for step in STEPS:
        start = time.time()
        print(f"== {step}", flush=True)
        subprocess.run([sys.executable, str(SRC / step)], check=True)
        print(f"   done in {time.time() - start:.0f}s", flush=True)
