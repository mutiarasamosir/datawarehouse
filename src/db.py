# Membuka koneksi DuckDB dan menghubungkan seluruh database domain yang tersedia.

import duckdb
from src.config import DATABASES

def get_connection(read_only=True):
    main_db = DATABASES["inflasi"]

    if not main_db.exists():
        raise FileNotFoundError(
            f"Database utama tidak ditemukan: {main_db}")

    con = duckdb.connect(
        str(main_db),
        read_only=read_only,)

    try:
        for alias, db_path in DATABASES.items():
            if alias == "inflasi":
                continue
            if not db_path.exists():
                raise FileNotFoundError(
                    f"Database {alias} tidak ditemukan: {db_path}")
            con.execute(
                f"ATTACH '{db_path.as_posix()}' AS {alias} "
                " (READ_ONLY)")
        return con

    except Exception:
        con.close()
        raise