ATTACH 'databases/ihk.duckdb' AS ihk_db;

SELECT
    dw.nama_provinsi,
    dt.bulan,
    dt.tahun,
    fi.inflasi_umum,
    ihk.nilai_ihk
FROM inflasi.main.fact_inflasi fi

JOIN inflasi.main.dim_wilayah dw
    ON fi.id_provinsi = dw.id_provinsi

JOIN inflasi.main.dim_waktu dt
    ON fi.id_waktu = dt.id_waktu

JOIN ihk_db.main.fact_ihk ihk
    ON fi.id_provinsi = ihk.provinsi_id

JOIN ihk_db.main.dim_bulan db
    ON ihk.bulan = db.bulan
    AND db.tahun = dt.tahun
    AND db.nomor_bulan = dt.bulan;