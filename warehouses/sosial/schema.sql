
CREATE TABLE IF NOT EXISTS dim_provinsi (
    provinsi_id INTEGER PRIMARY KEY,
    nama_provinsi VARCHAR NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_wilayah (
    wilayah_id INTEGER PRIMARY KEY,
    nama_wilayah VARCHAR NOT NULL,
    jenis_wilayah VARCHAR NOT NULL,
    provinsi_id INTEGER,
    FOREIGN KEY (provinsi_id) REFERENCES dim_provinsi(provinsi_id)
);

CREATE TABLE IF NOT EXISTS dim_periode (
    periode_id INTEGER PRIMARY KEY,
    tahun INTEGER NOT NULL,
    periode VARCHAR NOT NULL,
    UNIQUE (tahun, periode)
);

CREATE TABLE IF NOT EXISTS fact_penduduk (
    provinsi_id INTEGER NOT NULL,
    periode_id INTEGER NOT NULL,
    jumlah_penduduk_ribu DOUBLE NOT NULL DEFAULT 0,
    laju_pertumbuhan DOUBLE NOT NULL DEFAULT 0,
    persentase_penduduk DOUBLE NOT NULL DEFAULT 0,
    kepadatan_penduduk DOUBLE NOT NULL DEFAULT 0,
    rasio_jenis_kelamin DOUBLE NOT NULL DEFAULT 0,
    FOREIGN KEY (provinsi_id) REFERENCES dim_provinsi(provinsi_id),
    FOREIGN KEY (periode_id) REFERENCES dim_periode(periode_id)
);

CREATE TABLE IF NOT EXISTS fact_pengeluaran_per_kapita (
    wilayah_id INTEGER NOT NULL,
    periode_id INTEGER NOT NULL,
    pengeluaran_laki_laki DOUBLE NOT NULL DEFAULT 0,
    pengeluaran_perempuan DOUBLE NOT NULL DEFAULT 0,
    FOREIGN KEY (wilayah_id) REFERENCES dim_wilayah(wilayah_id),
    FOREIGN KEY (periode_id) REFERENCES dim_periode(periode_id)
);
