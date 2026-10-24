"""Section 6 — Conclusions: what we can say, and what we cannot."""

from __future__ import annotations

import streamlit as st

from utils import constants as C
from utils import io


def render(f) -> None:
    st.header("6 · What to take away")
    lo, hi = f.years
    kpi = io.load_table("kpi")
    k = kpi[(kpi["year"].between(lo, hi)) & (kpi["metro"])]
    out_share = (k[k["agg_label"] == "Outside built-up area"]["killed"].sum()
                 / max(k["killed"].sum(), 1) * 100)

    st.markdown(
        f"""
**Three things the data show (metropolitan France, {lo}–{hi}):**

1. **Frequency and severity tell opposite stories.** Most accidents happen in town and
   at rush hour, but about **{out_share:.0f}% of deaths happen outside built-up areas**,
   and the rural departments with the fewest accidents are the deadliest per accident.
2. **Night is the deadly multiplier.** A night-time accident kills far more often than a
   daytime one, even though there are fewer of them.
3. **Who dies is not who you'd guess.** Powered two-wheelers carry a share of deaths far
   above their presence; e-scooters injure many but kill few; and deaths peak twice by
   age — young adults (18–24) and the elderly (75+).
        """
    )
    st.markdown(
        """
**What this page does *not* say:**

- **No per-trip or per-kilometre risk** — the data hold no exposure (distance travelled
  per mode), so "mode X is N times more dangerous" is out of reach here.
- **No causation** — night, open roads and speed go together; we show co-occurrence.
- **No policy evaluation** and **no individual data**.

**Where to go next:** add exposure data (traffic counts, km by mode) to turn shares into
risks; bring in population to compute deaths per capita; extend to the long 2005–2024
series for deaths only.
        """
    )
    st.caption(
        f"Source: {C.PRODUCER} — BAAC, data.gouv.fr ({C.LICENCE}). "
        "Joins, harmonisation, aggregation and derived indicators by the author."
    )
