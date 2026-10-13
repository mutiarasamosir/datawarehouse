-- Analisis harga pangan per provinsi dan bulan

SELECT
    dp.provinsi,
    db.bulan,
    dk.nama_komoditas,
    fp.harga
FROM pangan.main.fact_harga_pangan AS fp
JOIN pangan.main.dim_provinsi AS dp
    ON fp.provinsi_id = dp.provinsi_id
JOIN pangan.main.dim_bulan AS db
    ON fp.bulan = db.bulan
JOIN pangan.main.dim_komoditas AS dk
    ON fp.komoditas_id = dk.komoditas_id
ORDER BY
    dp.provinsi,
    db.bulan,
    dk.nama_komoditas;