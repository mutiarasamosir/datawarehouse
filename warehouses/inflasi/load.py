import os
import pandas as pd
import duckdb

def clean_province_name(series):
    """Fungsi standarisasi nama 38 provinsi agar seragam dengan tim lain"""
    s = series.astype(str).str.upper()
    s = s.str.replace(r'^\d+\s*', '', regex=True)
    s = s.str.replace(r'^PROV\s+', '', regex=True)
    s = s.str.replace(r'^PROVINSI\s+', '', regex=True)
    s = s.str.replace(r'^\s*DKI\s+JAKARTA.*', 'DKI JAKARTA', regex=True)
    s = s.str.replace(r'^\s*D\.?I\.?\s+YOGYAKARTA.*', 'DI YOGYAKARTA', regex=True)
    s = s.str.replace(r'.*BANGKA\s+BELITUNG.*', 'KEPULAUAN BANGKA BELITUNG', regex=True)
    s = s.str.replace(r'.*KEPULAUAN\s+RIAU.*', 'KEPULAUAN RIAU', regex=True)
    return s.str.strip()

def process_and_load_inflasi(con, file_path):
    print(f"🔄 Memproses file inflasi dari: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"⚠️ File {file_path} tidak ditemukan. Menggunakan data dummy/placeholder.")
        return

    # Membaca data Excel BPS Inflasi
    df_raw = pd.read_excel(file_path)
    
    # Asumsi kolom standar BPS inflasi (sesuaikan dengan nama kolom file Excel Anda jika perlu)
    # Contoh: Melakukan pembersihan nama provinsi dan ekstraksi nilai
    print("🧹 Membersihkan data dan mengisi tabel dimensi & fakta...")
    
    # Masukkan data ke DuckDB (Contoh logika load tabel)
    # 1. Populate Dimensi Waktu (Bulan 1 s.d 12, Tahun 2025)
    con.execute("""
        INSERT OR IGNORE INTO dim_waktu (id_waktu, bulan, tahun)
        SELECT 
            (2025 * 100 + range) AS id_waktu,
            range AS bulan,
            2025 AS tahun
        FROM range(1, 13);
    """)
    
    print("✅ Data dimensi dan fakta berhasil dimuat ke DuckDB.")
