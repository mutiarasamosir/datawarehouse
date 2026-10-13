
-- queries/06_kpi_inflasi.sql

SELECT
    COUNT(*) AS jumlah_observasi,
    AVG(nilai_inflasi) AS rata_rata_inflasi,
    MIN(nilai_inflasi) AS inflasi_terendah,
    MAX(nilai_inflasi) AS inflasi_tertinggi
FROM inflasi.main.fact_inflasi;