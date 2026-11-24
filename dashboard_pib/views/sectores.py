"""Pestaña Sectores: estructura, treemap y detalle de actividades."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

import charts
import components as c
import model

MEDIDAS_SNAPSHOT = ["estructura_real", "var_real", "contribucion_real", "real"]


def _totales(tree: pd.DataFrame) -> dict[str, float]:
    """Cada padre vale al menos la suma de sus hijos (redondeo de INEGI)."""
    valores = tree["estructura_real"].to_dict()
    hijos: dict[str, list[str]] = {}
    for path, padre in tree["parent"].items():
        hijos.setdefault(padre, []).append(path)

    def total(path: str) -> float:
        return max(
            float(valores.get(path, 0.0)),
            sum(total(hijo) for hijo in hijos.get(path, [])),
        )

    return {path: total(path) for path in tree.index}


def render(filters: model.Filters) -> None:
    c.section("Estructura sectorial", "composición y desempeño de las actividades")
    est_anual = model.PIB[
        (model.PIB.medida == "estructura_real") & (model.PIB.periodo == "Anual")
    ]
    anios = sorted(est_anual.anio.unique(), reverse=True)
    c1, c2, c3 = st.columns([1, 2.2, 1.2])
    with c1:
        anio = st.selectbox("Año", options=anios, index=0)
    with c2:
        periodo = st.radio("Periodo", ["Anual", "T1", "T2", "T3", "T4"], horizontal=True)
    with c3:
        profundidad = st.selectbox(
            "Profundidad",
            ["Hasta ramas (2 dígitos)", "Hasta subsectores (3 dígitos)"],
        )
    max_nivel = 3 if profundidad.startswith("Hasta subsectores") else 2

    snap = model.PIB[
        (model.PIB.anio == anio)
        & (model.PIB.periodo == periodo)
        & (model.PIB.medida.isin(MEDIDAS_SNAPSHOT))
    ]
    if snap.empty:
        st.warning(f"No hay información para {anio} {periodo}.")
        return

    piv = snap.pivot_table(
        index="path", columns="medida", values="valor", aggfunc="first"
    )
    for col in MEDIDAS_SNAPSHOT:
        if col not in piv.columns:
            piv[col] = np.nan
    piv = piv.join(model.CAT.set_index("path")[["nombre", "nivel", "parent"]])

    tree = piv[
        piv.index.str.startswith("Valor agregado bruto")
        & (piv.nivel <= max_nivel)
        & (piv.nivel >= 1)
    ].copy()
    tree = tree[tree["estructura_real"].notna()]
    if tree.empty:
        st.warning("No hay estructura disponible para el periodo seleccionado.")
        return

    totals = _totales(tree)
    ids = list(tree.index)
    labels = [tree.loc[path, "nombre"] for path in ids]
    parents = [
        tree.loc[path, "parent"]
        if tree.loc[path, "parent"] not in ("", "Valor agregado bruto")
        else ""
        for path in ids
    ]

    col_a, col_b = st.columns([2.1, 1])
    with col_a:
        c.section(
            "Treemap de actividades",
            f"{anio} {periodo} · tamaño = estructura %, color = variación real anual",
        )
        c.plot(charts.treemap(tree, totals, ids, labels, parents))

    with col_b:
        c.section("Tres grandes actividades", f"{anio} {periodo} · % del PIB")
        rows = [
            (
                label,
                piv.loc[path, "estructura_real"] if path in piv.index else np.nan,
                color,
            )
            for path, label, color in model.ACTIVIDADES_PIE
        ]
        rows = [r for r in rows if pd.notna(r[1])]
        c.plot(
            charts.pie(
                rows,
                hole=0.55,
                height=250,
                legend=dict(orientation="h", y=-0.05, font=dict(size=10)),
                margin=dict(t=6, b=6, l=6, r=6),
            )
        )

        c.section("Top ramas", "por participación en el PIB")
        top = piv[(piv.nivel == 2) & piv["estructura_real"].notna()].nlargest(
            8, "estructura_real"
        )
        c.plot(charts.top_bars(top))

    c.section(
        "Detalle de actividades", f"{anio} · estructura, crecimiento y contribución"
    )
    tbl = piv[piv.nivel <= 2].copy()
    tbl = tbl.dropna(subset=["estructura_real"]).sort_values(
        "estructura_real", ascending=False
    )
    out = pd.DataFrame(
        {
            "Actividad": [
                "    " * int(n) + nm for n, nm in zip(tbl.nivel, tbl.nombre)
            ],
            "Estructura %": tbl["estructura_real"].values,
            "Var. real anual %": tbl["var_real"].values,
            "Contribución pp": tbl["contribucion_real"].values,
            "Nivel real (b)": tbl["real"].values / 1e6,
        }
    )
    c.table(
        out,
        height=420,
        column_config={
            "Estructura %": st.column_config.NumberColumn(format="%.2f"),
            "Var. real anual %": st.column_config.NumberColumn(format="%.2f"),
            "Contribución pp": st.column_config.NumberColumn(format="%+.2f"),
            "Nivel real (b)": st.column_config.NumberColumn(format="%.2f"),
        },
    )
