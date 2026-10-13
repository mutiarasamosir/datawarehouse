
-- Integrasi inflasi umum dengan faktor pangan, energi, bencana, ekonomi, dan sosial.
-- Grain: satu baris per provinsi per bulan.

WITH pangan_bulanan AS (
    SELECT
        UPPER(TRIM(dp.provinsi)) AS provinsi,
        YEAR(fp.bulan) AS tahun,
        MONTH(fp.bulan) AS bulan,
        AVG(fp.harga) AS rata_rata_harga_pangan
    FROM pangan.main.fact_harga_pangan AS fp
    JOIN pangan.main.dim_provinsi AS dp
        ON fp.provinsi_id = dp.provinsi_id
    GROUP BY
        UPPER(TRIM(dp.provinsi)),
        YEAR(fp.bulan),
        MONTH(fp.bulan)
),

energi_bulanan AS (
    SELECT
        UPPER(TRIM(dp.provinsi)) AS provinsi,
        db.tahun,
        db.nomor_bulan AS bulan,
        AVG(fe.nilai_inflasi) AS inflasi_energi
    FROM energi.main.fact_inflasi_energi AS fe
    JOIN energi.main.dim_provinsi AS dp
        ON fe.provinsi_id = dp.provinsi_id
    JOIN energi.main.dim_bulan AS db
        ON fe.bulan = db.bulan
    GROUP BY
        UPPER(TRIM(dp.provinsi)),
        db.tahun,
        db.nomor_bulan
),

bencana_bulanan AS (
    SELECT
        UPPER(TRIM(dp.provinsi)) AS provinsi,
        db.tahun,
        db.nomor_bulan AS bulan,
        SUM(COALESCE(fb.jumlah_kejadian, 0)) AS jumlah_kejadian,
        SUM(COALESCE(fb.korban_meninggal, 0)) AS korban_meninggal,
        SUM(COALESCE(fb.korban_luka, 0)) AS korban_luka
    FROM bencana.main.fact_bencana AS fb
    JOIN bencana.main.dim_provinsi AS dp
        ON fb.provinsi_id = dp.provinsi_id
    JOIN bencana.main.dim_bulan AS db
        ON fb.bulan = db.bulan
    GROUP BY
        UPPER(TRIM(dp.provinsi)),
        db.tahun,
        db.nomor_bulan
),

ekonomi_tahunan AS (
    SELECT
        UPPER(TRIM(dp.nama_provinsi)) AS provinsi,
        dper.tahun,
        MAX(ump.nilai_ump) AS nilai_ump
    FROM ekonomi.main.dim_provinsi AS dp
    JOIN ekonomi.main.fact_ump AS ump
        ON dp.provinsi_id = ump.provinsi_id
    JOIN ekonomi.main.dim_periode AS dper
        ON ump.periode_id = dper.periode_id
    GROUP BY
        UPPER(TRIM(dp.nama_provinsi)),
        dper.tahun
),

sosial_tahunan AS (
    SELECT
        UPPER(TRIM(dp.nama_provinsi)) AS provinsi,
        dper.tahun,
        MAX(fp.jumlah_penduduk_ribu) AS jumlah_penduduk_ribu,
        MAX(fp.laju_pertumbuhan) AS laju_pertumbuhan,
        MAX(fp.kepadatan_penduduk) AS kepadatan_penduduk
    FROM sosial.main.fact_penduduk AS fp
    JOIN sosial.main.dim_provinsi AS dp
        ON fp.provinsi_id = dp.provinsi_id
    JOIN sosial.main.dim_periode AS dper
        ON fp.periode_id = dper.periode_id
    GROUP BY
        UPPER(TRIM(dp.nama_provinsi)),
        dper.tahun
)

SELECT
    dw.nama_provinsi,
    dt.tahun,
    dt.bulan,
    fi.inflasi_umum,

    pb.rata_rata_harga_pangan,
    eb.inflasi_energi,

    COALESCE(bb.jumlah_kejadian, 0) AS jumlah_kejadian,
    COALESCE(bb.korban_meninggal, 0) AS korban_meninggal,
    COALESCE(bb.korban_luka, 0) AS korban_luka,

    CASE
        WHEN dt.bulan = 2 THEN tpt.nilai_tpt
        WHEN dt.bulan = 8 THEN tpt.nilai_tpt
        ELSE NULL
    END AS nilai_tpt,

    CASE
        WHEN dt.bulan = 2 THEN tpak.nilai_tpak
        WHEN dt.bulan = 8 THEN tpak.nilai_tpak
        ELSE NULL
    END AS nilai_tpak,

    et.nilai_ump,

    st.jumlah_penduduk_ribu,
    st.laju_pertumbuhan,
    st.kepadatan_penduduk

FROM inflasi.main.fact_inflasi AS fi

JOIN inflasi.main.dim_wilayah AS dw
    ON fi.id_provinsi = dw.id_provinsi

JOIN inflasi.main.dim_waktu AS dt
    ON fi.id_waktu = dt.id_waktu

LEFT JOIN pangan_bulanan AS pb
    ON UPPER(TRIM(dw.nama_provinsi)) = pb.provinsi
    AND dt.tahun = pb.tahun
    AND dt.bulan = pb.bulan

LEFT JOIN energi_bulanan AS eb
    ON UPPER(TRIM(dw.nama_provinsi)) = eb.provinsi
    AND dt.tahun = eb.tahun
    AND dt.bulan = eb.bulan

LEFT JOIN bencana_bulanan AS bb
    ON UPPER(TRIM(dw.nama_provinsi)) = bb.provinsi
    AND dt.tahun = bb.tahun
    AND dt.bulan = bb.bulan

LEFT JOIN ekonomi_tahunan AS et
    ON UPPER(TRIM(dw.nama_provinsi)) = et.provinsi
    AND dt.tahun = et.tahun

LEFT JOIN sosial_tahunan AS st
    ON UPPER(TRIM(dw.nama_provinsi)) = st.provinsi
    AND dt.tahun = st.tahun

LEFT JOIN ekonomi.main.dim_provinsi AS dep
    ON UPPER(TRIM(dw.nama_provinsi)) =
       UPPER(TRIM(dep.nama_provinsi))

LEFT JOIN ekonomi.main.dim_periode AS dpe_feb
    ON dpe_feb.tahun = dt.tahun
    AND dpe_feb.periode = 'Februari'

LEFT JOIN ekonomi.main.dim_periode AS dpe_aug
    ON dpe_aug.tahun = dt.tahun
    AND dpe_aug.periode = 'Agustus'

LEFT JOIN ekonomi.main.fact_tpt AS tpt
    ON tpt.provinsi_id = dep.provinsi_id
    AND tpt.periode_id = CASE
        WHEN dt.bulan = 2 THEN dpe_feb.periode_id
        WHEN dt.bulan = 8 THEN dpe_aug.periode_id
        ELSE NULL
    END

LEFT JOIN ekonomi.main.fact_tpak AS tpak
    ON tpak.provinsi_id = dep.provinsi_id
    AND tpak.periode_id = CASE
        WHEN dt.bulan = 2 THEN dpe_feb.periode_id
        WHEN dt.bulan = 8 THEN dpe_aug.periode_id
        ELSE NULL
    END

ORDER BY
    dw.nama_provinsi,
    dt.tahun,
    dt.bulan;