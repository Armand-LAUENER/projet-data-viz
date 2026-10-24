"""Section 5 — Can we trust these numbers? (quality, validation, ethics)."""

from __future__ import annotations

import streamlit as st

from utils import constants as C
from utils import io, viz


def render(f) -> None:
    st.header("5 · Can we trust these numbers?")
    qr = io.load_table("quality_report").set_index("metric")["value"]
    geo = io.load_table("geo_quality")
    geo_last = geo[geo["year"] == C.LAST_YEAR]["geoloc_pct"]
    geo_pct = float(geo_last.iloc[0]) if len(geo_last) else float("nan")

    st.subheader(
        "The pipeline reproduces the official ONISR figures exactly — and the known "
        "fragilities are shown openly, not hidden."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Duplicate accident ids", int(qr.get("Duplicate accident ids", 0)))
    c2.metric("Orphan users", int(qr.get("Orphan users (no accident)", 0)))
    c3.metric(f"Killed metro {C.LAST_YEAR}", int(qr.get("Killed, metro 2024", 0)),
              help="ONISR reference: 3193.")
    c4.metric(f"Geolocated {C.LAST_YEAR}", f"{geo_pct:.0f}%",
              help="Share of accidents with coordinates; point maps would be partial.")

    st.markdown("#### Validation against the official ONISR 2024 figures")
    rows = [
        {"Figure": "Killed, metropolitan France", "This app": int(qr.get("Killed, metro 2024", 0)),
         "ONISR": 3193},
        {"Figure": "Male share of the killed (%)",
         "This app": qr.get("Male share of killed 2024 (%)", 0), "ONISR": 77},
    ]
    st.dataframe(rows, hide_index=True, width="stretch")

    st.plotly_chart(viz.missingness_heatmap(io.load_table("missingness")),
                    width="stretch", theme="streamlit")
    st.caption(
        "Share of missing values in key fields. Age and sex missingness rises from "
        "2021, when hit-and-run offenders were added to the data with little info on "
        "them — an honest artefact, flagged here."
    )

    with st.expander("Known breaks & caveats"):
        st.markdown(
            """
- **Hospitalised injuries broke in 2018** and are no longer officially labelled; we
  work on **deaths** (the reliable 30-day indicator), never on injury trends across 2018.
- **Hit-and-run offenders added in 2021** → more missing age/sex from 2021 on.
- **2020 COVID lockdowns** cut traffic and accidents — any comparison with 2020 must be
  read with that in mind.
- **Not all accidents are precisely geolocated** → department totals are used, not point
  maps. **The accident key is named `Accident_Id` in 2022** and `Num_Acc` elsewhere —
  harmonised on read. **Lieux has several rows per accident in some years** — de-duplicated.
- **Injury counts are not reproducible**: ONISR corrects them with a separate method; we
  do not try to match them.
            """
        )

    st.markdown("#### Ethics & privacy")
    st.markdown(
        f"""
This dataset describes **people**, including those who died. Our safeguards:
- **Only aggregates are deployed** — no individual record ever leaves the pipeline.
- **No point map of fatal accidents** with date/age/sex (that combination could identify
  a victim in a small town).
- **Suppression threshold**: crossed cells with fewer than **{C.CONFIDENTIALITY_MIN}**
  deaths are masked (age × sex).
- **Sober tone**, and a reminder that the mix of victims also reflects exposure, which is
  unknown here.
        """
    )
    st.divider()
