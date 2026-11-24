"""Pestaña Datos: series completas, descriptivos y descarga CSV."""

from __future__ import annotations

import pandas as pd
import streamlit as st

import charts
import components as c
import model



def render(filters: model.Filters) -> None:
    c.section("Descarga y análisis", "series completas y estadística descriptiva")
    c1, c2 = st.columns([2.4, 1.6])
    with c1:
        seleccion = st.multiselect(
            "Indicadores",
            options=list(model.CAT.path),
            default=model.default_paths(),
            format_func=lambda p: model.DISP.get(p, p),
        )
    with c2:
        medida = st.selectbox(
            "Métrica",
            options=[m[0] for m in model.METRICAS],
            format_func=lambda m: model.METRICA_LABEL[m],
            index=0,
            key="dat_medida",
        )

    if not seleccion:
        st.info("Selecciona al menos un indicador.")
        return

    unidad = model.unidad(medida)
    frames = {}
    for path in seleccion:
        df = model.series(
            medida, path, filters.frecuencia, filters.anio_min,
            filters.anio_max, filters.prelim,
        )
        if df.empty:
            continue
        frames[model.SHORT.get(path, path)[:40]] = df.set_index("fecha").valor
    if not frames:
        st.warning("Sin datos para la selección.")
        return

    wide = pd.DataFrame(frames).sort_index()
    divisor, _ = model.escala(unidad)
    show = (wide / divisor).reset_index().rename(columns={"fecha": "Periodo"})
    fechas = show["Periodo"]
    if filters.trimestral:
        trimestre = ((fechas.dt.month - 1) // 3 + 1).astype(str)
        show["Periodo"] = fechas.dt.year.astype(str) + " T" + trimestre
    else:
        show["Periodo"] = fechas.dt.year.astype(str)
    unidad_hint = " · billones de pesos" if unidad == "mdp" else ""

    col_a, col_b = st.columns([1.6, 1])
    with col_a:
        c.section(
            "Tabla de series",
            f"{filters.etiqueta_frecuencia} · {model.METRICA_LABEL[medida]}{unidad_hint}",
        )
        c.table(show, height=460, column_config=c.num_cols(frames))
        st.download_button(
            "⬇ Descargar CSV",
            data=show.to_csv(index=False).encode("utf-8-sig"),
            file_name=(
                f"pib_{medida}_"
                f"{'trimestral' if filters.trimestral else 'anual'}.csv"
            ),
            mime="text/csv",
            width="content",
        )
    with col_b:
        c.section("Estadística descriptiva", "por indicador")
        rows = []
        for name, s in wide.items():
            est = model.resumen_estadistico(s)
            if est["n"] == 0:
                continue
            rows.append(
                {
                    "Indicador": name[:28],
                    "n": est["n"],
                    "Media": est["media"],
                    "Mediana": est["mediana"],
                    "Desv. est.": est["desv"],
                    "CV %": est["cv"],
                    "Mín.": est["minimo"],
                    "Máx.": est["maximo"],
                    "Último": est["ultimo"],
                }
            )
        c.table(
            pd.DataFrame(rows),
            height=300,
            column_config={
                "n": st.column_config.NumberColumn(format="%d"),
                **c.num_cols(
                    ["Media", "Mediana", "Desv. est.", "CV %", "Mín.", "Máx.",
                     "Último"]
                ),
            },
        )

        c.section("Resumen del periodo", "todas las series seleccionadas")
        c.plot(charts.series_lines(wide, unidad))

    with st.expander("Datos originales (registros filtrados)"):
        raw = model.PIB[
            (model.PIB.medida == medida)
            & (model.PIB.path.isin(seleccion))
            & (model.PIB.anio >= filters.anio_min)
            & (model.PIB.anio <= filters.anio_max)
        ]
        st.caption(f"{len(raw):,} registros · {model.METRICA_LABEL[medida]}")
        c.table(
            raw[["path", "anio", "periodo", "flag", "valor"]].rename(
                columns={
                    "path": "Indicador",
                    "anio": "Año",
                    "periodo": "Periodo",
                    "flag": "Cifra",
                    "valor": "Valor",
                }
            ),
            height=300,
        )
