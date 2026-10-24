"""Pure data transformations.

Every function takes the raw long snapshot (as produced by
``scripts/download_data.py``) and returns a tidy, analysis-ready table. No
Streamlit, no I/O, no network -- so the logic that the narrative depends on is
unit-tested in ``tests/test_prep.py``.

Convention: the input ``raw`` has columns
``[unit, sector, na_item, geo, year, value]``.
"""

from __future__ import annotations

import pandas as pd

from utils import constants as C


# --- Building blocks -------------------------------------------------------
def _pc_gdp_main(raw: pd.DataFrame) -> pd.DataFrame:
    """Rows in % of GDP for the fixed analytical sector (S13_S212)."""
    return raw[(raw["unit"] == C.UNIT_PC_GDP) & (raw["sector"] == C.SECTOR_MAIN)]


def country_name(geo: str) -> str:
    return C.COUNTRY_NAMES.get(geo, geo)


# --- Headline tax-to-GDP ratio --------------------------------------------
def tax_ratio(raw: pd.DataFrame) -> pd.DataFrame:
    """Total tax-to-GDP ratio per geo x year, with derived features.

    Columns: geo, year, ratio, country, iso3, is_eu_member, is_provisional,
    eu_ratio, gap_vs_eu, rank (rank within EU27 members, 1 = highest).
    """
    df = _pc_gdp_main(raw)
    df = df[df["na_item"] == C.NA_TOTAL][["geo", "year", "value"]].copy()
    df = df.rename(columns={"value": "ratio"})

    df["country"] = df["geo"].map(country_name)
    df["iso3"] = df["geo"].map(C.EUROSTAT_TO_ISO3)
    df["is_eu_member"] = df["geo"].isin(C.EU27_MEMBERS)
    df["is_provisional"] = df["year"] > C.LAST_COMPLETE_YEAR

    # EU reference line and the gap that measures "the French exception".
    eu = (
        df[df["geo"] == C.EU_AGGREGATE][["year", "ratio"]]
        .rename(columns={"ratio": "eu_ratio"})
    )
    df = df.merge(eu, on="year", how="left")
    df["gap_vs_eu"] = (df["ratio"] - df["eu_ratio"]).round(2)

    # Rank among the 27 member states only (aggregates are not ranked).
    members = df[df["is_eu_member"]].copy()
    members["rank"] = (
        members.groupby("year")["ratio"].rank(ascending=False, method="min").astype(int)
    )
    df = df.merge(members[["geo", "year", "rank"]], on=["geo", "year"], how="left")
    return df.sort_values(["year", "geo"]).reset_index(drop=True)


# --- Category composition --------------------------------------------------
def categories(raw: pd.DataFrame) -> pd.DataFrame:
    """The four tax categories in % of GDP, per geo x year.

    Columns: geo, year, category, value, country, share_of_total.
    """
    df = _pc_gdp_main(raw)
    df = df[df["na_item"].isin(C.CATEGORY_CODES)][["geo", "year", "na_item", "value"]].copy()
    df["category"] = df["na_item"].map(C.CATEGORY_CODES)
    df["country"] = df["geo"].map(country_name)

    total = df.groupby(["geo", "year"])["value"].transform("sum")
    df["share_of_total"] = (df["value"] / total * 100).round(2)
    return df.drop(columns=["na_item"]).reset_index(drop=True)


def metric_map(raw: pd.DataFrame, year: int, category: str | None = None) -> pd.DataFrame:
    """Per-geo value for one year, for the map and ranking.

    ``category=None`` returns the headline total; otherwise the value of that
    one category (one of ``constants.CATEGORY_ORDER``). Columns match
    ``tax_ratio`` where possible: geo, country, iso3, is_eu_member, ratio, rank.
    """
    if category is None:
        return tax_ratio(raw)[tax_ratio(raw)["year"] == year].copy()
    cats = categories(raw)
    df = cats[(cats["year"] == year) & (cats["category"] == category)][["geo", "value"]].copy()
    df = df.rename(columns={"value": "ratio"})
    df["country"] = df["geo"].map(country_name)
    df["iso3"] = df["geo"].map(C.EUROSTAT_TO_ISO3)
    df["is_eu_member"] = df["geo"].isin(C.EU27_MEMBERS)
    members = df[df["is_eu_member"]].copy()
    members["rank"] = members["ratio"].rank(ascending=False, method="min").astype(int)
    df = df.merge(members[["geo", "rank"]], on="geo", how="left")
    return df.reset_index(drop=True)


def gap_by_category(raw: pd.DataFrame, geo: str, year: int) -> pd.DataFrame:
    """Contribution of each category to the ``geo`` vs EU gap in a given year.

    Columns: category, geo_value, eu_value, gap (geo - EU, in pts).
    """
    cats = categories(raw)
    sub = cats[cats["year"] == year]
    g = sub[sub["geo"] == geo].set_index("category")["value"]
    eu = sub[sub["geo"] == C.EU_AGGREGATE].set_index("category")["value"]
    out = pd.DataFrame({"geo_value": g, "eu_value": eu})
    out["gap"] = (out["geo_value"] - out["eu_value"]).round(2)
    return out.reindex(C.CATEGORY_ORDER).reset_index().rename(columns={"index": "category"})


# --- "Who collects": subsector shares -------------------------------------
def subsector_shares(raw: pd.DataFrame, year: int) -> pd.DataFrame:
    """Share of total receipts collected by each government subsector (%).

    Uses MIO_EUR totals so the shares are of money actually collected.
    Columns: geo, country, subsector, value, share.
    """
    df = raw[
        (raw["unit"] == C.UNIT_MIO)
        & (raw["sector"].isin(C.SUBSECTORS))
        & (raw["na_item"] == C.NA_TOTAL)
        & (raw["year"] == year)
    ][["geo", "sector", "value"]].copy()
    df["subsector"] = df["sector"].map(C.SUBSECTORS)
    df["country"] = df["geo"].map(country_name)
    total = df.groupby("geo")["value"].transform("sum")
    df["share"] = (df["value"] / total * 100).round(1)
    return df.reset_index(drop=True)


# --- Data-quality tables ---------------------------------------------------
def completeness_grid(raw: pd.DataFrame) -> pd.DataFrame:
    """Boolean geo x year grid: is the headline total present?

    Returns a wide frame indexed by geo (EU members + non-EU), columns = years,
    values = 1 (present) / 0 (missing). Feeds the completeness heatmap.
    """
    df = _pc_gdp_main(raw)
    df = df[df["na_item"] == C.NA_TOTAL]
    geos = C.EU27_MEMBERS + C.NON_EU
    years = list(range(int(df["year"].min()), int(df["year"].max()) + 1))
    present = df.set_index(["geo", "year"]).index
    grid = pd.DataFrame(0, index=geos, columns=years)
    for geo, year in present:
        if geo in grid.index and year in grid.columns:
            grid.loc[geo, year] = 1
    grid.index = [country_name(g) for g in grid.index]
    return grid


def duplicate_count(raw: pd.DataFrame) -> int:
    """Number of duplicated observations on the natural key (expected 0)."""
    key = ["geo", "year", "na_item", "sector", "unit"]
    return int(raw.duplicated(key).sum())


def sum_coherence(raw: pd.DataFrame) -> pd.DataFrame:
    """Compare the sum of the 4 categories (minus D995) to the reported total.

    Returns per geo x year: cat_sum, reported_total, abs_diff. Used both for a
    quality check in the app and as a regression test.
    """
    df = _pc_gdp_main(raw)
    cat = (
        df[df["na_item"].isin(C.CATEGORY_CODES)]
        .groupby(["geo", "year"])["value"].sum()
        .rename("cat_sum")
    )
    unc = (
        df[df["na_item"] == C.NA_UNCOLLECTABLE]
        .set_index(["geo", "year"])["value"].rename("uncollectable")
    )
    tot = (
        df[df["na_item"] == C.NA_TOTAL]
        .set_index(["geo", "year"])["value"].rename("reported_total")
    )
    out = pd.concat([cat, unc, tot], axis=1)
    out["uncollectable"] = out["uncollectable"].fillna(0.0)
    out["cat_sum"] = (out["cat_sum"] - out["uncollectable"]).round(3)
    out["abs_diff"] = (out["cat_sum"] - out["reported_total"]).abs().round(3)
    return out.dropna(subset=["reported_total"]).reset_index()


def abrupt_changes(raw: pd.DataFrame, threshold: float = 3.0) -> pd.DataFrame:
    """Year-on-year ratio jumps larger than ``threshold`` points (outliers)."""
    df = tax_ratio(raw)
    df = df[df["is_eu_member"] | (df["geo"] == C.EU_AGGREGATE)].copy()
    df = df.sort_values(["geo", "year"])
    df["delta"] = df.groupby("geo")["ratio"].diff().round(2)
    out = df[df["delta"].abs() >= threshold][["country", "year", "ratio", "delta"]]
    return out.sort_values("delta", key=lambda s: s.abs(), ascending=False).reset_index(drop=True)
