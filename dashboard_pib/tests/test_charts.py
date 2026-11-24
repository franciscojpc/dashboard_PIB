"""Pruebas de los constructores de figuras."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import charts  # noqa: E402
import theme  # noqa: E402


@pytest.fixture
def serie() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "fecha": pd.to_datetime(["2024-01-01", "2024-04-01", "2024-07-01"]),
            "valor": [100.0, 102.0, 101.0],
            "yoy": [1.0, -2.5, 3.0],
        }
    )


def test_sparkline(serie: pd.DataFrame) -> None:
    fig = charts.sparkline(serie, theme.ACCENT)
    assert fig.data[0].type == "scatter"
    assert list(fig.data[0].y) == [100.0, 102.0, 101.0]


def test_level_with_yoy(serie: pd.DataFrame) -> None:
    fig = charts.level_with_yoy(
        serie, "PIB", theme.ACCENT, "rgba(56,189,248,0.07)", 400, 0.25, "%Y %b"
    )
    assert [t.type for t in fig.data] == ["scatter", "bar"]
    assert fig.data[1].marker.color[1] == theme.NEG
    assert fig.data[1].marker.color[2] == theme.POS


def test_pie_respeta_orden_y_colores() -> None:
    rows = [("Primarias", 3.5, "#34D399"), ("Secundarias", 30.0, "#38BDF8")]
    fig = charts.pie(rows, hole=0.62, height=400)
    assert list(fig.data[0].labels) == ["Primarias", "Secundarias"]
    assert list(fig.data[0].values) == [3.5, 30.0]
    assert list(fig.data[0].marker.colors) == ["#34D399", "#38BDF8"]


def test_explorer_variacion_usa_barras() -> None:
    df = pd.DataFrame(
        {
            "fecha": pd.to_datetime(["2024-01-01", "2024-04-01"]),
            "valor": [-1.0, 2.0],
            "yoy": [0.0, 0.0],
        }
    )
    fig = charts.explorer_series(df, "Actividad", "variacion", False, "var %")
    assert fig.data[0].type == "bar"
    assert list(fig.data[0].marker.color) == [theme.NEG, theme.POS]


def test_ranking_bar(serie: pd.DataFrame) -> None:
    rank = pd.DataFrame({"Indicador": ["A", "B"], "valor": [10.0, -2.0]})
    fig = charts.ranking_bar(rank, "%", lambda v, u, d=2: f"{v:.2f}%")
    assert fig.data[0].orientation == "h"
    assert list(fig.data[0].marker.color) == [theme.POS, theme.NEG]


def test_treemap_padres_mayores_que_hijos() -> None:
    tree = pd.DataFrame(
        {
            "nombre": ["Secundarias", "Minería"],
            "parent": ["", "Valor agregado bruto › Actividades secundarias"],
            "estructura_real": [30.0, 3.0],
            "var_real": [1.0, -2.0],
        },
        index=[
            "Valor agregado bruto › Actividades secundarias",
            "Valor agregado bruto › Actividades secundarias › Minería",
        ],
    )
    ids = list(tree.index)
    totals = {ids[0]: 30.0, ids[1]: 3.0}
    fig = charts.treemap(
        tree, totals, ids, ["Secundarias", "Minería"],
        ["", "Valor agregado bruto › Actividades secundarias"],
    )
    assert list(fig.data[0].values) == [30.0, 3.0]
    assert fig.data[0].branchvalues == "total"
