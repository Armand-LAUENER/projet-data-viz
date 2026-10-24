"""Section 0 — Intro: the hook and the definitions."""

from __future__ import annotations

import streamlit as st

from utils import constants as C
from utils import io


def render(f) -> None:
    dep = io.load_table("by_dep")
    killed_last = int(dep[dep["year"] == C.LAST_YEAR]["killed"].sum())
    per_day = killed_last / 365

    st.header("The hook")
    st.subheader(
        f"In {C.LAST_YEAR}, **{killed_last:,} people** were killed on the roads of "
        f"metropolitan France — about **{per_day:.0f} every day**.".replace(",", " ")
    )
    st.markdown(
        "But a death is not a random event. It clusters in **specific hours, places "
        "and road-user profiles**. The thread of this page: **where accidents are most "
        "frequent is not where they are most deadly.**"
    )

    with st.expander("Definitions — how to read these numbers", expanded=False):
        st.markdown(
            """
- **Data**: *BAAC* — a form filled by the police for every injury accident, published
  by the **ONISR** on data.gouv.fr. Four tables (accidents, locations, vehicles, road
  users) joined on the accident id.
- **Killed**: a person who died on the spot or **within 30 days** of the accident.
  This is the reliable indicator; hospitalised-injury counts broke in 2018 and are not
  used for trends (see the data-quality section).
- **Gravity index** = *people killed per 100 injury accidents*. It lets us compare
  hours, places and modes **without any external denominator** (no population, no km).
- **Scope**: metropolitan France, 2019–2024 (the homogeneous data format). Overseas
  territories are excluded for comparability with ONISR headline figures.

> What this page can't say: it has **no exposure** (km travelled per mode), so it never
> ranks modes by risk per trip — only compares shares and severity.
            """
        )
    st.divider()
