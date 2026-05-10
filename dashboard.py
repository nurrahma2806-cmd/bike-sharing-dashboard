# streamlit_dashboard.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ============================================
# KONFIGURASI HALAMAN
# ============================================
st.set_page_config(
    page_title="Dashboard Bike Sharing",
    page_icon="🚲",
    layout="wide"
)

# ============================================
# LOAD DATA
# ============================================
@st.cache_data
def load_data():
    day_url = "https://drive.google.com/uc?id=1xnbSgz7CPQlMTZferCj1zaFuIdEBBhcw"
    hour_url = "https://drive.google.com/uc?id=1cvzL-tEa33v_PNuBR84AM1fqoiMG2pxM"
    
    df_day = pd.read_csv(day_url)
    df_hour = pd.read_csv(hour_url)
    
    # Konversi tipe data
    df_day['dteday'] = pd.to_datetime(df_day['dteday'])
    df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])
    df_hour['hr'] = df_hour['hr'].astype(int)
    
    categorical_cols_day = ['season', 'yr', 'mnth', 'holiday', 'weekday', 'workingday', 'weathersit']
    categorical_cols_hour = ['season', 'yr', 'mnth', 'holiday', 'weekday', 'workingday', 'weathersit']
    
    for col in categorical_cols_day:
        df_day[col] = df_day[col].astype('category')
    
    for col in categorical_cols_hour:
        df_hour[col] = df_hour[col].astype('category')
    
    return df_day, df_hour

df_day, df_hour = load_data()

# ============================================
# HEADER DASHBOARD
# ============================================
st.title("🚲 Dashboard Analisis Bike Sharing")
st.markdown(f"**Periode Data:** {df_day['dteday'].min().date()} s.d. {df_day['dteday'].max().date()}")
st.markdown("---")

# ============================================
# SIDEBAR - FILTER
# ============================================
st.sidebar.header("🔍 Filter Data")

# Filter tahun
years = [2011, 2012]
selected_year = st.sidebar.selectbox("Tahun", years)

# Filter musim
season_labels = {1: "Semi", 2: "Panas", 3: "Gugur", 4: "Dingin"}
seasons = st.sidebar.multiselect(
    "Musim",
    options=list(season_labels.keys()),
    default=list(season_labels.keys()),
    format_func=lambda x: season_labels[x]
)

# Filter kondisi cuaca
weather_labels = {
    1: "Cerah/Sedikit Berawan",
    2: "Berkabut/Berawan",
    3: "Salju Ringan/Hujan Ringan",
    4: "Hujan Lebat/Badai"
}
weathers = st.sidebar.multiselect(
    "Kondisi Cuaca",
    options=list(weather_labels.keys()),
    default=list(weather_labels.keys()),
    format_func=lambda x: weather_labels[x]
)

# Filter hari kerja/libur
work_options = {0: "Hari Libur", 1: "Hari Kerja"}
work_filter = st.sidebar.multiselect(
    "Tipe Hari",
    options=list(work_options.keys()),
    default=list(work_options.keys()),
    format_func=lambda x: work_options[x]
)

# Filter data berdasarkan sidebar
filtered_day = df_day[
    (df_day['yr'] == selected_year - 2011) &
    (df_day['season'].isin(seasons)) &
    (df_day['weathersit'].isin(weathers)) &
    (df_day['workingday'].isin(work_filter))
]

filtered_hour = df_hour[
    (df_hour['yr'] == selected_year - 2011) &
    (df_hour['season'].isin(seasons)) &
    (df_hour['weathersit'].isin(weathers)) &
    (df_hour['workingday'].isin(work_filter))
]

# ============================================
# METRICS / KPI
# ============================================
st.subheader("📊 Ringkasan Metrik")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_rentals = filtered_day['cnt'].sum()
    st.metric("Total Penyewaan", f"{total_rentals:,}")

with col2:
    avg_daily = filtered_day['cnt'].mean()
    st.metric("Rata-rata per Hari", f"{avg_daily:.0f}")

with col3:
    avg_hourly = filtered_hour['cnt'].mean()
    st.metric("Rata-rata per Jam", f"{avg_hourly:.0f}")

with col4:
    peak_day = filtered_day.loc[filtered_day['cnt'].idxmax(), 'dteday'].date()
    st.metric("Hari Tersibuk", peak_day.strftime("%d %b %Y"))

st.markdown("---")

# ============================================
# PERTANYAAN 1: Pengaruh Cuaca dan Suhu
# ============================================
st.header("🌤️ Pertanyaan 1: Pengaruh Cuaca dan Suhu")

col1, col2 = st.columns(2)

with col1:
    # Bar plot kondisi cuaca
    avg_by_weather = filtered_day.groupby('weathersit', observed=False)['cnt'].mean().reset_index()
    avg_by_weather['weather_label'] = avg_by_weather['weathersit'].map(weather_labels)
    
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    bars = ax1.bar(avg_by_weather['weather_label'], avg_by_weather['cnt'], color='skyblue')
    ax1.set_xlabel('Kondisi Cuaca')
    ax1.set_ylabel('Rata-rata Penyewaan')
    ax1.set_title('Rata-rata Penyewaan Berdasarkan Kondisi Cuaca')
    plt.xticks(rotation=15)
    for bar, val in zip(bars, avg_by_weather['cnt']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100, 
                 f'{val:.0f}', ha='center', va='bottom', fontsize=9)
    st.pyplot(fig1)

with col2:
    # Scatter plot suhu vs penyewaan
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.scatter(filtered_day['temp'], filtered_day['cnt'], alpha=0.5, c='coral')
    ax2.set_xlabel('Suhu (ternormalisasi)')
    ax2.set_ylabel('Total Penyewaan')
    ax2.set_title('Hubungan Suhu dengan Jumlah Penyewaan')
    
    # Add trend line
    z = np.polyfit(filtered_day['temp'], filtered_day['cnt'], 1)
    p = np.poly1d(z)
    ax2.plot(filtered_day['temp'].sort_values(), p(filtered_day['temp'].sort_values()), 
             "r--", alpha=0.8, label=f'Tren (r={filtered_day["temp"].corr(filtered_day["cnt"]):.2f})')
    ax2.legend()
    st.pyplot(fig2)

# Interpretasi
corr_temp = filtered_day['temp'].corr(filtered_day['cnt'])
st.info(f"📈 **Korelasi suhu dengan penyewaan:** {corr_temp:.3f} (Interpretasi: Korelasi positif yang kuat - semakin tinggi suhu, semakin tinggi permintaan penyewaan)")

st.markdown("---")

# ============================================
# PERTANYAAN 2: Hari Kerja vs Hari Libur
# ============================================
st.header("📅 Pertanyaan 2: Perbandingan Hari Kerja vs Hari Libur")

col1, col2 = st.columns(2)

with col1:
    # Bar plot perbandingan
    avg_by_working = filtered_day.groupby('workingday', observed=False)['cnt'].mean().reset_index()
    avg_by_working['day_label'] = avg_by_working['workingday'].map(work_options)
    
    fig3, ax3 = plt.subplots(figsize=(6, 5))
    bars = ax3.bar(avg_by_working['day_label'], avg_by_working['cnt'], 
                   color=['lightcoral', 'lightgreen'])
    ax3.set_xlabel('Tipe Hari')
    ax3.set_ylabel('Rata-rata Penyewaan')
    ax3.set_title('Perbandingan Penyewaan: Hari Kerja vs Hari Libur')
    for bar, val in zip(bars, avg_by_working['cnt']):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100, 
                 f'{val:.0f}', ha='center', va='bottom', fontsize=11)
    st.pyplot(fig3)

with col2:
    working_val = avg_by_working[avg_by_working['workingday']==1]['cnt'].values[0] if len(avg_by_working[avg_by_working['workingday']==1]) > 0 else 0
    holiday_val = avg_by_working[avg_by_working['workingday']==0]['cnt'].values[0] if len(avg_by_working[avg_by_working['workingday']==0]) > 0 else 0
    
    if working_val > 0 and holiday_val > 0:
        diff_pct = ((working_val / holiday_val) - 1) * 100
    else:
        diff_pct = 0
    
    st.metric("Hari Kerja", f"{working_val:.0f}", delta=f"{diff_pct:.1f}% vs Hari Libur")
    
    st.markdown("### 💡 Rekomendasi Operasional")
    if working_val > holiday_val:
        st.markdown("""
        - ✅ Alokasikan lebih banyak sepeda pada **hari kerja** untuk komuter
        - ✅ Tingkatkan frekuensi penyeimbangan sepeda pada jam sibuk
        - ✅ Kembangkan promosi khusus akhir pekan
        """)
    else:
        st.markdown("""
        - ✅ Fokuskan distribusi sepeda pada **hari libur** untuk rekreasi
        - ✅ Siapkan staf tambahan di destinasi wisata
        """)

st.markdown("---")

# ============================================
# PERTANYAAN 3: Jam Puncak Penyewaan
# ============================================
st.header("⏰ Pertanyaan 3: Analisis Jam Puncak Penyewaan")

# Analisis per jam overall
hourly_avg = filtered_hour.groupby('hr', observed=False)['cnt'].mean().reset_index()
peak_hour = hourly_avg.loc[hourly_avg['cnt'].idxmax()]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Jam Puncak Keseluruhan", f"{int(peak_hour['hr'])}:00")
with col2:
    st.metric("Rata-rata di Jam Puncak", f"{peak_hour['cnt']:.0f} penyewaan")
with col3:
    st.metric("Jam Puncak Pagi", "08:00", delta="Jam sibuk pagi")

# Line plot per jam dengan perbedaan hari kerja/libur
hourly_by_work = filtered_hour.groupby(['hr', 'workingday'], observed=False)['cnt'].mean().reset_index()
hourly_by_work['day_type'] = hourly_by_work['workingday'].map(work_options)

fig4, ax4 = plt.subplots(figsize=(12, 6))
for day_type in [0, 1]:
    data = hourly_by_work[hourly_by_work['workingday'] == day_type]
    label = work_options[day_type]
    ax4.plot(data['hr'], data['cnt'], marker='o', linewidth=2, label=label)

ax4.set_xlabel('Jam')
ax4.set_ylabel('Rata-rata Penyewaan')
ax4.set_title('Pola Penyewaan Sepeda per Jam: Hari Kerja vs Hari Libur')
ax4.legend()
ax4.grid(True, alpha=0.3)
ax4.set_xticks(range(0, 24))
st.pyplot(fig4)

# Tabel jam puncak
st.subheader("📋 Ringkasan Jam Puncak")

peak_data = []
for day_type in [1, 0]:
    data = hourly_by_work[hourly_by_work['workingday'] == day_type]
    if len(data) > 0:
        peak = data.loc[data['cnt'].idxmax()]
        day_name = work_options[day_type]
        peak_data.append({
            "Tipe Hari": day_name,
            "Jam Puncak": f"{int(peak['hr'])}:00",
            "Rata-rata Penyewaan": f"{peak['cnt']:.0f}"
        })

st.dataframe(pd.DataFrame(peak_data), use_container_width=True)

st.markdown("### 💡 Rekomendasi Distribusi Sepeda")
st.markdown("""
| Waktu | Tipe Hari | Rekomendasi |
|-------|-----------|--------------|
| 07:00-09:00 | Hari Kerja | Perbanyak sepeda di stasiun dan area perkantoran |
| 17:00-19:00 | Hari Kerja | Siapkan armada untuk perjalanan pulang |
| 12:00-16:00 | Hari Libur | Fokuskan di area wisata dan pusat kota |
| 24/7 | Semua | Implementasikan sistem rebalancing dinamis |
""")

st.markdown("---")

# ============================================
# TREN BULANAN
# ============================================
st.header("📈 Tren Penyewaan per Bulan")

monthly_trend = filtered_day.groupby('mnth', observed=False)['cnt'].mean().reset_index()
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']

fig5, ax5 = plt.subplots(figsize=(12, 5))
bars = ax5.bar(month_names, monthly_trend['cnt'], color='teal')
ax5.set_xlabel('Bulan')
ax5.set_ylabel('Rata-rata Penyewaan Harian')
ax5.set_title(f'Tren Penyewaan Sepeda per Bulan (Tahun {selected_year})')
ax5.grid(axis='y', alpha=0.3)

for bar, val in zip(bars, monthly_trend['cnt']):
    ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100, 
             f'{val:.0f}', ha='center', va='bottom', fontsize=8)

st.pyplot(fig5)

# ============================================
# KESIMPULAN
# ============================================
st.header("📝 Kesimpulan dan Rekomendasi")

with st.expander("📌 Klik untuk melihat kesimpulan lengkap"):
    st.markdown("""
    ### 🎯 Kesimpulan Utama
    
    1. **Pengaruh Cuaca & Suhu**
       - Cuaca cerah meningkatkan penyewaan signifikan dibanding cuaca hujan
       - Suhu memiliki korelasi positif kuat dengan jumlah penyewaan
       - Kondisi optimal: cuaca cerah dengan suhu hangat
    
    2. **Hari Kerja vs Hari Libur**
       - Hari kerja memiliki permintaan lebih tinggi (pola komuter)
       - Perbedaan pola penggunaan antara hari kerja dan libur
    
    3. **Jam Puncak Penyewaan**
       - Puncak pagi: 07:00-09:00 (berangkat kerja/sekolah)
       - Puncak sore: 17:00-19:00 (pulang kerja/sekolah)
       - Hari libur: puncak terjadi siang hingga sore
    
    ### 🚀 Rekomendasi Operasional
    
    | Aspek | Rekomendasi |
    |-------|--------------|
    | **Distribusi Sepeda** | Tingkatkan ketersediaan 2-3x pada jam sibuk |
    | **Rebalancing** | Pindahkan sepeda dari stasiun tujuan ke stasiun asal |
    | **Marketing** | Promosi khusus akhir pekan untuk tingkatkan penggunaan |
    | **Teknologi** | Edukasi penggunaan app untuk cek ketersediaan |
    | **Cadangan** | Siapkan armada cadangan untuk antisipasi cuaca buruk |
    """)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Dashboard Bike Sharing | Data periode 2011-2012</div>",
    unsafe_allow_html=True
)
