
-- queries/05_inflasi_bencana.sql

WITH bencana_agregat AS (
    SELECT
        bulan,
        provinsi_id,
        COUNT(*) AS jumlah_kategori_bencana_tercatat
    FROM bencana.main.fact_bencana
    GROUP BY bulan, provinsi_id
)
SELECT
    i.bulan,
    i.provinsi_id,
    i.nilai_inflasi,
    b.jumlah_kategori_bencana_tercatat
FROM inflasi.main.fact_inflasi AS i
LEFT JOIN bencana_agregat AS b
    ON i.bulan = b.bulan
   AND i.provinsi_id = b.provinsi_id
ORDER BY
    i.bulan,
    i.provinsi_id;