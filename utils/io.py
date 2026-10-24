"""Load the pre-aggregated tables and the basemap. The app never hits the network.

Caching lives here (``st.cache_data``); the transformations in ``aggregate.py``
and ``prep.py`` stay pure so they can be tested without a Streamlit runtime.
"""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from utils import constants as C


@st.cache_data(show_spinner=False)
def load_table(name: str) -> pd.DataFrame:
    """Load one processed Parquet table (e.g. 'by_dep')."""
    path = C.PROCESSED_DIR / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} missing. Run `make data && make tables` first."
        )
    return pd.read_parquet(path)


@st.cache_data(show_spinner=False)
def load_geojson() -> dict:
    """Metropolitan departments basemap (properties.code == BAAC dep)."""
    return json.loads(C.GEOJSON.read_text())


@st.cache_data(show_spinner=False)
def snapshot_date() -> str:
    """Download date recorded in the raw MANIFEST, if present."""
    manifest = C.RAW_DIR / "MANIFEST.json"
    if manifest.exists():
        try:
            return json.loads(manifest.read_text()).get("_downloaded", "n/a")
        except json.JSONDecodeError:
            pass
    return "n/a"
