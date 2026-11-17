"""Consistency check between the incident file and the SPVM's official monthly statistics.

The PoC used the Bilan mensuel sur la criminalite (official monthly statistics, January 2023
onward). The final analysis uses Actes criminels (incident records, January 2015 onward),
which the portal describes as not being the SPVM's official statistics. This script compares
the four categories that exist in both files over the months they share. Both come from the
same police records system, so agreement is a consistency check, not independent validation.

Both keep only the most serious offence per event. The Bilan counts crimes against the person
(robbery is one) by victim; whether that explains the robbery gap is not established.

Usage:
    python src/course_bilan_check.py              # use the committed Bilan aggregate
    python src/course_bilan_check.py --download   # refresh it from the open data API first
"""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

import pandas as pd

from course_data import COURSE_RESULTS, ROOT, SNAPSHOT

BILAN_DIR = ROOT / "data" / "bilan"
BILAN_FILE = BILAN_DIR / "bilan_citywide_by_subgroup.csv"
BILAN_META = BILAN_DIR / "bilan_citywide_by_subgroup.json"
RESOURCE = "9ae09144-f418-4d08-ba54-c5d65e5bd6bb"
API = "https://donnees.montreal.ca/api/3/action/datastore_search"

# Bilan subgroup -> Actes criminels category
MATCHED = {
    "02-02 Introduction par effraction": "Introduction",
    "02-03 Vol de véhicules à moteur": "Vol de véhicule à moteur",
    "02-07 Méfaits": "Méfait",
    "01-06 Vols qualifiés": "Vols qualifiés",
}
LABELS = {"Introduction": "Break and enter", "Vol de véhicule à moteur": "Vehicle theft",
          "Méfait": "Mischief", "Vols qualifiés": "Robbery"}


def download() -> None:
    records, offset = [], 0
    while True:
        query = urllib.parse.urlencode({"resource_id": RESOURCE, "limit": 32000,
                                        "offset": offset})
        result = json.load(urllib.request.urlopen(f"{API}?{query}", timeout=180))["result"]
        records += result["records"]
        offset += len(result["records"])
        if not result["records"] or offset >= result["total"]:
            break
    raw = pd.DataFrame(records)
    raw["month"] = (raw["ANNEE"].astype(int).astype(str) + "-"
                    + raw["MOIS"].astype(int).map("{:02d}".format))
    raw["TOTAL"] = pd.to_numeric(raw["TOTAL"])
    agg = (raw.groupby(["month", "GROUPE", "SOUS-GROUPE"])["TOTAL"].sum()
           .rename("count").reset_index().rename(columns={"GROUPE": "group",
                                                          "SOUS-GROUPE": "subgroup"}))
    BILAN_DIR.mkdir(parents=True, exist_ok=True)
    agg.to_csv(BILAN_FILE, index=False)
    meta = {"source": "https://donnees.montreal.ca/dataset/bilan-mensuel-criminalite",
            "resource_id": RESOURCE,
            "downloaded_utc": f"{datetime.now(timezone.utc):%Y-%m-%dT%H:%M:%SZ}",
            "source_rows": len(raw), "first_month": agg["month"].min(),
            "last_month": agg["month"].max(), "total_count": int(agg["count"].sum()),
            "note": "Citywide monthly totals by subgroup (summed over PDQ). License CC BY 4.0."}
    BILAN_META.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Bilan: {len(raw):,} rows, {meta['first_month']} to {meta['last_month']}")


def compare() -> pd.DataFrame:
    bilan = pd.read_csv(BILAN_FILE)
    bilan = bilan[bilan["subgroup"].isin(MATCHED)]
    bilan = bilan.assign(category=bilan["subgroup"].map(MATCHED)).groupby(
        ["month", "category"])["count"].sum().rename("bilan")
    actes = pd.read_csv(SNAPSHOT).groupby(["month", "category"])["count"].sum().rename("actes")
    both = pd.concat([bilan, actes], axis=1, join="inner").reset_index()
    last_full = pd.read_csv(SNAPSHOT)["month"].max()  # partial month in the snapshot
    both = both[both["month"] < last_full]
    rows = []
    for cat, g in both.groupby("category"):
        rows.append({"category": LABELS[cat], "months": len(g),
                     "first_month": g["month"].min(), "last_month": g["month"].max(),
                     "bilan_total": int(g["bilan"].sum()), "actes_total": int(g["actes"].sum()),
                     "ratio_actes_to_bilan": round(g["actes"].sum() / g["bilan"].sum(), 3),
                     "monthly_correlation": round(g["actes"].corr(g["bilan"]), 3),
                     "largest_monthly_gap_pct": round(
                         ((g["actes"] - g["bilan"]).abs() / g["bilan"]).max() * 100, 1)})
    return pd.DataFrame(rows)


def main() -> None:
    if "--download" in sys.argv or not BILAN_FILE.exists():
        download()
    out = compare()
    COURSE_RESULTS.mkdir(parents=True, exist_ok=True)
    out.to_csv(COURSE_RESULTS / "bilan_consistency.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
