-- =========================================================
-- QUERY 11: INTEGRASI SEMUA FAKTOR INFLASI
-- Domain: Inflasi, Pangan, Bencana, IHK, Ekonomi, Sosial
-- Grain: Satu baris per provinsi per bulan
-- Output: analytics.main.hasil_integrasi
-- =========================================================
CREATE OR REPLACE TABLE analytics.main.hasil_integrasi AS

WITH

-- =========================================================
-- 1. DATA PANGAN BULANAN
-- =========================================================
pangan_bulanan AS (
    SELECT
        UPPER(TRIM(dp.provinsi)) AS provinsi_key,
        YEAR(db.bulan) AS tahun,
        MONTH(db.bulan) AS bulan,
        AVG(fp.harga) AS rata_rata_harga_pangan

    FROM pangan.main.fact_harga_pangan fp

    JOIN pangan.main.dim_provinsi dp
        ON fp.provinsi_id = dp.provinsi_id

    JOIN pangan.main.dim_bulan db
        ON fp.bulan = db.bulan

    GROUP BY
        UPPER(TRIM(dp.provinsi)),
        YEAR(db.bulan),
        MONTH(db.bulan)
),

-- =========================================================
-- 2. DATA BENCANA BULANAN
-- =========================================================
bencana_bulanan AS (
    SELECT
        UPPER(TRIM(dp.provinsi)) AS provinsi_key,
        YEAR(db.bulan) AS tahun,
        MONTH(db.bulan) AS bulan,

        SUM(fb.jumlah_kejadian) AS jumlah_kejadian,
        SUM(fb.korban_meninggal) AS korban_meninggal,
        SUM(fb.korban_luka) AS korban_luka

    FROM bencana.main.fact_bencana fb

    JOIN bencana.main.dim_provinsi dp
        ON fb.provinsi_id = dp.provinsi_id

    JOIN bencana.main.dim_bulan db
        ON fb.bulan = db.bulan

    GROUP BY
        UPPER(TRIM(dp.provinsi)),
        YEAR(db.bulan),
        MONTH(db.bulan)
),

-- =========================================================
-- 3. DATA IHK BULANAN
-- =========================================================
ihk_bulanan AS (
    SELECT
        ihk.provinsi_id,
        db.tahun,
        db.nomor_bulan AS bulan,
        AVG(ihk.nilai_ihk) AS nilai_ihk

    FROM ihk_db.main.fact_ihk ihk

    JOIN ihk_db.main.dim_bulan db
        ON ihk.bulan = db.bulan

    GROUP BY
        ihk.provinsi_id,
        db.tahun,
        db.nomor_bulan
),

-- =========================================================
-- 4. DATA EKONOMI
-- TPT dan TPAK tersedia pada Februari dan Agustus.
-- UMP merupakan indikator tahunan.
-- =========================================================
ekonomi_tahunan AS (
    SELECT
        UPPER(TRIM(dp.nama_provinsi)) AS provinsi_key,
        dper.tahun,

        MAX(
            CASE
                WHEN LOWER(dper.periode) LIKE '%feb%'
                THEN tpt.nilai_tpt
            END
        ) AS nilai_tpt_februari,

        MAX(
            CASE
                WHEN LOWER(dper.periode) LIKE '%agu%'
                THEN tpt.nilai_tpt
            END
        ) AS nilai_tpt_agustus,

        MAX(
            CASE
                WHEN LOWER(dper.periode) LIKE '%feb%'
                THEN tpak.nilai_tpak
            END
        ) AS nilai_tpak_februari,

        MAX(
            CASE
                WHEN LOWER(dper.periode) LIKE '%agu%'
                THEN tpak.nilai_tpak
            END
        ) AS nilai_tpak_agustus,

        MAX(ump.nilai_ump) AS nilai_ump

    FROM ekonomi.main.dim_provinsi dp

    JOIN ekonomi.main.fact_tpt tpt
        ON dp.provinsi_id = tpt.provinsi_id

    JOIN ekonomi.main.dim_periode dper
        ON tpt.periode_id = dper.periode_id

    LEFT JOIN ekonomi.main.fact_tpak tpak
        ON dp.provinsi_id = tpak.provinsi_id
        AND dper.periode_id = tpak.periode_id

    LEFT JOIN ekonomi.main.fact_ump ump
        ON dp.provinsi_id = ump.provinsi_id
        AND dper.tahun = (
            SELECT dper_ump.tahun
            FROM ekonomi.main.dim_periode dper_ump
            WHERE dper_ump.periode_id = ump.periode_id
        )

    GROUP BY
        UPPER(TRIM(dp.nama_provinsi)),
        dper.tahun
),

-- =========================================================
-- 5. DATA SOSIAL TAHUNAN
-- =========================================================
sosial_tahunan AS (
    SELECT
        UPPER(TRIM(dp.nama_provinsi)) AS provinsi_key,
        dper.tahun,

        AVG(fs.jumlah_penduduk_ribu) AS jumlah_penduduk_ribu,
        AVG(fs.laju_pertumbuhan) AS laju_pertumbuhan,
        AVG(fs.kepadatan_penduduk) AS kepadatan_penduduk

    FROM sosial.main.fact_penduduk fs

    JOIN sosial.main.dim_provinsi dp
        ON fs.provinsi_id = dp.provinsi_id

    JOIN sosial.main.dim_periode dper
        ON fs.periode_id = dper.periode_id

    GROUP BY
        UPPER(TRIM(dp.nama_provinsi)),
        dper.tahun
)

-- =========================================================
-- 6. INTEGRASI SELURUH DATA
-- =========================================================
SELECT
    dw.id_provinsi,
    dw.nama_provinsi,

    dt.tahun,
    dt.bulan,

    -- Variabel utama
    fi.inflasi_umum,

    -- Variabel pangan
    p.rata_rata_harga_pangan,

    -- Variabel bencana
    b.jumlah_kejadian,
    b.korban_meninggal,
    b.korban_luka,

    -- Variabel IHK
    i.nilai_ihk,

    -- Variabel ekonomi
    CASE
        WHEN dt.bulan = 2 THEN e.nilai_tpt_februari
        WHEN dt.bulan = 8 THEN e.nilai_tpt_agustus
    END AS nilai_tpt,

    CASE
        WHEN dt.bulan = 2 THEN e.nilai_tpak_februari
        WHEN dt.bulan = 8 THEN e.nilai_tpak_agustus
    END AS nilai_tpak,

    e.nilai_ump,

    -- Variabel sosial
    s.jumlah_penduduk_ribu,
    s.laju_pertumbuhan,
    s.kepadatan_penduduk

FROM inflasi.main.fact_inflasi fi

JOIN inflasi.main.dim_wilayah dw
    ON fi.id_provinsi = dw.id_provinsi

JOIN inflasi.main.dim_waktu dt
    ON fi.id_waktu = dt.id_waktu

LEFT JOIN pangan_bulanan p
    ON UPPER(TRIM(dw.nama_provinsi)) = p.provinsi_key
    AND dt.tahun = p.tahun
    AND dt.bulan = p.bulan

LEFT JOIN bencana_bulanan b
    ON UPPER(TRIM(dw.nama_provinsi)) = b.provinsi_key
    AND dt.tahun = b.tahun
    AND dt.bulan = b.bulan

LEFT JOIN ihk_bulanan i
    ON fi.id_provinsi = i.provinsi_id
    AND dt.tahun = i.tahun
    AND dt.bulan = i.bulan

LEFT JOIN ekonomi_tahunan e
    ON UPPER(TRIM(dw.nama_provinsi)) = e.provinsi_key
    AND dt.tahun = e.tahun

LEFT JOIN sosial_tahunan s
    ON UPPER(TRIM(dw.nama_provinsi)) = s.provinsi_key
    AND dt.tahun = s.tahun;