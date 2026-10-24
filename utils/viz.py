"""Unified Plotly chart factory for the road-safety story.

Colours encode data; text/backgrounds are left to Streamlit's theme (charts are
rendered with theme="streamlit"). Tone is deliberately sober. Every chart gets a
source note and titled axes with units.
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

# Metric metadata shared across charts.
METRICS = {
    "Accidents": ("accidents", "Number of accidents", C.COLOR_ACCIDENTS),
    "Killed": ("killed", "People killed", C.COLOR_KILLED),
    "Gravity index": ("gravity_index", "Killed per 100 accidents", C.COLOR_GRAVITY),
}


def _style(fig: go.Figure, source: bool = True) -> go.Figure:
    fig.update_layout(
        font=dict(family="system-ui, -apple-system, Segoe UI, sans-serif", size=14),
        margin=dict(l=10, r=10, t=56, b=42),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    if source:
        fig.add_annotation(text=SOURCE_NOTE, xref="paper", yref="paper", x=0, y=-0.18,
                           showarrow=False, font=dict(size=11, color=C.COLOR_REF))
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
        z=pivot.values, x=[f"{h:02d}h" for h in pivot.columns],
        y=[WEEKDAYS[int(i)] for i in pivot.index], colorscale=C.SEQ_SCALE,
        colorbar=dict(title=label),
        hovertemplate="%{y} %{x}<br>" + label + ": %{z:.1f}<extra></extra>",
    ))
    fig.update_layout(title=f"{metric} by hour and weekday",
                      xaxis_title="Hour of day", yaxis_title=None)
    fig.update_yaxes(autorange="reversed")
    return _style(fig)


# --- V2: monthly curve -----------------------------------------------------
def monthly_curve(df: pd.DataFrame) -> go.Figure:
    g = df.groupby("month", observed=True).agg(
        accidents=("accidents", "sum"), killed=("killed", "sum")).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[MONTHS[int(m) - 1] for m in g["month"]], y=g["accidents"],
                             name="Accidents", line=dict(color=C.COLOR_ACCIDENTS, width=2.5),
                             yaxis="y1"))
    fig.add_trace(go.Scatter(x=[MONTHS[int(m) - 1] for m in g["month"]], y=g["killed"],
                             name="Killed", line=dict(color=C.COLOR_KILLED, width=2.5),
                             yaxis="y2"))
    fig.update_layout(
        title="Seasonality: accidents and deaths by month",
        xaxis_title="Month",
        yaxis=dict(title="Accidents", color=C.COLOR_ACCIDENTS),
        yaxis2=dict(title="Killed", color=C.COLOR_KILLED, overlaying="y", side="right"),
    )
    return _style(fig)


# --- V3: choropleth by department -----------------------------------------
def choropleth_dep(df: pd.DataFrame, geojson: dict, metric: str) -> go.Figure:
    col, label, _ = METRICS[metric]
    g = df.groupby(["dep"], observed=True).agg(
        accidents=("accidents", "sum"), killed=("killed", "sum")).reset_index()
    g["gravity_index"] = (g["killed"] / g["accidents"].replace(0, pd.NA) * 100).round(2)
    fig = px.choropleth(
        g, geojson=geojson, locations="dep", featureidkey="properties.code",
        color=col, color_continuous_scale=C.SEQ_SCALE,
        labels={col: label},
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_traces(marker_line_width=0.3, marker_line_color="white",
                      hovertemplate="Dép. %{location}<br>" + label + ": %{z:.1f}<extra></extra>")
    fig.update_layout(title=f"{metric} by department", coloraxis_colorbar=dict(title=label))
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
            text=g[metric].map(lambda v: f"{v:.0f}%"), textposition="outside",
            hovertemplate="%{x}<br>" + metric + ": %{y:.0f}%<extra></extra>",
        ))
    fig.update_layout(barmode="group", title="Where accidents happen vs. where people die",
                      xaxis_title=None, yaxis_title="Share of total (%)")
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
            mode="lines", line=dict(color=C.COLOR_REF, width=2), showlegend=False,
            hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=g["vic_share"], y=g["mode"], mode="markers", name="% of victims",
                             marker=dict(color=C.COLOR_ACCIDENTS, size=11),
                             hovertemplate="%{y}<br>%{x:.1f}% of victims<extra></extra>"))
    fig.add_trace(go.Scatter(x=g["kill_share"], y=g["mode"], mode="markers", name="% of killed",
                             marker=dict(color=C.COLOR_KILLED, size=11),
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
    fig = go.Figure()
    fig.add_trace(go.Bar(y=piv.index, x=-piv.get("Male", 0), name="Male", orientation="h",
                         marker_color=C.COLOR_ACCIDENTS,
                         hovertemplate="Male %{y}: %{customdata}<extra></extra>",
                         customdata=piv.get("Male", 0)))
    fig.add_trace(go.Bar(y=piv.index, x=piv.get("Female", 0), name="Female", orientation="h",
                         marker_color=C.COLOR_GRAVITY,
                         hovertemplate="Female %{y}: %{x}<extra></extra>"))
    fig.update_layout(barmode="relative", title="People killed by age band and sex",
                      xaxis_title="People killed (Male ◀ | ▶ Female)", yaxis_title="Age band")
    fig.update_xaxes(tickformat="~s")
    return _style(fig)


# --- V7: small multiples, gravity by condition -----------------------------
def conditions_facets(df: pd.DataFrame) -> go.Figure:
    g = df.groupby(["dimension", "modality"], observed=True).agg(
        accidents=("accidents", "sum"), fatal=("fatal", "sum")).reset_index()
    g["gravity_index"] = (g["fatal"] / g["accidents"].replace(0, pd.NA) * 100).round(2)
    fig = px.bar(g.sort_values("gravity_index"), x="gravity_index", y="modality",
                 facet_col="dimension", facet_col_wrap=2, orientation="h",
                 color_discrete_sequence=[C.COLOR_GRAVITY],
                 labels={"gravity_index": "Killed per 100 accidents", "modality": ""})
    fig.update_yaxes(matches=None)
    fig.update_xaxes(matches=None)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1], font_size=13))
    fig.update_layout(title="Severity (killed per 100 accidents) by condition", height=620,
                      showlegend=False)
    return _style(fig)


# --- V9: missingness heatmap ----------------------------------------------
def missingness_heatmap(df: pd.DataFrame) -> go.Figure:
    piv = df.pivot(index="variable", columns="year", values="missing_pct")
    fig = go.Figure(go.Heatmap(
        z=piv.values, x=[str(c) for c in piv.columns], y=list(piv.index),
        colorscale="OrRd", zmin=0, colorbar=dict(title="% missing"), xgap=1, ygap=1,
        hovertemplate="%{y} · %{x}: %{z:.1f}% missing<extra></extra>"))
    fig.update_layout(title="Missing values in key fields, by year",
                      xaxis_title="Year", yaxis_title=None, height=320)
    return _style(fig, source=False)
