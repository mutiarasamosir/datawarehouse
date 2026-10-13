-- Schema untuk Warehouse Inflasi & Dimensi (Orang 1)

-- 1. Tabel Dimensi Wilayah (Standar 38 Provinsi)
CREATE TABLE IF NOT EXISTS dim_wilayah (
    id_provinsi INTEGER PRIMARY KEY,
    nama_provinsi VARCHAR UNIQUE
);

-- 2. Tabel Dimensi Waktu (Bulan 1-12 dan Tahun 2025)
CREATE TABLE IF NOT EXISTS dim_waktu (
    id_waktu INTEGER PRIMARY KEY,
    bulan INTEGER,
    tahun INTEGER
);

-- 3. Tabel Fakta Inflasi
CREATE TABLE IF NOT EXISTS fact_inflasi (
    id_provinsi INTEGER,
    id_waktu INTEGER,
    inflasi_umum DOUBLE,
    FOREIGN KEY (id_provinsi) REFERENCES dim_wilayah(id_provinsi),
    FOREIGN KEY (id_waktu) REFERENCES dim_waktu(id_waktu)
);