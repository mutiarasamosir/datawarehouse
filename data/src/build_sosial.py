
from pathlib import Path
import re

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "raw" / "sosial"
DB_DIR = ROOT / "warehouses"
DB_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "penduduk": "Penduduk, Laju Pertumbuhan Penduduk",
    "pengeluaran_per_kapita": "Pengeluaran per Kapita",
}


def find_file(keyword):
    matches = [
        f for f in DATA_DIR.glob("*.csv")
        if keyword.lower() in f.name.lower()
    ]

    if len(matches) != 1:
        raise FileNotFoundError(
            f"Keyword '{keyword}' cocok dengan "
            f"{len(matches)} file."
        )

    return matches[0]


def read_csv(file):
    df = pd.read_csv(
        file,
        sep=None,
        engine="python",
        dtype=str,
        encoding="utf-8-sig",
    )

    # Buang kolom kosong dari ekspor spreadsheet
    df = df.loc[
        :, ~df.columns.astype(str).str.startswith("Unnamed:")
    ].copy()

    df = df.dropna(how="all").reset_index(drop=True)

    for col in df.columns:
        df[col] = df[col].astype("string").str.strip()
        df[col] = df[col].replace(
            {"-": pd.NA, "—": pd.NA, "": pd.NA}
        )

    return df


def to_number(series):
    values = series.astype("string").str.strip()
    values = values.str.replace(",", ".", regex=False)
    return pd.to_numeric(values, errors="coerce")


def clean_name(name):
    name = re.sub(
        r"[^a-zA-Z0-9]+", "_", str(name).strip().lower()
    ).strip("_") or "kolom"

    if name[0].isdigit():
        name = "kolom_" + name

    return name


def prepare_table(table, df):
    if table == "penduduk":
        expected = [
            "provinsi",
            "jumlah_penduduk_ribu",
            "laju_pertumbuhan_penduduk_per_tahun",
            "persentase_penduduk",
            "kepadatan_penduduk_per_km2",
            "rasio_jenis_kelamin_penduduk",
        ]

        if len(df.columns) != 6:
            raise ValueError(
                f"Data penduduk seharusnya 6 kolom, "
                f"ditemukan {len(df.columns)}."
            )

        df.columns = expected

        numeric_cols = expected[1:]

        for col in numeric_cols:
            df[col] = to_number(df[col])

    elif table == "pengeluaran_per_kapita":
        expected = ["wilayah", "laki_laki", "perempuan"]

        if len(df.columns) != 3:
            raise ValueError(
                f"Data pengeluaran seharusnya 3 kolom, "
                f"ditemukan {len(df.columns)}."
            )

        df.columns = expected

        for col in ["laki_laki", "perempuan"]:
            df[col] = to_number(df[col])

    df.columns = [clean_name(col) for col in df.columns]

    return df


def main():
    db_path = DB_DIR / "sosial.duckdb"
    con = duckdb.connect(str(db_path))

    try:
        for table, keyword in FILES.items():
            file = find_file(keyword)
            df = read_csv(file)
            df = prepare_table(table, df)

            if df.empty:
                raise ValueError(f"Data kosong: {file.name}")

            con.register("source_df", df)
            con.execute(
                f'CREATE OR REPLACE TABLE "{table}" '
                "AS SELECT * FROM source_df"
            )
            con.unregister("source_df")

            print(f"\nTabel: {table}")
            print(f"File: {file.name}")
            print(f"Jumlah baris: {len(df)}")
            print(f"Kolom: {list(df.columns)}")

        print(f"\nBuild selesai: {db_path}")

    finally:
        con.close()


if __name__ == "__main__":
    main()
