
# Koneksi DuckDB:
# analytics menjadi database utama (READ-WRITE).
# Seluruh database domain menjadi sumber (READ-ONLY).

import duckdb

from src.config import DATABASES


def get_connection():

    analytics_db = DATABASES["analytics"]

    # Pastikan folder database tersedia.
    analytics_db.parent.mkdir(parents=True, exist_ok=True)

    # Buat file analytics jika belum tersedia.
    if not analytics_db.exists():
        temp_con = duckdb.connect(str(analytics_db))
        temp_con.close()

    # PENTING:
    # Analytics menjadi database utama dan bisa ditulis.
    con = duckdb.connect(str(analytics_db))

    try:
        # Attach seluruh database sumber sebagai READ-ONLY.
        for alias, path in DATABASES.items():

            if alias == "analytics":
                continue

            if not path.exists():
                raise FileNotFoundError(
                    f"Database {alias} tidak ditemukan: {path}"
                )

            escaped_path = path.as_posix().replace("'", "''")

            con.execute(
                f"ATTACH '{escaped_path}' AS {alias} (READ_ONLY)"
            )

        return con

    except Exception:
        con.close()
        raise