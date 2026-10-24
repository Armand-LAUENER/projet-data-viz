"""Section 3 — Who? (mode dumbbell + age pyramid)."""

from __future__ import annotations

import streamlit as st

from utils import constants as C
from utils import io, viz


def render(f) -> None:
    st.header("3 · Who?")
    lo, hi = f.years
    mode = io.load_table("by_mode")
    m = mode[(mode["year"].between(lo, hi)) & (mode["mode"].isin(f.modes))]

    # Insight: powered two-wheelers over-represented; e-scooters the opposite.
    g = m.groupby("mode", observed=True).agg(
        victims=("victims", "sum"), killed=("killed", "sum")).reset_index()
    tv, tk = g["victims"].sum(), g["killed"].sum()
    g["gap"] = (g["killed"] / tk - g["victims"] / tv) * 100 if tv and tk else 0
    p2w = g.loc[g["mode"] == "Powered two-wheeler", "killed"]
    p2w_share = float(p2w.iloc[0]) / tk * 100 if len(p2w) and tk else 0
    st.subheader(
        f"Powered two-wheelers are **{p2w_share:.0f}% of deaths** — far above their "
        "share of road traffic; e-scooters are the mirror image (many injuries, few deaths)."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(viz.dumbbell_mode(m), width="stretch", theme="streamlit")
        st.caption(
            "For each mode, share of all victims (blue) vs. share of all deaths (red). "
            "A red dot to the right of the blue one means that mode dies more than it is "
            "injured. No exposure data: this is not a per-km risk."
        )
    with col2:
        agesex = io.load_table("by_age_sex")
        st.plotly_chart(viz.age_pyramid(agesex[agesex["year"].between(lo, hi)]),
                        width="stretch", theme="streamlit")
        st.caption(
            "People killed by age band and sex. Two peaks stand out: the 18–24 (young "
            f"drivers) and the 75+ (often pedestrians). Cells with fewer than "
            f"{C.CONFIDENTIALITY_MIN} deaths are suppressed for privacy."
        )
    st.divider()
