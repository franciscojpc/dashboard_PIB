"""Carga y normaliza los tabulados del PIB trimestral de INEGI.

Cada archivo del directorio ``tabulados_PIBT`` contiene una hoja ``Tabulado``
con dos filas de encabezado (año y periodo) y uno o varios bloques de datos
(niveles, variaciones, estructura, contribuciones). Este módulo los convierte
en una sola tabla larga y la cachea en ``data/pib.parquet``.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RAW_DIR = ROOT / "tabulados_PIBT"
DATA_DIR = HERE / "data"
PARQUET = DATA_DIR / "pib.parquet"
META_PATH = DATA_DIR / "meta.json"

# id de medida -> (archivo, bloque en la hoja, etiqueta, unidad, tipo)
MEDIDAS = [
    dict(
        id="real",
        file="PIBT_2",
        block="Millones de pesos a precios de 2018",
        label="PIB real",
        short="Nivel real",
        unidad="mdp",
        kind="nivel",
        desc="Millones de pesos de 2018, anualizados. Serie original.",
    ),
    dict(
        id="nominal",
        file="PIBT_3",
        block="Millones de pesos a precios corrientes",
        label="PIB nominal",
        short="Nivel nominal",
        unidad="mdp",
        kind="nivel",
        desc="Millones de pesos corrientes, anualizados. Serie original.",
    ),
    dict(
        id="var_real",
        file="PIBT_2",
        block="Variación porcentual anual",
        label="Variación real anual",
        short="Var. real anual",
        unidad="%",
        kind="variacion",
        desc="Variación porcentual anual del PIB real (precios de 2018).",
    ),
    dict(
        id="var_nominal",
        file="PIBT_3",
        block="Variación porcentual anual",
        label="Variación nominal anual",
        short="Var. nominal anual",
        unidad="%",
        kind="variacion",
        desc="Variación porcentual anual del PIB a precios corrientes.",
    ),
    dict(
        id="deflactor",
        file="PIBT_4",
        block="Índice de precios implícitos base 2018=100",
        label="Deflactor implícito",
        short="Deflactor",
        unidad="indice",
        kind="indice",
        desc="Índice de precios implícitos del PIB, base 2018 = 100.",
    ),
    dict(
        id="inflacion",
        file="PIBT_4",
        block="Variación porcentual anual",
        label="Inflación implícita anual",
        short="Inflación implícita",
        unidad="%",
        kind="variacion",
        desc="Variación porcentual anual del deflactor implícito del PIB.",
    ),
    dict(
        id="estructura_real",
        file="PIBT_2",
        block="Estructura porcentual",
        label="Estructura del PIB real",
        short="Estructura",
        unidad="%",
        kind="estructura",
        desc="Participación porcentual de cada actividad en el PIB real.",
    ),
    dict(
        id="estructura_nominal",
        file="PIBT_3",
        block="Estructura porcentual",
        label="Estructura del PIB nominal",
        short="Estructura nominal",
        unidad="%",
        kind="estructura",
        desc="Participación porcentual de cada actividad en el PIB nominal.",
    ),
    dict(
        id="contribucion_real",
        file="PIBT_2",
        block="Contribución a la variación nacional",
        label="Contribución real (pp)",
        short="Contribución",
        unidad="pp",
        kind="contribucion",
        desc="Contribución de cada actividad a la variación anual del PIB real.",
    ),
    dict(
        id="contribucion_nominal",
        file="PIBT_3",
        block="Contribución a la variación nacional",
        label="Contribución nominal (pp)",
        short="Contribución nominal",
        unidad="pp",
        kind="contribucion",
        desc="Contribución de cada actividad a la variación anual del PIB nominal.",
    ),
    dict(
        id="real_larga",
        file="PIBT_r_2",
        block=None,
        label="PIB real, serie larga",
        short="PIB real 1980–",
        unidad="mdp",
        kind="nivel",
        desc="PIB real (millones de pesos de 2018) desde 1980. Solo agregados.",
    ),
    dict(
        id="var_real_larga",
        file="PIBT_r_3",
        block=None,
        label="Variación real anual, serie larga",
        short="Var. real 1980–",
        unidad="%",
        kind="variacion",
        desc="Variación porcentual anual del PIB real desde 1981.",
    ),
]

MEDIDA_BY_ID = {m["id"]: m for m in MEDIDAS}
BLOCK_NAMES = {m["block"] for m in MEDIDAS if m["block"]}
FILE_MEDIDA = {m["file"]: m for m in MEDIDAS}

PERIODOS = ["T1", "T2", "T3", "T4", "6 Meses", "9 Meses", "Anual"]
TRIMESTRES = ["T1", "T2", "T3", "T4"]

_FOOTNOTE_PREFIXES = (
    "aLos códigos",
    "aLas",
    "aA precios",
    "bLos códigos",
    "NA ",
    "RCifras",
    "PCifras",
    "Nota:",
    "Fuente:",
    "Ello implica",
    "Este producto",
    "La suma de",
)
_CODE_RE = re.compile(
    r"^([0-9]{2,5}(?:\s*-\s*[0-9]{2,5})?|[A-Z][0-9A-Za-z.\-]{1,24})\s+-\s+(.+)$"
)
_YEAR_RE = re.compile(r"(\d{4})")
_PERIOD_RE = re.compile(r"^(T[1-4]|6 Meses|9 Meses|Anual)\s*([RP])?$")


def _clean(value) -> str:
    return re.sub(r"[ \t]+", " ", str(value)).strip()


def _split_code(label: str) -> tuple[str, str]:
    """Separa el código de la actividad del nombre legible."""
    if label.startswith("_"):
        return "", label.split(" - ", 1)[-1]
    match = _CODE_RE.match(label)
    if match:
        return match.group(1).replace(" ", ""), match.group(2).strip()
    return "", label


def _period_columns(raw: pd.DataFrame) -> list[tuple[int, str, str]]:
    """Devuelve [(columna, periodo, bandera R/P)] a partir de las filas 4 y 5."""
    years = raw.iloc[4].ffill().tolist()
    labels = raw.iloc[5].tolist()
    out: list[tuple[int, str, str]] = []
    for col in range(1, raw.shape[1]):
        year_match = _YEAR_RE.search(_clean(years[col]))
        if not year_match or pd.isna(labels[col]):
            continue
        period_match = _PERIOD_RE.match(_clean(labels[col]))
        if not period_match:
            continue
        out.append(
            (
                col,
                int(year_match.group(1)),
                period_match.group(1),
                period_match.group(2) or "",
            )
        )
    return out


def parse_workbook(path: Path) -> pd.DataFrame:
    """Convierte la hoja ``Tabulado`` de un archivo en filas largas."""
    stem = path.stem
    medida = FILE_MEDIDA[stem]
    raw = pd.read_excel(path, sheet_name="Tabulado", header=None)
    cols = _period_columns(raw)

    # Solo las columnas que nos interesan, como matriz de números.
    numeric = raw.iloc[:, [c[0] for c in cols]].apply(pd.to_numeric, errors="coerce")

    records: list[dict] = []
    active = medida["id"] if medida["block"] is None else None
    stack: list[tuple[int, str]] = []
    seen_indents: set[int] = set()
    orden = 0

    for row in range(6, len(raw)):
        cell = raw.iat[row, 0]
        if pd.isna(cell):
            continue
        label = str(cell)
        text = _clean(label)
        if not text:
            continue

        # Inicio de un nuevo bloque dentro de la hoja.
        if text in BLOCK_NAMES:
            active = next(
                (
                    m["id"]
                    for m in MEDIDAS
                    if m["file"] == stem and m["block"] == text
                ),
                None,
            )
            stack, seen_indents, orden = [], set(), 0
            continue

        if active is None:
            continue
        if text.startswith(_FOOTNOTE_PREFIXES):
            break

        values = numeric.iloc[row]
        if values.notna().sum() == 0:
            continue

        indent = len(label) - len(label.lstrip(" "))
        while stack and stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1] if stack else ""
        codigo, nombre = _split_code(text)
        path_ = f"{parent} › {nombre}" if parent else nombre
        stack.append((indent, path_))
        seen_indents.add(indent)
        nivel = sum(1 for x in seen_indents if x < indent)

        for col, anio, periodo, flag in cols:
            valor = values.get(col)
            if pd.isna(valor):
                continue
            records.append(
                {
                    "medida": active,
                    "path": path_,
                    "nombre": nombre,
                    "codigo": codigo,
                    "nivel": nivel,
                    "parent": parent,
                    "orden": orden,
                    "anio": anio,
                    "periodo": periodo,
                    "flag": flag,
                    "valor": float(valor),
                }
            )
        orden += 1

    return pd.DataFrame.from_records(records)


def build(force: bool = False) -> pd.DataFrame:
    """Parsea todos los tabulados y guarda el resultado en parquet."""
    sources = sorted(RAW_DIR.glob("*.xlsx"))
    if not sources:
        raise FileNotFoundError(f"No hay tabulados en {RAW_DIR}")

    if (
        not force
        and PARQUET.exists()
        and PARQUET.stat().st_mtime >= max(p.stat().st_mtime for p in sources)
    ):
        return pd.read_parquet(PARQUET)

    frames = [parse_workbook(p) for p in sources]
    df = pd.concat(frames, ignore_index=True)
    df["anio"] = df["anio"].astype("int16")
    df["nivel"] = df["nivel"].astype("int8")
    df["orden"] = df["orden"].astype("int16")
    df["valor"] = df["valor"].astype("float64")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PARQUET, index=False)

    meta = {
        "generado": pd.Timestamp.now().isoformat(timespec="seconds"),
        "filas": int(len(df)),
        "anios": [int(df.anio.min()), int(df.anio.max())],
        "conceptos": int(df[df.medida == "real"]["path"].nunique()),
        "medidas": {m["id"]: m["label"] for m in MEDIDAS},
        "fuente": "INEGI · SCNM · PIB Trimestral, año base 2018",
    }
    META_PATH.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return df


def load(force: bool = False) -> pd.DataFrame:
    return build(force=force)


if __name__ == "__main__":
    data = build(force="--force" in __import__("sys").argv)
    print(f"{len(data):,} filas · {data.medida.nunique()} medidas · "
          f"{data.anio.min()}–{data.anio.max()}")
    for medida in data.medida.unique():
        sub = data[(data.medida == medida) & (data.periodo == "Anual")]
        print(f"  {medida:20s} conceptos={sub.path.nunique():3d} "
              f"años={sub.anio.nunique():2d}")
