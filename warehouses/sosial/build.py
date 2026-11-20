
from pathlib import Path
import duckdb

from load import load_data


# ==================================================
# KONFIGURASI PATH
# ==================================================

ROOT = Path(__file__).resolve().parents[2]

DB_FILE = ROOT / "databases" / "sosial.duckdb"
SCHEMA_FILE = ROOT / "warehouses" / "sosial" / "schema.sql"

OUTPUT_DIR = ROOT / "data" / "sosial" / "parquet"


# ==================================================
# EKSPOR TABEL KE PARQUET
# ==================================================

def export_parquet(con):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tables = [
        "dim_provinsi",
        "dim_wilayah",
        "dim_periode",
        "fact_penduduk",
        "fact_pengeluaran_per_kapita",
    ]

    print("\n=== EKSPOR PARQUET SOSIAL ===")

    for table in tables:
        output_file = OUTPUT_DIR / f"{table}.parquet"
        output_path = output_file.as_posix().replace("'", "''")

        con.execute(f"""
            COPY "{table}"
            TO '{output_path}'
            (FORMAT PARQUET);
        """)

        print(f"Berhasil: {output_file}")


# ==================================================
# BUILD DATA WAREHOUSE SOSIAL
# ==================================================

def build():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(DB_FILE))

    try:
        con.execute("BEGIN TRANSACTION")

        # Hapus tabel warehouse lama agar build dapat diulang.
        for table in [
            "fact_pengeluaran_per_kapita",
            "fact_penduduk",
            "dim_wilayah",
            "dim_periode",
            "dim_provinsi",
            "warehouse_load_log",
        ]:
            con.execute(f'DROP TABLE IF EXISTS "{table}"')

        # Buat tabel sesuai skema baru.
        con.execute(SCHEMA_FILE.read_text(encoding="utf-8"))

        # Muat data yang telah dibersihkan.
        load_data(con)

        # Validasi jumlah baris.
        print("\n=== VALIDASI SOSIAL ===")

        tables = [
            "dim_provinsi",
            "dim_wilayah",
            "dim_periode",
            "fact_penduduk",
            "fact_pengeluaran_per_kapita",
        ]

        for table in tables:
            count = con.execute(
                f'SELECT COUNT(*) FROM "{table}"'
            ).fetchone()[0]

            print(f"{table}: {count} baris")

        # Simpan transaksi database.
        con.execute("COMMIT")

        print(f"\nDatabase berhasil dibuat: {DB_FILE}")

        # Ekspor tabel ke Parquet.
        export_parquet(con)

        print("\nBUILD SOSIAL SELESAI!")

    except Exception:
        con.execute("ROLLBACK")
        raise

    finally:
        con.close()


if __name__ == "__main__":
    build()
