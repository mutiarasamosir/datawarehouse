
from pathlib import Path
import duckdb

# File ini berada di data/src/
ROOT = Path(__file__).resolve().parents[2]
DB_DIR = ROOT / "warehouses"

EXPECTED = {
    "ekonomi.duckdb": ["ump", "tpt", "tpak", "upah"],
    "sosial.duckdb": ["penduduk", "pengeluaran_per_kapita"],
}


def test_database(filename, expected_tables):
    db_path = DB_DIR / filename

    print(f"\nMemeriksa database: {filename}")

    assert db_path.exists(), (
        f"Database tidak ditemukan: {db_path}"
    )

    con = duckdb.connect(str(db_path), read_only=True)

    try:
        tables = {
            row[0]
            for row in con.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'main'
            """).fetchall()
        }

        # Pastikan semua tabel yang diharapkan tersedia
        for table in expected_tables:
            assert table in tables, (
                f"Tabel '{table}' tidak ditemukan."
            )

            quoted = '"' + table.replace('"', '""') + '"'

            # Periksa jumlah baris
            row_count = con.execute(
                f"SELECT COUNT(*) FROM {quoted}"
            ).fetchone()[0]

            # Periksa nama kolom dan tipe data
            schema = con.execute(
                f"DESCRIBE SELECT * FROM {quoted}"
            ).fetchall()

            assert row_count > 0, (
                f"Tabel '{table}' tidak memiliki data."
            )
            assert len(schema) > 0, (
                f"Tabel '{table}' tidak memiliki kolom."
            )

            print(f"\n  Tabel: {table}")
            print(f"  Jumlah baris: {row_count}")
            print("  Kolom dan tipe data:")

            for column in schema:
                print(f"    - {column[0]}: {column[1]}")

            print("  Status: LULUS")

        print(f"\nLULUS: {filename}")

    finally:
        con.close()


if __name__ == "__main__":
    for filename, tables in EXPECTED.items():
        test_database(filename, tables)

    print("\nSemua pengujian dasar berhasil!")
