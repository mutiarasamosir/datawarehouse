
from pathlib import Path

import pandas as pd


BULAN = {
    "Januari": 1,
    "Februari": 2,
    "Maret": 3,
    "April": 4,
    "Mei": 5,
    "Juni": 6,
    "Juli": 7,
    "Agustus": 8,
    "September": 9,
    "Oktober": 10,
    "November": 11,
    "Desember": 12,
}


def clean_province_name(name):
    name = str(name).strip().upper()

    for prefix in ("PROVINSI ", "PROV "):
        if name.startswith(prefix):
            name = name[len(prefix):]
            break

    return name.strip()


def process_and_load_inflasi(con, file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File sumber inflasi tidak ditemukan: {file_path}"
        )

    # Excel memiliki header di baris pertama.
    df = pd.read_excel(file_path, sheet_name="Sheet1")
    df.columns = [str(col).strip() for col in df.columns]

    kolom_provinsi = df.columns[0]

    kolom_wajib = [kolom_provinsi, *BULAN.keys()]
    kolom_hilang = [
        kolom for kolom in kolom_wajib
        if kolom not in df.columns
    ]

    if kolom_hilang:
        raise ValueError(
            f"Kolom Excel tidak ditemukan: {kolom_hilang}"
        )

    df = df[kolom_wajib].copy()
    df = df.rename(columns={kolom_provinsi: "nama_provinsi"})

    df["nama_provinsi"] = df["nama_provinsi"].apply(
        clean_province_name
    )

    # Ubah format lebar menjadi satu baris per provinsi per bulan.
    df_long = df.melt(
        id_vars=["nama_provinsi"],
        value_vars=list(BULAN.keys()),
        var_name="nama_bulan",
        value_name="inflasi_umum",
    )

    df_long["bulan"] = df_long["nama_bulan"].map(BULAN)
    df_long["tahun"] = 2025
    df_long["inflasi_umum"] = pd.to_numeric(
        df_long["inflasi_umum"], errors="coerce"
    )

    df_long = df_long.dropna(
        subset=["nama_provinsi", "inflasi_umum"]
    )

    df_long["id_waktu"] = (
        df_long["tahun"] * 100 + df_long["bulan"]
    )

    # Masukkan daftar provinsi ke dimensi.
    provinsi = sorted(df_long["nama_provinsi"].unique())

    con.executemany(
        """
        INSERT INTO dim_wilayah (id_provinsi, nama_provinsi)
        VALUES (?, ?)
        """,
        [(i, nama) for i, nama in enumerate(provinsi, start=1)],
    )

    # Masukkan periode Januari–Desember 2025.
    con.executemany(
    """
    INSERT OR IGNORE INTO dim_waktu (id_waktu, bulan, tahun)
    VALUES (?, ?, ?)
    """,
    [
        (202500 + bulan, bulan, 2025)
        for bulan in range(1, 13)
    ],)

    # Buat pemetaan nama provinsi ke ID dimensi.
    id_provinsi = {
        nama: i for i, nama in enumerate(provinsi, start=1)
    }

    df_long["id_provinsi"] = df_long["nama_provinsi"].map(
        id_provinsi
    )

    con.register("df_inflasi", df_long)

    try:
        con.execute(
            """
            INSERT INTO fact_inflasi
                (id_provinsi, id_waktu, inflasi_umum)
            SELECT
                id_provinsi,
                id_waktu,
                inflasi_umum
            FROM df_inflasi
            """
        )
    finally:
        con.unregister("df_inflasi")

    print(f"Provinsi dimuat: {len(provinsi)}")
    print(f"Baris fakta dimuat: {len(df_long)}")