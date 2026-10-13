
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "pangan" / "data_pangan.xlsx"

KOMODITAS = [
    "cabai_merah",
    "beras",
    "bawang_merah",
    "ayam",
    "telur",
    "minyak_goreng",
    "gula_pasir",
    "daging",
    "cabai_rawit",
]


def load_data(con):
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"File sumber tidak ditemukan: {DATA_FILE}"
        )

    df = pd.read_excel(DATA_FILE)

    kolom_wajib = [
        "provinsi",
        "provinsi_ID",
        "bulan",
        *KOMODITAS,
    ]

    missing = set(kolom_wajib) - set(df.columns)
    if missing:
        raise ValueError(
            f"Kolom wajib tidak ditemukan: {sorted(missing)}"
        )

    # Validasi dan normalisasi data
    df = df[kolom_wajib].copy()
    df["provinsi"] = df["provinsi"].astype("string").str.strip()
    df["provinsi_ID"] = pd.to_numeric(
        df["provinsi_ID"], errors="raise"
    ).astype("int32")

    df["bulan"] = pd.to_datetime(
        df["bulan"].astype(str) + "-01",
        format="%Y-%m-%d",
        errors="raise",
    ).dt.date

    if df["provinsi"].isna().any() or (df["provinsi"] == "").any():
        raise ValueError("Ada nama provinsi yang kosong.")

    if df["bulan"].isna().any():
        raise ValueError("Ada periode bulan yang kosong.")

    if df.duplicated(["provinsi_ID", "bulan"]).any():
        raise ValueError(
            "Ditemukan duplikasi kombinasi provinsi dan bulan."
        )

    # Ubah harga ke format numerik
    for kolom in KOMODITAS:
        df[kolom] = pd.to_numeric(
            df[kolom], errors="raise"
        )

        if (df[kolom].dropna() < 0).any():
            raise ValueError(
                f"Harga negatif ditemukan pada kolom {kolom}."
            )

    # Satu baris fakta = satu provinsi, bulan, dan komoditas
    long_df = df.melt(
        id_vars=["provinsi", "provinsi_ID", "bulan"],
        value_vars=KOMODITAS,
        var_name="nama_komoditas",
        value_name="harga",
    )

    # Harga kosong tidak dimasukkan sebagai fakta
    long_df = long_df.dropna(subset=["harga"]).copy()

    # Bersihkan tabel fakta dan dimensi dalam urutan yang aman
    con.execute("DELETE FROM fact_harga_pangan")
    con.execute("DELETE FROM dim_komoditas")
    con.execute("DELETE FROM dim_provinsi")
    con.execute("DELETE FROM dim_bulan")

    # Isi dimensi provinsi
    provinsi = (
        df[["provinsi_ID", "provinsi"]]
        .drop_duplicates()
        .rename(columns={"provinsi_ID": "provinsi_id"})
    )

    if provinsi["provinsi_id"].duplicated().any():
        raise ValueError("Satu ID provinsi memiliki nama berbeda.")

    if provinsi["provinsi"].duplicated().any():
        raise ValueError("Satu nama provinsi memiliki ID berbeda.")

    con.register("tmp_provinsi", provinsi)
    con.execute("""
        INSERT INTO dim_provinsi
        SELECT provinsi_id, provinsi
        FROM tmp_provinsi
    """)
    con.unregister("tmp_provinsi")

    # Isi dimensi bulan
    bulan = pd.DataFrame({
        "bulan": sorted(df["bulan"].unique())
    })
    bulan["tahun"] = pd.to_datetime(bulan["bulan"]).dt.year
    bulan["nomor_bulan"] = pd.to_datetime(
        bulan["bulan"]
    ).dt.month

    con.register("tmp_bulan", bulan)
    con.execute("""
        INSERT INTO dim_bulan
        SELECT bulan, tahun, nomor_bulan
        FROM tmp_bulan
    """)
    con.unregister("tmp_bulan")

    # Isi dimensi komoditas
    komoditas = pd.DataFrame({
        "komoditas_id": range(1, len(KOMODITAS) + 1),
        "nama_komoditas": KOMODITAS,
    })

    con.register("tmp_komoditas", komoditas)
    con.execute("""
        INSERT INTO dim_komoditas
        SELECT komoditas_id, nama_komoditas
        FROM tmp_komoditas
    """)
    con.unregister("tmp_komoditas")

    # Isi tabel fakta
    con.register("tmp_harga", long_df)

    con.execute("""
        INSERT INTO fact_harga_pangan (
            bulan, provinsi_id, komoditas_id, harga
        )
        SELECT
            h.bulan,
            h.provinsi_ID,
            k.komoditas_id,
            h.harga
        FROM tmp_harga h
        JOIN dim_komoditas k
          ON h.nama_komoditas = k.nama_komoditas
    """)

    con.unregister("tmp_harga")

    print(f"Baris sumber       : {len(df)}")
    print(f"Jumlah provinsi    : {len(provinsi)}")
    print(f"Jumlah bulan       : {len(bulan)}")
    print(f"Jumlah komoditas   : {len(komoditas)}")
    print(f"Baris fakta        : {len(long_df)}")
