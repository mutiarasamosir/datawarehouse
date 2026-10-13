SELECT
    iw.nama_provinsi AS provinsi,
    w.tahun,
    w.bulan AS nomor_bulan,
    kp.nama_komoditas AS komoditas,
    ROUND(fi.inflasi_umum, 2) AS inflasi_umum,
    ROUND(fp.harga, 2) AS harga_pangan
FROM inflasi.main.fact_inflasi fi
JOIN inflasi.main.dim_wilayah iw
    ON fi.id_provinsi = iw.id_provinsi
JOIN inflasi.main.dim_waktu w
    ON fi.id_waktu = w.id_waktu
JOIN pangan.main.dim_provinsi pp
    ON UPPER(TRIM(iw.nama_provinsi)) = UPPER(TRIM(pp.provinsi))
JOIN pangan.main.fact_harga_pangan fp
    ON fp.provinsi_id = pp.provinsi_id
JOIN pangan.main.dim_bulan pb
    ON fp.bulan = pb.bulan
JOIN pangan.main.dim_komoditas kp
    ON fp.komoditas_id = kp.komoditas_id
WHERE w.tahun = pb.tahun
  AND w.bulan = pb.nomor_bulan
LIMIT 20;
