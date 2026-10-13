
-- queries/04_inflasi_energi.sql

SELECT
    i.bulan,
    i.provinsi_id,
    i.nilai_inflasi,
    e.*
        EXCLUDE (bulan, provinsi_id)
FROM inflasi.main.fact_inflasi AS i
LEFT JOIN energi.main.fact_energi AS e
    ON i.bulan = e.bulan
   AND i.provinsi_id = e.provinsi_id
ORDER BY
    i.bulan,
    i.provinsi_id;
