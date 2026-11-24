"""Formateo numérico del tablero (sin Streamlit)."""

from __future__ import annotations

import pandas as pd


def fmt_mdp(v: float) -> tuple[str, str]:
    if pd.isna(v):
        return "—", ""
    if abs(v) >= 1e6:
        return f"{v / 1e6:,.2f}", "billones"
    if abs(v) >= 1e3:
        return f"{v / 1e3:,.1f}", "mdp"
    return f"{v:,.1f}", "mdp"


def fmt_value(v: float, unidad: str) -> tuple[str, str]:
    if v is None or pd.isna(v):
        return "—", ""
    if unidad == "mdp":
        return fmt_mdp(v)
    if unidad == "%":
        return f"{v:,.2f}", "%"
    if unidad == "pp":
        return f"{v:+,.2f}", "pp"
    if unidad == "indice":
        return f"{v:,.1f}", ""
    return f"{v:,.2f}", ""


def fmt_num(v: float, unidad: str, decimals: int = 2) -> str:
    if v is None or pd.isna(v):
        return "—"
    if unidad == "mdp":
        if abs(v) >= 1e6:
            return f"{v / 1e6:,.{decimals}f} b"
        return f"{v / 1e3:,.{decimals}f} m"
    if unidad == "%":
        return f"{v:,.{decimals}f}%"
    if unidad == "pp":
        return f"{v:+,.{decimals}f} pp"
    return f"{v:,.{decimals}f}"


def delta_html(v: float, unidad: str = "%", label: str = "") -> str:
    if v is None or pd.isna(v):
        return label
    arrow = "▲" if v > 0 else "▼" if v < 0 else "•"
    cls = "up" if v > 0 else "down" if v < 0 else ""
    return f'<span class="{cls}">{arrow} {abs(v):,.2f}{unidad}</span> {label}'
