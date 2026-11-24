# Tablero del PIB · México

Dashboard interactivo del **Producto Interno Bruto trimestral de México**
(INEGI, Sistema de Cuentas Nacionales, año base 2018), construido con
Streamlit, Plotly, pandas, Matplotlib y Seaborn.

**▶ App en línea:** <https://dashboardpib-ejwfmwktxnex4up2d2epgq.streamlit.app/>

## Instalación

Desde la raíz del repositorio:

```bash
python3 -m venv .venv
.venv/bin/pip install -r dashboard_pib/requirements.txt
```

## Ejecutar

```bash
cd dashboard_pib
../.venv/bin/streamlit run app.py
```

Abre <http://localhost:8501>.

La primera ejecución genera `dashboard_pib/data/pib.parquet` a partir de los
Excel de `tabulados_PIBT/` (unos segundos); después se reutiliza la caché.

Para regenerar la caché a partir de los tabulados:

```bash
cd dashboard_pib
../.venv/bin/python build_data.py --force
```

Pruebas (modelo, formato, gráficas y app completa vía `AppTest`):

```bash
cd dashboard_pib
../.venv/bin/python -m pytest
```

## Pestañas

| Pestaña | Qué muestra |
|---|---|
| **Resumen** | KPIs del último trimestre, PIB real y crecimiento, estructura por grandes actividades, crecimiento por actividad, mapa de calor trimestral, últimos trimestres y serie larga 1980–2026. |
| **Indicadores** | Selector jerárquico de **184 actividades** (PIB total, grandes actividades, ramas y subsectores) × **10 métricas** (nivel real/nominal, variaciones, deflactor, inflación implícita, estructura, contribución). Incluye estadística descriptiva, distribución, índice 2018 = 100 y CAGR. |
| **Comparar** | Hasta varias actividades a la vez, en índice base 2018 o valores; ranking del último periodo, matriz de correlación de crecimientos y tabla descriptiva. |
| **Sectores** | Treemap de la estructura económica (tamaño = participación, color = crecimiento), dona de las tres grandes actividades, top de ramas y tabla detallada con estructura, variación y contribución. |
| **Datos y estadística** | Series completas, estadística descriptiva por indicador y descarga CSV. |

Filtros globales en la barra lateral: rango de años, periodicidad
(trimestral/anual) e inclusión de cifras preliminares (P).

## Fuente de datos

`tabulados_PIBT/` contiene cinco tabulados de INEGI:

| Archivo | Contenido |
|---|---|
| `PIBT_2.xlsx` | Series originales · millones de pesos de 2018 (anualizados) + variación, estructura y contribución |
| `PIBT_3.xlsx` | Series originales · millones de pesos corrientes (anualizados) + variación, estructura y contribución |
| `PIBT_4.xlsx` | Índice de precios implícitos, 2018 = 100 + variación |
| `PIBT_r_2.xlsx` | Valores constantes 2018 · agregados 1980–2026 |
| `PIBT_r_3.xlsx` | Variación porcentual anual · agregados 1980–2026 |

Notas:

- Las series trimestrales de nivel están **anualizadas** (la columna «Anual» es
  el promedio de los cuatro trimestres, no la suma).
- `R` = cifra revisada, `P` = preliminar. El último dato disponible es
  **2026 T3P**; el último año completo es **2025**.
- La estructura porcentual y las contribuciones provienen de los tabulados
  originales de INEGI; la suma de parciales puede diferir por redondeo.

## Estructura del repositorio

```
.
├── README.md
├── .gitignore
├── dashboard_pib/
│   ├── app.py              # entrada: configuración, filtros y pestañas
│   ├── model.py            # dominio: catálogo, series, periodos, estadísticos
│   ├── charts.py           # constructores de figuras (Plotly / Matplotlib)
│   ├── components.py       # KPI, secciones y envoltorios de Streamlit
│   ├── formatting.py       # formato numérico (mdp, %, pp, índices)
│   ├── theme.py            # paleta, CSS, plantilla Plotly y Matplotlib
│   ├── pib_data.py         # ingesta de los Excel → tabla larga + parquet
│   ├── build_data.py       # regeneración de la caché
│   ├── views/              # una pestaña por archivo
│   ├── tests/              # pruebas de comportamiento (pytest + AppTest)
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── .streamlit/config.toml
└── tabulados_PIBT/         # tabulados fuente de INEGI
```

`dashboard_pib/data/` se genera al ejecutar la app y no se versiona.

## Arquitectura

- **Frontera de datos:** `pib_data.py` es el único módulo que lee Excel; valida
  y normaliza una vez, y todo lo demás consume `data/pib.parquet`.
- **Dominio puro:** `model.py` no importa Streamlit; expone `series()`,
  `add_yoy()`, `cagr_anual()`, `resumen_estadistico()`, etiquetas de periodo y
  catálogo. Se prueba directamente.
- **Una pestaña, un archivo:** cada vista recibe `model.Filters` y solo compone
  componentes; no conoce la hoja de cálculo.
- **Decisiones en un solo lugar:** escalas por unidad (`model.escala`), colores
  de actividades y estadísticos descriptivos viven en un único módulo.
