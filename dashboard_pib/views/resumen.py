"""Pestaña Resumen: panorama del último trimestre y serie larga."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

import charts
import components as c
import formatting as f
import model
import theme

PIB_PATH = "Producto interno bruto"


def render(filters: model.Filters) -> None:
    real_q = model.series_yoy("real", PIB_PATH, "Q", 1993, model.ANIO_MAX, True)
    nom_q = model.series_yoy("nominal", PIB_PATH, "Q", 1993, model.ANIO_MAX, True)
    def_q = model.series_yoy("deflactor", PIB_PATH, "Q", 1993, model.ANIO_MAX, True)
    real_a = model.series_yoy("real", PIB_PATH, "A", 1993, model.ANIO_MAX, True)

    lr, ln, ld = model.last_row(real_q), model.last_row(nom_q), model.last_row(def_q)
    la = model.last_row(real_a)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        v, u = f.fmt_mdp(lr["valor"])
        c.kpi(
            "PIB real · último trimestre", v, u,
            f.delta_html(lr["yoy"], "%", f"anual · {model.row_label(lr)}"),
        )
    with c2:
        v, u = f.fmt_mdp(ln["valor"])
        c.kpi(
            "PIB nominal · último trimestre", v, u,
            f.delta_html(ln["yoy"], "%", f"anual · {model.row_label(ln)}"),
        )
    with c3:
        c.kpi(
            "Deflactor implícito", f"{ld['valor']:,.1f}", "",
            f.delta_html(ld["yoy"], "%", f"inflación anual · {model.row_label(ld)}"),
        )
    with c4:
        v, u = f.fmt_mdp(la["valor"])
        c.kpi(
            f"PIB real {int(la['anio'])}", v, u,
            f.delta_html(la["yoy"], "%", "crecimiento anual"),
        )

    st.write("")

    col_a, col_b = st.columns([2.2, 1])
    with col_a:
        c.section(
            "PIB real y crecimiento anual",
            "Serie original, miles de millones de pesos de 2018",
        )
        q = real_q[real_q.anio >= filters.anio_min]
        c.plot(
            charts.level_with_yoy(
                q.assign(valor=q.valor / 1e6),
                "PIB real",
                theme.ACCENT,
                "rgba(56,189,248,0.07)",
                height=400,
                bargap=0.25,
                hover_fecha="%Y %b",
                line_width=2.2,
                bar_opacity=0.45,
                margin=dict(t=24),
            )
        )

    with col_b:
        c.section("Estructura del PIB", f"{model.ULTIMO_ANIO} · participación %")
        rows = [
            (label, valor, color)
            for label, valor, color in model.estructura_rows(model.ULTIMO_ANIO)
            if pd.notna(valor)
        ]
        center = (
            f"<b>{model.ULTIMO_ANIO}</b><br>"
            f"<span style='font-size:10px;color:{theme.MUTED}'>estructura</span>"
        )
        c.plot(charts.pie(rows, hole=0.62, height=400, center=center))

    c.section("Crecimiento por actividad", "Variación real anual, últimos 12 años")
    cols = st.columns(4)
    for col, (path, nombre, color) in zip(cols, model.ACTIVIDADES_SERIE):
        df = model.series_yoy("real", path, "A", 1993, model.ANIO_MAX, True)
        df = df.dropna(subset=["yoy"]).tail(12)
        ultimo = df.iloc[-1] if len(df) else None
        with col:
            val = ultimo["yoy"] if ultimo is not None else float("nan")
            arrow = "▲" if val >= 0 else "▼"
            cls = "up" if val >= 0 else "down"
            anio = int(ultimo["anio"]) if ultimo is not None else ""
            st.markdown(
                f"""<div style="font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;
                color:{theme.MUTED};font-weight:700">{nombre}</div>
                <div style="font-size:1.35rem;font-weight:700;margin:2px 0 0">
                <span class="{cls}" style="color:{theme.POS if val>=0 else theme.NEG}">{arrow} {abs(val):.2f}%</span>
                <span style="font-size:.72rem;color:{theme.MUTED};font-weight:500">anual {anio}</span>
                </div>""",
                unsafe_allow_html=True,
            )
            c.plot(charts.sparkline(df, color))

    st.write("")
    sec_a, sec_b = st.columns([1.45, 1])
    with sec_a:
        c.section("Mapa de calor del crecimiento", "Var. real anual por trimestre (%)")
        fig = charts.heatmap_yoy(
            model.PIB[
                (model.PIB.medida == "var_real") & (model.PIB.path == PIB_PATH)
            ],
            anios=14,
        )
        c.pyplot(fig)
        plt.close(fig)
    with sec_b:
        c.section("Últimos trimestres", "PIB real, nominal y deflactor")
        last_q = real_q.dropna(subset=["valor"]).tail(8)
        rows = []
        for _, r in last_q.iterrows():
            nom = nom_q[nom_q.fecha == r.fecha]
            defl = def_q[def_q.fecha == r.fecha]
            rows.append(
                {
                    "Periodo": f"{int(r.anio)} {r.periodo}",
                    "PIB real (b)": r.valor / 1e6,
                    "Var. real %": r.yoy,
                    "PIB nominal (b)": nom.valor.iloc[0] / 1e6 if len(nom) else float("nan"),
                    "Deflactor": defl.valor.iloc[0] if len(defl) else float("nan"),
                }
            )
        c.table(
            pd.DataFrame(rows),
            height=330,
            column_config={
                "PIB real (b)": st.column_config.NumberColumn(format="%.2f"),
                "Var. real %": st.column_config.NumberColumn(format="%.2f"),
                "PIB nominal (b)": st.column_config.NumberColumn(format="%.2f"),
                "Deflactor": st.column_config.NumberColumn(format="%.1f"),
            },
        )

    with st.expander("Serie larga 1980 – 2026 · agregados"):
        larga = model.series_yoy(
            "real_larga", PIB_PATH, "A", 1980, model.ANIO_MAX, True
        )
        c.plot(
            charts.level_with_yoy(
                larga.assign(valor=larga.valor / 1e6),
                "PIB real",
                "#A78BFA",
                "rgba(167,139,250,0.08)",
                height=420,
                bargap=0.2,
                hover_fecha="%Y",
                line_width=2.4,
                bar_opacity=0.4,
            )
        )
        st.caption(
            "Serie enlazada del PIB trimestral (INEGI). 1980–1992 proviene de las series "
            "de valores constantes; 1993 en adelante, del tabulado detallado."
        )
