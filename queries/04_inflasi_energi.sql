-- Analisis inflasi energi per provinsi dan bulan

SELECT
    dp.provinsi,
    db.tahun,
    db.nomor_bulan AS bulan,
    fe.nilai_inflasi
FROM energi.main.fact_inflasi_energi AS fe
JOIN energi.main.dim_provinsi AS dp
    ON fe.provinsi_id = dp.provinsi_id
JOIN energi.main.dim_bulan AS db
    ON fe.bulan = db.bulan
ORDER BY
    dp.provinsi,
    db.tahun,
    db.nomor_bulan;