from pathlib import Path
from src.db import get_connection

def main():
    folder_queries = Path("queries")
    files = sorted(folder_queries.glob("*.sql"))

    if not files:
        print("Belum ada file SQL di folder queries!")
        return

    con = get_connection()

    try:
        for file in files:
            print(f"\n=== {file.name} ===")

            sql = file.read_text(encoding="utf-8")
            df = con.execute(sql).df()

            print(df.head(5).to_string(index=False))
            print(f"Total baris: {len(df)}")

    except Exception as e:
        print(f"Terjadi error: {e}")

    finally:
        con.close()

if __name__ == "__main__":
    main()