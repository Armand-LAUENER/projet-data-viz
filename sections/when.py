"""Section 1 — When? (hour x weekday heatmap + monthly curve)."""

from __future__ import annotations

import streamlit as st

from utils import io, viz


def render(f) -> None:
    st.header("1 · When?")
    lo, hi = f.years
    hd = io.load_table("by_hour_dow")
    hd = hd[hd["year"].between(lo, hi)]

    # Insight computed live: day vs night gravity.
    night = hd[hd["hour"].isin([22, 23, 0, 1, 2, 3, 4, 5])]
    day = hd[~hd["hour"].isin([22, 23, 0, 1, 2, 3, 4, 5])]
    gi_n = night["killed"].sum() / max(night["accidents"].sum(), 1) * 100
    gi_d = day["killed"].sum() / max(day["accidents"].sum(), 1) * 100
    st.subheader(
        f"Accidents peak at commuting hours — but a night-time accident is far "
        f"deadlier ({gi_n:.1f} vs {gi_d:.1f} killed per 100 accidents)."
    )

    st.plotly_chart(viz.heatmap_hour_dow(hd, f.metric), width="stretch", theme="streamlit")
    st.caption(
        f"{f.metric} by hour of day (x) and weekday (y). Switch the metric in the "
        "sidebar: 'Accidents' peaks on weekday rush hours, 'Gravity index' lights up "
        "at night and on weekend small hours."
    )

    month = io.load_table("by_month")
    st.plotly_chart(viz.monthly_curve(month[month["year"].between(lo, hi)]),
                    width="stretch", theme="streamlit")
    st.caption("Accidents (left axis) and deaths (right axis) by month; both rise over "
               "the summer driving season.")
    st.divider()
