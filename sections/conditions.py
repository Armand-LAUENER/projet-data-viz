"""Section 4 — In what conditions? (small multiples, bonus)."""

from __future__ import annotations

import streamlit as st

from utils import io, viz


def render(f) -> None:
    st.header("4 · In what conditions? *(bonus)*")
    cond = io.load_table("by_condition")
    st.subheader(
        "Night, open roads and higher speed limits all raise the share of accidents "
        "that kill."
    )
    st.plotly_chart(viz.conditions_facets(cond), width="stretch", theme="streamlit")
    st.caption(
        "Gravity index (killed per 100 accidents) by lighting, weather, road type and "
        "speed limit, over 2019–2024. Read it as co-occurrence, not causation: these "
        "conditions go together (open roads are faster, darker and less supervised)."
    )
    st.divider()
