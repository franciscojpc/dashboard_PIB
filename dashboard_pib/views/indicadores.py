"""Pestaña Indicadores: explorador de una actividad y una métrica."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

import charts
import components as c
import formatting as f
import model

PIB_PATH = "Producto interno bruto"


def render(filters: model.Filters) -> None:
    c.section("Explorador de indicadores", "Elige una actividad y una métrica")
    c1, c2, c3, c4 = st.columns([2.6, 1.9, 1, 1])
    with c1:
        path = st.selectbox(
            "Indicador económico",
            options=list(model.CAT.path),
            index=list(model.CAT.path).index(PIB_PATH),
            format_func=lambda p: model.DISP.get(p, p),
        )
    with c2:
        medida = st.selectbox(
            "Métrica",
            options=[m[0] for m in model.METRICAS],
            format_func=lambda m: model.METRICA_LABEL[m],
            index=0,
        )
    with c3:
        log = st.toggle(
            "Escala log", value=False, disabled=model.kind(medida) != "nivel"
        )
    with c4:
        compare = st.toggle("Comparar con PIB", value=False)

    unidad = model.unidad(medida)
    kind = model.kind(medida)

    df = model.series(
        medida, path, filters.frecuencia, filters.anio_min,
        filters.anio_max, filters.prelim,
    )
    if df.empty:
        st.warning("No hay datos para esta combinación de filtros.")
        return

    show_yoy = kind == "nivel" and medida != "deflactor"
    df = (
        model.add_yoy(df, filters.frecuencia)
        if show_yoy
        else df.assign(yoy=np.nan)
    )

    divisor, ylabel = model.escala(unidad)
    plot_df = df.assign(valor=df.valor / divisor)

    compare_df = None
    if compare and path != PIB_PATH:
        compare_df = model.series_yoy(
            medida, PIB_PATH, filters.frecuencia, filters.anio_min,
            filters.anio_max, filters.prelim,
        )
        compare_df = compare_df.assign(valor=compare_df.valor / divisor)

    c.plot(
        charts.explorer_series(
            plot_df,
            model.SHORT.get(path, path),
            kind,
            show_yoy,
            ylabel,
            log=log,
            compare=compare_df,
        )
    )

    valores = df.valor.dropna()
    last = model.last_row(df)
    yoy_last = df.yoy.dropna().iloc[-1] if df.yoy.notna().any() else np.nan
    cagr = (
        model.cagr_anual(valores, filters.periodos_por_anio)
        if kind == "nivel"
        else np.nan
    )
    imax, imin = valores.idxmax(), valores.idxmin()
    max_row = df.loc[imax]
    min_row = df.loc[imin]

    k1, k2, k3, k4, k5 = st.columns(5)
    v, u = f.fmt_value(last["valor"], unidad)
    with k1:
        c.kpi("Último valor", v, u, model.row_label(last))
    with k2:
        if kind == "nivel":
            c.kpi(
                "Variación anual",
                f"{yoy_last:,.2f}" if pd.notna(yoy_last) else "—",
                "%" if pd.notna(yoy_last) else "",
                "vs. mismo periodo del año anterior",
            )
        else:
            c.kpi(
                "Desviación estándar", f.fmt_num(valores.std(), unidad), "",
                f"{len(valores):,} observaciones",
            )
    with k3:
        c.kpi(
            "Promedio", f.fmt_num(valores.mean(), unidad), "",
            f"{len(valores):,} observaciones",
        )
    with k4:
        c.kpi(
            "Máximo", f.fmt_num(valores.loc[imax], unidad), "",
            f"{int(max_row.anio)} {max_row.periodo}",
        )
    with k5:
        c.kpi(
            "Mínimo", f.fmt_num(valores.loc[imin], unidad), "",
            f"{int(min_row.anio)} {min_row.periodo}",
        )

    col_a, col_b = st.columns([1.35, 1])
    with col_a:
        c.section(
            "Últimas observaciones", "valor, variación anual e índice base 2018"
        )
        tbl = df.dropna(subset=["valor"]).tail(14).copy()
        base = (
            df[df.anio == 2018].valor.mean() if (df.anio == 2018).any() else np.nan
        )
        tbl["indice"] = tbl.valor / base * 100 if base and base > 0 else np.nan
        valor_col = "Valor (b)" if unidad == "mdp" else "Valor"
        cols = {
            "Periodo": [f"{int(r.anio)} {r.periodo}" for _, r in tbl.iterrows()],
            valor_col: tbl.valor.values / divisor,
        }
        config = {
            valor_col: st.column_config.NumberColumn(
                format="%+.2f" if unidad == "pp" else "%.2f"
            )
        }
        if show_yoy:
            cols["Var. anual %"] = tbl.yoy.values
            config["Var. anual %"] = st.column_config.NumberColumn(format="%.2f")
        if kind in ("nivel", "indice"):
            cols["Índice 2018"] = tbl.indice.values
            config["Índice 2018"] = st.column_config.NumberColumn(format="%.1f")
        c.table(pd.DataFrame(cols), height=420, column_config=config)

    with col_b:
        c.section("Distribución", "histograma del periodo seleccionado")
        c.plot(
            charts.histogram(
                df.valor / divisor, valores.mean() / divisor, unidad
            )
        )
        desc = pd.DataFrame(
            {
                "estadístico": [
                    "n", "media", "mediana", "desv. estándar",
                    "mínimo", "máximo", "CAGR anual",
                ],
                "valor": [
                    f"{len(valores):,}",
                    f.fmt_num(valores.mean(), unidad),
                    f.fmt_num(valores.median(), unidad),
                    f.fmt_num(valores.std(), unidad),
                    f.fmt_num(valores.min(), unidad),
                    f.fmt_num(valores.max(), unidad),
                    f"{cagr:,.2f}%" if pd.notna(cagr) else "—",
                ],
            }
        )
        c.table(desc, height=220)
