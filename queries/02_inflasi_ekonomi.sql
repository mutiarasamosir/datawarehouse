-- queries/02_inflasi_ekonomi.sql

SELECT
    i.bulan,
    i.provinsi_id,
    i.nilai_inflasi,
    e.*
        EXCLUDE (bulan, provinsi_id)
FROM inflasi.main.fact_inflasi AS i
LEFT JOIN ekonomi.main.fact_ekonomi AS e
    ON i.bulan = e.bulan
   AND i.provinsi_id = e.provinsi_id
ORDER BY
    i.bulan,
    i.provinsi_id;