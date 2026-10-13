
from pathlib import Path

import duckdb

from load import load_data


ROOT = Path(__file__).resolve().parents[2]
DB_FILE = ROOT / "databases" / "pangan.duckdb"
SCHEMA_FILE = ROOT / "warehouses" / "pangan" / "schema.sql"


def build():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(DB_FILE))

    try:
        con.execute("BEGIN TRANSACTION")

        schema = SCHEMA_FILE.read_text(encoding="utf-8")
        con.execute(schema)

        load_data(con)

        print("\n=== VALIDASI DATABASE PANGAN ===")

        tabel = [
            "dim_provinsi",
            "dim_bulan",
            "dim_komoditas",
            "fact_harga_pangan",
        ]

        for nama_tabel in tabel:
            jumlah = con.execute(
                f"SELECT COUNT(*) FROM {nama_tabel}"
            ).fetchone()[0]

            print(f"{nama_tabel}: {jumlah:,} baris")

        duplikat = con.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT bulan, provinsi_id, komoditas_id
                FROM fact_harga_pangan
                GROUP BY bulan, provinsi_id, komoditas_id
                HAVING COUNT(*) > 1
            ) AS d
        """).fetchone()[0]

        assert duplikat == 0, "Ada fakta duplikat!"

        con.execute("COMMIT")
        print(f"\nDatabase berhasil dibangun: {DB_FILE}")

    except Exception:
        con.execute("ROLLBACK")
        raise

    finally:
        con.close()


if __name__ == "__main__":
    build()
