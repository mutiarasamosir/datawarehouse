-- KPI inflasi umum tahun 2025

SELECT
    t.tahun,
    COUNT(*) AS jumlah_data,
    ROUND(AVG(f.inflasi_umum), 2) AS rata_rata_inflasi,
    ROUND(MIN(f.inflasi_umum), 2) AS inflasi_terendah,
    ROUND(MAX(f.inflasi_umum), 2) AS inflasi_tertinggi
FROM inflasi.main.fact_inflasi AS f
JOIN inflasi.main.dim_waktu AS t
    ON f.id_waktu = t.id_waktu
GROUP BY
    t.tahun
ORDER BY
    t.tahun;