
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "inflasi_energi" / "inflasi_energi.xlsx"

KOLOM_BULAN = [
    "januari", "februari", "maret", "april",
    "mei", "juni", "juli", "agustus",
    "september", "oktober", "november", "desember",
]

NOMOR_BULAN = {
    nama: nomor
    for nomor, nama in enumerate(KOLOM_BULAN, start=1)
}

# Ubah jika tahun pada sumber data bukan 2025.
TAHUN_DATA = 2025


def load_data(con):
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"File energi tidak ditemukan: {DATA_FILE}"
        )

    df = pd.read_excel(DATA_FILE)

    kolom_wajib = ["provinsi", "provinsi_id", *KOLOM_BULAN]
    missing = set(kolom_wajib) - set(df.columns)

    if missing:
        raise ValueError(
            f"Kolom wajib tidak ditemukan: {sorted(missing)}"
        )

    df = df[kolom_wajib].copy()

    df["provinsi"] = df["provinsi"].astype("string").str.strip()
    df["provinsi_id"] = pd.to_numeric(
        df["provinsi_id"], errors="raise"
    ).astype("int32")

    if df["provinsi"].isna().any() or (df["provinsi"] == "").any():
        raise ValueError("Nama provinsi kosong.")

    if df["provinsi_id"].duplicated().any():
        raise ValueError("Ada ID provinsi duplikat.")

    if df["provinsi"].duplicated().any():
        raise ValueError("Ada nama provinsi duplikat.")

    for bulan in KOLOM_BULAN:
        df[bulan] = pd.to_numeric(df[bulan], errors="raise")

    # Bentuk wide menjadi long:
    # satu baris = satu provinsi dan satu bulan
    long_df = df.melt(
        id_vars=["provinsi", "provinsi_id"],
        value_vars=KOLOM_BULAN,
        var_name="nama_bulan",
        value_name="nilai_inflasi",
    )

    if long_df["nilai_inflasi"].isna().any():
        raise ValueError("Ada nilai inflasi energi yang kosong.")

    long_df["nomor_bulan"] = (
        long_df["nama_bulan"].map(NOMOR_BULAN)
    )

    long_df["bulan"] = pd.to_datetime({
        "year": [TAHUN_DATA] * len(long_df),
        "month": long_df["nomor_bulan"],
        "day": [1] * len(long_df),
    }).dt.date

    provinsi = (
        df[["provinsi_id", "provinsi"]]
        .sort_values("provinsi_id")
    )

    bulan_df = pd.DataFrame({
        "bulan": sorted(long_df["bulan"].unique())
    })
    bulan_df["tahun"] = pd.to_datetime(
        bulan_df["bulan"]
    ).dt.year
    bulan_df["nomor_bulan"] = pd.to_datetime(
        bulan_df["bulan"]
    ).dt.month

    # Bersihkan data lama sebelum mengisi ulang
    con.execute("DELETE FROM fact_inflasi_energi")
    con.execute("DELETE FROM dim_provinsi")
    con.execute("DELETE FROM dim_bulan")

    con.register("tmp_provinsi", provinsi)
    con.execute("""
        INSERT INTO dim_provinsi (provinsi_id, provinsi)
        SELECT provinsi_id, provinsi
        FROM tmp_provinsi
    """)
    con.unregister("tmp_provinsi")

    con.register("tmp_bulan", bulan_df)
    con.execute("""
        INSERT INTO dim_bulan (bulan, tahun, nomor_bulan)
        SELECT bulan, tahun, nomor_bulan
        FROM tmp_bulan
    """)
    con.unregister("tmp_bulan")

    con.register("tmp_energi", long_df)
    con.execute("""
        INSERT INTO fact_inflasi_energi (
            bulan, provinsi_id, nilai_inflasi
        )
        SELECT bulan, provinsi_id, nilai_inflasi
        FROM tmp_energi
    """)
    con.unregister("tmp_energi")

    print(f"Baris sumber: {len(df)}")
    print(f"Jumlah provinsi: {len(provinsi)}")
    print(f"Jumlah bulan: {len(bulan_df)}")
    print(f"Baris fakta: {len(long_df)}")
