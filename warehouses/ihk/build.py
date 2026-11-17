
from pathlib import Path

import duckdb

from load import load_data


ROOT = Path(__file__).resolve().parents[2]

DB_PATH = ROOT / "databases" / "ihk.duckdb"
SCHEMA_PATH = ROOT / "warehouses" / "ihk" / "schema.sql"


def build_database():
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Schema tidak ditemukan: {SCHEMA_PATH}"
        )

    # Buat koneksi database
    con = duckdb.connect(str(DB_PATH))

    try:
        con.execute("BEGIN TRANSACTION")

        # Jalankan schema
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        con.execute(schema_sql)

        # Jalankan proses loading
        load_data(con)

        # Validasi jumlah data
        jumlah_provinsi = con.execute(
            "SELECT COUNT(*) FROM dim_provinsi"
        ).fetchone()[0]

        jumlah_bulan = con.execute(
            "SELECT COUNT(*) FROM dim_bulan"
        ).fetchone()[0]

        jumlah_fakta = con.execute(
            "SELECT COUNT(*) FROM fact_ihk"
        ).fetchone()[0]

        print("\n===== VALIDASI DATABASE IHK =====")
        print("Jumlah provinsi:", jumlah_provinsi)
        print("Jumlah bulan:", jumlah_bulan)
        print("Jumlah fakta:", jumlah_fakta)

        # Validasi hasil yang diharapkan
        if jumlah_provinsi != 38:
            raise ValueError("Jumlah provinsi seharusnya 38.")

        if jumlah_bulan != 12:
            raise ValueError("Jumlah bulan seharusnya 12.")

        if jumlah_fakta != 456:
            raise ValueError("Jumlah fakta seharusnya 456.")

        con.execute("COMMIT")

        print("\nDatabase IHK berhasil dibangun!")
        print("Lokasi:", DB_PATH)

    except Exception:
        con.execute("ROLLBACK")
        raise

    finally:
        con.close()


if __name__ == "__main__":
    build_database()
