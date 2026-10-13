-- Ringkasan inflasi dan dampak bencana per provinsi/bulan

WITH bencana_bulanan AS (
    SELECT
        dp.provinsi,
        fb.bulan,
        SUM(fb.jumlah_kejadian) AS jumlah_kejadian,
        SUM(fb.korban_meninggal) AS korban_meninggal,
        SUM(fb.korban_luka) AS korban_luka
    FROM bencana.main.fact_bencana AS fb
    JOIN bencana.main.dim_provinsi AS dp
        ON fb.provinsi_id = dp.provinsi_id
    GROUP BY
        dp.provinsi,
        fb.bulan
)
SELECT
    w.nama_provinsi,
    tw.tahun,
    tw.bulan,
    COALESCE(bb.jumlah_kejadian, 0) AS jumlah_kejadian,
    COALESCE(bb.korban_meninggal, 0) AS korban_meninggal,
    COALESCE(bb.korban_luka, 0) AS korban_luka,
    fi.inflasi_umum
FROM inflasi.main.fact_inflasi AS fi
JOIN inflasi.main.dim_wilayah AS w
    ON fi.id_provinsi = w.id_provinsi
JOIN inflasi.main.dim_waktu AS tw
    ON fi.id_waktu = tw.id_waktu
LEFT JOIN bencana_bulanan AS bb
    ON UPPER(TRIM(w.nama_provinsi)) = UPPER(TRIM(bb.provinsi))
    AND MAKE_DATE(tw.tahun, tw.bulan, 1) = bb.bulan
ORDER BY
    w.nama_provinsi,
    tw.tahun,
    tw.bulan;