"""Pruebas del modelo de dominio (sin Streamlit)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import model  # noqa: E402


def test_catalogo_de_indicadores() -> None:
    assert len(model.CAT) == 184
    assert "Producto interno bruto" in set(model.CAT.path)
    assert model.CAT.nivel.max() == 4
    assert model.DISP["Producto interno bruto"] == "Producto interno bruto"


def test_series_trimestrales_ultimo_dato() -> None:
    df = model.series("real", "Producto interno bruto", "Q", 1993, 2026, True)
    ultimo = model.last_row(df)
    assert (int(ultimo["anio"]), ultimo["periodo"]) == (2026, "T3")
    assert ultimo["valor"] == pytest.approx(26_412_827.196, abs=1e-3)


def test_variacion_anual_calculada() -> None:
    df = model.add_yoy(
        model.series("real", "Producto interno bruto", "Q", 1993, 2026, True), "Q"
    )
    assert model.last_row(df)["yoy"] == pytest.approx(3.306097, abs=1e-5)


def test_anual_y_ultimo_anio_completo() -> None:
    df = model.series("real", "Producto interno bruto", "A", 1993, 2026, True)
    assert len(df) == 33
    assert int(df.anio.max()) == 2025
    assert model.ULTIMO_ANIO == 2025


def test_period_label() -> None:
    assert model.period_label(2026, "T3", "P") == "2026 T3P"
    assert model.period_label(2026, "T1", "R") == "2026 T1R"
    assert model.period_label(2025, "Anual", "") == "2025"
    assert model.period_label(2024, "T4", "") == "2024 T4"


def test_estructura_suma_cien() -> None:
    filas = model.estructura_rows(2025, "Anual")
    assert len(filas) == 4
    assert sum(v for _, v, _ in filas) == pytest.approx(100.0, abs=1e-6)


def test_sin_preliminares() -> None:
    df = model.series("real", "Producto interno bruto", "Q", 1993, 2026, False)
    ultimo = model.last_row(df)
    assert (int(ultimo["anio"]), ultimo["periodo"]) == (2026, "T2")


def test_escala_por_unidad() -> None:
    assert model.escala("mdp") == (1e6, "billones de pesos")
    assert model.escala("%")[0] == 1.0
    assert model.escala("indice")[0] == 1.0


def test_default_paths() -> None:
    rutas = model.default_paths()
    assert rutas[0] == "Producto interno bruto"
    assert len(rutas) == 4


def test_resumen_estadistico() -> None:
    stats = model.resumen_estadistico(pd.Series([1.0, 2.0, 3.0, None]))
    assert stats["n"] == 3
    assert stats["media"] == pytest.approx(2.0)
    assert stats["mediana"] == pytest.approx(2.0)
    assert stats["ultimo"] == pytest.approx(3.0)


def test_cagr_anual() -> None:
    assert model.cagr_anual(pd.Series([100.0, 121.0]), 1) == pytest.approx(21.0)
    assert pd.isna(model.cagr_anual(pd.Series([100.0, -5.0]), 1))
    assert pd.isna(model.cagr_anual(pd.Series([100.0]), 1))


def test_metricas_declaradas() -> None:
    assert len(model.METRICAS) == 10
    assert model.METRICA_LABEL["real"].startswith("Nivel real")
    assert model.unidad("deflactor") == "indice"
    assert model.kind("contribucion_real") == "contribucion"
