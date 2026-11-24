"""Componentes de interfaz reutilizables (envoltorios delgados de Streamlit)."""

from __future__ import annotations

import html

import pandas as pd
import streamlit as st

import theme


def kpi(label: str, value: str, unit: str = "", sub: str = "") -> None:
    st.markdown(
        f"""<div class="kpi">
            <div class="label">{html.escape(label)}</div>
            <div class="value">{value}<span class="unit">{unit}</span></div>
            <div class="sub">{sub}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def section(title: str, hint: str = "") -> None:
    st.markdown(
        f'<div class="sec"><span class="bar"></span><h3>{html.escape(title)}</h3>'
        f'<span class="hint">{html.escape(hint)}</span></div>',
        unsafe_allow_html=True,
    )


def plot(fig, **kwargs) -> None:
    st.plotly_chart(fig, width="stretch", config=theme.PLOTLY_CONFIG, **kwargs)


def pyplot(fig) -> None:
    st.pyplot(fig, width="stretch")


def table(df: pd.DataFrame, **kwargs) -> None:
    kwargs.setdefault("hide_index", True)
    kwargs.setdefault("width", "stretch")
    st.dataframe(df, **kwargs)


def num_cols(names, fmt: str = "%.2f") -> dict:
    return {name: st.column_config.NumberColumn(format=fmt) for name in names}
