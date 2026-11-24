"""Tablero interactivo del PIB trimestral de México (INEGI, base 2018).

Punto de entrada: configura la página, la barra lateral y las pestañas.
La lógica vive en model.py, los gráficos en charts.py y cada pestaña en views/.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

import model
import theme
from views import comparar, datos, indicadores, resumen, sectores

st.set_page_config(
    page_title="PIB México · Tablero",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

theme.inject_css()
theme.mpl_style()

with st.sidebar:
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:18px">
          <div style="width:10px;height:10px;border-radius:50%;background:{theme.ACCENT};
                      box-shadow:0 0 12px {theme.ACCENT}"></div>
          <div style="font-weight:800;letter-spacing:.14em;font-size:.8rem;color:#E8EFF9">
            PIB · MÉXICO
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("##### Filtros")
    anio_min, anio_max = st.slider(
        "Rango de años",
        min_value=1993,
        max_value=model.ANIO_MAX,
        value=(2012, model.ANIO_MAX),
        step=1,
        help="Aplica a las pestañas de indicadores, comparación y datos.",
    )
    etiqueta_frecuencia = st.radio(
        "Periodicidad", ["Trimestral", "Anual"], index=0, horizontal=True
    )
    prelim = st.toggle(
        "Incluir cifras preliminares (P)",
        value=True,
        help="Las cifras marcadas P son preliminares; R son revisadas.",
    )
    st.divider()
    st.caption(
        "**Fuente:** INEGI · Sistema de Cuentas Nacionales de México.  \n"
        "PIB Trimestral, año base 2018. Serie del primer trimestre de 1993 "
        "a la fecha; serie larga desde 1980."
    )
    st.caption(
        f"Último dato: **{model.row_label(model.ULTIMO)}** · "
        f"{model.ULTIMO_ANIO} último año completo."
    )

filters = model.Filters(
    anio_min=anio_min,
    anio_max=anio_max,
    frecuencia="Q" if etiqueta_frecuencia == "Trimestral" else "A",
    etiqueta_frecuencia=etiqueta_frecuencia,
    prelim=prelim,
)

st.markdown(
    f"""
    <div class="hero">
      <div class="kicker">INEGI · SCNM · PIB trimestral · Base 2018</div>
      <h1>Producto Interno Bruto de México</h1>
      <p>Tablero interactivo para explorar niveles, crecimiento, estructura y contribución
      de las actividades económicas. Selecciona indicadores, métricas y periodos en cada
      pestaña.</p>
      <div class="chips">
        <span class="chip live">Último dato {model.row_label(model.ULTIMO)}</span>
        <span class="chip">Base 2018 = 100</span>
        <span class="chip">1993 – {model.ANIO_MAX} · serie larga 1980 – {model.ANIO_MAX}</span>
        <span class="chip">Fuente: INEGI</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tabs = st.tabs(["Resumen", "Indicadores", "Comparar", "Sectores", "Datos y estadística"])

with tabs[0]:
    resumen.render(filters)
with tabs[1]:
    indicadores.render(filters)
with tabs[2]:
    comparar.render(filters)
with tabs[3]:
    sectores.render(filters)
with tabs[4]:
    datos.render(filters)

st.markdown(
    f"""
    <div style="margin-top:34px;padding-top:14px;border-top:1px solid {theme.BORDER};
                color:{theme.MUTED};font-size:.74rem;display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap">
      <span>Elaborado con datos abiertos del INEGI · Sistema de Cuentas Nacionales de México ·
      PIB Trimestral, año base 2018.</span>
      <span>Último dato disponible: {model.row_label(model.ULTIMO)}</span>
    </div>
    """,
    unsafe_allow_html=True,
)
