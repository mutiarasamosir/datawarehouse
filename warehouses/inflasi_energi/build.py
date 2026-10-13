
from pathlib import Path

import duckdb

from load import load_data


ROOT = Path(__file__).resolve().parents[2]
DB_FILE = ROOT / "databases" / "inflasi_energi.duckdb"
SCHEMA_FILE = ROOT / "warehouses" / "inflasi_energi" / "schema.sql"


def build():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(DB_FILE))

    try:
        con.execute("BEGIN TRANSACTION")

        schema = SCHEMA_FILE.read_text(encoding="utf-8")
        con.execute(schema)

        load_data(con)

        print("\n=== VALIDASI WAREHOUSE ENERGI ===")

        for tabel in [
            "dim_provinsi",
            "dim_bulan",
            "fact_inflasi_energi",
        ]:
            jumlah = con.execute(
                f"SELECT COUNT(*) FROM {tabel}"
            ).fetchone()[0]
            print(f"{tabel}: {jumlah:,} baris")

        duplikat = con.execute("""
            SELECT COUNT(*)
            FROM (
                SELECT bulan, provinsi_id
                FROM fact_inflasi_energi
                GROUP BY bulan, provinsi_id
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
