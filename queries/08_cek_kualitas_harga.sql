-- Memeriksa harga pangan nol atau NULL

SELECT
    dk.nama_komoditas,
    COUNT(*) AS total_data,
    COUNT(*) FILTER (WHERE fp.harga = 0) AS harga_nol,
    COUNT(*) FILTER (WHERE fp.harga IS NULL) AS harga_kosong,
    COUNT(*) FILTER (WHERE fp.harga > 0) AS harga_valid
FROM pangan.main.fact_harga_pangan AS fp
JOIN pangan.main.dim_komoditas AS dk
    ON fp.komoditas_id = dk.komoditas_id
GROUP BY
    dk.nama_komoditas
ORDER BY
    dk.nama_komoditas;