-- Analisis indikator ekonomi per provinsi dan periode


-- Analisis indikator ekonomi per provinsi dan periode
-- UMP tahunan digabungkan berdasarkan provinsi

SELECT
    dp.nama_provinsi,
    dper.tahun,
    dper.periode,
    tpt.nilai_tpt,
    tpak.nilai_tpak,
    ump.nilai_ump
FROM ekonomi.main.dim_provinsi AS dp
JOIN ekonomi.main.fact_tpt AS tpt
    ON dp.provinsi_id = tpt.provinsi_id
JOIN ekonomi.main.dim_periode AS dper
    ON tpt.periode_id = dper.periode_id
LEFT JOIN ekonomi.main.fact_tpak AS tpak
    ON tpt.provinsi_id = tpak.provinsi_id
    AND tpt.periode_id = tpak.periode_id
LEFT JOIN ekonomi.main.fact_ump AS ump
    ON tpt.provinsi_id = ump.provinsi_id
ORDER BY
    dp.nama_provinsi,
    dper.tahun,
    dper.periode;