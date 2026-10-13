
CREATE TABLE IF NOT EXISTS dim_provinsi (
    provinsi_id INTEGER PRIMARY KEY,
    provinsi VARCHAR NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_bulan (
    bulan DATE PRIMARY KEY,
    tahun INTEGER NOT NULL,
    nomor_bulan INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_inflasi_energi (
    bulan DATE NOT NULL,
    provinsi_id INTEGER NOT NULL,
    nilai_inflasi DOUBLE NOT NULL,

    PRIMARY KEY (bulan, provinsi_id),

    FOREIGN KEY (bulan)
        REFERENCES dim_bulan(bulan),

    FOREIGN KEY (provinsi_id)
        REFERENCES dim_provinsi(provinsi_id)
);
