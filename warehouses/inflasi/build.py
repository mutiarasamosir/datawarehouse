import os
import duckdb
from load import process_and_load_inflasi

def main():
    # Tentukan path database output di folder databases/
    db_dir = "../../databases"
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "inflasi.duckdb")
    
    schema_path = "schema.sql"
    
    print(f"🚀 Membangun database DuckDB di: {db_path}")
    con = duckdb.connect(db_path)
    
    # 1. Jalankan schema.sql untuk membuat tabel kosong
    if os.path.exists(schema_path):
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        con.execute(schema_sql)
        print("✅ Skema tabel berhasil dibuat.")
    else:
        print(f"❌ File {schema_path} tidak ditemukan di direktori ini!")
        return

    # 2. Tentukan lokasi file data mentah BPS di folder data/
    # Sesuaikan nama file dengan file Excel inflasi yang Anda miliki di folder data/
    data_file = "../../data/inflasi_energi/inflasi_energi.xlsx" # atau path file Anda
    
    # 3. Jalankan fungsi load data
    process_and_load_inflasi(con, data_file)
    
    # 4. Testing hasil query singkat
    print("\n--- Hasil Uji Coba Query (Preview dim_waktu) ---")
    df_test = con.execute("SELECT * FROM dim_waktu LIMIT 5").df()
    print(df_test)
    
    con.close()
    print("\n🎉 Proses Build Warehouse Inflasi Sempurna!")

if __name__ == "__main__":
    main()