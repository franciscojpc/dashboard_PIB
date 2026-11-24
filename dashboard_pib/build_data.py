"""Regenera la caché ``data/pib.parquet`` a partir de los tabulados de INEGI."""

from __future__ import annotations

import sys

from pib_data import build


def main() -> None:
    df = build(force="--force" in sys.argv)
    print(
        f"{len(df):,} registros · {df.medida.nunique()} medidas · "
        f"{df.anio.min()}–{df.anio.max()}"
    )
    for medida, group in df.groupby("medida", sort=False):
        anual = group[group.periodo == "Anual"]
        print(
            f"  {medida:22s} conceptos={anual.path.nunique():3d} "
            f"años={anual.anio.nunique():2d}"
        )


if __name__ == "__main__":
    main()
