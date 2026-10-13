
CREATE TABLE IF NOT EXISTS dim_provinsi (
    provinsi_id INTEGER PRIMARY KEY,
    provinsi VARCHAR NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_bulan (
    bulan DATE PRIMARY KEY,
    tahun INTEGER NOT NULL,
    nomor_bulan INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_komoditas (
    komoditas_id INTEGER PRIMARY KEY,
    nama_komoditas VARCHAR NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS fact_harga_pangan (
    bulan DATE NOT NULL,
    provinsi_id INTEGER NOT NULL,
    komoditas_id INTEGER NOT NULL,
    harga DOUBLE NOT NULL,

    PRIMARY KEY (bulan, provinsi_id, komoditas_id),

    FOREIGN KEY (bulan)
        REFERENCES dim_bulan(bulan),

    FOREIGN KEY (provinsi_id)
        REFERENCES dim_provinsi(provinsi_id),

    FOREIGN KEY (komoditas_id)
        REFERENCES dim_komoditas(komoditas_id)
);
