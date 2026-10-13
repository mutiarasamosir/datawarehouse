
from pathlib import Path
import re
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "ekonomi"
TAHUN = 2025

BULAN_PERIODE = {
    "Februari": 2,
    "Mei": 5,
    "Agustus": 8,
    "November": 11,
}


def clean_number(value):
    """Nilai numerik kosong atau tanda '-' menjadi 0."""
    if pd.isna(value) or str(value).strip() in {"", "-"}:
        return 0.0

    if isinstance(value, str):
        value = value.strip().replace(",", "")

    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0



def clean_province(value):
    """Menstandarkan nama provinsi dari seluruh sumber ekonomi."""
    name = str(value).strip().upper()

    if name in {"INDONESIA", "", "NAN"}:
        return None

    # Hilangkan kode angka di depan nama provinsi, misalnya "11 ACEH".
    name = re.sub(r"^\d+\s+", "", name)

    # Samakan variasi nama dari file sumber.
    aliases = {
        "KEP. BANGKA BELITUNG": "KEPULAUAN BANGKA BELITUNG",
        "KEP. RIAU": "KEPULAUAN RIAU",
        "DI YOGYAKARTA": "DI YOGYAKARTA",
    }

    return aliases.get(name, name)


def add_period(con, periode):
    con.execute("""
        INSERT INTO dim_periode (periode_id, tahun, periode)
        VALUES (
            (SELECT COALESCE(MAX(periode_id), 0) + 1
             FROM dim_periode),
            ?, ?
        )
        ON CONFLICT (tahun, periode) DO NOTHING
    """, [TAHUN, periode])

    return con.execute("""
        SELECT periode_id
        FROM dim_periode
        WHERE tahun = ? AND periode = ?
    """, [TAHUN, periode]).fetchone()[0]


def add_province(con, name):
    con.execute("""
        INSERT INTO dim_provinsi (provinsi_id, nama_provinsi)
        VALUES (
            (SELECT COALESCE(MAX(provinsi_id), 0) + 1
             FROM dim_provinsi),
            ?
        )
        ON CONFLICT (nama_provinsi) DO NOTHING
    """, [name])

    return con.execute("""
        SELECT provinsi_id
        FROM dim_provinsi
        WHERE nama_provinsi = ?
    """, [name]).fetchone()[0]


def add_sector(con, code):
    con.execute("""
        INSERT INTO dim_sektor
            (sektor_id, kode_sektor, nama_sektor)
        VALUES (
            (SELECT COALESCE(MAX(sektor_id), 0) + 1
             FROM dim_sektor),
            ?, ?
        )
        ON CONFLICT (kode_sektor) DO NOTHING
    """, [code, code])

    return con.execute("""
        SELECT sektor_id
        FROM dim_sektor
        WHERE kode_sektor = ?
    """, [code]).fetchone()[0]


def insert_fact(con, table, columns, values):
    col_sql = ", ".join(columns)
    placeholders = ", ".join(["?"] * len(values))

    con.execute(
        f"INSERT INTO {table} ({col_sql}) VALUES ({placeholders})",
        values,
    )


def load_data(con):
    files = list(DATA_DIR.glob("*.xlsx"))
    if not files:
        raise FileNotFoundError(f"Tidak ada file Excel di {DATA_DIR}")

    # TPAK
    file_tpak = next(f for f in files if "TPAK" in f.name)
    df = pd.read_excel(file_tpak)
    df.columns = [str(c).strip() for c in df.columns]

    for _, row in df.iterrows():
        provinsi = clean_province(row["38 Provinsi"])
        if provinsi is None:
            continue

        pid = add_province(con, provinsi)

        for periode in ["Februari", "Agustus"]:
            period_id = add_period(con, periode)
            insert_fact(
                con, "fact_tpak",
                ["provinsi_id", "periode_id", "nilai_tpak"],
                [pid, period_id, clean_number(row[periode])],
            )

    # TPT
    file_tpt = next(f for f in files if "Pengangguran" in f.name)
    df = pd.read_excel(file_tpt)
    df.columns = [str(c).strip() for c in df.columns]

    for _, row in df.iterrows():
        provinsi = clean_province(row["38 Provinsi"])
        if provinsi is None:
            continue

        pid = add_province(con, provinsi)

        for periode in ["Februari", "Agustus"]:
            period_id = add_period(con, periode)
            insert_fact(
                con, "fact_tpt",
                ["provinsi_id", "periode_id", "nilai_tpt"],
                [pid, period_id, clean_number(row[periode])],
            )

    # Upah rata-rata menurut sektor
    file_upah = next(f for f in files if "Upah_Gaji" in f.name)
    df = pd.read_excel(file_upah)
    df.columns = [str(c).strip() for c in df.columns]

    for _, row in df.iterrows():
        sektor = str(row["17 sektor"]).strip()

        # Baris rata-rata adalah agregat, bukan sektor.
        if sektor.upper() == "RATA-RATA":
            continue

        sid = add_sector(con, sektor)

        for periode in BULAN_PERIODE:
            period_id = add_period(con, periode)
            insert_fact(
                con, "fact_upah_sektor",
                ["sektor_id", "periode_id", "nilai_upah"],
                [sid, period_id, clean_number(row[periode])],
            )

    # UMP
    file_ump = next(f for f in files if "UMP" in f.name)
    df = pd.read_excel(file_ump)
    df.columns = [str(c).strip() for c in df.columns]

    periode_id = add_period(con, "Tahunan")

    for _, row in df.iterrows():
        provinsi = clean_province(row["Provinsi di Indonesia"])
        if provinsi is None:
            continue

        pid = add_province(con, provinsi)
        insert_fact(
            con, "fact_ump",
            ["provinsi_id", "periode_id", "nilai_ump"],
            [pid, periode_id, clean_number(row["2025"])],
        )

    print("Pemuatan data ekonomi selesai.")


if __name__ == "__main__":
    import duckdb

    db = ROOT / "databases" / "ekonomi.duckdb"
    con = duckdb.connect(str(db))

    try:
        con.execute("BEGIN TRANSACTION")
        load_data(con)
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    finally:
        con.close()
