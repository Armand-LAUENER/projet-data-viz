"""Download a dated snapshot of Eurostat gov_10a_taxag.

Why a snapshot and not a live API call at app start-up:
  * Eurostat revises figures at any time; a frozen snapshot keeps the demo and
    the grading run showing the same numbers.
  * No network dependency / latency when the app boots.

The snapshot is a tidy *long* table (one row per geo x year x unit x sector x
na_item), written to ``data/gov_10a_taxag_<YYYY-MM-DD>.parquet``. It is only a
few hundred kB once filtered, so it is safe to commit and ship in the zip.

Run with:  python scripts/download_data.py   (or: make data)
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pandas as pd

# Allow "python scripts/download_data.py" from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import constants as C

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Units and sectors we keep. PC_GDP drives every comparison; MIO_EUR backs the
# "who collects" shares; the three subsectors answer that same section.
UNITS = [C.UNIT_PC_GDP, C.UNIT_MIO]
SECTORS = [C.SECTOR_MAIN, *C.SUBSECTORS]


def download() -> pd.DataFrame:
    """Fetch the filtered dataset from Eurostat and reshape it to long form."""
    import eurostat  # imported lazily so the app never needs this dependency

    wide = eurostat.get_data_df(
        C.DATASET_CODE,
        filter_pars={
            "unit": UNITS,
            "sector": SECTORS,
            "na_item": C.NA_ITEMS_USED,
        },
    )
    if wide is None or wide.empty:
        raise RuntimeError("Eurostat returned no data -- check the dataset code / network.")

    # The eurostat package names the geo column 'geo\\TIME_PERIOD'.
    geo_col = next(c for c in wide.columns if c.startswith("geo"))
    id_vars = ["freq", "unit", "sector", "na_item", geo_col]
    year_cols = [c for c in wide.columns if str(c).isdigit()]

    long = wide.melt(
        id_vars=id_vars, value_vars=year_cols,
        var_name="year", value_name="value",
    ).rename(columns={geo_col: "geo"})

    long["year"] = long["year"].astype(int)
    long = long.drop(columns=["freq"])
    # Drop rows with no observation (keeps the file small, missingness is
    # recomputed in the app against the full country x year grid).
    long = long.dropna(subset=["value"]).reset_index(drop=True)
    return long


def main() -> Path:
    DATA_DIR.mkdir(exist_ok=True)
    df = download()
    stamp = date.today().isoformat()
    out = DATA_DIR / f"{C.DATASET_CODE}_{stamp}.parquet"
    df.to_parquet(out, index=False)
    print(f"Wrote {len(df):,} rows to {out}")
    print(f"  years   : {df['year'].min()}–{df['year'].max()}")
    print(f"  geos    : {df['geo'].nunique()}")
    print(f"  na_items: {sorted(df['na_item'].unique())}")
    return out


if __name__ == "__main__":
    main()
