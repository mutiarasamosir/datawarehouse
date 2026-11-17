
from pathlib import Path

import duckdb
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

CSV_PATH = ROOT / "data" / "ihk" / "data_ihk_2025.csv"
INFLASI_DB = ROOT / "databases" / "inflasi.duckdb"


def load_data(con):
    # 1. Periksa keberadaan file
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV tidak ditemukan: {CSV_PATH}")

    if not INFLASI_DB.exists():
        raise FileNotFoundError(
            f"Database inflasi tidak ditemukan: {INFLASI_DB}"
        )

    # 2. Baca CSV
    df = pd.read_csv(CSV_PATH)

    required_columns = [
        "provinsi",
        "bulan",
        "tahun",
        "nomor_bulan",
        "nilai_ihk"
    ]

    missing = set(required_columns) - set(df.columns)

    if missing:
        raise ValueError(f"Kolom tidak ditemukan: {missing}")

    # 3. Bersihkan tipe data
    df["provinsi"] = (
        df["provinsi"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df["bulan"] = pd.to_datetime(
        df["bulan"], errors="raise"
    ).dt.date

    df["tahun"] = pd.to_numeric(
        df["tahun"], errors="raise"
    ).astype(int)

    df["nomor_bulan"] = pd.to_numeric(
        df["nomor_bulan"], errors="raise"
    ).astype(int)

    df["nilai_ihk"] = pd.to_numeric(
        df["nilai_ihk"], errors="raise"
    )

    if df[required_columns].isnull().any().any():
        raise ValueError("Ada nilai kosong pada kolom data IHK.")

    # 4. Validasi duplikasi
    if df.duplicated(["provinsi", "bulan"]).any():
        raise ValueError("Ada duplikasi kombinasi provinsi dan bulan.")

    # 5. Ambil ID provinsi dari database inflasi
    inflasi_con = duckdb.connect(
        str(INFLASI_DB),
        read_only=True
    )

    try:
        wilayah = inflasi_con.execute("""
            SELECT
                id_provinsi,
                UPPER(TRIM(nama_provinsi)) AS provinsi
            FROM dim_wilayah
        """).df()
    finally:
        inflasi_con.close()

    province_map = dict(
        zip(wilayah["provinsi"], wilayah["id_provinsi"])
    )

    df["provinsi_id"] = df["provinsi"].map(province_map)

    # 6. Pastikan semua provinsi cocok
    unmatched = sorted(
        df.loc[df["provinsi_id"].isna(), "provinsi"].unique()
    )

    if unmatched:
        raise ValueError(
            f"Provinsi tidak cocok dengan database inflasi: {unmatched}"
        )

    if df["provinsi"].nunique() != 38:
        raise ValueError(
            f"Jumlah provinsi tidak sesuai: {df['provinsi'].nunique()}"
        )

    # 7. Siapkan dimensi provinsi
    dim_provinsi = (
        df[["provinsi_id", "provinsi"]]
        .drop_duplicates()
        .sort_values("provinsi_id")
    )

    # 8. Siapkan dimensi bulan
    dim_bulan = (
        df[["bulan", "tahun", "nomor_bulan"]]
        .drop_duplicates()
        .sort_values("bulan")
    )

    # 9. Kosongkan data lama sebelum reload
    con.execute("DELETE FROM fact_ihk")
    con.execute("DELETE FROM dim_bulan")
    con.execute("DELETE FROM dim_provinsi")

    # 10. Masukkan data dimensi provinsi
    con.executemany(
        """
        INSERT INTO dim_provinsi
        (provinsi_id, provinsi)
        VALUES (?, ?)
        """,
        dim_provinsi.values.tolist()
    )

    # 11. Masukkan data dimensi bulan
    con.executemany(
        """
        INSERT INTO dim_bulan
        (bulan, tahun, nomor_bulan)
        VALUES (?, ?, ?)
        """,
        dim_bulan.values.tolist()
    )

    # 12. Masukkan data fakta
    fact_data = df[
        ["bulan", "provinsi_id", "nilai_ihk"]
    ]

    con.executemany(
        """
        INSERT INTO fact_ihk
        (bulan, provinsi_id, nilai_ihk)
        VALUES (?, ?, ?)
        """,
        fact_data.values.tolist()
    )

    print("Loading data IHK berhasil.")
    print("Jumlah provinsi:", df["provinsi"].nunique())
    print("Jumlah bulan:", df["bulan"].nunique())
    print("Jumlah data fakta:", len(df))
