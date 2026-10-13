# Membuka koneksi DuckDB dan menghubungkan seluruh database domain yang tersedia.

import duckdb

from src.config import DATABASES

def get_connection():
    main_db = DATABASES["inflasi"]

    if not main_db.exists():
        raise FileNotFoundError(
            f"Database utama tidak ditemukan: {main_db}"
        )

    con = duckdb.connect(
        str(main_db),
        read_only=True,
    )

    try:
        for alias, path in DATABASES.items():
            if alias == "inflasi":
                continue

            if not path.exists():
                raise FileNotFoundError(
                    f"Database {alias} tidak ditemukan: {path}"
                )

            escaped_path = path.as_posix().replace("'", "''")

            con.execute(
                f"ATTACH '{escaped_path}' AS {alias} "
                "(READ_ONLY)"
            )

        return con

    except Exception:
        con.close()
        raise