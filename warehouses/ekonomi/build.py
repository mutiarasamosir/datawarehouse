
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
        con.execute(SCHEMA_FILE.read_text(encoding="utf-8"))
        load_data(con)

        print("\n=== VALIDASI EKONOMI ===")
        logs = con.execute("""
            SELECT source_file, target_table, row_count
            FROM warehouse_load_log
            ORDER BY source_file
        """).fetchall()

        for source_file, table, rows in logs:
            print(f"{source_file} -> {table}: {rows} baris")

        print("Jumlah dataset:", len(logs))
        con.execute("COMMIT")
        print(f"\nDatabase berhasil dibuat: {DB_FILE}")

    except Exception:
        con.execute("ROLLBACK")
        raise

    finally:
        con.close()


if __name__ == "__main__":
    build()
