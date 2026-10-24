"""The French tax exception? — a data story on tax-to-GDP ratios in Europe.

Single-page, linear narrative (Hook -> Context -> Insights -> Implications).
Run with:  streamlit run app.py   (or: make run)
"""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from sections import conclusions, deep_dives, intro, overview, quality
from utils import constants as C
from utils import io, prep

st.set_page_config(
    page_title="The French tax exception?",
    page_icon="🇪🇺",
    layout="wide",
    initial_sidebar_state="expanded",
)


@dataclass
class Filters:
    year_range: tuple[int, int]
    ref_year: int
    compare: list[str]
    focal: str
    category: str | None
    include_non_eu: bool


def build_sidebar(raw) -> Filters:
    years = sorted(raw["year"].unique())
    y_min, y_max = int(years[0]), int(years[-1])

    st.sidebar.title("Controls")
    st.sidebar.caption("Every control changes something in the story.")

    year_range = st.sidebar.slider(
        "Period (time series)", y_min, y_max, (y_min, C.LAST_COMPLETE_YEAR),
        help="Range used by the trend and gap charts.",
    )
    ref_year = st.sidebar.select_slider(
        "Reference year (map, ranking, KPIs)", options=years, value=C.LAST_COMPLETE_YEAR,
        help=f"{C.LAST_COMPLETE_YEAR} is the last fully reported year; "
             f"{y_max} is still incomplete (provisional).",
    )

    member_opts = {C.COUNTRY_NAMES[g]: g for g in C.EU27_MEMBERS}
    focal_name = st.sidebar.selectbox(
        "Focal country", list(member_opts), index=list(member_opts).index("France"),
        help="Drives the KPIs and the gap chart.",
    )
    focal = member_opts[focal_name]

    default_cmp = [C.COUNTRY_NAMES[g] for g in C.COMPARE_DEFAULT]
    cmp_names = st.sidebar.multiselect(
        "Countries compared (trends, composition)", list(member_opts),
        default=default_cmp, help="Lines and stacked bars.",
    )
    compare = [member_opts[n] for n in cmp_names] or [focal]
    if focal not in compare:
        compare = [focal, *compare]

    cat_choice = st.sidebar.radio(
        "Metric shown on the map & ranking", ["Total tax-to-GDP", *C.CATEGORY_ORDER],
        help="Switch from the headline ratio to a single category.",
    )
    category = None if cat_choice == "Total tax-to-GDP" else cat_choice

    include_non_eu = st.sidebar.toggle(
        "Include non-EU (IS, NO, CH)", value=False,
        help="Adds Iceland, Norway and Switzerland to the map and ranking.",
    )

    st.sidebar.divider()
    st.sidebar.caption(
        f"Snapshot: {io.snapshot_date().isoformat()} · Eurostat {C.DATASET_CODE} · CC BY 4.0"
    )
    return Filters(year_range, int(ref_year), compare, focal, category, include_non_eu)


def kpi_header(raw, f: Filters) -> None:
    tr = prep.tax_ratio(raw)
    cur = tr[tr["year"] == f.ref_year]
    prev = tr[tr["year"] == f.ref_year - 1]
    start = tr[tr["year"] == f.year_range[0]]

    def val(frame, geo, col="ratio"):
        s = frame.loc[frame["geo"] == geo, col]
        return float(s.iloc[0]) if len(s) and not s.isna().all() else None

    focal_name = C.COUNTRY_NAMES[f.focal]
    fr, fr_prev = val(cur, f.focal), val(prev, f.focal)
    eu, eu_prev = val(cur, C.EU_AGGREGATE), val(prev, C.EU_AGGREGATE)
    gap = val(cur, f.focal, "gap_vs_eu")
    gap_start = val(start, f.focal, "gap_vs_eu")
    rank = val(cur, f.focal, "rank")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"{focal_name} tax-to-GDP", f"{fr:.1f}%" if fr else "n/a",
              f"{fr - fr_prev:+.1f} pts vs {f.ref_year - 1}" if fr and fr_prev else None)
    c2.metric("EU27 average", f"{eu:.1f}%" if eu else "n/a",
              f"{eu - eu_prev:+.1f} pts vs {f.ref_year - 1}" if eu and eu_prev else None)
    c3.metric(f"{focal_name} − EU27", f"{gap:+.1f} pts" if gap is not None else "n/a",
              f"{gap - gap_start:+.1f} pts since {f.year_range[0]}"
              if gap is not None and gap_start is not None else None,
              delta_color="off")
    c4.metric(f"{focal_name} rank in EU27", f"{int(rank)} / 27" if rank else "n/a",
              help="1 = highest ratio.")


def main() -> None:
    raw = io.load_raw()
    f = build_sidebar(raw)

    st.title("The French tax exception?")
    st.markdown(
        "**For a curious, non-specialist reader** who has heard that *“France is "
        "Europe's tax champion”* and wants to know what that actually means. "
        "Everything below is **descriptive**: it compares and decomposes, it does "
        "not judge whether taxes are *too high* and makes **no causal claim**."
    )
    kpi_header(raw, f)
    st.divider()

    intro.render(raw, f)
    overview.render(raw, f)
    deep_dives.render(raw, f)
    quality.render(raw, f)
    conclusions.render(raw, f)


if __name__ == "__main__":
    main()
