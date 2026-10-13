-- Analisis inflasi bulanan per provinsi tahun 2025

SELECT
    w.nama_provinsi,
    t.tahun,
    t.bulan,
    f.inflasi_umum
FROM inflasi.main.fact_inflasi AS f
JOIN inflasi.main.dim_wilayah AS w
    ON f.id_provinsi = w.id_provinsi
JOIN inflasi.main.dim_waktu AS t
    ON f.id_waktu = t.id_waktu
ORDER BY
    w.nama_provinsi,
    t.tahun,
    t.bulan;