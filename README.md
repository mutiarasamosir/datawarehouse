data-warehouse-project/
├── data/
│   └── processed/
│       ├── inflasi (1)/
│       ├── pangan (9)/
│       ├── energi (1)/
│       ├── ekonomi (4)/
│       ├── sosial (2)/
│       └── bencana (1)/
│
├── warehouses/
│   ├── inflasi/
│   │   ├── schema.sql
│   │   ├── load.py
│   │   └── build.py
│   ├── pangan/
│   │   ├── schema.sql
│   │   ├── load.py
│   │   └── build.py
│   ├── energi/
│   ├── ekonomi/
│   ├── sosial/
│   └── bencana/
│
├── databases/
│   ├── inflasi.duckdb
│   ├── inflasi_energi.duckdb
│   ├── pangan.duckdb
│   ├── energi.duckdb
│   ├── ekonomi.duckdb
│   ├── sosial.duckdb
│   └── bencana.duckdb
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── db.py
│   └── data_access.py
│
├── queries/
│   ├── 01_inflasi_bulanan.sql
│   ├── 02_harga_pangan_provinsi.sql
│   ├── 03_inflasi_vs_harga_pangan.sql
│   ├── 04_inflasi_energi.sql
│   ├── 05_inflasi_bencana.sql
│   ├── 06_kpi_inflasi.sql
│   ├── 07_kpi_harga_pangan.sql
│   ├── 08_cek_kualitas_harga.sql
│   ├── 09_analisis_ekonomi.sql
│   └── 10_analisis_sosial.sql
│
├── dashboard/
│   ├── app.py
│   ├── pages/
│   └── components/
│
├── tests/
├── scripts/
│   └── build_all.py
├── requirements.txt
├── .gitignore
└── README.md