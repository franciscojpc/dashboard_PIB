"""Constructores de figuras (Plotly y Matplotlib). Sin Streamlit."""

from __future__ import annotations

import html

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
from plotly.subplots import make_subplots

import theme
from pib_data import TRIMESTRES

TRIM = tuple(TRIMESTRES)
ACCENT, MUTED, POS, NEG = theme.ACCENT, theme.MUTED, theme.POS, theme.NEG


def rgba(color: str, alpha: float) -> str:
    return (
        f"rgba({int(color[1:3], 16)},{int(color[3:5], 16)},"
        f"{int(color[5:7], 16)},{alpha})"
    )


def sparkline(df: pd.DataFrame, color: str, height: int = 96) -> go.Figure:
    fig = go.Figure(
        go.Scatter(
            x=df["fecha"],
            y=df["valor"],
            mode="lines",
            line=dict(color=color, width=2),
            fill="tozeroy",
            fillcolor=rgba(color, 0.12),
            hovertemplate="%{x|%Y} · %{y:,.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=4, b=0),
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        hovermode="x",
    )
    return fig


def heatmap_yoy(var_real: pd.DataFrame, anios: int = 14) -> plt.Figure:
    df = var_real[var_real.periodo.isin(TRIM)].copy()
    years = sorted(df.anio.unique())[-anios:]
    piv = (
        df[df.anio.isin(years)]
        .pivot_table(index="anio", columns="periodo", values="valor", aggfunc="first")
        .reindex(columns=list(TRIM))
        .dropna(how="any")
    )
    cmap = theme.heatmap_cmap()
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    sns.heatmap(
        piv,
        ax=ax,
        cmap=cmap,
        center=0,
        annot=True,
        fmt=".1f",
        annot_kws={"fontsize": 7.5, "fontweight": "600"},
        linewidths=2,
        linecolor=theme.BG,
        cbar_kws={"shrink": 0.7, "pad": 0.02},
        xticklabels=list(TRIM),
        yticklabels=[int(y) for y in piv.index],
    )
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(colors=MUTED, labelsize=8.5)
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(colors=MUTED, labelsize=8)
    cbar.outline.set_edgecolor(theme.BORDER)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    return fig


def pie(
    rows: list[tuple[str, float, str]],
    hole: float,
    height: int,
    center: str | None = None,
    legend: dict | None = None,
    margin: dict | None = None,
) -> go.Figure:
    fig = go.Figure(
        go.Pie(
            labels=[r[0] for r in rows],
            values=[r[1] for r in rows],
            hole=hole,
            marker=dict(
                colors=[r[2] for r in rows],
                line=dict(color=theme.BG, width=2),
            ),
            textinfo="none",
            hovertemplate="%{label} · %{value:.1f}%<extra></extra>",
            sort=False,
        )
    )
    if center:
        fig.add_annotation(
            text=center, x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color=theme.TEXT),
        )
    fig.update_layout(
        height=height,
        showlegend=True,
        legend=legend
        or dict(orientation="v", x=1.02, y=0.5, font=dict(size=10)),
        margin=margin or dict(t=10, b=10, l=10, r=10),
    )
    return fig


def level_with_yoy(
    df: pd.DataFrame,
    name: str,
    color: str,
    fill_color: str,
    height: int,
    bargap: float,
    hover_fecha: str,
    line_width: float = 2.2,
    bar_opacity: float = 0.45,
    margin: dict | None = None,
) -> go.Figure:
    """Nivel en línea (billones) + variación anual en barras."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=df.fecha,
            y=df.valor,
            name=name,
            mode="lines",
            line=dict(color=color, width=line_width),
            fill="tozeroy",
            fillcolor=fill_color,
            hovertemplate="%{x|" + hover_fecha + "} · %{y:,.2f} b<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(
            x=df.fecha,
            y=df.yoy,
            name="Var. anual %",
            marker_color=[POS if v >= 0 else NEG for v in df.yoy],
            marker_line_width=0,
            opacity=bar_opacity,
            hovertemplate="%{x|" + hover_fecha + "} · %{y:,.2f}%<extra></extra>",
        ),
        secondary_y=True,
    )
    fig.update_yaxes(title_text="billones de pesos", secondary_y=False)
    fig.update_yaxes(title_text="var. anual %", secondary_y=True, showgrid=False)
    layout = dict(height=height, bargap=bargap)
    if margin is not None:
        layout["margin"] = margin
    fig.update_layout(**layout)
    return fig


def explorer_series(
    df: pd.DataFrame,
    name: str,
    kind: str,
    show_yoy: bool,
    ylabel: str,
    log: bool = False,
    compare: pd.DataFrame | None = None,
) -> go.Figure:
    """Serie principal del explorador, con barras o línea según la métrica."""
    plot_df = df
    fig = make_subplots(specs=[[{"secondary_y": show_yoy}]])

    if kind in ("variacion", "contribucion"):
        fig.add_trace(
            go.Bar(
                x=plot_df.fecha,
                y=plot_df.valor,
                name=name,
                marker_color=[POS if v >= 0 else NEG for v in plot_df.valor],
                marker_line_width=0,
                hovertemplate="%{x|%Y %b} · %{y:,.2f}<extra></extra>",
            ),
            secondary_y=False,
        )
        fig.add_hline(y=0, line_color=theme.BORDER, line_width=1)
    else:
        fig.add_trace(
            go.Scatter(
                x=plot_df.fecha,
                y=plot_df.valor,
                name=name,
                mode="lines",
                line=dict(color=ACCENT, width=2.4),
                fill="tozeroy",
                fillcolor="rgba(56,189,248,0.08)",
                hovertemplate="%{x|%Y %b} · %{y:,.2f}<extra></extra>",
            ),
            secondary_y=False,
        )

    if compare is not None:
        fig.add_trace(
            go.Scatter(
                x=compare.fecha,
                y=compare.valor,
                name="PIB total",
                mode="lines",
                line=dict(color=MUTED, width=1.6, dash="dot"),
                hovertemplate="PIB · %{y:,.2f}<extra></extra>",
            ),
            secondary_y=False,
        )

    if show_yoy:
        fig.add_trace(
            go.Bar(
                x=plot_df.fecha,
                y=plot_df.yoy,
                name="Var. anual %",
                marker_color=[POS if v >= 0 else NEG for v in plot_df.yoy],
                marker_line_width=0,
                opacity=0.35,
                hovertemplate="%{x|%Y %b} · %{y:,.2f}%<extra></extra>",
            ),
            secondary_y=True,
        )
        fig.update_yaxes(title_text="var. anual %", secondary_y=True, showgrid=False)

    fig.update_yaxes(title_text=ylabel, secondary_y=False)
    if log and kind == "nivel":
        fig.update_yaxes(type="log")
    fig.update_layout(height=460, bargap=0.22)
    return fig


def histogram(values: pd.Series, mean: float, unidad: str, height: int = 250) -> go.Figure:
    fig = go.Figure(
        go.Histogram(
            x=values,
            nbinsx=28,
            marker=dict(color=ACCENT, opacity=0.75, line=dict(color=theme.BG, width=1)),
            hovertemplate="%{x:,.2f} · %{y}<extra></extra>",
        )
    )
    fig.add_vline(x=mean, line_color=POS, line_dash="dash", line_width=1.4)
    fig.add_annotation(
        x=mean, y=1, yref="paper", yanchor="bottom",
        text="media", showarrow=False, font=dict(color=POS, size=10),
    )
    fig.update_layout(
        height=height, bargap=0.05, margin=dict(t=24),
        xaxis=dict(title=("billones de pesos" if unidad == "mdp" else None)),
    )
    return fig


def comparison_lines(
    series_map: dict[str, pd.DataFrame],
    use_index: bool,
    unidad: str,
    short: dict[str, str],
    ylabel: str | None = None,
    zero_line: bool = False,
) -> go.Figure:
    fig = go.Figure()
    for i, (p, df) in enumerate(series_map.items()):
        df = df.copy()
        if use_index:
            base_rows = df[df.anio == 2018]
            base = base_rows.valor.mean() if len(base_rows) else df.valor.iloc[0]
            df["y"] = df.valor / base * 100
        else:
            df["y"] = df.valor / 1e6 if unidad == "mdp" else df.valor
        nombre = short.get(p, p)
        fig.add_trace(
            go.Scatter(
                x=df.fecha,
                y=df.y,
                name=nombre[:38],
                mode="lines",
                line=dict(color=theme.ACCENTS[i % len(theme.ACCENTS)], width=2),
                hovertemplate=(
                    "%{x|%Y %b} · %{y:,.1f}<extra>" + html.escape(nombre) + "</extra>"
                ),
            )
        )
    etiqueta = (
        "índice (2018 = 100)"
        if use_index
        else ylabel or ("billones de pesos" if unidad == "mdp" else "variación %")
    )
    fig.update_yaxes(title_text=etiqueta)
    if zero_line:
        fig.add_hline(y=0, line_color=theme.BORDER, line_width=1)
    fig.update_layout(height=440, margin=dict(t=30))
    return fig


def ranking_bar(rank: pd.DataFrame, unidad: str, fmt_num) -> go.Figure:
    scaled = rank.valor / 1e6 if unidad == "mdp" else rank.valor
    fig = go.Figure(
        go.Bar(
            x=scaled,
            y=rank.Indicador,
            orientation="h",
            marker_color=[POS if v >= 0 else NEG for v in rank.valor],
            marker_line_width=0,
            text=[fmt_num(v, unidad, 1) for v in rank.valor],
            textposition="outside",
            textfont=dict(color=MUTED, size=10),
            hovertemplate="%{y} · %{x:,.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        height=max(280, 44 * len(rank) + 80), margin=dict(t=20, r=90)
    )
    return fig


def correlation_heatmap(mat: pd.DataFrame) -> plt.Figure:
    corr = mat.corr()
    cmap = sns.diverging_palette(10, 190, s=90, l=45, as_cmap=True)
    altura = max(3.4, 0.55 * len(corr) + 1.6)
    fig, ax = plt.subplots(figsize=(5.6, altura))
    sns.heatmap(
        corr, annot=True, fmt=".2f", cmap=cmap, center=0, vmin=-1, vmax=1,
        square=True, linewidths=2, linecolor=theme.BG,
        annot_kws={"fontsize": 9},
        cbar_kws={"shrink": 0.7},
        ax=ax,
    )
    ax.tick_params(colors=MUTED, labelsize=8)
    for spine in ax.spines.values():
        spine.set_visible(False)
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(colors=MUTED, labelsize=8)
    cbar.outline.set_edgecolor(theme.BORDER)
    fig.tight_layout()
    return fig


def treemap(
    tree: pd.DataFrame,
    totals: dict[str, float],
    ids: list[str],
    labels: list[str],
    parents: list[str],
    values_min: float = -8,
    values_max: float = 8,
) -> go.Figure:
    var = tree["var_real"].fillna(0)
    fig = go.Figure(
        go.Treemap(
            ids=ids,
            labels=labels,
            parents=parents,
            values=[totals[p] for p in ids],
            branchvalues="total",
            customdata=[
                [tree.loc[p, "estructura_real"], tree.loc[p, "var_real"]] for p in ids
            ],
            texttemplate="<b>%{label}</b><br>%{customdata[0]:.1f}% · %{customdata[1]:+.1f}%",
            textfont=dict(size=11, color="#F4F8FE"),
            marker=dict(
                colors=[var.get(p, 0) for p in ids],
                colorscale=[
                    [0.0, "#B45309"],
                    [0.35, "#5B3A12"],
                    [0.5, "#1A2740"],
                    [0.65, "#0B4A5E"],
                    [1.0, "#38BDF8"],
                ],
                cmid=0,
                cmin=values_min,
                cmax=values_max,
                line=dict(color=theme.BG, width=2),
                showscale=False,
            ),
            hovertemplate=(
                "<b>%{label}</b><br>estructura: %{customdata[0]:.2f}%"
                "<br>var. real anual: %{customdata[1]:+.2f}%<extra></extra>"
            ),
            root_color=theme.PANEL,
            tiling=dict(pad=2),
        )
    )
    fig.update_layout(height=520, margin=dict(t=10, l=0, r=0, b=0))
    return fig


def top_bars(top: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=top["estructura_real"],
            y=[n[:34] for n in top.nombre],
            orientation="h",
            marker_color=[ACCENT] * len(top),
            marker_line_width=0,
            text=[f"{v:.1f}%" for v in top["estructura_real"]],
            textposition="outside",
            textfont=dict(color=MUTED, size=9),
            hovertemplate="%{y} · %{x:.2f}%<extra></extra>",
        )
    )
    fig.update_layout(height=300, margin=dict(t=10, r=40), xaxis=dict(showgrid=True))
    return fig


def series_lines(wide: pd.DataFrame, unidad: str) -> go.Figure:
    fig = go.Figure()
    for i, (name, s) in enumerate(wide.items()):
        y = s / 1e6 if unidad == "mdp" else s
        fig.add_trace(
            go.Scatter(
                x=s.index, y=y, mode="lines", name=name[:24],
                line=dict(color=theme.ACCENTS[i % len(theme.ACCENTS)], width=1.8),
                hovertemplate="%{x|%Y %b} · %{y:,.2f}<extra></extra>",
            )
        )
    fig.update_layout(height=330, margin=dict(t=16, r=8), showlegend=True)
    return fig
