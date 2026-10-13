
from pathlib import Path
import sys

import duckdb

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from load import process_and_load_inflasi


def main():
    db_path = ROOT / "databases" / "inflasi.duckdb"
    schema_path = ROOT / "warehouses" / "inflasi" / "schema.sql"
    data_file = (
        ROOT
        / "data"
        / "inflasi"
        / "Inflasi Tahunan (Y-on-Y) 38 Provinsi (2022=100), 2025 (1).xlsx"
    )

    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Gunakan transaksi agar perubahan bisa dibatalkan jika gagal.
    con = duckdb.connect(str(db_path))

    try:
        con.execute("BEGIN TRANSACTION")

        con.execute(schema_path.read_text(encoding="utf-8"))

        # Muat data setelah tabel tersedia.
        process_and_load_inflasi(con, data_file)

        # Validasi hasil sebelum commit.
        for tabel in ("dim_wilayah", "dim_waktu", "fact_inflasi"):
            jumlah = con.execute(
                f"SELECT COUNT(*) FROM {tabel}"
            ).fetchone()[0]
            print(f"{tabel}: {jumlah} baris")

        con.execute("COMMIT")
        print(f"\nWarehouse inflasi berhasil dibangun: {db_path}")

    except Exception:
        con.execute("ROLLBACK")
        raise

    finally:
        con.close()


if __name__ == "__main__":
    main()