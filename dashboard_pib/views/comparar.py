"""Pestaña Comparar: varias actividades bajo una misma métrica."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

import charts
import components as c
import formatting as f
import model



def render(filters: model.Filters) -> None:
    c.section("Comparador de indicadores", "Varias actividades, una métrica común")
    incluir_sub = st.toggle(
        "Incluir ramas y subsectores (nivel 2 y 3)", value=False
    )
    max_nivel = 3 if incluir_sub else 1
    opts = model.CAT[model.CAT.nivel <= max_nivel]

    c1, c2, c3 = st.columns([3.2, 1.6, 1.1])
    with c1:
        seleccion = st.multiselect(
            "Indicadores",
            options=list(opts.path),
            default=model.default_paths(),
            format_func=lambda p: model.DISP.get(p, p),
        )
    with c2:
        medida = st.selectbox(
            "Métrica",
            options=[m[0] for m in model.METRICAS if m[0] != "estructura_nominal"],
            format_func=lambda m: model.METRICA_LABEL[m],
            index=0,
            key="cmp_medida",
        )
    with c3:
        if model.kind(medida) in ("nivel", "indice"):
            modo = st.radio(
                "Vista", ["Índice", "Valores"], index=0, horizontal=False,
                key="cmp_modo",
            )
        else:
            modo = "Valores"
            st.caption("Vista: valores de la métrica")

    if not seleccion:
        st.info("Selecciona al menos un indicador.")
        return

    unidad = model.unidad(medida)
    kind = model.kind(medida)

    series = {}
    for path in seleccion:
        df = model.series(
            medida, path, filters.frecuencia, filters.anio_min,
            filters.anio_max, filters.prelim,
        )
        if not df.empty:
            series[path] = df

    if not series:
        st.warning("Sin datos para la selección.")
        return

    use_index = modo == "Índice" and kind in ("nivel", "indice")
    ylabel = (
        "billones de pesos"
        if (unidad == "mdp" and not use_index)
        else model.META[medida]["short"]
    )
    c.plot(
        charts.comparison_lines(
            series,
            use_index,
            unidad,
            model.SHORT,
            ylabel,
            zero_line=kind in ("variacion", "contribucion"),
        )
    )

    col_a, col_b = st.columns([1, 1])
    with col_a:
        c.section("Ranking del último periodo", "ordenado de mayor a menor")
        rows = []
        for path, df in series.items():
            last = model.last_row(df)
            if last is None:
                continue
            rows.append(
                {
                    "Indicador": model.SHORT.get(path, path),
                    "valor": last.valor,
                    "periodo": f"{int(last.anio)} {last.periodo}",
                }
            )
        rank = pd.DataFrame(rows).sort_values("valor", ascending=True)
        c.plot(charts.ranking_bar(rank, unidad, f.fmt_num))

    with col_b:
        c.section("Correlación de crecimientos", "var. real anual de cada indicador")
        yoy_data = {}
        for path in series:
            anual = model.series_yoy(
                "real", path, "A", filters.anio_min, filters.anio_max,
                filters.prelim,
            )
            if not anual.empty:
                yoy_data[model.SHORT.get(path, path)[:28]] = anual.set_index(
                    "anio"
                ).yoy
        if len(yoy_data) >= 2:
            mat = pd.DataFrame(yoy_data).dropna()
            if len(mat) >= 3:
                fig = charts.correlation_heatmap(mat)
                c.pyplot(fig)
                plt.close(fig)
            else:
                st.info("Se necesitan al menos 3 años en común.")
        else:
            st.info("Selecciona al menos dos indicadores con serie anual.")

    c.section("Estadística descriptiva", "sobre la métrica y frecuencia elegidas")
    rows = []
    for path, df in series.items():
        est = model.resumen_estadistico(df.valor)
        if est["n"] == 0:
            continue
        cagr = model.cagr_anual(df.valor, filters.periodos_por_anio)
        rows.append(
            {
                "Indicador": model.SHORT.get(path, path),
                "n": est["n"],
                "Media": est["media"],
                "Mediana": est["mediana"],
                "Desv. est.": est["desv"],
                "Mínimo": est["minimo"],
                "Máximo": est["maximo"],
                "CAGR %": cagr,
                "Último": est["ultimo"],
            }
        )
    if rows:
        c.table(
            pd.DataFrame(rows),
            column_config={
                "n": st.column_config.NumberColumn(format="%d"),
                **c.num_cols(
                    ["Media", "Mediana", "Desv. est.", "Mínimo", "Máximo",
                     "CAGR %", "Último"]
                ),
            },
        )
