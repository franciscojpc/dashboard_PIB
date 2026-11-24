"""Tema visual del tablero: paleta oscura, plantilla Plotly y estilos Streamlit."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

BG = "#060A11"
PANEL = "#0C1422"
PANEL_2 = "#101B2D"
BORDER = "#1B2940"
TEXT = "#E8EFF9"
MUTED = "#7E90AA"
GRID = "#16223A"
ACCENT = "#38BDF8"
POS = "#34D399"
NEG = "#FB7185"
SECTOR = {"primarias": "#34D399", "secundarias": "#38BDF8", "terciarias": "#A78BFA"}
ACCENTS = [
    "#38BDF8",
    "#F59E0B",
    "#A78BFA",
    "#34D399",
    "#FB7185",
    "#22D3EE",
    "#F472B6",
    "#FACC15",
    "#4ADE80",
    "#818CF8",
    "#F97316",
    "#2DD4BF",
]

FONT_STACK = (
    "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
    "Helvetica, Arial, sans-serif"
)

_TEMPLATE = go.layout.Template(
    layout=dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_STACK, color=TEXT, size=12),
        colorway=ACCENTS,
        xaxis=dict(
            gridcolor=GRID,
            zerolinecolor=BORDER,
            linecolor=BORDER,
            tickcolor=BORDER,
            ticks="outside",
            ticklen=3,
            showgrid=False,
            showline=True,
            title=dict(font=dict(color=MUTED, size=11)),
        ),
        yaxis=dict(
            gridcolor=GRID,
            zerolinecolor=BORDER,
            linecolor=BORDER,
            ticks="outside",
            ticklen=3,
            showgrid=True,
            gridwidth=1,
            title=dict(font=dict(color=MUTED, size=11)),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0,
            font=dict(color=MUTED, size=11),
        ),
        margin=dict(l=12, r=12, t=48, b=12),
        hoverlabel=dict(
            bgcolor=PANEL_2,
            bordercolor=BORDER,
            font=dict(color=TEXT, size=12, family=FONT_STACK),
        ),
        hovermode="x unified",
        separators=".,",
    )
)
pio.templates["pib"] = _TEMPLATE
pio.templates.default = "pib"

PLOTLY_CONFIG = {
    "displayModeBar": False,
    "scrollZoom": False,
    "responsive": True,
}


def new_fig(height: int = 380, **layout) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(template="pib", height=height, **layout)
    return fig


def finish(fig: go.Figure, title: str | None = None, subtitle: str | None = None) -> go.Figure:
    """Título alineado a la izquierda con subtítulo opcional."""
    annotations = []
    if title:
        annotations.append(
            dict(
                text=f"<b>{title}</b>",
                x=0,
                y=1.16,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14, color=TEXT),
                xanchor="left",
            )
        )
    if subtitle:
        annotations.append(
            dict(
                text=subtitle,
                x=0,
                y=1.06,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=11, color=MUTED),
                xanchor="left",
            )
        )
    fig.update_layout(annotations=annotations, margin=dict(t=70 if subtitle else 56))
    return fig


def style_axes(fig: go.Figure, ytitle: str | None = None, xtitle: str | None = None) -> go.Figure:
    fig.update_xaxes(title_text=xtitle, showline=True)
    fig.update_yaxes(title_text=ytitle)
    return fig


def inject_css() -> None:
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {{
  --bg: {BG};
  --panel: {PANEL};
  --panel-2: {PANEL_2};
  --border: {BORDER};
  --text: {TEXT};
  --muted: {MUTED};
  --accent: {ACCENT};
  --pos: {POS};
  --neg: {NEG};
}}

html, body, [class*="css"] {{ font-family: {FONT_STACK}; }}

.stApp {{
  background:
    radial-gradient(1100px 520px at 8% -12%, rgba(56,189,248,.10), transparent 60%),
    radial-gradient(900px 480px at 92% -8%, rgba(167,139,250,.07), transparent 60%),
    {BG};
  color: {TEXT};
}}

header[data-testid="stHeader"] {{ background: transparent; }}
#MainMenu, footer {{ visibility: hidden; }}

.block-container {{ padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1480px; }}

[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, #0A1120 0%, #070C15 100%);
  border-right: 1px solid {BORDER};
}}
[data-testid="stSidebar"] .block-container {{ padding-top: 1.6rem; }}
[data-testid="stSidebar"] * {{ color: {TEXT}; }}

/* ---------- Hero ---------- */
.hero {{
  position: relative;
  border: 1px solid {BORDER};
  border-radius: 18px;
  padding: 22px 26px 20px;
  margin-bottom: 16px;
  overflow: hidden;
  background:
    linear-gradient(120deg, rgba(56,189,248,.10) 0%, rgba(167,139,250,.05) 38%, rgba(12,20,34,.55) 100%);
}}
.hero:before {{
  content: ""; position: absolute; inset: 0 auto 0 0; width: 4px;
  background: linear-gradient(180deg, {ACCENT}, #A78BFA);
}}
.hero .kicker {{
  color: {ACCENT}; font-size: .71rem; font-weight: 700;
  letter-spacing: .18em; text-transform: uppercase;
}}
.hero h1 {{
  margin: 6px 0 6px; font-size: 1.95rem; font-weight: 800;
  letter-spacing: -.02em; color: #F4F8FE; line-height: 1.15;
}}
.hero p {{ margin: 0; color: #93A6C0; font-size: .9rem; max-width: 980px; }}
.chips {{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px; }}
.chip {{
  border: 1px solid #22334F; background: rgba(16,27,45,.75);
  color: #9FB2CA; font-size: .71rem; font-weight: 600;
  padding: 4px 10px; border-radius: 999px; letter-spacing: .02em;
}}
.chip.live {{ color: {POS}; border-color: rgba(52,211,153,.35); }}
.chip.live:before {{
  content: ""; display: inline-block; width: 6px; height: 6px; border-radius: 50%;
  background: {POS}; margin-right: 6px; vertical-align: 1px;
}}

/* ---------- KPI cards ---------- */
.kpi {{
  border: 1px solid {BORDER}; border-radius: 14px; padding: 14px 16px 12px;
  background: linear-gradient(180deg, rgba(16,27,45,.9), rgba(10,17,29,.9));
  height: 100%;
}}
.kpi .label {{
  font-size: .68rem; font-weight: 700; letter-spacing: .12em;
  text-transform: uppercase; color: {MUTED};
}}
.kpi .value {{
  margin: 7px 0 3px; font-size: 1.8rem; font-weight: 700;
  letter-spacing: -.02em; color: #F4F8FE; line-height: 1.08;
  font-variant-numeric: tabular-nums;
}}
.kpi .value .unit {{ font-size: .78rem; font-weight: 500; color: #8FA2BC; margin-left: 4px; }}
.kpi .sub {{ font-size: .77rem; color: #8FA2BC; font-variant-numeric: tabular-nums; }}
.kpi .sub .up {{ color: {POS}; font-weight: 600; }}
.kpi .sub .down {{ color: {NEG}; font-weight: 600; }}

/* ---------- Section heading ---------- */
.sec {{ display: flex; align-items: center; gap: 10px; margin: 6px 0 10px; }}
.sec .bar {{ width: 3px; height: 17px; border-radius: 2px; background: {ACCENT}; }}
.sec h3 {{ margin: 0; font-size: .98rem; font-weight: 700; color: {TEXT}; letter-spacing: .01em; }}
.sec .hint {{ margin-left: auto; color: #6E8099; font-size: .76rem; }}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] {{
  gap: 4px; background: rgba(12,20,34,.7); padding: 5px;
  border-radius: 12px; border: 1px solid {BORDER};
}}
.stTabs [data-baseweb="tab"] {{
  height: 36px; border-radius: 8px; padding: 0 16px;
  color: #8FA2BC; font-weight: 600; font-size: .84rem;
}}
.stTabs [aria-selected="true"] {{
  background: linear-gradient(180deg, rgba(56,189,248,.20), rgba(56,189,248,.08));
  color: #E9F7FF !important;
  border: 1px solid rgba(56,189,248,.38) !important;
}}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {{ display: none; }}

/* ---------- Widgets ---------- */
[data-baseweb="select"] > div {{
  background: {PANEL} !important; border-color: #22334F !important; border-radius: 9px !important;
}}
[data-baseweb="select"] svg {{ color: {MUTED}; }}
.stSlider [data-baseweb="slider"] div[role="slider"] {{ background: {ACCENT}; }}
.stRadio [role="radiogroup"] {{ gap: .25rem; }}
[data-testid="stExpander"] details {{
  background: rgba(12,20,34,.55); border: 1px solid {BORDER}; border-radius: 12px;
}}
[data-testid="stDataFrame"] {{ border: 1px solid {BORDER}; border-radius: 12px; }}
hr {{ border-color: {BORDER}; }}
.stDownloadButton button, .stButton button {{
  background: {PANEL_2}; border: 1px solid #22334F; color: #DCE7F5;
  border-radius: 9px; font-weight: 600;
}}
.stDownloadButton button:hover, .stButton button:hover {{
  border-color: {ACCENT}; color: #FFFFFF;
}}
[data-testid="stAlert"] {{ border-radius: 12px; }}
</style>
""",
        unsafe_allow_html=True,
    )


def mpl_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": BG,
            "axes.facecolor": PANEL,
            "savefig.facecolor": BG,
            "axes.edgecolor": BORDER,
            "axes.labelcolor": MUTED,
            "axes.titlecolor": TEXT,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "text.color": TEXT,
            "font.family": "sans-serif",
            "font.size": 10,
            "axes.grid": False,
        }
    )


def heatmap_cmap(positive_cyan: bool = True):
    """Colormap divergente oscuro: rojo/ámbar para negativo, cian para positivo."""
    from matplotlib.colors import LinearSegmentedColormap

    colors = (
        ["#FB7185", "#5B2434", PANEL, "#0B4E67", "#38BDF8"]
        if positive_cyan
        else ["#F59E0B", "#5A3A12", PANEL, "#1E3A8A", "#818CF8"]
    )
    return LinearSegmentedColormap.from_list("pib_div", colors)

