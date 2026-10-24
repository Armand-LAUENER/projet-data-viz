"""Section 0 — Intro: the hook and the definition (what the ratio measures)."""

from __future__ import annotations

import streamlit as st

from utils import constants as C
from utils import prep


def render(raw, f) -> None:
    tr = prep.tax_ratio(raw)
    cur = tr[tr["year"] == f.ref_year]
    fr = cur.loc[cur["geo"] == f.focal, "ratio"]
    eu = cur.loc[cur["geo"] == C.EU_AGGREGATE, "ratio"]
    gap = cur.loc[cur["geo"] == f.focal, "gap_vs_eu"]
    focal_name = C.COUNTRY_NAMES[f.focal]

    st.header("The hook")
    if len(fr) and len(eu):
        st.subheader(
            f"In {f.ref_year}, {focal_name} raised **{fr.iloc[0]:.1f}% of GDP** in taxes "
            f"and social contributions — about **{gap.iloc[0]:+.1f} points** versus the "
            f"EU27 average of {eu.iloc[0]:.1f}%."
        )
    st.markdown(
        "That headline is real — but *“tax champion”* hides more than it reveals. "
        "This page unpacks **how big the gap is, when it opened, and what it is made of.**"
    )

    with st.expander("Definition — what exactly is this ratio?", expanded=False):
        st.markdown(
            """
**Tax-to-GDP ratio** = total government revenue from **taxes** (on production,
income, wealth and capital) **plus net social contributions**, divided by GDP.

- Source: **Eurostat**, *Main national accounts tax aggregates* (`gov_10a_taxag`),
  sector **S13_S212** (general government + EU institutions), expressed in **% of GDP**.
- One source, one definition, for every country — so comparisons are fair.
- A high ratio reflects a **choice about how to finance public spending**
  (publicly vs. privately); it is **not** a measure of how much a given household pays,
  nor of whether public money is well spent.

> Note on definitions: national sources can differ. The French INSEE publishes a
> slightly different “compulsory levies” figure because its scope differs from
> Eurostat's. We stay with Eurostat throughout and never mix the two.
            """
        )
    st.divider()
