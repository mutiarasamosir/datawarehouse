
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"

for domain in ["ekonomi", "sosial"]:
    folder = RAW / domain

    print(f"\n{'=' * 60}")
    print(f"DOMAIN: {domain.upper()}")
    print("=" * 60)

    for file in sorted(folder.glob("*.csv")):
        print(f"\nFILE: {file.name}")

        try:
            df = pd.read_csv(
                file,
                header=None,
                dtype=str,
                sep=None,
                engine="python",
                nrows=8,
                encoding="utf-8-sig",
            )

            print(df.to_string(index=False, header=False))
        except Exception as exc:
            print(f"Gagal membaca file: {exc}")
