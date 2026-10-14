
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from src.data_access import query_df
QUERY_FILE = ROOT / "queries" / "11_integrasi_semua_faktor.sql"

st.set_page_config(
    page_title="Dashboard Data Indonesia",
    page_icon="📊",
    layout="wide",
)

st.title("Dashboard Data Indonesia")
st.caption(
    "Integrasi data inflasi, harga pangan, energi, bencana, "
    "ekonomi, dan sosial."
)


@st.cache_data
def load_data():
    if not QUERY_FILE.exists():
        raise FileNotFoundError(
            f"File query tidak ditemukan: {QUERY_FILE}"
        )

    sql = QUERY_FILE.read_text(encoding="utf-8")
    return query_df(sql)


try:
    df = load_data()
except Exception as e:
    st.error(f"Gagal mengambil data: {e}")
    st.stop()

required = [
    "nama_provinsi",
    "tahun",
    "bulan",
    "inflasi_umum",
    "rata_rata_harga_pangan",
    "jumlah_kejadian",
]

missing = [col for col in required if col not in df.columns]

if missing:
    st.error(f"Kolom belum tersedia: {', '.join(missing)}")
    st.stop()

for col in [
    "tahun",
    "bulan",
    "inflasi_umum",
    "rata_rata_harga_pangan",
    "jumlah_kejadian",
]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(
    subset=["nama_provinsi", "tahun", "bulan"]
).copy()

st.sidebar.header("Filter Dashboard")

provinces = ["Semua Provinsi"] + sorted(
    df["nama_provinsi"].dropna().unique().tolist()
)
province = st.sidebar.selectbox("Provinsi", provinces)

years = sorted(df["tahun"].dropna().astype(int).unique())
year = st.sidebar.selectbox("Tahun", years, index=len(years) - 1)

month_names = {
    1: "Januari", 2: "Februari", 3: "Maret",
    4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September",
    10: "Oktober", 11: "November", 12: "Desember",
}

months = st.sidebar.multiselect(
    "Bulan",
    options=list(month_names),
    default=list(month_names),
    format_func=lambda m: month_names[m],
)

filtered = df[df["tahun"] == year].copy()

if province != "Semua Provinsi":
    filtered = filtered[filtered["nama_provinsi"] == province]

if months:
    filtered = filtered[filtered["bulan"].isin(months)]
else:
    filtered = filtered.iloc[0:0]

filtered = filtered.sort_values(["bulan", "nama_provinsi"])

if filtered.empty:
    st.warning("Tidak ada data untuk filter yang dipilih.")
    st.stop()

st.subheader("Ringkasan Indikator")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Rata-rata Inflasi",
    f"{filtered['inflasi_umum'].mean():.2f}%"
)

c2.metric(
    "Rata-rata Harga Pangan",
    f"Rp {filtered['rata_rata_harga_pangan'].mean():,.0f}"
)

c3.metric(
    "Total Kejadian Bencana",
    f"{filtered['jumlah_kejadian'].sum():,.0f}"
)

st.caption(
    "Ringkasan dihitung dari data yang sesuai dengan filter. "
    "Harga pangan merupakan rata-rata sesuai definisi pada query SQL."
)

st.divider()
st.subheader("Tren Bulanan")

monthly = (
    filtered.groupby("bulan", as_index=False)
    .agg(
        inflasi=("inflasi_umum", "mean"),
        harga_pangan=("rata_rata_harga_pangan", "mean"),
        jumlah_bencana=("jumlah_kejadian", "sum"),
    )
    .sort_values("bulan")
)

monthly["Bulan"] = monthly["bulan"].map(month_names)
monthly = monthly.set_index("Bulan")

left, right = st.columns(2)

with left:
    st.markdown("**Tren Inflasi (%)**")
    st.line_chart(monthly[["inflasi"]])

with right:
    st.markdown("**Rata-rata Harga Pangan (Rp)**")
    st.line_chart(monthly[["harga_pangan"]])

st.markdown("**Jumlah Kejadian Bencana**")
st.bar_chart(monthly[["jumlah_bencana"]])

st.divider()
st.subheader("Data Terintegrasi")
st.dataframe(filtered, use_container_width=True, hide_index=True)

st.download_button(
    "Unduh Data Hasil Filter (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8-sig"),
    file_name="data_terintegrasi.csv",
    mime="text/csv",
)
