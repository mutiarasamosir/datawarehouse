from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

# Lokasi seluruh database DuckDB
DATA_DIR = BASE_DIR / "warehouses"

DATABASES = {
    "inflasi": DATA_DIR / "inflasi.duckdb",
    "ekonomi": DATA_DIR / "ekonomi.duckdb",
    "sosial": DATA_DIR / "sosial.duckdb",
    "pangan": DATA_DIR / "pangan.duckdb",
    "energi": DATA_DIR / "energi.duckdb",
    "bencana": DATA_DIR / "bencana.duckdb",
}