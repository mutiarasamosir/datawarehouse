
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

for domain in ["ekonomi", "sosial"]:
    folder = ROOT / "data" / domain

    print("\n" + "=" * 70)
    print(f"DOMAIN: {domain.upper()}")
    print("=" * 70)

    for file in sorted(folder.glob("*.xlsx")):
        print(f"\nFILE: {file.name}")

        try:
            sheets = pd.read_excel(file, sheet_name=None)

            for sheet_name, df in sheets.items():
                print(f"\nSHEET: {sheet_name}")
                print(f"Jumlah baris: {len(df)}")
                print(f"Jumlah kolom: {len(df.columns)}")
                print("Kolom:")
                print(df.columns.tolist())

                print("\nContoh data:")
                print(df.head(5).to_string(index=False))

                print("\nJumlah nilai kosong per kolom:")
                print(df.isna().sum().to_string())

                numeric = df.select_dtypes(include="number")
                print("\nJumlah nilai nol per kolom numerik:")
                print((numeric == 0).sum().to_string())

        except Exception as e:
            print(f"Gagal membaca file: {e}")
