
from pathlib import Path
import re

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "raw" / "ekonomi"
DB_DIR = ROOT / "warehouses"
DB_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "ump": "Upah Minimum Provinsi",
    "tpt": "Tingkat Pengangguran Terbuka",
    "tpak": "Persentase Angkatan Kerja",
    "upah": "Rata-Rata Upah",
}


def find_file(keyword):
    matches = [
        f for f in DATA_DIR.glob("*.csv")
        if keyword.lower() in f.name.lower()
    ]

    if len(matches) != 1:
        raise FileNotFoundError(
            f"Keyword '{keyword}' cocok dengan {len(matches)} file."
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

    # Buang kolom kosong akibat ekspor spreadsheet.
    df = df.loc[
        :, ~df.columns.astype(str).str.startswith("Unnamed:")
    ].copy()

    # Buang baris yang seluruh nilainya kosong.
    df = df.dropna(how="all").reset_index(drop=True)

    # Rapikan nilai teks dan tanda data tidak tersedia.
    for col in df.columns:
        df[col] = df[col].astype("string").str.strip()
        df[col] = df[col].replace(
            {"-": pd.NA, "—": pd.NA, "": pd.NA}
        )

    return df


def clean_name(name):
    name = re.sub(
        r"[^a-zA-Z0-9]+", "_", str(name).strip().lower()
    ).strip("_") or "kolom"

    if name[0].isdigit():
        name = "kolom_" + name

    return name


def make_unique(columns):
    result = []
    seen = {}

    for col in columns:
        base = clean_name(col)
        seen[base] = seen.get(base, 0) + 1
        result.append(
            base if seen[base] == 1
            else f"{base}_{seen[base]}"
        )

    return result


def to_number(series):
    # Konversi nilai numerik; teks yang tidak valid menjadi NULL.
    values = series.astype("string").str.strip()
    values = values.str.replace(",", ".", regex=False)
    return pd.to_numeric(values, errors="coerce")


def prepare_table(table, df):
    # Header dinormalisasi berdasarkan posisi kolom.
    if table == "ump":
        if len(df.columns) != 2:
            raise ValueError("Struktur CSV UMP tidak sesuai.")

        df.columns = ["wilayah_sumber", "ump_rupiah"]

        # Contoh: '11 Aceh' menjadi kode '11' dan provinsi 'Aceh'.
        parts = df["wilayah_sumber"].str.extract(
            r"^\s*(\d{2})\s+(.+?)\s*$"
        )

        df.insert(0, "kode_provinsi", parts[0])
        df["provinsi"] = parts[1].fillna(
            df["wilayah_sumber"]
        )
        df = df.drop(columns=["wilayah_sumber"])

        df["ump_rupiah"] = to_number(df["ump_rupiah"])

    elif table in ("tpt", "tpak"):
        expected = (
            ["provinsi", "februari", "agustus", "tahunan"]
            if table == "tpt"
            else ["provinsi", "februari", "agustus"]
        )

        if len(df.columns) != len(expected):
            raise ValueError(
                f"Jumlah kolom {table} tidak sesuai: {len(df.columns)}"
            )

        df.columns = expected

        for col in expected[1:]:
            df[col] = to_number(df[col])

    elif table == "upah":
        expected = [
            "sektor", "februari", "mei", "agustus", "november"
        ]

        if len(df.columns) != len(expected):
            raise ValueError(
                f"Jumlah kolom upah tidak sesuai: {len(df.columns)}"
            )

        df.columns = expected

        for col in expected[1:]:
            df[col] = to_number(df[col])

    return df


def main():
    db_path = DB_DIR / "ekonomi.duckdb"
    con = duckdb.connect(str(db_path))

    try:
        for table, keyword in FILES.items():
            file = find_file(keyword)
            df = read_csv(file)
            df = prepare_table(table, df)
            df.columns = make_unique(df.columns)

            if df.empty:
                raise ValueError(f"Tidak ada data: {file.name}")

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
