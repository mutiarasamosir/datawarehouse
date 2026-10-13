
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
files = list(ROOT.rglob("data_pangan.xlsx"))

if not files:
    raise FileNotFoundError(
        "File data_pangan.xlsx tidak ditemukan di project."
    )

file_path = files[0]

print("Lokasi file:", file_path)

xls = pd.ExcelFile(file_path)
print("Daftar sheet:", xls.sheet_names)

for sheet in xls.sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet)

    print("\n" + "=" * 60)
    print("SHEET:", sheet)
    print("Ukuran data:", df.shape)
    print("Nama kolom:", df.columns.tolist())

    print("\n5 baris pertama:")
    print(df.head().to_string())

    print("\nTipe data:")
    print(df.dtypes)
