"""Targeted tests on the transformations the narrative depends on.

Not an exhaustive suite: four checks that, if they broke, would silently
mislead the story (§8.4 of the project plan).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from utils import constants as C
from utils import prep

DATA = sorted((Path(__file__).resolve().parent.parent / "data").glob(
    f"{C.DATASET_CODE}_*.parquet"))


@pytest.fixture(scope="module")
def raw() -> pd.DataFrame:
    if not DATA:
        pytest.skip("No snapshot in data/ — run `make data` first.")
    return pd.read_parquet(DATA[-1])


def test_no_duplicates(raw):
    """The natural key must be unique."""
    assert prep.duplicate_count(raw) == 0


def test_category_sum_matches_total(raw):
    """Σ(4 categories) − D995 must equal the reported total within rounding."""
    coh = prep.sum_coherence(raw)
    # Observations are published to 0.1 pt; allow a small rounding tolerance.
    assert coh["abs_diff"].max() <= 0.3


def test_reproduces_official_eu_and_fr(raw):
    """The chosen sector must reproduce the published headline figures."""
    tr = prep.tax_ratio(raw)

    def ratio(geo, year):
        return float(tr.loc[(tr["geo"] == geo) & (tr["year"] == year), "ratio"].iloc[0])

    assert ratio("FR", 2024) == pytest.approx(45.3, abs=0.1)   # INSEE/Eurostat
    assert ratio("EU27_2020", 2023) == pytest.approx(39.9, abs=0.1)  # Eurostat
    # 2024 France sits at rank 2 behind Denmark (official top-3: DK, FR, BE).
    top3 = set(tr[(tr["year"] == 2024) & (tr["is_eu_member"])]
               .nsmallest(3, "rank")["geo"])
    assert top3 == {"DK", "FR", "BE"}


def test_iso3_mapping_covers_all_shown_countries(raw):
    """Every displayed geo (incl. EL→GRC) must have an ISO-3 code for the map."""
    shown = set(C.EU27_MEMBERS) | set(C.NON_EU)
    missing = shown - set(C.EUROSTAT_TO_ISO3)
    assert not missing, f"Missing ISO-3 mapping for: {missing}"
    assert C.EUROSTAT_TO_ISO3["EL"] == "GRC"


def test_gap_decomposition_reconciles(raw):
    """Category gaps must sum to the total FR−EU gap within tolerance."""
    tbl = prep.gap_by_category(raw, "FR", 2024)
    tr = prep.tax_ratio(raw)
    total_gap = float(tr.loc[(tr["geo"] == "FR") & (tr["year"] == 2024), "gap_vs_eu"].iloc[0])
    assert tbl["gap"].sum() == pytest.approx(total_gap, abs=0.4)
