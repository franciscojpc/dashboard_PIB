"""Modelo de dominio del tablero.

Una sola fuente para: carga de datos, catálogo de indicadores, series por
medida/frecuencia, etiquetas de periodo y constantes del dominio. Funciones
sin Streamlit, para poder probarlas directamente.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import pandas as pd

import pib_data

TRIM = ("T1", "T2", "T3", "T4")
META = pib_data.MEDIDA_BY_ID

METRICAS = [
    ("real", "Nivel real · mdp de 2018"),
    ("nominal", "Nivel nominal · mdp corrientes"),
    ("var_real", "Variación real anual · %"),
    ("var_nominal", "Variación nominal anual · %"),
    ("deflactor", "Deflactor implícito · 2018 = 100"),
    ("inflacion", "Inflación implícita anual · %"),
    ("estructura_real", "Estructura del PIB real · %"),
    ("estructura_nominal", "Estructura del PIB nominal · %"),
    ("contribucion_real", "Contribución real · pp"),
    ("contribucion_nominal", "Contribución nominal · pp"),
]
METRICA_LABEL = dict(METRICAS)

# Las cuatro piezas que suman el PIB: tres grandes actividades + impuestos.
ACTIVIDADES_PIE = [
    (
        "Valor agregado bruto › Actividades primarias",
        "Primarias",
        "#34D399",
    ),
    (
        "Valor agregado bruto › Actividades secundarias",
        "Secundarias",
        "#38BDF8",
    ),
    (
        "Valor agregado bruto › Actividades terciarias",
        "Terciarias",
        "#A78BFA",
    ),
    (
        "Producto interno bruto › Impuestos sobre los productos, netos",
        "Impuestos",
        "#64748B",
    ),
]

# Series para las mini-gráficas de crecimiento.
ACTIVIDADES_SERIE = [
    ("Producto interno bruto", "PIB total", "#38BDF8"),
    ("Valor agregado bruto › Actividades primarias", "Primarias", "#34D399"),
    ("Valor agregado bruto › Actividades secundarias", "Secundarias", "#38BDF8"),
    ("Valor agregado bruto › Actividades terciarias", "Terciarias", "#A78BFA"),
]

BASE_PATHS = [
    "Producto interno bruto",
    "Valor agregado bruto › Actividades primarias",
    "Valor agregado bruto › Actividades secundarias",
    "Valor agregado bruto › Actividades terciarias",
]

PIB = pib_data.load()

CAT = (
    PIB[PIB.medida == "real"][["path", "nombre", "codigo", "nivel", "parent", "orden"]]
    .drop_duplicates("path")
    .sort_values("orden")
    .reset_index(drop=True)
)
CAT["display"] = CAT.apply(
    lambda r: ("    " * int(r.nivel))
    + (f"{r.codigo} · " if r.codigo else "")
    + r.nombre,
    axis=1,
)
DISP = dict(zip(CAT.path, CAT.display))
SHORT = dict(zip(CAT.path, CAT.nombre))

ULTIMO = (
    PIB[(PIB.medida == "real") & (PIB.periodo.isin(TRIM))]
    .sort_values(["anio", "periodo"])
    .iloc[-1]
)
ULTIMO_ANIO = int(PIB[(PIB.medida == "real") & (PIB.periodo == "Anual")].anio.max())
ANIO_MIN = int(PIB.anio.min())
ANIO_MAX = int(PIB.anio.max())


@dataclass(frozen=True)
class Filters:
    """Filtros globales de la barra lateral."""

    anio_min: int
    anio_max: int
    frecuencia: str  # "Q" | "A"
    etiqueta_frecuencia: str
    prelim: bool

    @property
    def trimestral(self) -> bool:
        return self.frecuencia == "Q"

    @property
    def periodos_por_anio(self) -> int:
        return 4 if self.trimestral else 1


def unidad(medida: str) -> str:
    return META[medida]["unidad"]


def kind(medida: str) -> str:
    return META[medida]["kind"]


def escala(unidad_: str) -> tuple[float, str]:
    """Divisor de presentación y etiqueta del eje para una unidad."""
    if unidad_ == "mdp":
        return 1e6, "billones de pesos"
    labels = {
        "%": "variación %",
        "pp": "puntos porcentuales",
        "indice": "índice 2018 = 100",
    }
    return 1.0, labels.get(unidad_, "")


@lru_cache(maxsize=None)
def _series(
    medida: str,
    path: str,
    freq: str,
    anio_min: int,
    anio_max: int,
    prelim: bool,
) -> pd.DataFrame:
    df = PIB[
        (PIB.medida == medida)
        & (PIB.path == path)
        & (PIB.anio >= anio_min)
        & (PIB.anio <= anio_max)
    ].copy()
    if not prelim:
        df = df[df.flag != "P"]
    if freq == "A":
        df = df[df.periodo == "Anual"].copy()
        if df.empty:
            return df
        df["fecha"] = pd.to_datetime(dict(year=df.anio, month=1, day=1))
    else:
        df = df[df.periodo.isin(TRIM)].copy()
        if df.empty:
            return df
        df["q"] = df.periodo.str[1].astype(int)
        df["fecha"] = pd.to_datetime(
            dict(year=df.anio, month=(df.q - 1) * 3 + 1, day=1)
        )
    df = df.sort_values("fecha").drop_duplicates("fecha").reset_index(drop=True)
    df["valor"] = df["valor"].astype(float)
    return df


def series(
    medida: str,
    path: str,
    freq: str = "Q",
    anio_min: int = 1993,
    anio_max: int = ANIO_MAX,
    prelim: bool = True,
) -> pd.DataFrame:
    """Serie de un indicador, con fecha y sin mutaciones compartidas."""
    return _series(medida, path, freq, anio_min, anio_max, prelim).copy()


def add_yoy(df: pd.DataFrame, freq: str) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    lag = 4 if freq == "Q" else 1
    df["yoy"] = df["valor"].pct_change(lag, fill_method=None) * 100
    return df


def series_yoy(
    medida: str,
    path: str,
    freq: str = "Q",
    anio_min: int = 1993,
    anio_max: int = ANIO_MAX,
    prelim: bool = True,
) -> pd.DataFrame:
    return add_yoy(series(medida, path, freq, anio_min, anio_max, prelim), freq)


def last_row(df: pd.DataFrame) -> pd.Series | None:
    df = df.dropna(subset=["valor"])
    return df.iloc[-1] if len(df) else None


def period_label(anio: int, periodo: str, flag: str = "") -> str:
    """Etiqueta legible: '2026 T3P', '2025', '2024 T4'."""
    badge = flag if flag in ("P", "R") else ""
    if periodo in TRIM:
        return f"{int(anio)} {periodo}{badge}"
    return f"{int(anio)}{' ' + badge if badge else ''}"


def row_label(row: pd.Series) -> str:
    return period_label(int(row["anio"]), row["periodo"], row.get("flag", ""))


def default_paths() -> list[str]:
    """Indicadores preseleccionados en las pestañas de comparación y datos."""
    disponibles = set(CAT.path)
    return [p for p in BASE_PATHS if p in disponibles]


def resumen_estadistico(valores: pd.Series) -> dict[str, float]:
    """Estadísticos descriptivos de una serie, calculados en un solo lugar."""
    v = valores.dropna()
    media = v.mean()
    return {
        "n": len(v),
        "media": media,
        "mediana": v.median(),
        "desv": v.std(),
        "minimo": v.min(),
        "maximo": v.max(),
        "ultimo": v.iloc[-1] if len(v) else np.nan,
        "cv": (v.std() / media * 100) if media else np.nan,
    }


def cagr_anual(valores: pd.Series, periodos_por_anio: int) -> float:
    """Crecimiento anual compuesto; NaN si la serie no es positiva.

    Una serie de n observaciones cubre n-1 intervalos.
    """
    v = valores.dropna()
    if len(v) < 2 or v.iloc[0] <= 0 or v.iloc[-1] <= 0:
        return np.nan
    anios = (len(v) - 1) / periodos_por_anio
    if anios <= 0:
        return np.nan
    return ((v.iloc[-1] / v.iloc[0]) ** (1 / anios) - 1) * 100


def estructura_rows(anio: int, periodo: str = "Anual") -> list[tuple[str, float, str]]:
    """Participación de las tres actividades + impuestos, en sus colores."""
    est = PIB[
        (PIB.medida == "estructura_real")
        & (PIB.anio == anio)
        & (PIB.periodo == periodo)
    ]
    valores = dict(zip(est.path, est.valor))
    return [
        (label, valores.get(path, np.nan), color)
        for path, label, color in ACTIVIDADES_PIE
    ]
