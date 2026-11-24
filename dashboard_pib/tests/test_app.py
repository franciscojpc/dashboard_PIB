"""Pruebas de comportamiento de la app tal como la ve el usuario (AppTest)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest  # noqa: E402


def run_app() -> AppTest:
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=300)
    at.run()
    return at


def _markdown(at: AppTest) -> str:
    return "\n".join(str(m.value) for m in at.markdown)


def test_render_inicial() -> None:
    at = run_app()
    assert not at.exception
    assert len(at.tabs) == 5
    assert "Producto Interno Bruto de México" in _markdown(at)
    assert "PIB real · último trimestre" in _markdown(at)
    assert "https://github.com/franciscojpc/dashboard_PIB" in _markdown(at)
    assert len(at.selectbox[0].options) == 184
    assert len(at.selectbox[1].options) == 10
    assert len(at.get("download_button")) == 1
    assert len(at.dataframe) == 8
    assert len(at.get("plotly_chart")) == 15


def test_kpi_pib_real_ultimo_trimestre() -> None:
    at = run_app()
    texto = _markdown(at)
    assert "PIB real · último trimestre" in texto
    assert "26.41" in texto  # billones de pesos, 2026 T3
    assert "2026 T3P" in texto
    assert "2026 T3PP" not in texto


def test_todas_las_metricas_renderizan() -> None:
    at = run_app()
    for i, etiqueta in enumerate(at.selectbox[1].options):
        at.selectbox[1].select_index(i)
        at.run()
        assert not at.exception, f"métrica {i}: {etiqueta}"


def test_indicador_profundo_y_comparacion() -> None:
    at = run_app()
    opciones = at.selectbox[0].options
    indice = next(i for i, o in enumerate(opciones) if "311 · Industria alimentaria" in o)
    at.selectbox[0].select_index(indice)
    at.selectbox[1].select_index(8)  # contribución real
    at.run()
    assert not at.exception

    at.selectbox[1].select_index(0)
    at.run()
    at.toggle[0].set_value(True)  # escala log
    at.toggle[1].set_value(True)  # comparar con PIB
    at.run()
    assert not at.exception


def test_comparador_subsectores() -> None:
    at = run_app()
    at.toggle[2].set_value(True)
    at.run()
    at.selectbox[2].select_index(2)  # variación real
    at.run()
    assert not at.exception


def test_sectores_anios_y_periodos() -> None:
    at = run_app()
    total = len(at.selectbox[3].options)
    for i in (0, total // 2, total - 1):
        at.selectbox[3].select_index(i)
        at.run()
        assert not at.exception, f"año índice {i}"
    for periodo in ("T1", "T4", "Anual"):
        at.radio[1].set_value(periodo)
        at.run()
        assert not at.exception, periodo
    at.selectbox[4].select_index(1)
    at.run()
    assert not at.exception


def test_filtros_globales() -> None:
    at = run_app()
    at.slider[0].set_value((1993, 2026))
    at.run()
    assert not at.exception
    at.radio[2].set_value("Anual")
    at.run()
    assert not at.exception
    at.toggle[3].set_value(False)  # sin preliminares
    at.run()
    assert not at.exception


@pytest.mark.parametrize("indice", [0, 2, 4])
def test_metricas_de_datos(indice: int) -> None:
    at = run_app()
    at.selectbox[5].select_index(indice)
    at.run()
    assert not at.exception
