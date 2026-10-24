"""Unified Plotly chart factory for the road-safety story.

Colours encode data; text/backgrounds are left to Streamlit's theme (charts are
rendered with theme="streamlit"). Palette is colourblind-safe (Cividis) and the
tone is deliberately sober. Every chart gets a clean source note, titled axes
with units, and consistent spacing.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils import constants as C

SOURCE_NOTE = "Source: ONISR / BAAC (data.gouv.fr, Licence Ouverte) · metropolitan France"
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
_GRID = "rgba(128,128,128,0.18)"

# Metric metadata shared across charts.
METRICS = {
    "Accidents": ("accidents", "Number of accidents", C.COLOR_ACCIDENTS),
    "Killed": ("killed", "People killed", C.COLOR_KILLED),
    "Gravity index": ("gravity_index", "Killed per 100 accidents", C.COLOR_GRAVITY),
}


def _style(fig: go.Figure, source: bool = True) -> go.Figure:
    """Shared layout: typography, spacing, subtle grid, clean source note."""
    fig.update_layout(
        font=dict(family="system-ui, -apple-system, Segoe UI, sans-serif", size=14,
                  color="#3c3c3c"),
        title=dict(font=dict(size=17), x=0, xanchor="left", y=0.97, yanchor="top"),
        margin=dict(l=14, r=14, t=62, b=64),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(font_size=13),
    )
    fig.update_xaxes(showgrid=False, title_standoff=8, zeroline=False)
    fig.update_yaxes(gridcolor=_GRID, zeroline=False, title_standoff=8)
    if source:
        # Fixed-pixel offset below the plot so it never collides with axis titles.
        fig.add_annotation(text=SOURCE_NOTE, xref="paper", yref="paper", x=0, y=0,
                           yanchor="top", yshift=-46, xanchor="left", showarrow=False,
                           font=dict(size=10.5, color=C.COLOR_REF))
    return fig


# --- V1: hour x weekday heatmap -------------------------------------------
def heatmap_hour_dow(df: pd.DataFrame, metric: str) -> go.Figure:
    col, label, _ = METRICS[metric]
    grid = (df.groupby(["weekday", "hour"], observed=True)
            .agg(accidents=("accidents", "sum"), killed=("killed", "sum")).reset_index())
    if col == "gravity_index":
        grid["gravity_index"] = (grid["killed"] / grid["accidents"].replace(0, pd.NA) * 100)
    pivot = grid.pivot(index="weekday", columns="hour", values=col).reindex(range(7))
    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=[f"{h:02d}" for h in pivot.columns],
        y=[WEEKDAYS[int(i)] for i in pivot.index], colorscale=C.SEQ_SCALE,
        xgap=1.5, ygap=1.5,
        colorbar=dict(title=dict(text=label, side="right"), thickness=12, len=0.85),
        hovertemplate="%{y} · %{x}h<br>" + label + ": %{z:.1f}<extra></extra>",
    ))
    fig.update_layout(title=f"{metric} by hour and weekday",
                      xaxis_title="Hour of day", yaxis_title=None)
    fig.update_xaxes(dtick=2, ticksuffix="h")
    fig.update_yaxes(autorange="reversed")
    return _style(fig)


# --- V2: monthly curve -----------------------------------------------------
def monthly_curve(df: pd.DataFrame) -> go.Figure:
    g = df.groupby("month", observed=True).agg(
        accidents=("accidents", "sum"), killed=("killed", "sum")).reset_index()
    x = [MONTHS[int(m) - 1] for m in g["month"]]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=g["accidents"], name="Accidents", yaxis="y1",
                             mode="lines+markers", marker=dict(size=6),
                             line=dict(color=C.COLOR_ACCIDENTS, width=2.5),
                             hovertemplate="%{x}: %{y:,} accidents<extra></extra>"))
    fig.add_trace(go.Scatter(x=x, y=g["killed"], name="Killed", yaxis="y2",
                             mode="lines+markers", marker=dict(size=6),
                             line=dict(color=C.COLOR_KILLED, width=2.5),
                             hovertemplate="%{x}: %{y:,} killed<extra></extra>"))
    fig.update_layout(
        title="Seasonality: accidents and deaths by month", xaxis_title="Month",
        yaxis=dict(title="Accidents", color=C.COLOR_ACCIDENTS, gridcolor=_GRID),
        yaxis2=dict(title="Killed", color=C.COLOR_KILLED, overlaying="y", side="right",
                    showgrid=False),
    )
    return _style(fig)


# --- V3: choropleth by department -----------------------------------------
def choropleth_dep(df: pd.DataFrame, geojson: dict, metric: str) -> go.Figure:
    col, label, _ = METRICS[metric]
    g = df.groupby(["dep"], observed=True).agg(
        accidents=("accidents", "sum"), killed=("killed", "sum")).reset_index()
    g["gravity_index"] = (g["killed"] / g["accidents"].replace(0, pd.NA) * 100).round(2)
    names = {ft["properties"]["code"]: ft["properties"]["nom"] for ft in geojson["features"]}
    g["nom"] = g["dep"].map(names).fillna(g["dep"])

    fig = px.choropleth(
        g, geojson=geojson, locations="dep", featureidkey="properties.code",
        color=col, color_continuous_scale=C.SEQ_SCALE, custom_data=["nom"],
        labels={col: label},
    )
    fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
    fig.update_traces(marker_line_width=0.4, marker_line_color="rgba(255,255,255,0.7)",
                      hovertemplate="<b>%{customdata[0]}</b><br>" + label +
                      ": %{z:.1f}<extra></extra>")
    fig.update_layout(title=f"{metric} by department", height=520,
                      coloraxis_colorbar=dict(title=dict(text=label, side="right"),
                                              thickness=12, len=0.75))
    return _style(fig)


# --- V4: built-up vs outside (share of accidents vs deaths) ----------------
def agg_share_bars(df: pd.DataFrame) -> go.Figure:
    g = df.groupby("agg_label", observed=True).agg(
        accidents=("accidents", "sum"), killed=("killed", "sum")).reset_index().dropna()
    g["Accidents"] = g["accidents"] / g["accidents"].sum() * 100
    g["Killed"] = g["killed"] / g["killed"].sum() * 100
    fig = go.Figure()
    for metric, color in [("Accidents", C.COLOR_ACCIDENTS), ("Killed", C.COLOR_KILLED)]:
        fig.add_trace(go.Bar(
            x=g["agg_label"], y=g[metric], name=metric, marker_color=color,
            marker_line_width=0, text=g[metric].map(lambda v: f"{v:.0f}%"),
            textposition="outside", textfont=dict(size=14),
            hovertemplate="%{x}<br>" + metric + ": %{y:.0f}%<extra></extra>",
        ))
    fig.update_layout(barmode="group", bargap=0.35, title="Where accidents happen vs. where people die",
                      xaxis_title=None, yaxis_title="Share of total (%)",
                      yaxis=dict(range=[0, 78]))
    return _style(fig)


# --- V5: dumbbell victims vs killed share by mode --------------------------
def dumbbell_mode(df: pd.DataFrame) -> go.Figure:
    g = df.groupby("mode", observed=True).agg(
        victims=("victims", "sum"), killed=("killed", "sum")).reset_index()
    g["vic_share"] = g["victims"] / g["victims"].sum() * 100
    g["kill_share"] = g["killed"] / g["killed"].sum() * 100
    g = g.set_index("mode").reindex([m for m in C.MODE_ORDER if m in g.index]).reset_index()
    fig = go.Figure()
    for _, r in g.iterrows():
        fig.add_trace(go.Scatter(
            x=[r["vic_share"], r["kill_share"]], y=[r["mode"], r["mode"]],
            mode="lines", line=dict(color=_GRID.replace("0.18", "0.6"), width=3),
            showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=g["vic_share"], y=g["mode"], mode="markers", name="% of victims",
                             marker=dict(color=C.COLOR_ACCIDENTS, size=13,
                                         line=dict(width=1, color="white")),
                             hovertemplate="%{y}<br>%{x:.1f}% of victims<extra></extra>"))
    fig.add_trace(go.Scatter(x=g["kill_share"], y=g["mode"], mode="markers", name="% of killed",
                             marker=dict(color=C.COLOR_KILLED, size=13,
                                         line=dict(width=1, color="white")),
                             hovertemplate="%{y}<br>%{x:.1f}% of killed<extra></extra>"))
    fig.update_layout(title="Share of victims vs. share of deaths, by mode",
                      xaxis_title="Share (%)", yaxis_title=None, height=440)
    fig.update_yaxes(autorange="reversed")
    return _style(fig)


# --- V6: age pyramid of the killed, by sex ---------------------------------
def age_pyramid(df: pd.DataFrame) -> go.Figure:
    g = (df.groupby(["age_band", "sexe_label"], observed=True)["killed"].sum()
         .reset_index())
    piv = g.pivot(index="age_band", columns="sexe_label", values="killed").reindex(C.AGE_LABELS)
    male, female = piv.get("Male", 0), piv.get("Female", 0)
    fig = go.Figure()
    fig.add_trace(go.Bar(y=piv.index, x=-male, name="Male", orientation="h",
                         marker_color=C.COLOR_ACCIDENTS, marker_line_width=0,
                         customdata=male, hovertemplate="Male %{y}: %{customdata}<extra></extra>"))
    fig.add_trace(go.Bar(y=piv.index, x=female, name="Female", orientation="h",
                         marker_color=C.COLOR_GRAVITY, marker_line_width=0,
                         hovertemplate="Female %{y}: %{x}<extra></extra>"))
    fig.update_layout(barmode="relative", bargap=0.18,
                      title="People killed by age band and sex",
                      xaxis_title="People killed (Male ◀ | ▶ Female)", yaxis_title="Age band")
    fig.update_xaxes(tickformat="~s", tickvals=[-400, -200, 0, 200, 400],
                     ticktext=["400", "200", "0", "200", "400"])
    return _style(fig)


# --- V7: small multiples, gravity by condition -----------------------------
def conditions_facets(df: pd.DataFrame) -> go.Figure:
    g = df.groupby(["dimension", "modality"], observed=True).agg(
        accidents=("accidents", "sum"), fatal=("fatal", "sum")).reset_index()
    g["gravity_index"] = (g["fatal"] / g["accidents"].replace(0, pd.NA) * 100).round(2)
    fig = px.bar(g.sort_values("gravity_index"), x="gravity_index", y="modality",
                 facet_col="dimension", facet_col_wrap=2, orientation="h",
                 color="gravity_index", color_continuous_scale=C.SEQ_SCALE,
                 labels={"gravity_index": "Killed per 100 accidents", "modality": ""})
    fig.update_yaxes(matches=None)
    fig.update_xaxes(matches=None)
    fig.update_traces(marker_line_width=0)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1], font_size=13))
    fig.update_layout(title="Severity (killed per 100 accidents) by condition", height=640,
                      coloraxis_showscale=False)
    fig.update_yaxes(ticksuffix="  ")
    return _style(fig)


# --- V9: missingness heatmap ----------------------------------------------
def missingness_heatmap(df: pd.DataFrame) -> go.Figure:
    piv = df.pivot(index="variable", columns="year", values="missing_pct")
    fig = go.Figure(go.Heatmap(
        z=piv.values, x=[str(c) for c in piv.columns], y=list(piv.index),
        colorscale="OrRd", zmin=0, xgap=2, ygap=2,
        colorbar=dict(title=dict(text="% missing", side="right"), thickness=12, len=0.9),
        text=piv.values, texttemplate="%{text:.0f}", textfont=dict(size=11),
        hovertemplate="%{y} · %{x}: %{z:.1f}% missing<extra></extra>"))
    fig.update_layout(title="Missing values in key fields, by year",
                      xaxis_title="Year", yaxis_title=None, height=320)
    return _style(fig, source=False)
