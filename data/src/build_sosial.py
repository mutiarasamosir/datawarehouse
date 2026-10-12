
from pathlib import Path
import duckdb
import pandas as pd
import re

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "raw" / "sosial"
DB_DIR = ROOT / "warehouses"

DB_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "penduduk": "Penduduk, Laju Pertumbuhan Penduduk",
    "pengeluaran_per_kapita": "Pengeluaran per Kapita",
}


def clean_columns(df):
    df = df.dropna(how="all")
    df = df.loc[
        :, ~df.columns.astype(str).str.startswith("Unnamed:")
    ].copy()

    columns = []
    used = set()

    for col in df.columns:
        name = re.sub(
            r"[^a-zA-Z0-9]+", "_", str(col).strip().lower()
        ).strip("_") or "kolom"

        if name[0].isdigit():
            name = "kolom_" + name

        base = name
        i = 2
        while name in used:
            name = f"{base}_{i}"
            i += 1

        used.add(name)
        columns.append(name)

    df.columns = columns
    return df


def main():
    csv_files = list(DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"Tidak ada file CSV di {DATA_DIR}"
        )

    db_path = DB_DIR / "sosial.duckdb"
    con = duckdb.connect(str(db_path))

    try:
        for table, keyword in FILES.items():
            matches = [
                f for f in csv_files
                if keyword.lower() in f.name.lower()
            ]

            if len(matches) != 1:
                raise ValueError(
                    f"File untuk {table} tidak ditemukan "
                    f"atau ditemukan lebih dari satu: {keyword}"
                )

            file = matches[0]
            df = pd.read_csv(file, sep=None, engine="python")
            df = clean_columns(df)

            if df.empty:
                raise ValueError(f"Data kosong: {file.name}")

            con.register("source_df", df)
            con.execute(
                f'CREATE OR REPLACE TABLE "{table}" '
                "AS SELECT * FROM source_df"
            )
            con.unregister("source_df")

            print(
                f"Berhasil: {table} | {len(df)} baris | "
                f"{len(df.columns)} kolom"
            )

        print(f"\nDatabase berhasil dibuat: {db_path}")

    finally:
        con.close()


if __name__ == "__main__":
    main()
