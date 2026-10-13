
from pathlib import Path

import duckdb

from load import load_data


ROOT = Path(__file__).resolve().parents[2]
DB_FILE = ROOT / "databases" / "bencana.duckdb"
SCHEMA_FILE = ROOT / "warehouses" / "bencana" / "schema.sql"


def build():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Bangun ulang dari nol: hapus database lama jika ada.
    # (DuckDB menolak DELETE pada tabel induk yang masih
    # direferensikan foreign key, jadi tabel tidak bisa
    # dikosongkan lalu diisi ulang pada database yang sama.)
    DB_FILE.unlink(missing_ok=True)

    con = duckdb.connect(str(DB_FILE))

    try:
        con.execute("BEGIN TRANSACTION")

        schema = SCHEMA_FILE.read_text(encoding="utf-8")
        con.execute(schema)

        load_data(con)

        print("\n=== VALIDASI WAREHOUSE BENCANA ===")

        for tabel in [
            "dim_provinsi",
            "dim_bulan",
            "dim_jenis_bencana",
            "fact_bencana",
        ]:
            jumlah = con.execute(
                f"SELECT COUNT(*) FROM {tabel}"
            ).fetchone()[0]
            print(f"{tabel}: {jumlah:,} baris")

        duplikat = con.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT bulan, provinsi_id, jenis_bencana_id
                FROM fact_bencana
                GROUP BY bulan, provinsi_id, jenis_bencana_id
                HAVING COUNT(*) > 1
            ) AS d
        """).fetchone()[0]

        assert duplikat == 0, "Ada fakta duplikat!"

        con.execute("COMMIT")
        print(f"\nDatabase berhasil dibuat: {DB_FILE}")

    except Exception:
        con.execute("ROLLBACK")
        raise

    finally:
        con.close()


if __name__ == "__main__":
    build()
