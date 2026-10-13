
from pathlib import Path
import duckdb

from load import load_data


ROOT = Path(__file__).resolve().parents[2]
DB_FILE = ROOT / "databases" / "ekonomi.duckdb"
SCHEMA_FILE = ROOT / "warehouses" / "ekonomi" / "schema.sql"


def build():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(DB_FILE))

    try:
        con.execute("BEGIN TRANSACTION")

        # Bersihkan tabel lama agar build dapat diulang.
        for table in [
            "fact_tpak",
            "fact_tpt",
            "fact_upah_sektor",
            "fact_ump",
            "dim_sektor",
            "dim_periode",
            "dim_provinsi",
            "warehouse_load_log",
        ]:
            con.execute(f'DROP TABLE IF EXISTS "{table}"')

        # Buat skema baru.
        con.execute(SCHEMA_FILE.read_text(encoding="utf-8"))

        # Muat dan transformasikan data.
        load_data(con)

        print("\n=== VALIDASI EKONOMI ===")

        for table in [
            "dim_provinsi",
            "dim_periode",
            "dim_sektor",
            "fact_tpak",
            "fact_tpt",
            "fact_upah_sektor",
            "fact_ump",
        ]:
            count = con.execute(
                f'SELECT COUNT(*) FROM "{table}"'
            ).fetchone()[0]
            print(f"{table}: {count} baris")

        con.execute("COMMIT")
        print(f"\nDatabase berhasil dibuat: {DB_FILE}")

    except Exception:
        con.execute("ROLLBACK")
        raise

    finally:
        con.close()


if __name__ == "__main__":
    build()
