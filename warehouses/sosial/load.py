
from pathlib import Path
import re
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "sosial"


def safe_name(value):
    name = str(value).strip().lower()
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    if not name:
        name = "kolom"
    if name[0].isdigit():
        name = "col_" + name
    return name


def clean_columns(columns):
    result = []
    used = set()

    for column in columns:
        base = safe_name(column)
        name = base
        suffix = 2

        while name in used:
            name = f"{base}_{suffix}"
            suffix += 1

        result.append(name)
        used.add(name)

    return result


def load_data(con):
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Folder tidak ditemukan: {DATA_DIR}")

    files = sorted(DATA_DIR.glob("*.xlsx"))
    if not files:
        raise FileNotFoundError(f"Tidak ada file Excel di {DATA_DIR}")

    con.execute("DELETE FROM warehouse_load_log")

    for file in files:
        excel = pd.ExcelFile(file)

        for sheet in excel.sheet_names:
            df = pd.read_excel(file, sheet_name=sheet)
            df.columns = clean_columns(df.columns)

            table = safe_name(file.stem + "_" + sheet)
            view = "tmp_source_sosial"

            con.register(view, df)

            try:
                con.execute(
                    f'CREATE OR REPLACE TABLE "{table}" AS '
                    f'SELECT * FROM "{view}"'
                )
            finally:
                con.unregister(view)

            con.execute(
                """
                INSERT INTO warehouse_load_log
                (source_file, source_sheet, target_table, row_count)
                VALUES (?, ?, ?, ?)
                """,
                [file.name, sheet, table, len(df)],
            )

            print(f"{table}: {len(df)} baris")
