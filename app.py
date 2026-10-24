"""When, where and for whom does a road accident turn deadly? — a data story.

Single-page, linear narrative (Hook -> Context -> Insights -> Implications) on the
French BAAC road-accident data. The spine is the contrast between *frequency* and
*severity*: where accidents happen is not where people die.

Run:  streamlit run app.py   (or: make run)
"""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from sections import conclusions, conditions, intro, quality, when, where, who
from utils import constants as C
from utils import io

st.set_page_config(page_title="When the road turns deadly",
                   page_icon="🚦", layout="wide", initial_sidebar_state="expanded")


@dataclass
class Filters:
    years: tuple[int, int]
    metric: str
    regions: list[str]
    modes: list[str]


def build_sidebar() -> Filters:
    st.sidebar.title("Controls")
    st.sidebar.caption("Every control changes something in the story.")

    years = st.sidebar.slider("Years", C.YEARS[0], C.YEARS[-1], (C.YEARS[0], C.LAST_YEAR),
                              help="Filters every chart and KPI.")
    metric = st.sidebar.radio(
        "Map & heatmap metric", ["Accidents", "Killed", "Gravity index"],
        index=2, help="Switch between how many and how deadly — this is the whole point.")
    regions = st.sidebar.multiselect("Regions (map & KPIs)", C.REGIONS, default=C.REGIONS,
                                     help="Metropolitan regions shown on the map.")
    modes = st.sidebar.multiselect("Modes (who section)", C.MODE_ORDER, default=C.MODE_ORDER,
                                   help="Road-user types in the mode comparison.")

    st.sidebar.divider()
    st.sidebar.caption(f"Snapshot: {io.snapshot_date()} · {C.PRODUCER} / BAAC · {C.LICENCE}")
    return Filters(years, metric, regions or C.REGIONS, modes or C.MODE_ORDER)


def kpi_header(f: Filters) -> None:
    dep = io.load_table("by_dep")
    kpi = io.load_table("kpi")
    lo, hi = f.years
    d = dep[(dep["year"].between(lo, hi)) & (dep["region"].isin(f.regions))]
    k = kpi[(kpi["year"].between(lo, hi)) & (kpi["metro"])]

    accidents = int(d["accidents"].sum())
    killed = int(d["killed"].sum())
    gravity = killed / accidents * 100 if accidents else 0
    out = k[k["agg_label"] == "Outside built-up area"]["killed"].sum()
    out_share = out / k["killed"].sum() * 100 if k["killed"].sum() else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Accidents", f"{accidents:,}".replace(",", " "))
    c2.metric("People killed", f"{killed:,}".replace(",", " "))
    c3.metric("Gravity index", f"{gravity:.1f}", help="Killed per 100 accidents.")
    c4.metric("Deaths outside built-up areas", f"{out_share:.0f}%",
              help="Metropolitan France, selected years (not region-filtered).")


def main() -> None:
    f = build_sidebar()
    st.title("When does a road accident turn deadly?")
    st.markdown(
        "**For a general audience — especially young drivers and vulnerable road "
        "users.** This page is **descriptive**: it compares *where* and *when* "
        "accidents happen with *where and when people die*. It makes **no causal "
        "claim**, and because the data hold no exposure (km travelled), it never "
        "says one mode is “more dangerous” per trip."
    )
    kpi_header(f)
    st.divider()

    intro.render(f)
    when.render(f)
    where.render(f)
    who.render(f)
    conditions.render(f)
    quality.render(f)
    conclusions.render(f)


if __name__ == "__main__":
    main()
