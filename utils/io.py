"""Load the local snapshot. The app never touches the network.

Caching lives here (``st.cache_data``); the transformations in ``prep.py`` stay
pure pandas so they can be unit-tested without a Streamlit runtime.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from utils import constants as C

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_SNAPSHOT_RE = re.compile(rf"{C.DATASET_CODE}_(\d{{4}}-\d{{2}}-\d{{2}})\.parquet$")


def latest_snapshot() -> Path:
    """Return the most recent dated snapshot in ``data/``."""
    candidates = sorted(DATA_DIR.glob(f"{C.DATASET_CODE}_*.parquet"))
    if not candidates:
        raise FileNotFoundError(
            "No snapshot found in data/. Run `make data` (or "
            "`python scripts/download_data.py`) first."
        )
    return candidates[-1]


def snapshot_date(path: Path | None = None) -> date:
    """Parse the snapshot date from the file name."""
    path = path or latest_snapshot()
    m = _SNAPSHOT_RE.search(path.name)
    return date.fromisoformat(m.group(1)) if m else date.fromtimestamp(path.stat().st_mtime)


@st.cache_data(show_spinner=False)
def load_raw() -> pd.DataFrame:
    """Load the raw long snapshot (geo, unit, sector, na_item, year, value)."""
    return pd.read_parquet(latest_snapshot())
