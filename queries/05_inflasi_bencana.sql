
-- Ringkasan inflasi dan dampak bencana berdasarkan provinsi, bulan, dan jenis bencana

WITH bencana_bulanan AS (
    SELECT
        dp.provinsi,
        db.tahun,
        db.nomor_bulan AS bulan,
        dj.jenis_bencana,
        SUM(COALESCE(fb.jumlah_kejadian, 0)) AS jumlah_kejadian,
        SUM(COALESCE(fb.korban_meninggal, 0)) AS korban_meninggal,
        SUM(COALESCE(fb.korban_luka, 0)) AS korban_luka
    FROM bencana.main.fact_bencana AS fb
    JOIN bencana.main.dim_provinsi AS dp
        ON fb.provinsi_id = dp.provinsi_id
    JOIN bencana.main.dim_jenis_bencana AS dj
        ON fb.jenis_bencana_id = dj.jenis_bencana_id
    JOIN bencana.main.dim_bulan AS db
        ON fb.bulan = db.bulan
    GROUP BY
        dp.provinsi,
        db.tahun,
        db.nomor_bulan,
        dj.jenis_bencana
)
SELECT
    w.nama_provinsi,
    tw.tahun,
    tw.bulan,
    bb.jenis_bencana,
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
    ON UPPER(TRIM(w.nama_provinsi))
       = UPPER(TRIM(bb.provinsi))
    AND tw.tahun = bb.tahun
    AND tw.bulan = bb.bulan
ORDER BY
    w.nama_provinsi,
    tw.tahun,
    tw.bulan,
    bb.jenis_bencana;