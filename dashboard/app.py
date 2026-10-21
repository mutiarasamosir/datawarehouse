from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data_access import query_df


# =========================================================
# KONFIGURASI
# =========================================================
ROOT = Path(__file__).resolve().parents[1]
QUERY_DIR = ROOT / "queries"

GREEN_DARK = "#14532D"
GREEN_DEEP = "#064E3B"
GREEN = "#15803D"
GREEN_MID = "#22A447"
GREEN_BRIGHT = "#4ADE80"
GREEN_LIGHT = "#86EFAC"
GREEN_PALE = "#DCFCE7"
GREEN_BG = "#F4FBF5"
WHITE = "#FFFFFF"
TEXT_DARK = "#123524"
TEXT_MUTED = "#64816E"

GREEN_PALETTE = [
    "#14532D",
    "#15803D",
    "#22A447",
    "#4ADE80",
    "#86EFAC",
    "#BBF7D0",
]

MONTH_LABELS = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
    5: "Mei", 6: "Jun", 7: "Jul", 8: "Agu",
    9: "Sep", 10: "Okt", 11: "Nov", 12: "Des",
}


# =========================================================
# KOORDINAT PUSAT PROVINSI INDONESIA
# Format: "NAMA PROVINSI": (latitude, longitude)
# =========================================================

PROVINCE_COORDS = {
    "ACEH": (4.70, 96.75),
    "SUMATERA UTARA": (2.12, 99.55),
    "SUMATERA BARAT": (-0.74, 100.80),
    "RIAU": (0.29, 101.71),
    "KEPULAUAN RIAU": (3.95, 108.14),
    "JAMBI": (-1.49, 102.44),
    "SUMATERA SELATAN": (-3.32, 103.91),
    "KEPULAUAN BANGKA BELITUNG": (-2.74, 106.44),
    "BENGKULU": (-3.58, 102.35),
    "LAMPUNG": (-4.56, 105.41),
    "DKI JAKARTA": (-6.21, 106.85),
    "JAWA BARAT": (-6.90, 107.57),
    "BANTEN": (-6.41, 106.06),
    "JAWA TENGAH": (-7.15, 110.14),
    "DI YOGYAKARTA": (-7.80, 110.37),
    "DAERAH ISTIMEWA YOGYAKARTA": (-7.80, 110.37),
    "JAWA TIMUR": (-7.54, 112.24),
    "BALI": (-8.41, 115.19),
    "NUSA TENGGARA BARAT": (-8.65, 117.36),
    "NUSA TENGGARA TIMUR": (-8.66, 121.08),
    "KALIMANTAN BARAT": (-0.28, 111.48),
    "KALIMANTAN TENGAH": (-1.68, 113.38),
    "KALIMANTAN SELATAN": (-3.09, 115.28),
    "KALIMANTAN TIMUR": (1.64, 116.42),
    "KALIMANTAN UTARA": (2.88, 116.67),
    "SULAWESI UTARA": (0.62, 123.98),
    "GORONTALO": (0.70, 122.45),
    "SULAWESI TENGAH": (-1.43, 121.45),
    "SULAWESI BARAT": (-2.84, 119.23),
    "SULAWESI SELATAN": (-3.67, 119.97),
    "SULAWESI TENGGARA": (-4.14, 122.17),
    "MALUKU": (-3.24, 130.15),
    "MALUKU UTARA": (1.57, 127.81),
    "PAPUA BARAT": (-1.34, 133.17),
    "PAPUA BARAT DAYA": (-0.87, 131.25),
    "PAPUA": (-4.27, 138.08),
    "PAPUA SELATAN": (-7.00, 139.50),
    "PAPUA TENGAH": (-3.90, 136.50),
    "PAPUA PEGUNUNGAN": (-4.00, 139.00),
}

st.set_page_config(
    page_title="Dashboard Data Warehouse Indonesia",
    page_icon="🌿",
    layout="wide",
)

# =========================================================
# CSS TEMA HIJAU MODERN
# =========================================================
st.markdown(
    """
    <style>
    .stApp {
        background: #F4FBF5;
        color: #123524;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg, #E8F5E9 0%, #F4FBF5 100%
        );
        border-right: 1px solid #CDE8D2;
    }

    [data-testid="stSidebar"] * {
        color: #123524;
    }

    h1, h2, h3 {
        color: #064E3B !important;
        font-weight: 750 !important;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(
            135deg, #FFFFFF 0%, #E8F8EC 100%
        );
        border: 1px solid #CDE8D2;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 3px 12px rgba(20, 83, 45, 0.05);
    }

    [data-testid="stMetricLabel"] {
        color: #426B50 !important;
    }

    [data-testid="stMetricValue"] {
        color: #14532D !important;
        font-weight: 750 !important;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background-color: #FFFFFF;
        border-color: #B7DCC0;
        border-radius: 10px;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF;
        border: 1px solid #DCEFE0;
        border-radius: 16px;
    }

    .stButton > button,
    .stDownloadButton > button {
        background-color: #15803D;
        color: #FFFFFF;
        border: none;
        border-radius: 10px;
        font-weight: 600;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background-color: #14532D;
        color: #FFFFFF;
        border: none;
    }

    hr {
        border-color: #D5EAD9;
    }

    div[data-testid="stPlotlyChart"] {
        background: #FFFFFF;
        border: 1px solid #E0EEE3;
        border-radius: 14px;
        padding: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# FUNGSI DASAR DATA
# =========================================================
@st.cache_data(ttl=300)
def load_query(filename: str) -> pd.DataFrame:
    """Menjalankan file SQL yang ada di folder queries."""
    path = QUERY_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"File SQL tidak ditemukan: {path}")

    sql = path.read_text(encoding="utf-8")
    return query_df(sql)


def safe_load(filename: str) -> pd.DataFrame:
    """Memuat data dan menampilkan peringatan jika query gagal."""
    try:
        return load_query(filename)
    except Exception as error:
        st.warning(f"Gagal memuat {filename}: {error}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def load_disaster_detail() -> pd.DataFrame:
    """
    Mencari tabel bencana detail pada DuckDB yang memiliki kolom
    jenis bencana. Jika tabel sumber tidak tersedia, kembalikan
    DataFrame kosong agar dashboard tetap berjalan.
    """
    try:
        tables = query_df("SHOW ALL TABLES")
    except Exception:
        return pd.DataFrame()

    if tables.empty:
        return pd.DataFrame()

    tables = clean_names(tables)
    table_col = find_column(tables, ["name", "table_name"])
    db_col = find_column(tables, ["database", "database_name", "catalog"])
    schema_col = find_column(tables, ["schema", "schema_name"])

    if not table_col:
        return pd.DataFrame()

    # Utamakan tabel yang namanya berkaitan dengan bencana.
    candidates = []
    for _, row in tables.iterrows():
        table_name = str(row.get(table_col, ""))
        database_name = str(row.get(db_col, "")) if db_col else ""
        combined = f"{database_name} {table_name}".lower()
        if "bencana" in combined or "disaster" in combined:
            candidates.append(row)

    for row in candidates:
        table_name = str(row.get(table_col, ""))
        database_name = str(row.get(db_col, "")) if db_col else ""
        schema_name = str(row.get(schema_col, "main")) if schema_col else "main"

        # Identifier di-quote untuk menangani nama yang memiliki spasi.
        qualified = ".".join(
            '"' + part.replace('"', '""') + '"'
            for part in [database_name, schema_name, table_name]
            if part and part.lower() != "nan"
        )

        try:
            candidate_df = query_df(f"SELECT * FROM {qualified} LIMIT 50000")
        except Exception:
            continue

        candidate_df = clean_names(candidate_df)
        type_col = find_column(
            candidate_df,
            [
                "jenis_bencana", "nama_bencana", "tipe_bencana",
                "jenis", "disaster_type", "event_type",
            ],
        )
        province_col = find_column(
            candidate_df,
            ["nama_provinsi", "provinsi", "province"],
        )
        if type_col and province_col:
            return candidate_df

    return pd.DataFrame()


def clean_names(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result.columns = [str(c).strip().lower() for c in result.columns]
    return result


def find_column(df: pd.DataFrame, candidates: list[str]):
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    return None


def prepare_month(
    df: pd.DataFrame,
    month_col: str = "bulan",
    year_col: str = "tahun",
) -> pd.DataFrame:
    """
    Menormalisasi kolom bulan dan tahun.
    Angka bulan 1-12 diperlakukan sebagai angka, bukan timestamp.
    """
    result = clean_names(df)

    if year_col in result.columns:
        result["_year"] = pd.to_numeric(
            result[year_col], errors="coerce"
        )
    else:
        result["_year"] = pd.Series(
            pd.NA, index=result.index, dtype="Float64"
        )

    if month_col not in result.columns:
        result["_month"] = pd.Series(
            pd.NA, index=result.index, dtype="Float64"
        )
    else:
        raw = result[month_col]
        numeric = pd.to_numeric(raw, errors="coerce")

        # Kolom bulan berupa angka 1 sampai 12
        numeric_valid = (
            numeric.notna().all()
            and numeric.between(1, 12).all()
        )

        if numeric_valid:
            result["_month"] = numeric
        else:
            # Kolom bulan berupa tanggal seperti 2025-01-01
            dates = pd.to_datetime(raw, errors="coerce")
            result["_month"] = dates.dt.month
            result["_year"] = result["_year"].fillna(dates.dt.year)

    result["_month"] = pd.to_numeric(
        result["_month"], errors="coerce"
    )
    result["_year"] = pd.to_numeric(
        result["_year"], errors="coerce"
    )
    result["_month_label"] = result["_month"].map(MONTH_LABELS)

    return result


def rename_for_display(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result.columns = [
        str(c).replace("_", " ").strip().title()
        for c in result.columns
    ]
    return result


def green_layout(fig, height: int = 390):
    fig.update_layout(
        height=height,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Arial, sans-serif",
            color="#294C35",
            size=12,
        ),
        title=dict(
            font=dict(size=17, color="#064E3B"),
            x=0.02,
            xanchor="left",
        ),
        margin=dict(l=25, r=25, t=65, b=35),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(color="#426B50"),
        ),
        colorway=GREEN_PALETTE,
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor="#DCEFE0",
        tickfont=dict(color="#64816E"),
        title_font=dict(color="#426B50"),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#E7F3E9",
        zerolinecolor="#CDE8D2",
        tickfont=dict(color="#64816E"),
        title_font=dict(color="#426B50"),
    )
    return fig


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    result = df.copy()

    if selected_year != "Semua" and "_year" in result.columns:
        result = result[
            pd.to_numeric(result["_year"], errors="coerce")
            == int(selected_year)
        ]

    province_col = find_column(
        result, ["nama_provinsi", "provinsi"]
    )
    if selected_province != "Semua" and province_col:
        result = result[
            result[province_col].astype(str).str.strip().str.upper()
            == selected_province.strip().upper()
        ]

    return result


# =========================================================
# MEMUAT QUERY WAREHOUSE
# =========================================================
q01 = prepare_month(safe_load("01_inflasi_bulanan.sql"))
q02 = prepare_month(safe_load("02_harga_pangan_provinsi.sql"))
q03 = prepare_month(safe_load("03_inflasi_vs_harga_pangan.sql"))
q04 = prepare_month(safe_load("04_inflasi_energi.sql"))
q05 = prepare_month(safe_load("05_inflasi_bencana.sql"))
q06 = safe_load("06_kpi_inflasi.sql")
q07 = safe_load("07_kpi_harga_pangan.sql")
q09 = safe_load("09_analisis_ekonomi.sql")
q10 = safe_load("10_analisis_sosial.sql")
q11 = prepare_month(safe_load("11_integrasi_semua_faktor.sql"))


# =========================================================
# FILTER SIDEBAR
# =========================================================
st.sidebar.markdown("# 🌿 Filter Dashboard")

year_values = set()
for frame in [q01, q02, q03, q04, q05, q11]:
    if not frame.empty and "_year" in frame.columns:
        years = pd.to_numeric(
            frame["_year"], errors="coerce"
        ).dropna()
        year_values.update(years.astype(int).tolist())

year_options = sorted(year_values)

selected_year = st.sidebar.selectbox(
    "Tahun",
    ["Semua"] + year_options,
)

province_col_sidebar = find_column(
    q11, ["nama_provinsi", "provinsi"]
)
province_options = []
if not q11.empty and province_col_sidebar:
    province_options = sorted(
        q11[province_col_sidebar].dropna().astype(str).unique().tolist()
    )

selected_province = st.sidebar.selectbox(
    "Provinsi",
    ["Semua"] + province_options,
)

commodity_col_sidebar = find_column(
    q02, ["nama_komoditas", "komoditas"]
)
commodity_options = []
if not q02.empty and commodity_col_sidebar:
    commodity_options = sorted(
        q02[commodity_col_sidebar].dropna().astype(str).unique().tolist()
    )

selected_commodity_sidebar = st.sidebar.selectbox(
    "Komoditas (untuk grafik harga pangan)",
    ["Semua"] + commodity_options,
)

st.sidebar.markdown("---")
st.sidebar.info(
    "Data diambil dari query SQL pada folder `queries`."
)


# Terapkan filter global setelah kontrol sidebar dibuat
f01 = apply_filters(q01)
f02 = apply_filters(q02)
f03 = apply_filters(q03)
f04 = apply_filters(q04)
f05 = apply_filters(q05)
f11 = apply_filters(q11)

if (
    selected_commodity_sidebar != "Semua"
    and not f02.empty
    and commodity_col_sidebar
):
    f02 = f02[
        f02[commodity_col_sidebar].astype(str)
        == selected_commodity_sidebar
    ]

if (
    selected_commodity_sidebar != "Semua"
    and not f03.empty
):
    commodity_col_q03 = find_column(
        f03, ["nama_komoditas", "komoditas"]
    )
    if commodity_col_q03:
        f03 = f03[
            f03[commodity_col_q03].astype(str)
            == selected_commodity_sidebar
        ]


# =========================================================
# HEADER
# =========================================================
st.title("Dashboard Data Warehouse Indonesia")
st.markdown(
    "Analisis inflasi, harga pangan, bencana, serta faktor ekonomi dan sosial."
)

st.divider()




# =========================================================
# KPI CARDS
# =========================================================
inflation_col = find_column(f11, ["inflasi_umum"])
disaster_col = find_column(f11, ["jumlah_kejadian"])
death_col = find_column(f11, ["korban_meninggal"])

avg_inflation = (
    pd.to_numeric(f11[inflation_col], errors="coerce").mean()
    if inflation_col and not f11.empty else float("nan")
)

total_disasters = (
    pd.to_numeric(f11[disaster_col], errors="coerce").sum()
    if disaster_col and not f11.empty else 0
)

total_deaths = (
    pd.to_numeric(f11[death_col], errors="coerce").sum()
    if death_col and not f11.empty else 0
)

# Data harga pangan berdasarkan filter tahun dan provinsi
food_data = apply_filters(q02).copy()

food_col = find_column(food_data, ["harga"])
commodity_col = find_column(
    food_data, ["nama_komoditas", "komoditas"]
)

if food_col and commodity_col and not food_data.empty:
    food_data[food_col] = pd.to_numeric(
        food_data[food_col], errors="coerce"
    )

    commodities = sorted(
        food_data[commodity_col]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
else:
    commodities = []

# Empat KPI Cards
k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Rata-rata Inflasi",
    f"{avg_inflation:.2f}%"
    if pd.notna(avg_inflation) else "N/A"
)

with k2:
    st.markdown("**Rata-rata Harga Pangan**")

    selected_food_kpi = st.selectbox(
        "Pilih komoditas",
        ["Semua Komoditas"] + commodities,
        key="kpi_filter_komoditas",
        label_visibility="collapsed"
    )

    filtered_food = food_data.copy()

    if (
        selected_food_kpi != "Semua Komoditas"
        and commodity_col
    ):
        filtered_food = filtered_food[
            filtered_food[commodity_col].astype(str)
            == selected_food_kpi
        ]

    avg_food = (
        filtered_food[food_col].mean()
        if food_col and not filtered_food.empty
        else float("nan")
    )

    st.metric(
        label=" ",
        value=(
            f"Rp {avg_food:,.0f}"
            if pd.notna(avg_food) else "N/A"
        )
    )

k3.metric(
    "Total Kejadian Bencana",
    f"{total_disasters:,.0f}"
)

k4.metric(
    "Total Korban Meninggal",
    f"{total_deaths:,.0f}"
)

st.markdown("")




# =========================================================
# VISUALISASI 1: PERINGKAT SELURUH PROVINSI
# =========================================================

def render_disaster_ranking_chart():
    st.subheader("1. Indikator Bencana Seluruh Provinsi")

    if f05.empty:
        st.info("Data bencana tidak tersedia.")
        return

    province_col = find_column(
        f05, ["nama_provinsi", "provinsi"]
    )

    indicator_options = {
        "Jumlah Kejadian": "jumlah_kejadian",
        "Korban Meninggal": "korban_meninggal",
        "Korban Terluka": "korban_luka",
    }

    available = {
        label: column
        for label, column in indicator_options.items()
        if column in f05.columns
    }

    if not province_col:
        st.warning("Kolom provinsi tidak ditemukan.")
        return

    if not available:
        st.warning("Kolom indikator bencana tidak ditemukan.")
        return

    selected_indicator = st.selectbox(
        "Indikator grafik",
        list(available.keys()),
        key="ranking_disaster_indicator",
    )

    value_col = available[selected_indicator]

    data = f05.copy()
    data[value_col] = pd.to_numeric(
        data[value_col], errors="coerce"
    )

    data = data.dropna(
        subset=[province_col, value_col]
    )

    # Jumlahkan nilai per provinsi
    summary = (
        data.groupby(province_col, as_index=False)[value_col]
        .sum(min_count=1)
        .sort_values(value_col, ascending=True)
    )

    if summary.empty:
        st.info("Tidak ada data valid untuk indikator ini.")
        return

    # Grafik seluruh provinsi, bukan hanya 15 teratas
    fig = px.bar(
        summary,
        x=value_col,
        y=province_col,
        orientation="h",
        color=value_col,
        text=value_col,
        color_continuous_scale=[
            "#DCFCE7", "#86EFAC",
            "#22A447", "#14532D"
        ],
        labels={
            province_col: "Provinsi",
            value_col: selected_indicator,
        },
        title=f"{selected_indicator} di Seluruh Provinsi",
    )

    fig.update_traces(
        texttemplate="%{x:,.0f}",
        textposition="outside",
        cliponaxis=False,
    )

    # Tinggi grafik menyesuaikan jumlah provinsi
    chart_height = max(650, len(summary) * 35)

    fig.update_layout(
        coloraxis_showscale=False,
        height=chart_height,
        margin=dict(l=30, r=50, t=65, b=45),
        yaxis=dict(
            title="Provinsi",
            automargin=True,
            tickfont=dict(size=10),
        ),
        xaxis=dict(
            title=selected_indicator,
            rangemode="tozero",
        ),
    )

    # Buat area scroll dengan tinggi tetap
    import streamlit.components.v1 as components

    chart_html = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        config={"responsive": True},
    )

    components.html(
        f"""
        <div style="
            height: 650px;
            overflow-y: auto;
            overflow-x: hidden;
            border: 1px solid #DCEFE0;
            border-radius: 14px;
            background: white;
        ">
            {chart_html}
        </div>
        """,
        height=670,
        scrolling=False,
    )

    st.caption(
        f"Menampilkan seluruh {len(summary)} provinsi "
        f"yang memiliki data valid untuk indikator "
        f"{selected_indicator.lower()}."
    )


# =========================================================
# VISUALISASI 2: KEJADIAN BENCANA PER BULAN
# =========================================================
def render_disaster_type_chart():
    st.subheader("2. Kejadian Bencana per Bulan")

    if f05.empty:
        st.info("Data bencana tidak tersedia.")
        return

    disaster_col = find_column(f05, ["jumlah_kejadian"])
    if not disaster_col:
        st.warning("Kolom jumlah kejadian tidak ditemukan.")
        return

    data = f05.copy()
    data[disaster_col] = pd.to_numeric(
        data[disaster_col], errors="coerce"
    )
    data["_month"] = pd.to_numeric(
        data["_month"], errors="coerce"
    )
    data = data.dropna(subset=["_month"])

    grouped = (
        data.groupby("_month", as_index=False)[disaster_col]
        .sum(min_count=1)
        .sort_values("_month")
    )
    grouped["Bulan"] = grouped["_month"].map(MONTH_LABELS)

    fig = px.bar(
        grouped,
        x="Bulan",
        y=disaster_col,
        text=disaster_col,
        color_discrete_sequence=["#22A447"],
        labels={
            "Bulan": "Bulan",
            disaster_col: "Jumlah Kejadian",
        },
        title="Jumlah Kejadian Bencana per Bulan",
    )
    fig.update_traces(
        textposition="outside",
        marker_line_width=0,
    )
    st.plotly_chart(
        green_layout(fig, 390),
        use_container_width=True,
    )
    st.caption(
        "Data query yang tersedia berupa jumlah bencana agregat per "
        "provinsi dan bulan. Jenis bencana seperti gempa, tsunami, dan "
        "banjir memerlukan kolom jenis bencana pada tabel sumber."
    )


# =========================================================
# VISUALISASI 3: INFLASI DAN HARGA PANGAN
# =========================================================
def render_inflation_food_chart():
    st.subheader("3. Inflasi dan Harga Pangan")

    if f03.empty:
        st.info("Data gabungan inflasi dan harga pangan tidak tersedia.")
        return

    commodity = find_column(
        f03, ["nama_komoditas", "komoditas"]
    )
    price = find_column(f03, ["harga"])
    inflation = find_column(f03, ["inflasi_umum"])

    if not commodity or not price or not inflation:
        st.warning("Kolom komoditas, harga, atau inflasi tidak ditemukan.")
        return

    data = f03.copy()
    data[price] = pd.to_numeric(data[price], errors="coerce")
    data[inflation] = pd.to_numeric(
        data[inflation], errors="coerce"
    )

    commodities = sorted(
        data[commodity].dropna().astype(str).unique().tolist()
    )
    if not commodities:
        st.info("Tidak ada komoditas yang dapat ditampilkan.")
        return

    default_index = 0
    if selected_commodity_sidebar != "Semua":
        if selected_commodity_sidebar in commodities:
            default_index = commodities.index(selected_commodity_sidebar)

    selected_commodity = st.selectbox(
        "Komoditas",
        commodities,
        index=default_index,
        key="commodity_inflation",
    )

    data = data[
        data[commodity].astype(str) == selected_commodity
    ]

    grouped = (
        data.groupby(["_year", "_month"], as_index=False)
        .agg(
            Harga=(price, "mean"),
            Inflasi=(inflation, "mean"),
        )
        .dropna(subset=["_month"])
        .sort_values(["_year", "_month"])
    )

    if grouped.empty:
        st.info("Tidak ada data untuk kombinasi filter ini.")
        return

    grouped["Periode"] = (
        grouped["_year"].astype("Int64").astype(str)
        + "-"
        + grouped["_month"].astype("Int64").astype(str).str.zfill(2)
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=grouped["Periode"],
            y=grouped["Harga"],
            name="Harga Pangan (Rp)",
            marker_color="#4ADE80",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=grouped["Periode"],
            y=grouped["Inflasi"],
            name="Inflasi Umum (%)",
            mode="lines+markers",
            line=dict(color="#14532D", width=3),
            marker=dict(size=7, color="#14532D"),
            yaxis="y2",
        )
    )
    fig.update_layout(
        title=f"Inflasi dan Harga {selected_commodity}",
        yaxis=dict(title="Harga Rata-rata (Rp)"),
        yaxis2=dict(
            title="Inflasi (%)",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        barmode="group",
    )
    st.plotly_chart(
        green_layout(fig, 420),
        use_container_width=True,
    )


# =========================================================
# VISUALISASI 4: TREN INFLASI UMUM DAN ENERGI
# =========================================================
def render_inflation_spikes():
    st.subheader("4. Perubahan Inflasi Umum dan Energi")

    records = []

    if not f01.empty:
        col = find_column(f01, ["inflasi_umum"])
        if col:
            temp = f01.copy()
            temp["Nilai"] = pd.to_numeric(
                temp[col], errors="coerce"
            )
            temp["Jenis"] = "Inflasi Umum"
            records.append(
                temp[["_year", "_month", "Nilai", "Jenis"]]
            )

    if not f04.empty:
        col = find_column(f04, ["nilai_inflasi"])
        if col:
            temp = f04.copy()
            temp["Nilai"] = pd.to_numeric(
                temp[col], errors="coerce"
            )
            temp["Jenis"] = "Inflasi Energi"
            records.append(
                temp[["_year", "_month", "Nilai", "Jenis"]]
            )

    if not records:
        st.info("Data inflasi umum dan energi tidak tersedia.")
        return

    combined = pd.concat(records, ignore_index=True)
    combined = combined.dropna(subset=["_month", "Nilai"])
    combined = (
        combined.groupby(
            ["_year", "_month", "Jenis"], as_index=False
        )["Nilai"]
        .mean()
        .sort_values(["_year", "_month"])
    )

    if combined.empty:
        st.info("Tidak ada nilai inflasi yang valid.")
        return

    combined["Periode"] = (
        combined["_year"].astype("Int64").astype(str)
        + "-"
        + combined["_month"].astype("Int64").astype(str).str.zfill(2)
    )

    fig = px.line(
        combined,
        x="Periode",
        y="Nilai",
        color="Jenis",
        markers=True,
        color_discrete_map={
            "Inflasi Umum": "#15803D",
            "Inflasi Energi": "#86EFAC",
        },
        labels={
            "Nilai": "Inflasi (%)",
            "Periode": "Periode",
        },
        title="Tren Inflasi Bulanan",
    )
    fig.update_traces(line=dict(width=3))
    st.plotly_chart(
        green_layout(fig, 390),
        use_container_width=True,
    )

    spikes = combined.nlargest(5, "Nilai")[
        ["Periode", "Jenis", "Nilai"]
    ]
    st.markdown("**Lima nilai inflasi tertinggi**")
    st.dataframe(
        rename_for_display(spikes),
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# VISUALISASI 5: FAKTOR EKONOMI DAN SOSIAL
# =========================================================
def render_economic_social():
    st.subheader("5. Faktor Ekonomi dan Sosial")

    if f11.empty:
        st.info("Data integrasi tidak tersedia.")
        return

    data = f11.copy()
    indicator_labels = {
        "nilai_tpt": "Tingkat Pengangguran Terbuka",
        "nilai_tpak": "Tingkat Partisipasi Angkatan Kerja",
        "nilai_ump": "Upah Minimum Provinsi",
        "jumlah_penduduk_ribu": "Jumlah Penduduk (Ribu)",
        "laju_pertumbuhan": "Laju Pertumbuhan Penduduk",
        "kepadatan_penduduk": "Kepadatan Penduduk",
    }

    available = [
        col for col in indicator_labels
        if col in data.columns
    ]
    if not available:
        st.warning("Kolom faktor ekonomi dan sosial tidak ditemukan.")
        return

    selected_indicator = st.selectbox(
        "Pilih indikator",
        available,
        format_func=lambda col: indicator_labels[col],
        key="economic_indicator",
    )

    province = find_column(
        data, ["nama_provinsi", "provinsi"]
    )
    if not province:
        st.warning("Kolom provinsi tidak ditemukan.")
        return

    data[selected_indicator] = pd.to_numeric(
        data[selected_indicator], errors="coerce"
    )
    grouped = (
        data.groupby(province, as_index=False)[selected_indicator]
        .mean()
        .dropna()
        .sort_values(selected_indicator, ascending=False)
        .head(15)
    )

    if grouped.empty:
        st.info("Tidak ada data indikator yang valid.")
        return

    fig = px.bar(
        grouped.sort_values(selected_indicator),
        x=selected_indicator,
        y=province,
        orientation="h",
        color=selected_indicator,
        color_continuous_scale=[
            "#DCFCE7", "#4ADE80", "#22A447", "#14532D"
        ],
        text=selected_indicator,
        labels={
            selected_indicator: indicator_labels[selected_indicator],
            province: "Provinsi",
        },
        title=f"{indicator_labels[selected_indicator]} per Provinsi",
    )
    fig.update_traces(
        texttemplate="%{x:,.2f}",
        textposition="outside",
        cliponaxis=False,
    )
    st.plotly_chart(
        green_layout(fig, 430),
        use_container_width=True,
    )


# =========================================================
# VISUALISASI 6: HARGA SEBELUM/SAAT/SESUDAH BENCANA
# =========================================================
def render_food_before_after_disaster():
    st.subheader("6. Harga Pangan Sebelum dan Sesudah Bencana")

    if f02.empty or f05.empty:
        st.info("Data harga pangan atau data bencana tidak tersedia.")
        return

    price_col = find_column(f02, ["harga"])
    commodity_col = find_column(
        f02, ["nama_komoditas", "komoditas"]
    )
    province_price = find_column(
        f02, ["provinsi", "nama_provinsi"]
    )
    province_disaster = find_column(
        f05, ["nama_provinsi", "provinsi"]
    )
    disaster_col = find_column(f05, ["jumlah_kejadian"])

    if not all([
        price_col, commodity_col,
        province_price, province_disaster, disaster_col,
    ]):
        st.warning(
            "Kolom yang dibutuhkan untuk analisis ini belum lengkap."
        )
        return

    prices = f02.copy()
    disasters = f05.copy()

    prices[price_col] = pd.to_numeric(
        prices[price_col], errors="coerce"
    )
    disasters[disaster_col] = pd.to_numeric(
        disasters[disaster_col], errors="coerce"
    )

    prices["_month_index"] = (
        pd.to_numeric(prices["_year"], errors="coerce") * 12
        + pd.to_numeric(prices["_month"], errors="coerce")
    )
    disasters["_month_index"] = (
        pd.to_numeric(disasters["_year"], errors="coerce") * 12
        + pd.to_numeric(disasters["_month"], errors="coerce")
    )

    prices["_province_key"] = (
        prices[province_price].astype(str).str.strip().str.upper()
    )
    disasters["_province_key"] = (
        disasters[province_disaster].astype(str).str.strip().str.upper()
    )

    commodities = sorted(
        prices[commodity_col].dropna().astype(str).unique().tolist()
    )
    if not commodities:
        st.info("Tidak ada komoditas yang tersedia.")
        return

    default_index = 0
    if selected_commodity_sidebar != "Semua":
        if selected_commodity_sidebar in commodities:
            default_index = commodities.index(selected_commodity_sidebar)

    selected_food = st.selectbox(
        "Komoditas untuk analisis bencana",
        commodities,
        index=default_index,
        key="food_disaster",
    )

    prices = prices[
        prices[commodity_col].astype(str) == selected_food
    ]
    prices = (
        prices.groupby(
            ["_province_key", "_month_index"],
            as_index=False,
        )[price_col]
        .mean()
    )

    events = disasters[
        disasters[disaster_col].fillna(0) > 0
    ][["_province_key", "_month_index"]].drop_duplicates()

    events = events.dropna(subset=["_month_index"])
    if events.empty:
        st.info("Tidak ditemukan kejadian bencana pada filter ini.")
        return

    event_frames = []
    for offset, label in [
        (-1, "Sebelum"),
        (0, "Saat Bencana"),
        (1, "Sesudah"),
    ]:
        temp = events.copy()
        temp["_target_index"] = temp["_month_index"] + offset
        temp["Periode Bencana"] = label
        event_frames.append(temp)

    event_periods = pd.concat(event_frames, ignore_index=True)

    merged = event_periods.merge(
        prices,
        left_on=["_province_key", "_target_index"],
        right_on=["_province_key", "_month_index"],
        how="left",
    )

    summary = (
        merged.groupby("Periode Bencana", as_index=False)[price_col]
        .mean()
    )

    order = ["Sebelum", "Saat Bencana", "Sesudah"]
    summary["Periode Bencana"] = pd.Categorical(
        summary["Periode Bencana"],
        categories=order,
        ordered=True,
    )
    summary = summary.sort_values("Periode Bencana")

    fig = px.bar(
        summary,
        x="Periode Bencana",
        y=price_col,
        color="Periode Bencana",
        color_discrete_map={
            "Sebelum": "#86EFAC",
            "Saat Bencana": "#22A447",
            "Sesudah": "#14532D",
        },
        text=price_col,
        labels={
            price_col: "Rata-rata Harga (Rp)",
            "Periode Bencana": "Periode",
        },
        title=f"Harga {selected_food}: Sebelum, Saat, dan Sesudah Bencana",
    )
    fig.update_traces(
        texttemplate="Rp %{y:,.0f}",
        textposition="outside",
        cliponaxis=False,
    )
    st.plotly_chart(
        green_layout(fig, 390),
        use_container_width=True,
    )
    st.caption(
        "Analisis ini bersifat deskriptif berdasarkan data bulanan. "
        "Perubahan harga tidak otomatis membuktikan bahwa bencana "
        "menjadi penyebab perubahan harga."
    )


# =========================================================
# LAYOUT DUA KOLOM: 6 VISUALISASI
# =========================================================
left, right = st.columns(2, gap="large")
with left:
    render_disaster_ranking_chart()
with right:
    render_disaster_type_chart()

st.divider()

left, right = st.columns(2, gap="large")
with left:
    render_inflation_food_chart()
with right:
    render_inflation_spikes()

st.divider()

left, right = st.columns(2, gap="large")
with left:
    render_economic_social()
with right:
    render_food_before_after_disaster()



# =========================================================
# VISUALISASI 7: PETA BENCANA BERDASARKAN KATEGORI
# Visualisasi ini terpisah dari grafik peringkat provinsi di atas.
# =========================================================
def discover_disaster_detail():
    """
    Cari tabel detail bencana di DuckDB yang mempunyai kategori bencana.
    Mendukung koordinat latitude/longitude atau nama provinsi.
    """
    try:
        tables = clean_names(query_df("SHOW ALL TABLES"))
    except Exception:
        return pd.DataFrame(), None

    table_col = find_column(tables, ["name", "table_name"])
    db_col = find_column(tables, ["database", "database_name", "catalog"])
    schema_col = find_column(tables, ["schema", "schema_name"])

    if not table_col:
        return pd.DataFrame(), None

    candidates = []
    for _, row in tables.iterrows():
        table_name = str(row.get(table_col, ""))
        db_name = str(row.get(db_col, "")) if db_col else ""
        combined_name = f"{db_name} {table_name}".lower()
        if "bencana" in combined_name or "disaster" in combined_name:
            candidates.append(row)

    category_names = [
        "jenis_bencana", "nama_bencana", "tipe_bencana",
        "jenis", "disaster_type", "event_type", "kategori_bencana",
    ]

    for row in candidates:
        table_name = str(row.get(table_col, ""))
        db_name = str(row.get(db_col, "")) if db_col else ""
        schema_name = str(row.get(schema_col, "main")) if schema_col else "main"

        parts = [
            part for part in [db_name, schema_name, table_name]
            if part and part.lower() != "nan"
        ]
        qualified = ".".join(
            '"' + part.replace('"', '""') + '"' for part in parts
        )

        try:
            data = clean_names(
                query_df(f"SELECT * FROM {qualified} LIMIT 100000")
            )
        except Exception:
            continue

        category_col = find_column(data, category_names)
        if not category_col:
            continue

        lat_col = find_column(
            data, ["latitude", "lat", "lintang", "y_coord", "y"]
        )
        lon_col = find_column(
            data, ["longitude", "lon", "lng", "bujur", "x_coord", "x"]
        )
        province_col = find_column(
            data, ["nama_provinsi", "provinsi", "province"]
        )

        if (lat_col and lon_col) or province_col:
            return data, {
                "category": category_col,
                "latitude": lat_col,
                "longitude": lon_col,
                "province": province_col,
                "table": table_name,
            }

    return pd.DataFrame(), None


def render_category_disaster_map():
    """
    Visualisasi 7: peta jumlah kejadian bencana berdasarkan kategori.
    Sumber kategori dan jumlah kejadian berasal dari hasil query f05
    (05_inflasi_bencana.sql), bukan dari pencarian tabel otomatis.
    """
    st.subheader("7. Peta Sebaran Bencana Indonesia")
    st.write(
        "Pilih kategori bencana untuk melihat jumlah kejadian "
        "di setiap provinsi."
    )

    if f05.empty:
        st.warning(
            "Data bencana kosong. Periksa query 05_inflasi_bencana.sql."
        )
        return

    province_col = find_column(
        f05, ["nama_provinsi", "provinsi"]
    )
    category_col = find_column(
        f05,
        [
            "jenis_bencana", "nama_bencana", "tipe_bencana",
            "kategori_bencana", "jenis",
        ],
    )
    count_col = find_column(f05, ["jumlah_kejadian"])

    missing = []
    if not province_col:
        missing.append("provinsi")
    if not category_col:
        missing.append("jenis_bencana")
    if not count_col:
        missing.append("jumlah_kejadian")

    if missing:
        st.error(
            "Kolom berikut belum tersedia pada hasil query 05: "
            + ", ".join(missing)
            + ". Pastikan query 05_inflasi_bencana.sql mengeluarkan "
              "kolom provinsi, jenis_bencana, dan jumlah_kejadian."
        )
        return

    data = f05.copy()
    data[count_col] = pd.to_numeric(
        data[count_col], errors="coerce"
    ).fillna(0)

    # Gunakan filter tahun dan provinsi yang sudah ada di sidebar.
    if selected_year != "Semua" and "_year" in data.columns:
        data = data[
            pd.to_numeric(data["_year"], errors="coerce")
            == int(selected_year)
        ]

    if selected_province != "Semua":
        data = data[
            data[province_col].astype(str).str.strip().str.upper()
            == selected_province.strip().upper()
        ]

    categories = sorted(
        data[category_col].dropna().astype(str).unique().tolist()
    )
    if not categories:
        st.info("Tidak ada kategori bencana pada filter yang dipilih.")
        return

    selected_category = st.selectbox(
        "Kategori Bencana",
        ["Semua Kategori"] + categories,
        key="category_disaster_map",
    )

    if selected_category != "Semua Kategori":
        data = data[
            data[category_col].astype(str) == selected_category
        ]

    # Jumlahkan kejadian per provinsi setelah kategori/tahun difilter.
    summary = (
        data.groupby(province_col, as_index=False)[count_col]
        .sum(min_count=1)
        .rename(columns={count_col: "Jumlah Kejadian"})
    )
    summary["_province_key"] = (
        summary[province_col].astype(str).str.strip().str.upper()
    )
    summary["Latitude"] = summary["_province_key"].map(
        lambda name: PROVINCE_COORDS.get(name, (None, None))[0]
    )
    summary["Longitude"] = summary["_province_key"].map(
        lambda name: PROVINCE_COORDS.get(name, (None, None))[1]
    )
    summary = summary.dropna(
        subset=["Latitude", "Longitude", "Jumlah Kejadian"]
    )

    if summary.empty:
        st.warning(
            "Data kategori tersedia, tetapi nama provinsi tidak cocok "
            "dengan daftar koordinat peta."
        )
        return

    fig = px.scatter_geo(
        summary,
        lat="Latitude",
        lon="Longitude",
        size="Jumlah Kejadian",
        color="Jumlah Kejadian",
        hover_name=province_col,
        hover_data={"Jumlah Kejadian": ":,.0f"},
        color_continuous_scale=[
            "#DCFCE7", "#86EFAC", "#22A447", "#14532D"
        ],
        size_max=34,
        projection="natural earth",
        title=(
            "Jumlah Kejadian per Provinsi — "
            + selected_category
        ),
        labels={"Jumlah Kejadian": "Jumlah Kejadian"},
    )

    fig.update_geos(
        scope="asia",
        center={"lat": -2.5, "lon": 118},
        lataxis_range=[-12, 8],
        lonaxis_range=[94, 142],
        showcountries=True,
        countrycolor="#9BBDA3",
        showland=True,
        landcolor="#E8F5E9",
        showocean=True,
        oceancolor="#F2FAF4",
        showcoastlines=True,
        coastlinecolor="#A5C9AC",
        bgcolor="#FFFFFF",
    )

    st.plotly_chart(
        green_layout(fig, 520),
        use_container_width=True,
    )
    st.caption(
        "Peta menampilkan jumlah kejadian untuk kategori yang dipilih. "
        "Titik mewakili pusat perkiraan provinsi, bukan lokasi kejadian "
        "bencana yang presisi."
    )


# Visualisasi ketujuh: peta kategori bencana, terpisah dari grafik peringkat provinsi.
st.divider()
render_category_disaster_map()


# =========================================================
# PETA INFLASI UMUM PER PROVINSI DAN BULAN
# =========================================================

def render_inflation_map():
    st.subheader("Peta Inflasi Umum per Provinsi")
    st.write(
        "Pilih tahun dan bulan untuk melihat distribusi "
        "inflasi umum di seluruh provinsi Indonesia."
    )

    if q01.empty:
        st.info("Data inflasi tidak tersedia.")
        return

    data = q01.copy()

    # Identifikasi kolom
    province_col = find_column(
        data, ["nama_provinsi", "provinsi"]
    )
    inflation_col = find_column(
        data, ["inflasi_umum"]
    )

    if not province_col or not inflation_col:
        st.warning(
            "Kolom provinsi atau inflasi_umum tidak ditemukan "
            "pada query 01_inflasi_bulanan.sql."
        )
        return

    # Terapkan filter tahun dari sidebar
    if selected_year != "Semua":
        data = data[
            pd.to_numeric(data["_year"], errors="coerce")
            == int(selected_year)
        ]

    if data.empty:
        st.info("Tidak ada data inflasi untuk tahun ini.")
        return

    # Filter bulan
    month_options = sorted(
        data["_month"].dropna().astype(int).unique().tolist()
    )

    month_labels = {
        month: MONTH_LABELS[month]
        for month in month_options
        if month in MONTH_LABELS
    }

    selected_month = st.selectbox(
        "Pilih Bulan Inflasi",
        options=list(month_labels.keys()),
        format_func=lambda month: month_labels[month],
        key="inflation_map_month",
    )

    # Filter data sesuai bulan terpilih
    data = data[
        pd.to_numeric(data["_month"], errors="coerce")
        == selected_month
    ].copy()

    data[inflation_col] = pd.to_numeric(
        data[inflation_col], errors="coerce"
    )

    # Normalisasi nama provinsi
    data["_province_key"] = (
        data[province_col]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Gabungkan jika terdapat lebih dari satu baris
    # untuk provinsi dan bulan yang sama
    summary = (
        data.groupby("_province_key", as_index=False)
        [inflation_col]
        .mean()
    )

    # Koordinat pusat provinsi dari PROVINCE_COORDS
    summary["Latitude"] = summary["_province_key"].map(
        lambda name: PROVINCE_COORDS.get(
            name, (None, None)
        )[0]
    )

    summary["Longitude"] = summary["_province_key"].map(
        lambda name: PROVINCE_COORDS.get(
            name, (None, None)
        )[1]
    )

    summary = summary.dropna(
        subset=[
            inflation_col,
            "Latitude",
            "Longitude",
        ]
    )

    if summary.empty:
        st.warning(
            "Tidak ada data koordinat yang cocok dengan "
            "nama provinsi pada data inflasi."
        )
        return

    # Peta Indonesia dengan warna sesuai nilai inflasi
    fig = px.scatter_geo(
        summary,
        lat="Latitude",
        lon="Longitude",
        color=inflation_col,
        hover_name="_province_key",
        hover_data={
            inflation_col: ":.2f",
            "Latitude": False,
            "Longitude": False,
        },
        color_continuous_scale=[
            "#DCFCE7",
            "#86EFAC",
            "#22A447",
            "#14532D",
        ],
        size_max=22,
        projection="natural earth",
        title=f"Inflasi Umum per Provinsi - {month_labels[selected_month]}",
        labels={
            inflation_col: "Inflasi Umum (%)",
            "_province_key": "Provinsi",
        },
    )

    fig.update_traces(
        marker=dict(size=14, line=dict(width=0.8, color="white"))
    )

    fig.update_geos(
        scope="asia",
        center={"lat": -2.5, "lon": 118},
        lataxis_range=[-12, 8],
        lonaxis_range=[94, 142],
        showcountries=True,
        countrycolor="#9BBDA3",
        showland=True,
        landcolor="#E8F5E9",
        showocean=True,
        oceancolor="#F2FAF4",
        showcoastlines=True,
        coastlinecolor="#A5C9AC",
        bgcolor="#FFFFFF",
    )

    fig.update_layout(
        height=550,
        coloraxis_colorbar=dict(
            title="Inflasi (%)"
        ),
    )

    st.plotly_chart(
        green_layout(fig, 550),
        use_container_width=True,
    )

    st.caption(
        "Warna menunjukkan nilai inflasi umum. "
        "Titik mewakili perkiraan pusat provinsi, "
        "bukan batas wilayah administratif."
    )


# =========================================================
# VISUALISASI: PETA INFLASI UMUM PER PROVINSI DAN BULAN
# =========================================================

def render_inflation_map():
    st.subheader("8. Peta Inflasi Umum per Provinsi")

    st.caption(
        "Distribusi inflasi umum berdasarkan provinsi dan "
        "bulan yang dipilih."
    )

    # 1. Validasi data
    if q01.empty:
        st.info("Data inflasi tidak tersedia.")
        return

    data = q01.copy()

    province_col = find_column(
        data, ["nama_provinsi", "provinsi"]
    )
    inflation_col = find_column(
        data, ["inflasi_umum"]
    )

    required_cols = ["_year", "_month"]

    if not province_col or not inflation_col:
        st.warning(
            "Kolom provinsi atau inflasi_umum tidak ditemukan "
            "pada data q01."
        )
        return

    missing_cols = [
        col for col in required_cols if col not in data.columns
    ]

    if missing_cols:
        st.warning(
            f"Kolom periode tidak ditemukan: {missing_cols}. "
            "Pastikan data sudah diproses oleh prepare_month()."
        )
        return

    # 2. Normalisasi tipe data
    data["_year"] = pd.to_numeric(
        data["_year"], errors="coerce"
    )
    data["_month"] = pd.to_numeric(
        data["_month"], errors="coerce"
    )
    data[inflation_col] = pd.to_numeric(
        data[inflation_col], errors="coerce"
    )

    data = data.dropna(
        subset=[
            province_col,
            "_year",
            "_month",
            inflation_col,
        ]
    )

    if data.empty:
        st.info("Tidak ada data inflasi yang valid.")
        return

    # 3. Filter tahun
    years = sorted(data["_year"].astype(int).unique())

    year_options = ["Semua"] + years

    map_year = st.selectbox(
        "Pilih Tahun",
        options=year_options,
        index=(
            year_options.index(selected_year)
            if selected_year in year_options
            else 0
        ),
        key="inflation_map_year",
    )

    if map_year != "Semua":
        data = data[data["_year"] == int(map_year)]

    # 4. Filter bulan
    month_options = sorted(
        data["_month"].astype(int).unique().tolist()
    )

    month_labels = {
        month: MONTH_LABELS.get(month, f"Bulan {month}")
        for month in month_options
        if 1 <= month <= 12
    }

    if not month_labels:
        st.info("Tidak ada data bulan yang tersedia.")
        return

    selected_month = st.selectbox(
        "Pilih Bulan",
        options=list(month_labels.keys()),
        format_func=lambda month: month_labels[month],
        key="inflation_map_month",
    )

    data = data[
        data["_month"] == selected_month
    ].copy()

    # 5. Standarisasi nama provinsi
    data["_province_key"] = (
        data[province_col]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # 6. Agregasi inflasi per provinsi
    summary = (
        data.groupby("_province_key", as_index=False)
        .agg(
            inflasi=(inflation_col, "mean")
        )
    )

    # 7. Ambil koordinat dari PROVINCE_COORDS
    # Format: {"NAMA PROVINSI": (latitude, longitude)}
    if "PROVINCE_COORDS" not in globals():
        st.error(
            "PROVINCE_COORDS belum didefinisikan. "
            "Gunakan kamus koordinat provinsi yang sudah "
            "ada pada kode visualisasi bencana."
        )
        return

    summary["Latitude"] = summary["_province_key"].map(
        lambda name: PROVINCE_COORDS.get(
            name, (None, None)
        )[0]
    )

    summary["Longitude"] = summary["_province_key"].map(
        lambda name: PROVINCE_COORDS.get(
            name, (None, None)
        )[1]
    )

    summary = summary.dropna(
        subset=["Latitude", "Longitude", "inflasi"]
    )

    if summary.empty:
        st.warning(
            "Tidak ada provinsi yang cocok dengan koordinat. "
            "Periksa penulisan nama provinsi."
        )
        return

    # 8. Buat peta titik inflasi
    fig = px.scatter_geo(
        summary,
        lat="Latitude",
        lon="Longitude",
        color="inflasi",
        hover_name="_province_key",
        hover_data={
            "inflasi": ":.2f",
            "Latitude": False,
            "Longitude": False,
        },
        color_continuous_scale=[
            "#DCFCE7",
            "#86EFAC",
            "#22A447",
            "#14532D",
        ],
        projection="natural earth",
        title=(
            f"Inflasi Umum per Provinsi - "
            f"{month_labels[selected_month]} "
            f"{map_year if map_year != 'Semua' else ''}"
        ),
        labels={
            "inflasi": "Inflasi Umum (%)",
            "_province_key": "Provinsi",
        },
    )

    fig.update_traces(
        marker=dict(
            size=13,
            opacity=0.9,
            line=dict(width=0.8, color="white"),
        )
    )

    fig.update_geos(
        scope="asia",
        center=dict(lat=-2.5, lon=118),
        lataxis_range=[-12, 8],
        lonaxis_range=[94, 142],
        showcountries=True,
        countrycolor="#9BBDA3",
        showland=True,
        landcolor="#E8F5E9",
        showocean=True,
        oceancolor="#F2FAF4",
        showcoastlines=True,
        coastlinecolor="#A5C9AC",
        bgcolor="white",
    )

    fig.update_layout(
        height=550,
        coloraxis_colorbar=dict(
            title="Inflasi (%)"
        ),
    )

    st.plotly_chart(
        green_layout(fig, 550),
        use_container_width=True,
    )

    st.caption(
        f"Menampilkan {len(summary)} provinsi yang memiliki "
        f"data dan koordinat valid. Titik menunjukkan "
        f"perkiraan pusat provinsi, bukan batas wilayah."
    )


# Tampilkan peta
st.divider()
render_inflation_map()

# =========================================================
# TABEL DATA TERINTEGRASI + DOWNLOAD CSV
# =========================================================
st.divider()
st.subheader("Data Terintegrasi Warehouse")

if not f11.empty:
    display_data = rename_for_display(f11)
    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True,
    )

    csv_data = display_data.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="Unduh Data CSV",
        data=csv_data,
        file_name="data_terintegrasi.csv",
        mime="text/csv",
    )
else:
    st.info(
        "Data terintegrasi kosong. Periksa query "
        "11_integrasi_semua_faktor.sql."
    )
