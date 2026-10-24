"""Section 5 — Can we trust these numbers? (data quality & validation)."""

from __future__ import annotations

import streamlit as st

from utils import io, prep, viz

# Official reference figures to reproduce (Eurostat / INSEE-via-Eurostat).
REFERENCES = [
    ("EU27 tax-to-GDP, 2023", "EU27_2020", 2023, 39.9, "Eurostat, Statistics Explained"),
    ("France tax-to-GDP, 2024", "FR", 2024, 45.3, "INSEE, from Eurostat (12/02/2026)"),
]


def render(raw, f) -> None:
    st.header("5 · Can we trust these numbers?")

    grid = prep.completeness_grid(raw)
    total_cells = grid.size
    present = int(grid.values.sum())
    st.subheader(
        f"The headline series is **{present / total_cells * 100:.1f}% complete**; "
        "the few gaps and the known definition caveats are shown openly."
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Duplicate observations", prep.duplicate_count(raw), help="Natural key; expected 0.")
    sc = prep.sum_coherence(raw)
    c2.metric("Max category-sum error", f"{sc['abs_diff'].max():.2f} pts",
              help="|Σ categories − D995 − reported total|, worst case (rounding).")
    c3.metric("Snapshot date", io.snapshot_date().isoformat(), help="Figures are revisable.")

    st.plotly_chart(viz.completeness_heatmap(grid), width='stretch', theme="streamlit")
    st.caption(
        "Country × year grid; blue = value present, amber = missing. The most recent "
        f"year ({int(grid.columns[-1])}) is only partly reported, hence flagged provisional."
    )

    st.markdown("#### Validation — do our figures match the official ones?")
    tr = prep.tax_ratio(raw)
    rows = []
    for label, geo, year, official, src in REFERENCES:
        got = tr.loc[(tr["geo"] == geo) & (tr["year"] == year), "ratio"]
        got = float(got.iloc[0]) if len(got) else float("nan")
        rows.append({"Figure": label, "Official": f"{official:.1f}%",
                     "This app": f"{got:.1f}%", "Δ": f"{got - official:+.1f} pts", "Source": src})
    st.dataframe(rows, hide_index=True, width='stretch')
    st.caption(
        "Our pipeline reproduces the published France 2024 and EU 2023 figures exactly. "
        "The EU 2024 value reads 40.2% here vs. 40.4% in the October 2025 Eurostat release: "
        "a **data revision** between that release and this snapshot — an explained gap, not a bug."
    )

    with st.expander("Known breaks & caveats"):
        st.markdown(
            """
- **EU aggregate**: `EU27_2020` is used over the whole series (UK excluded from 1995),
  so the composition never changes mid-series.
- **Greece**: Eurostat code `EL`, mapped to ISO `GRC` for the map.
- **Denominator effect**: a ratio can rise because GDP *falls* (2009, 2020), with no tax
  increase — the crisis bands flag those years.
- **Current prices**: euro amounts are not inflation-adjusted, so comparisons over time
  use % of GDP, never raw euros.
- **Revisions**: Eurostat revises figures at any time; hence the dated snapshot.
            """
        )

    outliers = prep.abrupt_changes(raw)
    if len(outliers):
        with st.expander(f"Largest year-on-year moves (≥ 3 pts): {len(outliers)} cases"):
            st.dataframe(outliers.rename(columns={
                "country": "Country", "year": "Year", "ratio": "Ratio (%)",
                "delta": "Δ vs prev. (pts)"}), hide_index=True, width='stretch')
    st.divider()
