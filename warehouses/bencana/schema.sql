
CREATE TABLE IF NOT EXISTS dim_provinsi (
    provinsi_id INTEGER PRIMARY KEY,
    provinsi VARCHAR NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_bulan (
    bulan DATE PRIMARY KEY,
    tahun INTEGER NOT NULL,
    nomor_bulan INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_jenis_bencana (
    jenis_bencana_id INTEGER PRIMARY KEY,
    jenis_bencana VARCHAR NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS fact_bencana (
    bulan DATE NOT NULL,
    provinsi_id INTEGER NOT NULL,
    jenis_bencana_id INTEGER NOT NULL,

    jumlah_kejadian INTEGER NOT NULL,
    korban_meninggal INTEGER NOT NULL,
    korban_hilang INTEGER NOT NULL,
    korban_luka INTEGER NOT NULL,
    korban_terdampak INTEGER NOT NULL,
    korban_mengungsi INTEGER NOT NULL,
    rumah_rusak INTEGER NOT NULL,

    PRIMARY KEY (bulan, provinsi_id, jenis_bencana_id),

    FOREIGN KEY (bulan)
        REFERENCES dim_bulan(bulan),

    FOREIGN KEY (provinsi_id)
        REFERENCES dim_provinsi(provinsi_id),

    FOREIGN KEY (jenis_bencana_id)
        REFERENCES dim_jenis_bencana(jenis_bencana_id)
);
