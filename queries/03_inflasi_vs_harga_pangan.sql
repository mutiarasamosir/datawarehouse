-- Integrasi inflasi umum dan harga pangan per provinsi/bulan

SELECT
    w.nama_provinsi,
    tw.tahun,
    tw.bulan,
    dk.nama_komoditas,
    fp.harga,
    fi.inflasi_umum
FROM inflasi.main.fact_inflasi AS fi
JOIN inflasi.main.dim_wilayah AS w
    ON fi.id_provinsi = w.id_provinsi
JOIN inflasi.main.dim_waktu AS tw
    ON fi.id_waktu = tw.id_waktu
JOIN pangan.main.fact_harga_pangan AS fp
    ON tw.tahun = YEAR(fp.bulan)
    AND tw.bulan = MONTH(fp.bulan)
JOIN pangan.main.dim_provinsi AS dp
    ON fp.provinsi_id = dp.provinsi_id
    AND UPPER(TRIM(w.nama_provinsi)) = UPPER(TRIM(dp.provinsi))
JOIN pangan.main.dim_komoditas AS dk
    ON fp.komoditas_id = dk.komoditas_id
ORDER BY
    w.nama_provinsi,
    tw.tahun,
    tw.bulan,
    dk.nama_komoditas;