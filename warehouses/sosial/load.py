from pathlib import Path
import re

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "sosial"
TAHUN = 2025

PROVINSI = {
    "ACEH",
    "SUMATERA UTARA",
    "SUMATERA BARAT",
    "RIAU",
    "JAMBI",
    "SUMATERA SELATAN",
    "BENGKULU",
    "LAMPUNG",
    "KEPULAUAN BANGKA BELITUNG",
    "KEPULAUAN RIAU",
    "DKI JAKARTA",
    "JAWA BARAT",
    "JAWA TENGAH",
    "DI YOGYAKARTA",
    "JAWA TIMUR",
    "BANTEN",
    "BALI",
    "NUSA TENGGARA BARAT",
    "NUSA TENGGARA TIMUR",
    "KALIMANTAN BARAT",
    "KALIMANTAN TENGAH",
    "KALIMANTAN SELATAN",
    "KALIMANTAN TIMUR",
    "KALIMANTAN UTARA",
    "SULAWESI UTARA",
    "SULAWESI TENGAH",
    "SULAWESI SELATAN",
    "SULAWESI TENGGARA",
    "GORONTALO",
    "SULAWESI BARAT",
    "MALUKU",
    "MALUKU UTARA",
    "PAPUA BARAT",
    "PAPUA BARAT DAYA",
    "PAPUA",
    "PAPUA SELATAN",
    "PAPUA TENGAH",
    "PAPUA PEGUNUNGAN",
}

ALIAS_PROVINSI = {
    "KEP. BANGKA BELITUNG": "KEPULAUAN BANGKA BELITUNG",
    "KEP. RIAU": "KEPULAUAN RIAU",
}


def clean_number(value):
    """Ubah angka menjadi float; nilai kosong atau '-' menjadi 0."""
    if pd.isna(value):
        return 0.0

    text = str(value).strip()

    if text in {"", "-"}:
        return 0.0

    text = text.replace(",", "")

    try:
        return float(text)
    except (ValueError, TypeError):
        return 0.0


def clean_name(value):
    """Bersihkan nama wilayah."""
    if pd.isna(value):
        return None

    name = re.sub(r"\s+", " ", str(value)).strip()

    if not name or name.upper() in {"NAN", "INDONESIA"}:
        return None

    return name


def normalize_province(value):
    """Normalisasi nama provinsi sesuai daftar provinsi."""
    name = clean_name(value)

    if name is None:
        return None

    name = re.sub(r"^\d+\s+", "", name).upper()
    name = ALIAS_PROVINSI.get(name, name)

    return name if name in PROVINSI else None


def add_province(con, name):
    """Masukkan provinsi jika belum ada, lalu kembalikan ID-nya."""
    name = normalize_province(name)

    if name is None:
        raise ValueError("Nama provinsi tidak valid.")

    con.execute(
        """
        INSERT INTO dim_provinsi (provinsi_id, nama_provinsi)
        SELECT COALESCE(MAX(provinsi_id), 0) + 1, ?
        FROM dim_provinsi
        ON CONFLICT (nama_provinsi) DO NOTHING
        """,
        [name],
    )

    return con.execute(
        """
        SELECT provinsi_id
        FROM dim_provinsi
        WHERE nama_provinsi = ?
        """,
        [name],
    ).fetchone()[0]


def add_period(con):
    """Buat periode tahunan 2025 jika belum tersedia."""
    con.execute(
        """
        INSERT INTO dim_periode (periode_id, tahun, periode)
        SELECT COALESCE(MAX(periode_id), 0) + 1, ?, 'Tahunan'
        FROM dim_periode
        ON CONFLICT (tahun, periode) DO NOTHING
        """,
        [TAHUN],
    )

    return con.execute(
        """
        SELECT periode_id
        FROM dim_periode
        WHERE tahun = ? AND periode = 'Tahunan'
        """,
        [TAHUN],
    ).fetchone()[0]


def add_region(con, name, kind, province_id=None):
    """Buat wilayah jika belum ada, lalu kembalikan ID-nya."""
    found = con.execute(
        """
        SELECT wilayah_id
        FROM dim_wilayah
        WHERE nama_wilayah = ?
          AND jenis_wilayah = ?
          AND provinsi_id IS NOT DISTINCT FROM ?
        LIMIT 1
        """,
        [name, kind, province_id],
    ).fetchone()

    if found:
        return found[0]

    next_id = con.execute(
        """
        SELECT COALESCE(MAX(wilayah_id), 0) + 1
        FROM dim_wilayah
        """
    ).fetchone()[0]

    con.execute(
        """
        INSERT INTO dim_wilayah (
            wilayah_id,
            nama_wilayah,
            jenis_wilayah,
            provinsi_id
        )
        VALUES (?, ?, ?, ?)
        """,
        [next_id, name, kind, province_id],
    )

    return next_id


def load_population(con, file, period_id):
    """Muat indikator penduduk untuk 38 provinsi."""
    df = pd.read_excel(file)

    df = df.loc[
        :,
        ~df.columns.astype(str).str.startswith("Unnamed:"),
    ]
    df = df.dropna(axis=1, how="all")

    if "Provinsi" not in df.columns:
        raise ValueError(
            f"Kolom 'Provinsi' tidak ditemukan dalam {file.name}"
        )

    df["_provinsi"] = df["Provinsi"].apply(normalize_province)
    df = df[df["_provinsi"].notna()].copy()

    # Pastikan setiap provinsi hanya muncul satu kali.
    df = df.drop_duplicates(subset=["_provinsi"], keep="first")

    if df["_provinsi"].nunique() != 38:
        daftar = sorted(df["_provinsi"].dropna().unique().tolist())
        raise ValueError(
            "Data penduduk tidak menghasilkan 38 provinsi. "
            f"Provinsi terbaca: {len(daftar)}; daftar: {daftar}"
        )

    kolom_indikator = {
        "Jumlah Penduduk (Ribu)": "jumlah_penduduk_ribu",
        "Laju Pertumbuhan Penduduk per Tahun": "laju_pertumbuhan",
        "Persentase Penduduk": "persentase_penduduk",
        "Kepadatan Penduduk per km persegi (Km2)": "kepadatan_penduduk",
        "Rasio Jenis Kelamin Penduduk": "rasio_jenis_kelamin",
    }

    for kolom in kolom_indikator:
        if kolom not in df.columns:
            raise ValueError(
                f"Kolom '{kolom}' tidak ditemukan pada data penduduk."
            )

    for _, row in df.iterrows():
        province_id = add_province(con, row["_provinsi"])

        values = [
            province_id,
            period_id,
            *[
                clean_number(row[kolom])
                for kolom in kolom_indikator
            ],
        ]

        con.execute(
            """
            INSERT INTO fact_penduduk (
                provinsi_id,
                periode_id,
                jumlah_penduduk_ribu,
                laju_pertumbuhan,
                persentase_penduduk,
                kepadatan_penduduk,
                rasio_jenis_kelamin
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            values,
        )

    print(f"Data penduduk dimuat: {len(df)} provinsi")


def load_expenditure(con, file, period_id):
    """Muat pengeluaran per kapita menurut wilayah dan jenis kelamin."""
    df = pd.read_excel(file)
    df.columns = df.columns.astype(str).str.strip()

    required_columns = {"Kota", "Laki-Laki", "Perempuan"}
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Kolom pengeluaran tidak ditemukan: {sorted(missing)}"
        )

    df = df.dropna(subset=["Kota"])
    df = df.drop_duplicates(subset=["Kota"], keep="first")

    province_ids = {
        row[1]: row[0]
        for row in con.execute(
            """
            SELECT provinsi_id, nama_provinsi
            FROM dim_provinsi
            """
        ).fetchall()
    }

    current_province_id = None
    total = 0

    for _, row in df.iterrows():
        raw_name = clean_name(row["Kota"])

        if raw_name is None:
            continue

        # Provinsi pada sumber ditulis dengan huruf kapital semua.
        province_name = normalize_province(raw_name)

        if raw_name == raw_name.upper() and province_name:
            current_province_id = province_ids.get(province_name)

            if current_province_id is None:
                raise ValueError(
                    f"ID provinsi tidak ditemukan: {province_name}"
                )

            region_name = province_name
            region_type = "provinsi"
            parent_id = current_province_id

        else:
            # Baris kabupaten/kota mengikuti provinsi sebelumnya.
            if current_province_id is None:
                continue

            region_name = raw_name
            region_type = "kabupaten_kota"
            parent_id = current_province_id

            # Bedakan kabupaten ini dari provinsinya.
            if raw_name.casefold() == "gorontalo":
                region_name = "Kabupaten Gorontalo"

        wilayah_id = add_region(
            con,
            region_name,
            region_type,
            parent_id,
        )

        con.execute(
            """
            INSERT INTO fact_pengeluaran_per_kapita (
                wilayah_id,
                periode_id,
                pengeluaran_laki_laki,
                pengeluaran_perempuan
            )
            VALUES (?, ?, ?, ?)
            """,
            [
                wilayah_id,
                period_id,
                clean_number(row["Laki-Laki"]),
                clean_number(row["Perempuan"]),
            ],
        )

        total += 1

    print(f"Data pengeluaran per kapita dimuat: {total} wilayah")


def load_data(con):
    """Panggil seluruh proses pemuatan data sosial."""
    files = list(DATA_DIR.glob("*.xlsx"))

    if not files:
        raise FileNotFoundError(
            f"Tidak ada file Excel di {DATA_DIR}"
        )

    population_files = [
        file for file in files
        if "Penduduk" in file.name
    ]

    expenditure_files = [
        file for file in files
        if "Pengeluaran" in file.name
    ]

    if len(population_files) != 1 or len(expenditure_files) != 1:
        raise FileNotFoundError(
            "Pastikan folder sosial memiliki satu file penduduk "
            "dan satu file pengeluaran per kapita."
        )

    period_id = add_period(con)

    load_population(con, population_files[0], period_id)
    load_expenditure(con, expenditure_files[0], period_id)

    print("Pemuatan data sosial selesai.")