"""Targeted tests on what would silently break the story (plan §8.5).

Raw-based tests skip when data/raw is absent (not committed); processed-based
tests always run against the committed aggregates.
"""

from __future__ import annotations

import pandas as pd
import pytest

from utils import constants as C
from utils import prep

RAW_AVAILABLE = (C.RAW_DIR / f"caracteristiques_{C.LAST_YEAR}.csv").exists()
PROC_AVAILABLE = (C.PROCESSED_DIR / "by_dep.parquet").exists()
raw_only = pytest.mark.skipif(not RAW_AVAILABLE, reason="data/raw missing (run `make data`)")
proc_only = pytest.mark.skipif(not PROC_AVAILABLE, reason="data/processed missing (run `make tables`)")


# --- Raw pipeline ----------------------------------------------------------
@raw_only
def test_accident_key_unique():
    """Num_Acc must be unique per year in caracteristiques (key harmonised)."""
    for year in C.YEARS:
        car = prep.read_raw(year, "caracteristiques")
        assert "Num_Acc" in car.columns, f"{year}: accident key not harmonised"
        assert car["Num_Acc"].duplicated().sum() == 0, f"{year}: duplicate accident ids"


@raw_only
def test_user_vehicle_join_does_not_duplicate():
    """Building the usager level must not inflate the number of road users."""
    year = C.LAST_YEAR
    n_users = len(prep.read_raw(year, "usagers"))
    assert len(prep.build_usager_level(year)) == n_users


@raw_only
def test_reproduces_onisr_killed_2024():
    """Metropolitan deaths in 2024 must match the official ONISR figure (3193)."""
    usr = prep.build_usager_level(2024)
    assert prep.killed_count(usr, metro_only=True) == pytest.approx(3193, abs=5)
    assert prep.killed_count(usr, metro_only=False) == pytest.approx(3432, abs=5)


@raw_only
def test_labels_cover_observed_codes():
    """grav / agg / lum codes present in the data must all have a label."""
    car = prep.read_raw(2024, "caracteristiques")
    usa = prep.read_raw(2024, "usagers")
    for series, labels in [
        (pd.to_numeric(usa["grav"], errors="coerce"), C.GRAV_LABELS),
        (pd.to_numeric(car["agg"], errors="coerce"), C.AGG_LABELS),
        (pd.to_numeric(car["lum"], errors="coerce"), C.LUM_LABELS),
    ]:
        codes = set(series.dropna().astype(int)) - {-1}
        assert codes <= set(labels), f"unlabelled codes: {codes - set(labels)}"


# --- Processed aggregates --------------------------------------------------
@proc_only
def test_dep_totals_match_national():
    """Summing the per-department table must reproduce the national death count."""
    dep = pd.read_parquet(C.PROCESSED_DIR / "by_dep.parquet")
    assert int(dep[dep["year"] == 2024]["killed"].sum()) == pytest.approx(3193, abs=5)


@proc_only
def test_modes_are_all_labelled():
    """Every mode in the aggregated table is a known plain-language label."""
    mode = pd.read_parquet(C.PROCESSED_DIR / "by_mode.parquet")
    assert set(mode["mode"]) <= set(C.MODE_ORDER)


@proc_only
def test_gravity_index_is_sane():
    """Gravity index (killed per 100 accidents) stays within a plausible range."""
    dep = pd.read_parquet(C.PROCESSED_DIR / "by_dep.parquet")
    gi = dep["gravity_index"].dropna()
    assert gi.between(0, 50).all()
