"""Section 1 — Where does each country stand? (map + ranking)."""

from __future__ import annotations

import streamlit as st

from utils import constants as C
from utils import prep, viz


def render(raw, f) -> None:
    st.header("1 · Where does each country stand?")

    metric = prep.metric_map(raw, f.ref_year, f.category)
    if not f.include_non_eu:
        metric = metric[~metric["geo"].isin(C.NON_EU)]

    focal_row = metric.loc[metric["geo"] == f.focal]
    rank = int(focal_row["rank"].iloc[0]) if len(focal_row) and focal_row["rank"].notna().any() else None
    label = f.category or "total tax-to-GDP"
    focal_name = C.COUNTRY_NAMES[f.focal]
    if rank:
        ordinal = {1: "the highest", 2: "the 2nd highest", 3: "the 3rd highest"}.get(
            rank, f"the {rank}th highest")
        st.subheader(f"On {label}, {focal_name} has {ordinal} ratio in the EU27 "
                     f"({f.ref_year}).")

    col_map, col_rank = st.columns([1, 1])
    with col_map:
        st.plotly_chart(viz.choropleth(metric, f.ref_year), width='stretch',
                        theme="streamlit")
        st.caption(
            f"Choropleth of {label} across Europe in {f.ref_year}; darker = higher. "
            "Greece uses Eurostat code EL (ISO GRC)."
        )
    with col_rank:
        st.plotly_chart(viz.ranking_bars(metric, f.focal, f.ref_year),
                        width='stretch', theme="streamlit")
        st.caption(
            f"Countries ranked by {label} in {f.ref_year}; {focal_name} highlighted, "
            "dashed line = EU27 average."
        )
    st.divider()
