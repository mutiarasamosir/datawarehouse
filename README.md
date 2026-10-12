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
│   ├── inflasi.sql
│   ├── pangan.sql
│   ├── energi.sql
│   ├── ekonomi.sql
│   ├── sosial.sql
│   └── bencana.sql
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