-- =========================================================
-- QUERY 13: KORELASI SELURUH VARIABEL TERHADAP INFLASI
-- Sumber: analytics.main.hasil_integrasi
-- =========================================================
SELECT
    -- Korelasi pangan
    CORR(inflasi_umum, rata_rata_harga_pangan)
        AS korelasi_pangan,

    -- Korelasi bencana
    CORR(inflasi_umum, jumlah_kejadian)
        AS korelasi_jumlah_bencana,

    CORR(inflasi_umum, korban_meninggal)
        AS korelasi_korban_meninggal,

    CORR(inflasi_umum, korban_luka)
        AS korelasi_korban_luka,

    -- Korelasi IHK
    CORR(inflasi_umum, nilai_ihk)
        AS korelasi_ihk,

    -- Korelasi ekonomi
    CORR(inflasi_umum, nilai_tpt)
        AS korelasi_tpt,

    CORR(inflasi_umum, nilai_tpak)
        AS korelasi_tpak,

    CORR(inflasi_umum, nilai_ump)
        AS korelasi_ump,

    -- Korelasi sosial
    CORR(inflasi_umum, jumlah_penduduk_ribu)
        AS korelasi_penduduk,

    CORR(inflasi_umum, laju_pertumbuhan)
        AS korelasi_pertumbuhan_penduduk,

    CORR(inflasi_umum, kepadatan_penduduk)
        AS korelasi_kepadatan_penduduk

FROM analytics.main.hasil_integrasi;