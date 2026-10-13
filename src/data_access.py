
import pandas as pd
from src.db import get_connection

def query_df(sql, params=None):
    con = get_connection()
    try:
        return con.execute(
            sql,
            params or []
        ).fetchdf()
    finally:
        con.close()

def get_data_inflasi():
    sql = """
        SELECT *
        FROM inflasi.main.nama_tabel_inflasi
    """
    return query_df(sql)


def get_kpi_inflasi():
    sql = """
        SELECT
            COUNT(*) AS jumlah_observasi,
            AVG(nilai_inflasi) AS rata_rata_inflasi,
            MIN(nilai_inflasi) AS inflasi_terendah,
            MAX(nilai_inflasi) AS inflasi_tertinggi
        FROM inflasi.main.nama_tabel_inflasi
    """
    return query_df(sql)