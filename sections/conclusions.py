"""Section 6 — Conclusions: what we can say, and what we cannot."""

from __future__ import annotations

import streamlit as st

from utils import constants as C
from utils import prep


def render(raw, f) -> None:
    st.header("6 · What to take away")
    tr = prep.tax_ratio(raw)
    cur = tr[tr["year"] == f.ref_year]
    focal_name = C.COUNTRY_NAMES[f.focal]
    fr = cur.loc[cur["geo"] == f.focal, "ratio"]
    gap = cur.loc[cur["geo"] == f.focal, "gap_vs_eu"]
    rank = cur.loc[cur["geo"] == f.focal, "rank"]
    gap_tbl = prep.gap_by_category(raw, f.focal, f.ref_year)
    drivers = gap_tbl[gap_tbl["gap"] > 0].sort_values("gap", ascending=False)["category"]

    if len(fr) and len(gap) and len(rank):
        st.markdown(
            f"""
**Three things the data show ({f.ref_year}):**

1. **{focal_name} really is near the top** — {fr.iloc[0]:.1f}% of GDP, rank
   {int(rank.iloc[0])} of 27, about {gap.iloc[0]:+.1f} points above the EU27 average.
2. **The gap is structural, not new** — it is visible across the whole 1995– period,
   not a recent spike (see section 2).
3. **The gap is not one single thing** — it comes mainly from
   **{" and ".join(drivers.head(2).str.lower().tolist())}**, while income & wealth taxes
   sit *at or below* the EU average. *“Tax champion”* is really a story about how
   social spending is financed, not a uniformly higher tax on everything.
            """
        )

    st.markdown(
        """
**What this page does *not* say:**

- No causal claim — the data cannot tell us what a high ratio *causes*.
- No political judgement — nothing here says taxes are *too high* or *too low*.
- Nothing about individual households — a % of GDP is not a personal tax rate.
- Nothing about whether public money is well spent.

**Where to go next:** break categories down further (VAT vs. other production taxes),
add a household-level perspective from a different dataset, or extend the comparison
beyond the EU with OECD data (different definitions apply).
        """
    )
    st.caption(
        f"Source: Eurostat, {C.DATASET_CODE} (DOI {C.DATASET_DOI}), CC BY 4.0. "
        "Filtering, category grouping and derived calculations by the author."
    )
