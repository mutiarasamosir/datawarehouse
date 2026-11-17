
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parent

inflasi_db = ROOT / "databases" / "inflasi.duckdb"
ihk_db = ROOT / "databases" / "ihk.duckdb"

con = duckdb.connect(str(inflasi_db))

try:
    con.execute(
        f"ATTACH '{ihk_db.as_posix()}' AS ihk_db (READ_ONLY)"
    )

    query = """
    SELECT
        dw.nama_provinsi,
        dt.bulan,
        dt.tahun,
        fi.inflasi_umum,
        fihk.nilai_ihk
    FROM fact_inflasi fi
    JOIN dim_wilayah dw
        ON fi.id_provinsi = dw.id_provinsi
    JOIN dim_waktu dt
        ON fi.id_waktu = dt.id_waktu
    JOIN ihk_db.main.fact_ihk fihk
        ON fi.id_provinsi = fihk.provinsi_id
    JOIN ihk_db.main.dim_bulan db
        ON fihk.bulan = db.bulan
        AND db.tahun = dt.tahun
        AND db.nomor_bulan = dt.bulan
    ORDER BY dw.nama_provinsi, dt.tahun, dt.bulan
    """

    hasil = con.execute(query).df()

    print("Jumlah data hasil integrasi:", len(hasil))
    print("\nSampel hasil integrasi:")
    print(hasil.head(10))

    print("\nProvinsi yang terintegrasi:")
    print(hasil["nama_provinsi"].nunique())

finally:
    con.close()
