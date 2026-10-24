"""Unified Plotly chart factory.

One place for every chart so the visual language stays consistent (fonts,
reference lines, source note, accessible palette). Colours encode *data*;
text and backgrounds are left to Streamlit's theme (charts are rendered with
``theme="streamlit"`` in the sections, so they adapt to light and dark).
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils import constants as C

SOURCE_NOTE = "Source: Eurostat, gov_10a_taxag (CC BY 4.0) · sector S13_S212, % of GDP"
_BAND_COLOR = "rgba(128,128,128,0.15)"
_REF_COLOR = "#888888"


def _style(fig: go.Figure, source: bool = True) -> go.Figure:
    """Apply shared layout: margins, legend, hover, optional source note."""
    fig.update_layout(
        font=dict(family="system-ui, -apple-system, Segoe UI, sans-serif", size=14),
        margin=dict(l=10, r=10, t=56, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None),
        hovermode="closest",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    if source:
        fig.add_annotation(
            text=SOURCE_NOTE, xref="paper", yref="paper", x=0, y=-0.16,
            showarrow=False, font=dict(size=11, color=_REF_COLOR), align="left",
        )
    return fig


def _crisis_bands(fig: go.Figure) -> None:
    """Shade the 2008-09 and 2020 crisis years (denominator-effect caveat)."""
    for start, end, label in C.CRISIS_EVENTS:
        fig.add_vrect(
            x0=start - 0.5, x1=end + 0.5, fillcolor=_BAND_COLOR, line_width=0,
            layer="below", annotation_text=label, annotation_position="top left",
            annotation_font_size=10, annotation_font_color=_REF_COLOR,
        )


# --- V1: choropleth --------------------------------------------------------
def choropleth(ratio_year: pd.DataFrame, year: int) -> go.Figure:
    """Europe choropleth of the tax-to-GDP ratio for one year."""
    d = ratio_year.dropna(subset=["iso3"])
    fig = px.choropleth(
        d, locations="iso3", color="ratio", scope="europe",
        color_continuous_scale="Cividis", hover_name="country",
        labels={"ratio": "% of GDP"},
        custom_data=["country", "ratio"],
    )
    fig.update_traces(
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]:.1f}% of GDP<extra></extra>"
    )
    fig.update_geos(showframe=False, showcoastlines=False, projection_type="mercator",
                    lataxis_range=[34, 71], lonaxis_range=[-12, 32])
    fig.update_layout(coloraxis_colorbar=dict(title="% of GDP", ticksuffix="%"),
                      title=f"Tax-to-GDP ratio, {year}")
    return _style(fig)


# --- V2: ranking bars ------------------------------------------------------
def ranking_bars(ratio_year: pd.DataFrame, focal: str, year: int) -> go.Figure:
    """Horizontal bars, highest ratio on top, EU average as a reference line."""
    d = ratio_year.dropna(subset=["ratio"]).sort_values("ratio")
    eu_value = d.loc[d["geo"] == C.EU_AGGREGATE, "ratio"]
    eu_value = float(eu_value.iloc[0]) if len(eu_value) else None
    bars = d[d["geo"] != C.EU_AGGREGATE]

    colors = [
        C.COLOR_FOCAL if g == focal else C.COLOR_OTHER for g in bars["geo"]
    ]
    fig = go.Figure(go.Bar(
        x=bars["ratio"], y=bars["country"], orientation="h",
        marker_color=colors, text=bars["ratio"].map(lambda v: f"{v:.1f}"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>%{x:.1f}% of GDP<extra></extra>",
    ))
    if eu_value is not None:
        fig.add_vline(x=eu_value, line_dash="dash", line_color=_REF_COLOR)
        fig.add_annotation(x=eu_value, y=1.0, yref="paper", yanchor="bottom",
                           text=f"EU27 avg {eu_value:.1f}%", showarrow=False,
                           font=dict(size=12, color=_REF_COLOR))
    fig.update_layout(title=f"Where each country stands, {year}",
                      xaxis_title="% of GDP", yaxis_title=None,
                      height=max(420, 20 * len(bars)))
    return _style(fig)


# --- V3: multi-country lines ----------------------------------------------
def lines_multi(ratio: pd.DataFrame, geos: list[str], yr_range: tuple[int, int]) -> go.Figure:
    """Tax-to-GDP trajectories for selected countries + EU reference."""
    lo, hi = yr_range
    d = ratio[(ratio["year"].between(lo, hi))]
    fig = go.Figure()
    # EU reference first (grey, dashed).
    eu = d[d["geo"] == C.EU_AGGREGATE]
    fig.add_trace(go.Scatter(x=eu["year"], y=eu["ratio"], name="EU27",
                             mode="lines", line=dict(color=C.COLOR_EU, dash="dash", width=2)))
    palette = iter(C.OKABE_ITO)
    for g in geos:
        sub = d[d["geo"] == g]
        if sub.empty:
            continue
        color = C.COLOR_FOCAL if g == C.FOCAL_DEFAULT else next(palette)
        fig.add_trace(go.Scatter(
            x=sub["year"], y=sub["ratio"], name=C.COUNTRY_NAMES.get(g, g),
            mode="lines", line=dict(color=color, width=2.5),
            hovertemplate=f"<b>{C.COUNTRY_NAMES.get(g, g)}</b><br>%{{x}}: %{{y:.1f}}%<extra></extra>",
        ))
    _crisis_bands(fig)
    fig.update_layout(title="Tax-to-GDP over time", xaxis_title="Year",
                      yaxis_title="% of GDP")
    return _style(fig)


# --- V4: gap line ----------------------------------------------------------
def gap_line(ratio: pd.DataFrame, focal: str, yr_range: tuple[int, int]) -> go.Figure:
    """Gap (focal - EU27) over time, with the min and max years annotated."""
    lo, hi = yr_range
    d = ratio[(ratio["geo"] == focal) & (ratio["year"].between(lo, hi))].dropna(subset=["gap_vs_eu"])
    name = C.COUNTRY_NAMES.get(focal, focal)
    fig = go.Figure(go.Scatter(
        x=d["year"], y=d["gap_vs_eu"], mode="lines", line=dict(color=C.COLOR_FOCAL, width=2.5),
        fill="tozeroy", fillcolor="rgba(213,94,0,0.12)",
        hovertemplate="%{x}: %{y:+.1f} pts<extra></extra>",
    ))
    fig.add_hline(y=0, line_color=_REF_COLOR, line_width=1)
    if not d.empty:
        for row, pos in ((d.loc[d["gap_vs_eu"].idxmax()], "top center"),
                         (d.loc[d["gap_vs_eu"].idxmin()], "bottom center")):
            fig.add_annotation(x=row["year"], y=row["gap_vs_eu"],
                               text=f"{row['gap_vs_eu']:+.1f} pts ({int(row['year'])})",
                               showarrow=True, arrowhead=0, font=dict(size=11))
    fig.update_layout(title=f"{name} minus EU27 average",
                      xaxis_title="Year", yaxis_title="Gap (percentage points)")
    return _style(fig)


# --- V5: stacked categories ------------------------------------------------
def stacked_categories(cats: pd.DataFrame, geos: list[str], year: int) -> go.Figure:
    """Stacked bars of the 4 categories (% of GDP) for selected countries."""
    d = cats[(cats["year"] == year) & (cats["geo"].isin(geos))]
    fig = go.Figure()
    for cat in C.CATEGORY_ORDER:
        sub = d[d["category"] == cat]
        order = [C.COUNTRY_NAMES.get(g, g) for g in geos]
        sub = sub.set_index("country").reindex(order).reset_index()
        fig.add_trace(go.Bar(
            x=sub["country"], y=sub["value"], name=cat,
            marker_color=C.CATEGORY_COLORS[cat],
            hovertemplate=f"<b>%{{x}}</b><br>{cat}: %{{y:.1f}}%<extra></extra>",
        ))
    fig.update_layout(barmode="stack", title=f"What the ratio is made of, {year}",
                      xaxis_title=None, yaxis_title="% of GDP")
    return _style(fig)


# --- V6: small multiples ---------------------------------------------------
def small_multiples(cats: pd.DataFrame, geos: list[str], yr_range: tuple[int, int]) -> go.Figure:
    """One panel per category; a line per country; shared Y scale."""
    lo, hi = yr_range
    d = cats[(cats["geo"].isin(geos)) & (cats["year"].between(lo, hi))].copy()
    d["category"] = pd.Categorical(d["category"], categories=C.CATEGORY_ORDER, ordered=True)
    color_map = {C.COUNTRY_NAMES.get(g, g): (C.COLOR_FOCAL if g == C.FOCAL_DEFAULT else c)
                 for g, c in zip(geos, C.OKABE_ITO)}
    fig = px.line(
        d.sort_values(["category", "year"]), x="year", y="value",
        color="country", facet_col="category", facet_col_wrap=2,
        color_discrete_map=color_map,
        labels={"value": "% of GDP", "year": "Year", "country": ""},
    )
    fig.update_yaxes(matches="y")  # comparable scales across panels
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1], font_size=13))
    fig.update_layout(title="Each category over time", height=560)
    return _style(fig)


# --- V7: completeness heatmap ----------------------------------------------
def completeness_heatmap(grid: pd.DataFrame) -> go.Figure:
    """Country x year grid: present (1) vs missing (0)."""
    fig = go.Figure(go.Heatmap(
        z=grid.values, x=[str(c) for c in grid.columns], y=list(grid.index),
        colorscale=[[0, "#E69F00"], [1, "#0072B2"]], showscale=False,
        xgap=1, ygap=1,
        hovertemplate="%{y} · %{x}: %{customdata}<extra></extra>",
        customdata=[["present" if v else "MISSING" for v in row] for row in grid.values],
    ))
    fig.update_layout(title="Data completeness (headline total)",
                      xaxis_title="Year", yaxis_title=None, height=640)
    fig.update_yaxes(autorange="reversed")
    return _style(fig, source=False)


# --- "Who collects": subsector 100% bars -----------------------------------
def subsector_bars(shares: pd.DataFrame, geos: list[str], year: int) -> go.Figure:
    """100%-stacked bars of who collects the money, per country."""
    order = [C.COUNTRY_NAMES.get(g, g) for g in geos]
    colors = {"Central government": "#0072B2", "Local government": "#E69F00",
              "Social security funds": "#009E73"}
    fig = go.Figure()
    for sub, color in colors.items():
        d = shares[(shares["subsector"] == sub) & (shares["geo"].isin(geos))]
        d = d.set_index("country").reindex(order).reset_index()
        fig.add_trace(go.Bar(
            x=d["share"], y=d["country"], orientation="h", name=sub,
            marker_color=color,
            hovertemplate=f"<b>%{{y}}</b><br>{sub}: %{{x:.1f}}%<extra></extra>",
        ))
    fig.update_layout(barmode="stack", title=f"Who collects the receipts, {year}",
                      xaxis_title="% of total receipts", yaxis_title=None,
                      xaxis=dict(ticksuffix="%"))
    return _style(fig)
