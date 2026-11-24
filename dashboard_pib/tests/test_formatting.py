"""Pruebas del formateo numérico y de etiquetas HTML."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import formatting  # noqa: E402


def test_fmt_mdp_escala() -> None:
    assert formatting.fmt_mdp(26_412_827.196) == ("26.41", "billones")
    assert formatting.fmt_mdp(820_362.897) == ("820.4", "mdp")
    assert formatting.fmt_mdp(950.2) == ("950.2", "mdp")
    assert formatting.fmt_mdp(float("nan")) == ("—", "")


def test_fmt_value_por_unidad() -> None:
    assert formatting.fmt_value(3.306, "%") == ("3.31", "%")
    assert formatting.fmt_value(-1.2, "pp") == ("-1.20", "pp")
    assert formatting.fmt_value(104.6, "indice") == ("104.6", "")
    assert formatting.fmt_value(None, "%") == ("—", "")


def test_fmt_num_por_unidad() -> None:
    assert formatting.fmt_num(26_412_827.196, "mdp") == "26.41 b"
    assert formatting.fmt_num(820_362.897, "mdp") == "820.36 m"
    assert formatting.fmt_num(3.306, "%") == "3.31%"
    assert formatting.fmt_num(-1.2, "pp") == "-1.20 pp"
    assert formatting.fmt_num(104.6, "indice", 1) == "104.6"


def test_delta_html() -> None:
    assert "up" in formatting.delta_html(3.31, "%", "anual")
    assert "▲" in formatting.delta_html(3.31, "%", "anual")
    assert "down" in formatting.delta_html(-2.0, "%")
    assert "▼" in formatting.delta_html(-2.0, "%")
    assert formatting.delta_html(float("nan"), "%", "sin dato") == "sin dato"
