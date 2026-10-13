
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = (
    ROOT / "data" / "bencana"
    / "data_bencana_dampak_spesifik_2025.xlsx"
)

NOMOR_BULAN = {
    "januari": 1, "februari": 2, "maret": 3, "april": 4,
    "mei": 5, "juni": 6, "juli": 7, "agustus": 8,
    "september": 9, "oktober": 10, "november": 11, "desember": 12,
}

# Kode provinsi BPS. Sama dengan provinsi_id di warehouse
# inflasi_energi dan pangan, supaya antar-database bisa di-join.
# Kunci memakai huruf besar agar tidak terpengaruh penulisan.
PROVINSI_ID = {
    "ACEH": 11,
    "SUMATERA UTARA": 12,
    "SUMATERA BARAT": 13,
    "RIAU": 14,
    "JAMBI": 15,
    "SUMATERA SELATAN": 16,
    "BENGKULU": 17,
    "LAMPUNG": 18,
    "KEPULAUAN BANGKA BELITUNG": 19,
    "KEPULAUAN RIAU": 21,
    "DKI JAKARTA": 31,
    "JAWA BARAT": 32,
    "JAWA TENGAH": 33,
    "DI YOGYAKARTA": 34,
    "JAWA TIMUR": 35,
    "BANTEN": 36,
    "BALI": 51,
    "NUSA TENGGARA BARAT": 52,
    "NUSA TENGGARA TIMUR": 53,
    "KALIMANTAN BARAT": 61,
    "KALIMANTAN TENGAH": 62,
    "KALIMANTAN SELATAN": 63,
    "KALIMANTAN TIMUR": 64,
    "KALIMANTAN UTARA": 65,
    "SULAWESI UTARA": 71,
    "SULAWESI TENGAH": 72,
    "SULAWESI SELATAN": 73,
    "SULAWESI TENGGARA": 74,
    "GORONTALO": 75,
    "SULAWESI BARAT": 76,
    "MALUKU": 81,
    "MALUKU UTARA": 82,
    "PAPUA BARAT": 91,
    "PAPUA": 94,
}

# Nama kolom di Excel -> nama kolom di database
KOLOM_UKURAN = {
    "Jumlah Kejadian": "jumlah_kejadian",
    "Korban Meninggal (Jiwa)": "korban_meninggal",
    "Korban Hilang (Jiwa)": "korban_hilang",
    "Korban Luka (Jiwa)": "korban_luka",
    "Korban Terdampak (Jiwa)": "korban_terdampak",
    "Korban Mengungsi (Jiwa)": "korban_mengungsi",
    "Rumah Rusak (Unit)": "rumah_rusak",
}


def load_data(con):
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"File bencana tidak ditemukan: {DATA_FILE}"
        )

    df = pd.read_excel(DATA_FILE)

    kolom_wajib = [
        "Provinsi", "Bulan", "Tahun", "Jenis Bencana",
        *KOLOM_UKURAN,
    ]
    missing = set(kolom_wajib) - set(df.columns)
    if missing:
        raise ValueError(
            f"Kolom wajib tidak ditemukan: {sorted(missing)}"
        )

    df = df[kolom_wajib].copy()

    # Rapikan teks
    df["Provinsi"] = df["Provinsi"].astype("string").str.strip()
    df["Jenis Bencana"] = (
        df["Jenis Bencana"].astype("string").str.strip()
    )
    df["Bulan"] = df["Bulan"].astype("string").str.strip().str.lower()

    if df[["Provinsi", "Bulan", "Jenis Bencana"]].isna().any().any():
        raise ValueError("Ada provinsi, bulan, atau jenis bencana kosong.")

    # Nama provinsi -> kode BPS
    df["provinsi_id"] = df["Provinsi"].str.upper().map(PROVINSI_ID)
    tak_dikenal = df.loc[df["provinsi_id"].isna(), "Provinsi"].unique()
    if len(tak_dikenal) > 0:
        raise ValueError(
            f"Provinsi tidak ada di PROVINSI_ID: {sorted(tak_dikenal)}"
        )
    df["provinsi_id"] = df["provinsi_id"].astype("int32")

    # Nama bulan + tahun -> tanggal (tanggal 1 tiap bulan)
    df["nomor_bulan"] = df["Bulan"].map(NOMOR_BULAN)
    if df["nomor_bulan"].isna().any():
        raise ValueError("Ada nama bulan yang tidak dikenali.")

    df["Tahun"] = pd.to_numeric(df["Tahun"], errors="raise").astype("int32")
    df["bulan"] = pd.to_datetime({
        "year": df["Tahun"],
        "month": df["nomor_bulan"],
        "day": 1,
    }).dt.date

    # Ukuran harus angka dan tidak negatif
    for asal, tujuan in KOLOM_UKURAN.items():
        df[tujuan] = pd.to_numeric(df[asal], errors="raise")
        if df[tujuan].isna().any():
            raise ValueError(f"Ada nilai kosong pada kolom {asal}.")
        if (df[tujuan] < 0).any():
            raise ValueError(f"Ada nilai negatif pada kolom {asal}.")
        df[tujuan] = df[tujuan].astype("int32")

    if df.duplicated(["bulan", "provinsi_id", "Jenis Bencana"]).any():
        raise ValueError(
            "Ada duplikasi kombinasi bulan, provinsi, dan jenis bencana."
        )

    # Dimensi
    provinsi = (
        df[["provinsi_id", "Provinsi"]]
        .drop_duplicates()
        .rename(columns={"Provinsi": "provinsi"})
        .sort_values("provinsi_id")
    )
    if provinsi["provinsi_id"].duplicated().any():
        raise ValueError("Satu ID provinsi memiliki nama berbeda.")

    bulan_df = pd.DataFrame({"bulan": sorted(df["bulan"].unique())})
    bulan_df["tahun"] = pd.to_datetime(bulan_df["bulan"]).dt.year
    bulan_df["nomor_bulan"] = pd.to_datetime(bulan_df["bulan"]).dt.month

    jenis_nama = sorted(df["Jenis Bencana"].unique())
    jenis = pd.DataFrame({
        "jenis_bencana_id": range(1, len(jenis_nama) + 1),
        "jenis_bencana": jenis_nama,
    })

    # Bersihkan data lama (fakta dulu, baru dimensi)
    con.execute("DELETE FROM fact_bencana")
    con.execute("DELETE FROM dim_jenis_bencana")
    con.execute("DELETE FROM dim_provinsi")
    con.execute("DELETE FROM dim_bulan")

    con.register("tmp_provinsi", provinsi)
    con.execute("""
        INSERT INTO dim_provinsi (provinsi_id, provinsi)
        SELECT provinsi_id, provinsi FROM tmp_provinsi
    """)
    con.unregister("tmp_provinsi")

    con.register("tmp_bulan", bulan_df)
    con.execute("""
        INSERT INTO dim_bulan (bulan, tahun, nomor_bulan)
        SELECT bulan, tahun, nomor_bulan FROM tmp_bulan
    """)
    con.unregister("tmp_bulan")

    con.register("tmp_jenis", jenis)
    con.execute("""
        INSERT INTO dim_jenis_bencana (jenis_bencana_id, jenis_bencana)
        SELECT jenis_bencana_id, jenis_bencana FROM tmp_jenis
    """)
    con.unregister("tmp_jenis")

    # Fakta: satu baris = satu bulan, provinsi, dan jenis bencana
    # DuckDB tidak membedakan huruf besar/kecil pada nama kolom,
    # jadi kolom asli "Bulan" harus dibuang agar tidak bentrok
    # dengan kolom "bulan" (tanggal).
    fakta = df[[
        "bulan", "provinsi_id", "Jenis Bencana",
        *KOLOM_UKURAN.values(),
    ]].rename(columns={"Jenis Bencana": "jenis_bencana"})

    con.register("tmp_bencana", fakta)
    con.execute("""
        INSERT INTO fact_bencana (
            bulan, provinsi_id, jenis_bencana_id,
            jumlah_kejadian, korban_meninggal, korban_hilang,
            korban_luka, korban_terdampak, korban_mengungsi,
            rumah_rusak
        )
        SELECT
            t.bulan, t.provinsi_id, j.jenis_bencana_id,
            t.jumlah_kejadian, t.korban_meninggal, t.korban_hilang,
            t.korban_luka, t.korban_terdampak, t.korban_mengungsi,
            t.rumah_rusak
        FROM tmp_bencana t
        JOIN dim_jenis_bencana j
          ON t.jenis_bencana = j.jenis_bencana
    """)
    con.unregister("tmp_bencana")

    print(f"Baris sumber: {len(df)}")
    print(f"Jumlah provinsi: {len(provinsi)}")
    print(f"Jumlah bulan: {len(bulan_df)}")
    print(f"Jumlah jenis bencana: {len(jenis)}")
    print(f"Baris fakta: {len(df)}")
