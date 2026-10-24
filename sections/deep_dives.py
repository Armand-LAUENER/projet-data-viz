"""Sections 2-4 — How did we get here, what is the gap made of, who collects."""

from __future__ import annotations

import streamlit as st

from utils import constants as C
from utils import prep, viz


def _trend(raw, f) -> None:
    st.header("2 · How did we get here?")
    tr = prep.tax_ratio(raw)
    focal_name = C.COUNTRY_NAMES[f.focal]

    gap = tr[(tr["geo"] == f.focal)].dropna(subset=["gap_vs_eu"])
    lo, hi = f.year_range
    g_start = gap.loc[gap["year"] == lo, "gap_vs_eu"]
    g_end = gap.loc[gap["year"] == hi, "gap_vs_eu"]
    if len(g_start) and len(g_end):
        delta = g_end.iloc[0] - g_start.iloc[0]
        verb = ("widened" if delta > 0.3 else "narrowed" if delta < -0.3 else "stayed broadly stable")
        st.subheader(
            f"Between {lo} and {hi}, the {focal_name}–EU27 gap {verb} "
            f"(from {g_start.iloc[0]:+.1f} to {g_end.iloc[0]:+.1f} pts)."
        )

    st.plotly_chart(viz.lines_multi(tr, f.compare, f.year_range),
                    width='stretch', theme="streamlit")
    st.caption(
        "Tax-to-GDP trajectories for the selected countries and the EU27 reference "
        "(dashed). Shaded bands mark the 2008–09 and 2020 crises — ratios can rise "
        "simply because GDP (the denominator) falls, without any tax increase."
    )
    st.plotly_chart(viz.gap_line(tr, f.focal, f.year_range),
                    width='stretch', theme="streamlit")
    st.caption(
        f"The {focal_name} gap versus the EU27 average over time; zero line = EU average, "
        "most extreme years annotated."
    )
    st.divider()


def _composition(raw, f) -> None:
    st.header("3 · What is the gap made of?")
    cats = prep.categories(raw)
    focal_name = C.COUNTRY_NAMES[f.focal]

    gap_tbl = prep.gap_by_category(raw, f.focal, f.ref_year)
    if not gap_tbl["gap"].isna().all():
        pos = gap_tbl[gap_tbl["gap"] > 0].sort_values("gap", ascending=False)
        drivers = " and ".join(pos["category"].head(2).str.lower().tolist())
        st.subheader(
            f"Most of the {focal_name} gap comes from **{drivers}** — "
            f"not from income & wealth taxes, which are close to or below the EU average."
        )
        st.dataframe(
            gap_tbl.rename(columns={
                "category": "Category", "geo_value": f"{focal_name} (% GDP)",
                "eu_value": "EU27 (% GDP)", "gap": "Gap (pts)"}),
            hide_index=True, width='stretch',
        )

    st.plotly_chart(viz.stacked_categories(cats, f.compare, f.ref_year),
                    width='stretch', theme="streamlit")
    st.caption(
        f"Each country's {f.ref_year} ratio split into four categories (% of GDP); "
        "plain-language labels, not SEC 2010 codes."
    )
    st.plotly_chart(viz.small_multiples(cats, f.compare, f.year_range),
                    width='stretch', theme="streamlit")
    st.caption("Each category's trajectory over time, one panel per category, shared Y scale.")
    st.divider()


def _who_collects(raw, f) -> None:
    st.header("4 · Who collects the money? *(bonus)*")
    shares = prep.subsector_shares(raw, f.ref_year)
    focal_name = C.COUNTRY_NAMES[f.focal]
    ssf = shares[(shares["geo"] == f.focal) & (shares["subsector"] == "Social security funds")]
    if len(ssf):
        st.subheader(
            f"In {focal_name}, **social security funds collect {ssf['share'].iloc[0]:.0f}%** "
            f"of all receipts in {f.ref_year}."
        )
    st.plotly_chart(viz.subsector_bars(shares, f.compare, f.ref_year),
                    width='stretch', theme="streamlit")
    st.caption(
        "Share of total receipts collected by central government, local government and "
        "social security funds, per country (based on amounts in € million)."
    )
    st.divider()


def render(raw, f) -> None:
    _trend(raw, f)
    _composition(raw, f)
    _who_collects(raw, f)
