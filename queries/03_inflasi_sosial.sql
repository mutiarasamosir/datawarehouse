
-- queries/03_inflasi_sosial.sql

SELECT
    i.bulan,
    i.provinsi_id,
    i.nilai_inflasi,
    s.*
        EXCLUDE (bulan, provinsi_id)
FROM inflasi.main.fact_inflasi AS i
LEFT JOIN sosial.main.fact_sosial AS s
    ON i.bulan = s.bulan
   AND i.provinsi_id = s.provinsi_id
ORDER BY
    i.bulan,
    i.provinsi_id;