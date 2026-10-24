"""Section 2 — Where? (choropleth + built-up vs outside bars). The inversion."""

from __future__ import annotations

import streamlit as st

from utils import io, viz


def render(f) -> None:
    st.header("2 · Where?")
    lo, hi = f.years
    dep = io.load_table("by_dep")
    d = dep[(dep["year"].between(lo, hi)) & (dep["region"].isin(f.regions))]

    # Insight: the map inverts (frequency vs severity are negatively correlated).
    by_dep = d.groupby("dep", observed=True).agg(
        accidents=("accidents", "sum"), killed=("killed", "sum")).reset_index()
    by_dep["gi"] = by_dep["killed"] / by_dep["accidents"].replace(0, 1) * 100
    corr = by_dep["accidents"].corr(by_dep["gi"])
    st.subheader(
        "The map inverts: the departments with the **most** accidents are the "
        f"**least** deadly per accident (correlation {corr:+.2f})."
    )

    col1, col2 = st.columns([3, 2])
    with col1:
        st.plotly_chart(viz.choropleth_dep(d, io.load_geojson(), f.metric),
                        width="stretch", theme="streamlit")
        st.caption(
            f"{f.metric} by department (2019–2024 selection). Toggle the metric: dense "
            "urban departments dominate 'Accidents', sparse rural ones dominate "
            "'Gravity index'. Not all accidents are precisely geolocated; department "
            "totals are reliable, point maps would not be."
        )
    with col2:
        kpi = io.load_table("kpi")
        k = kpi[(kpi["year"].between(lo, hi)) & (kpi["metro"])]
        st.plotly_chart(viz.agg_share_bars(k), width="stretch", theme="streamlit")
        st.caption(
            "Share of accidents vs. share of deaths, built-up area vs. outside. Most "
            "accidents happen in town; most deaths happen outside it — the core "
            "frequency-vs-severity contrast."
        )
    st.divider()
