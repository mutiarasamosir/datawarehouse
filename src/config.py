from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATABASE_DIR = ROOT / "databases"

DATABASES = {
    "inflasi": DATABASE_DIR / "inflasi.duckdb",
    "pangan": DATABASE_DIR / "pangan.duckdb",
    "energi": DATABASE_DIR / "inflasi_energi.duckdb",
    "ekonomi": DATABASE_DIR / "ekonomi.duckdb",
    "sosial": DATABASE_DIR / "sosial.duckdb",
    "bencana": DATABASE_DIR / "bencana.duckdb",
}