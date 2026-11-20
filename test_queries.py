
from pathlib import Path
from src.db import get_connection


def main():
    folder_queries = Path("queries")
    files = sorted(folder_queries.glob("*.sql"))

    if not files:
        print("Belum ada file SQL di folder queries!")
        return

    for file in files:
        print(f"\n=== {file.name} ===")

        con = None

        try:
            con = get_connection()

            sql = file.read_text(encoding="utf-8")
            df = con.execute(sql).df()

            print(df.head(5).to_string(index=False))
            print(f"Total baris: {len(df)}")

        except Exception as e:
            print(f"ERROR pada {file.name}: {e}")

        finally:
            if con is not None:
                con.close()


if __name__ == "__main__":
    main()