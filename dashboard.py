import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Dashboard Analisis Bike Sharing", layout="wide")
st.title("📊 Dashboard Analisis Penyewaan Sepeda")
st.markdown("Visualisasi dari data penyewaan sepeda tahun 2011-2012")

# --- Load Data dari File Lokal ---
@st.cache_data
def load_data():
    day_url = "https://drive.google.com/uc?id=1xnbSgz7CPQlMTZferCj1zaFuIdEBBhcw"
    hour_url = "https://drive.google.com/uc?id=1cvzL-tEa33v_PNuBR84AM1fqoiMG2pxM"
    
    df_day = pd.read_csv(day_path)
    df_hour = pd.read_csv(hour_path)
    
    # Konversi tipe data
    df_day['dteday'] = pd.to_datetime(df_day['dteday'])
    df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])
    
    categorical_cols_day = ['season', 'yr', 'mnth', 'holiday', 'weekday', 'workingday', 'weathersit']
    for col in categorical_cols_day:
        if col in df_day.columns:
            df_day[col] = df_day[col].astype('category')
    
    categorical_cols_hour = ['season', 'yr', 'mnth', 'hr', 'holiday', 'weekday', 'workingday', 'weathersit']
    for col in categorical_cols_hour:
        if col in df_hour.columns:
            df_hour[col] = df_hour[col].astype('category')
            
    return df_day, df_hour

# Load data dengan pesan loading
with st.spinner("Memuat data..."):
    df_day, df_hour = load_data()
st.success("Data berhasil dimuat!")

# --- Sidebar untuk Filter ---
st.sidebar.header("Filter Data")

# Konversi nilai yr ke label yang lebih mudah dipahami
year_labels = {0: '2011', 1: '2012'}
selected_years = st.sidebar.multiselect(
    "Pilih Tahun:",
    options=sorted(df_day['yr'].unique()),
    format_func=lambda x: year_labels.get(x, str(x)),
    default=sorted(df_day['yr'].unique())
)

# Label untuk kondisi cuaca
weather_labels = {
    1: 'Cerah/Sedikit Berawan',
    2: 'Berkabut/Berawan',
    3: 'Salju Ringan/Hujan Ringan',
    4: 'Hujan Lebat/Badai'
}
selected_weather = st.sidebar.multiselect(
    "Pilih Kondisi Cuaca:",
    options=sorted(df_day['weathersit'].unique()),
    format_func=lambda x: weather_labels.get(x, str(x)),
    default=sorted(df_day['weathersit'].unique())
)

# Filter data berdasarkan pilihan
filtered_df_day = df_day[
    (df_day['yr'].isin(selected_years)) & 
    (df_day['weathersit'].isin(selected_weather))
]

filtered_df_hour = df_hour[
    (df_hour['yr'].isin(selected_years)) & 
    (df_hour['weathersit'].isin(selected_weather))
]

# --- Dashboard Layout ---
st.markdown("---")

# Baris 1: Tren Penyewaan (Daily)
st.subheader("1. Tren Penyewaan Sepeda per Hari (2011-2012)")
col1, col2 = st.columns([3, 1])
with col1:
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(x='dteday', y='cnt', data=filtered_df_day, ax=ax, color='teal')
    ax.set_title('Total Penyewaan Sepeda Harian')
    ax.set_xlabel('Tanggal')
    ax.set_ylabel('Total Penyewaan (cnt)')
    ax.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig)
with col2:
    st.metric("Rata-rata Harian", f"{filtered_df_day['cnt'].mean():.0f}")
    st.metric("Total Keseluruhan", f"{filtered_df_day['cnt'].sum():,}")

st.markdown("---")

# Baris 2: Pengaruh Cuaca & Suhu
st.subheader("2. Analisis Pengaruh Cuaca dan Suhu")

col1, col2 = st.columns(2)
with col1:
    avg_rentals_weather = filtered_df_day.groupby('weathersit')['cnt'].mean().reset_index()
    avg_rentals_weather = avg_rentals_weather.sort_values('weathersit')
    
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x='weathersit', y='cnt', data=avg_rentals_weather, palette='Blues_d', ax=ax)
    ax.set_title('Rata-rata Penyewaan Berdasarkan Kondisi Cuaca')
    ax.set_xlabel('Kondisi Cuaca')
    ax.set_ylabel('Rata-rata Penyewaan')
    
    ax.set_xticks(range(len(weather_labels)))
    ax.set_xticklabels([weather_labels[i] for i in sorted(weather_labels.keys())], rotation=15, ha='right')
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.regplot(x='temp', y='cnt', data=filtered_df_day, scatter_kws={'alpha':0.3}, line_kws={'color':'red'}, ax=ax)
    ax.set_title('Hubungan Suhu vs Total Penyewaan')
    ax.set_xlabel('Suhu (Normalisasi)')
    ax.set_ylabel('Total Penyewaan')
    ax.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig)

st.markdown("---")

# Baris 3: Analisis Hari Kerja vs Libur & Pola Jam
st.subheader("3. Analisis Operasional (Hari Kerja vs Libur & Pola Waktu)")

col1, col2 = st.columns(2)
with col1:
    avg_rentals_workday = filtered_df_day.groupby('workingday')['cnt'].mean().reset_index()
    avg_rentals_workday['day_type'] = avg_rentals_workday['workingday'].map({0: 'Libur/Akhir Pekan', 1: 'Hari Kerja'})
    
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.barplot(x='day_type', y='cnt', data=avg_rentals_workday, palette='viridis', ax=ax)
    ax.set_title('Perbandingan Rata-rata Penyewaan')
    ax.set_xlabel('Tipe Hari')
    ax.set_ylabel('Rata-rata Penyewaan')
    st.pyplot(fig)

    st.info("Insight: Rata-rata penyewaan pada hari kerja cenderung lebih tinggi dibandingkan hari libur, menunjukkan bahwa banyak pengguna menggunakan sepeda untuk mobilitas kerja/sekolah.")

with col2:
    hourly_rentals = filtered_df_hour.groupby('hr')['cnt'].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.lineplot(x='hr', y='cnt', data=hourly_rentals, marker='o', markersize=6, color='orange', ax=ax)
    ax.set_title('Rata-rata Penyewaan per Jam dalam Sehari')
    ax.set_xlabel('Jam (0-23)')
    ax.set_ylabel('Rata-rata Penyewaan')
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # Highlight peak hours
    peak_morning = hourly_rentals.loc[hourly_rentals['cnt'].idxmax()]
    ax.axvline(x=peak_morning['hr'], color='red', linestyle='--', alpha=0.7)
    ax.text(peak_morning['hr'] + 0.5, peak_morning['cnt'] + 50, f'Peak: {int(peak_morning["hr"])}:00', color='red')
    
    # Highlight another potential peak (evening rush)
    evening_peak = hourly_rentals.iloc[17:20].loc[hourly_rentals.iloc[17:20]['cnt'].idxmax()]
    ax.axvline(x=evening_peak['hr'], color='red', linestyle='--', alpha=0.7)
    ax.text(evening_peak['hr'] + 0.5, evening_peak['cnt'] + 50, f'Peak: {int(evening_peak["hr"])}:00', color='red')
    
    st.pyplot(fig)

    st.success("Rekomendasi Operasional: Fokus distribusi sepeda pada jam sibuk (pagi dan sore hari) untuk mengantisipasi lonjakan permintaan.")

st.markdown("---")


# Baris 5: Informasi Tambahan
with st.expander("Informasi Dataset"):
    st.markdown(f"""
    - **Periode Data:** {df_day['dteday'].min().date()} hingga {df_day['dteday'].max().date()}
    - **Jumlah Data Harian:** {len(df_day)} hari
    - **Jumlah Data Per Jam:** {len(df_hour)} record
    - **Kolom Utama:** 
        - `cnt`: Total penyewaan
        - `temp`: Suhu (normalisasi)
        - `weathersit`: Kondisi cuaca (1: Cerah, 2: Berkabut, 3: Hujan Ringan, 4: Hujan Lebat)
        - `workingday`: Status hari kerja (0: Libur, 1: Hari Kerja)
        - `hr`: Jam (0-23)
    """)

st.markdown("---")
st.caption(f"Dashboard ini menggunakan data dari tahun {', '.join([year_labels.get(y, str(y)) for y in selected_years])} dengan kondisi cuaca: {', '.join([weather_labels.get(w, str(w)) for w in selected_weather])}")
