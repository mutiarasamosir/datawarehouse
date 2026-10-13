-- KPI harga pangan berdasarkan harga positif

SELECT
    dk.nama_komoditas,
    COUNT(*) AS jumlah_data_valid,
    ROUND(AVG(fp.harga), 2) AS rata_rata_harga,
    MIN(fp.harga) AS harga_terendah,
    MAX(fp.harga) AS harga_tertinggi
FROM pangan.main.fact_harga_pangan AS fp
JOIN pangan.main.dim_komoditas AS dk
    ON fp.komoditas_id = dk.komoditas_id
WHERE fp.harga > 0
GROUP BY
    dk.nama_komoditas
ORDER BY
    rata_rata_harga DESC;