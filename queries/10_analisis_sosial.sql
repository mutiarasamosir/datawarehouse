-- Analisis jumlah dan kepadatan penduduk per provinsi

SELECT
    dp.nama_provinsi,
    dper.tahun,
    dper.periode,
    fp.jumlah_penduduk_ribu,
    fp.laju_pertumbuhan,
    fp.persentase_penduduk,
    fp.kepadatan_penduduk,
    fp.rasio_jenis_kelamin
FROM sosial.main.fact_penduduk AS fp
JOIN sosial.main.dim_provinsi AS dp
    ON fp.provinsi_id = dp.provinsi_id
JOIN sosial.main.dim_periode AS dper
    ON fp.periode_id = dper.periode_id
ORDER BY
    dp.nama_provinsi,
    dper.tahun,
    dper.periode;