
CREATE TABLE IF NOT EXISTS dim_provinsi (
    provinsi_id INTEGER PRIMARY KEY,
    nama_provinsi VARCHAR NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_periode (
    periode_id INTEGER PRIMARY KEY,
    tahun INTEGER NOT NULL,
    periode VARCHAR NOT NULL,
    UNIQUE (tahun, periode)
);

CREATE TABLE IF NOT EXISTS dim_sektor (
    sektor_id INTEGER PRIMARY KEY,
    kode_sektor VARCHAR NOT NULL UNIQUE,
    nama_sektor VARCHAR
);

CREATE TABLE IF NOT EXISTS fact_tpak (
    provinsi_id INTEGER NOT NULL,
    periode_id INTEGER NOT NULL,
    nilai_tpak DOUBLE NOT NULL DEFAULT 0,
    FOREIGN KEY (provinsi_id) REFERENCES dim_provinsi(provinsi_id),
    FOREIGN KEY (periode_id) REFERENCES dim_periode(periode_id)
);

CREATE TABLE IF NOT EXISTS fact_tpt (
    provinsi_id INTEGER NOT NULL,
    periode_id INTEGER NOT NULL,
    nilai_tpt DOUBLE NOT NULL DEFAULT 0,
    FOREIGN KEY (provinsi_id) REFERENCES dim_provinsi(provinsi_id),
    FOREIGN KEY (periode_id) REFERENCES dim_periode(periode_id)
);

CREATE TABLE IF NOT EXISTS fact_upah_sektor (
    sektor_id INTEGER NOT NULL,
    periode_id INTEGER NOT NULL,
    nilai_upah DOUBLE NOT NULL DEFAULT 0,
    FOREIGN KEY (sektor_id) REFERENCES dim_sektor(sektor_id),
    FOREIGN KEY (periode_id) REFERENCES dim_periode(periode_id)
);

CREATE TABLE IF NOT EXISTS fact_ump (
    provinsi_id INTEGER NOT NULL,
    periode_id INTEGER NOT NULL,
    nilai_ump DOUBLE NOT NULL DEFAULT 0,
    FOREIGN KEY (provinsi_id) REFERENCES dim_provinsi(provinsi_id),
    FOREIGN KEY (periode_id) REFERENCES dim_periode(periode_id)
);
