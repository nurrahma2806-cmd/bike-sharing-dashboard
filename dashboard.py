# dashboard_simple.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

# Set style for plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

# Load data with caching
@st.cache_data
def load_data():
    day_url = "https://drive.google.com/uc?id=1xnbSgz7CPQlMTZferCj1zaFuIdEBBhcw"
    hour_url = "https://drive.google.com/uc?id=1cvzL-tEa33v_PNuBR84AM1fqoiMG2pxM"
    
    df = pd.read_csv(day_url)
    df_hour = pd.read_csv(hour_url)
    
    # Data cleaning
    df['dteday'] = pd.to_datetime(df['dteday'])
    df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])
    
    # Convert to categorical
    cat_cols = ['season', 'yr', 'mnth', 'holiday', 'weekday', 'workingday', 'weathersit']
    for col in cat_cols:
        df[col] = df[col].astype('category')
    
    cat_cols_hour = ['season', 'yr', 'mnth', 'hr', 'holiday', 'weekday', 'workingday', 'weathersit']
    for col in cat_cols_hour:
        df_hour[col] = df_hour[col].astype('category')
    
    # Add temperature groups
    df['temp_group'] = pd.cut(df['temp'], bins=5, 
                               labels=['Sangat Dingin', 'Dingin', 'Sedang', 'Hangat', 'Panas'])
    
    return df, df_hour

# Load data
df, df_hour = load_data()

# Sidebar
st.sidebar.image("https://img.icons8.com/color/96/000000/bicycle.png", width=80)
st.sidebar.title("🚲 Bike Sharing Dashboard")
st.sidebar.markdown("---")

# Filter options
st.sidebar.subheader("📅 Filter Data")

years = df['yr'].unique()
year_labels = {0: '2011', 1: '2012'}
selected_years = st.sidebar.multiselect(
    "Tahun",
    options=years,
    format_func=lambda x: year_labels[x],
    default=years
)

seasons = df['season'].unique()
season_labels = {1: 'Semi', 2: 'Panas', 3: 'Gugur', 4: 'Dingin'}
selected_seasons = st.sidebar.multiselect(
    "Musim",
    options=seasons,
    format_func=lambda x: season_labels[x],
    default=seasons
)

# Filter data
mask = df['yr'].isin(selected_years) & df['season'].isin(selected_seasons)
df_filtered = df[mask]
mask_hour = df_hour['yr'].isin(selected_years) & df_hour['season'].isin(selected_seasons)
df_hour_filtered = df_hour[mask_hour]

# Header
st.title("🚲 Analisis Penyewaan Sepeda")
st.markdown("### Dashboard Interaktif - Bike Sharing Dataset (2011-2012)")
st.markdown("---")

# Key Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Penyewaan", f"{df_filtered['cnt'].sum():,}")
with col2:
    st.metric("Rata-rata per Hari", f"{df_filtered['cnt'].mean():,.0f}")
with col3:
    st.metric("Penyewaan Tertinggi", f"{df_filtered['cnt'].max():,}")
with col4:
    st.metric("Total Hari Data", f"{len(df_filtered)}")

st.markdown("---")

# ==================== PERTANYAAN 1 ====================
st.header("📌 Pertanyaan 1: Pengaruh Cuaca dan Suhu")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Kondisi Cuaca")
    weather_data = df_filtered.groupby('weathersit')['cnt'].mean().reset_index()
    weather_labels = {1: 'Cerah/Berawan', 2: 'Berkabut', 3: 'Hujan Ringan', 4: 'Hujan Lebat'}
    weather_data['weather_label'] = weather_data['weathersit'].map(weather_labels)
    
    fig, ax = plt.subplots()
    bars = ax.bar(weather_data['weather_label'], weather_data['cnt'], 
                  color=['#2E7D32', '#66BB6A', '#A5D6A7', '#C8E6C9'])
    ax.set_xlabel('Kondisi Cuaca')
    ax.set_ylabel('Rata-rata Penyewaan')
    ax.set_title('Rata-rata Penyewaan Berdasarkan Kondisi Cuaca')
    plt.xticks(rotation=45)
    st.pyplot(fig)
    plt.close()

with col2:
    st.subheader("Kelompok Suhu")
    temp_data = df_filtered.groupby('temp_group')['cnt'].mean().reset_index()
    temp_order = ['Sangat Dingin', 'Dingin', 'Sedang', 'Hangat', 'Panas']
    
    fig, ax = plt.subplots()
    colors = ['#1B5E20', '#388E3C', '#4CAF50', '#81C784', '#A5D6A7']
    bars = ax.bar(temp_data['temp_group'], temp_data['cnt'], color=colors)
    ax.set_xlabel('Kelompok Suhu')
    ax.set_ylabel('Rata-rata Penyewaan')
    ax.set_title('Rata-rata Penyewaan Berdasarkan Kelompok Suhu')
    plt.xticks(rotation=45)
    st.pyplot(fig)
    plt.close()

st.markdown("---")

# ==================== PERTANYAAN 2 ====================
st.header("📌 Pertanyaan 2: Perbandingan Hari Kerja vs Hari Libur")

col1, col2 = st.columns([1, 1])

with col1:
    workingday_data = df_filtered.groupby('workingday')['cnt'].mean().reset_index()
    fig, ax = plt.subplots()
    colors = ['#FF9800', '#2E7D32']
    bars = ax.bar(['Hari Libur', 'Hari Kerja'], workingday_data['cnt'], color=colors)
    ax.set_ylabel('Rata-rata Penyewaan')
    ax.set_title('Rata-rata Penyewaan: Hari Kerja vs Hari Libur')
    st.pyplot(fig)
    plt.close()

with col2:
    diff_pct = ((workingday_data[workingday_data['workingday']==1]['cnt'].values[0] - 
                 workingday_data[workingday_data['workingday']==0]['cnt'].values[0]) / 
                workingday_data[workingday_data['workingday']==0]['cnt'].values[0] * 100)
    
    st.info(f"""
    ### 📈 Perbedaan Signifikan
    
    **{diff_pct:.1f}%** lebih tinggi pada **Hari Kerja**
    
    🎯 **Rekomendasi:**
    - Alokasikan lebih banyak sepeda pada hari kerja
    - Fokuskan promosi komuter pada hari kerja
    - Kembangkan paket rekreasi untuk hari libur
    """)

st.markdown("---")

# ==================== PERTANYAAN 3 ====================
st.header("📌 Pertanyaan 3: Pola Penyewaan per Jam")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Pola Penyewaan - Hari Kerja")
    hourly_working = df_hour_filtered[df_hour_filtered['workingday'] == 1].groupby('hr')['cnt'].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(hourly_working['hr'], hourly_working['cnt'], marker='o', color='#2E7D32', linewidth=2)
    ax.axvline(x=8, color='red', linestyle='--', alpha=0.7, label='Puncak Pagi')
    ax.axvline(x=17, color='red', linestyle='--', alpha=0.7, label='Puncak Sore')
    ax.set_xlabel('Jam')
    ax.set_ylabel('Rata-rata Penyewaan')
    ax.set_title('Pola Penyewaan pada Hari Kerja')
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    plt.close()

with col2:
    st.subheader("Pola Penyewaan - Hari Libur")
    hourly_holiday = df_hour_filtered[df_hour_filtered['workingday'] == 0].groupby('hr')['cnt'].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(hourly_holiday['hr'], hourly_holiday['cnt'], marker='o', color='#FF9800', linewidth=2)
    ax.axvline(x=13, color='orange', linestyle='--', alpha=0.7, label='Puncak Siang')
    ax.set_xlabel('Jam')
    ax.set_ylabel('Rata-rata Penyewaan')
    ax.set_title('Pola Penyewaan pada Hari Libur')
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    plt.close()

# Combined chart
st.subheader("Perbandingan Pola Penyewaan")
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(hourly_working['hr'], hourly_working['cnt'], marker='o', color='#2E7D32', linewidth=2, label='Hari Kerja')
ax.plot(hourly_holiday['hr'], hourly_holiday['cnt'], marker='s', color='#FF9800', linewidth=2, label='Hari Libur')
ax.set_xlabel('Jam')
ax.set_ylabel('Rata-rata Penyewaan')
ax.set_title('Perbandingan Pola Penyewaan: Hari Kerja vs Hari Libur')
ax.legend()
ax.grid(True, alpha=0.3)
st.pyplot(fig)
plt.close()

st.markdown("---")

# ==================== KESIMPULAN ====================
st.header("📝 Kesimpulan dan Rekomendasi")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### ✅ Kesimpulan
    
    **1. Pengaruh Cuaca & Suhu**
    - Cuaca cerah meningkatkan penyewaan hingga 2x lipat
    - Suhu hangat (20-30°C) adalah kondisi ideal
    
    **2. Hari Kerja vs Libur**
    - Hari kerja memiliki penyewaan lebih tinggi (+15-20%)
    - Hari kerja: pola komuter (pagi & sore)
    - Hari libur: pola rekreasi (siang hari)
    
    **3. Pola per Jam**
    - Hari kerja: Puncak 07:00-09:00 & 16:00-18:00
    - Hari libur: Puncak 10:00-16:00
    """)

with col2:
    st.markdown("""
    ### 🎯 Rekomendasi Aksi
    
    **1. Alokasi Sepeda**
    - Tingkatkan stok 40-50% saat cuaca cerah
    - Fokus area perkantoran jam puncak hari kerja
    - Fokus area wisata siang hari libur
    
    **2. Strategi Pemasaran**
    - Promosi komuter pada jam sibuk hari kerja
    - Paket rekreasi akhir pekan di area wisata
    
    **3. Operasional**
    - Lakukan perawatan saat jam sepi (01:00-05:00)
    - Implementasi sistem redistribusi real-time
    """)

st.markdown("---")
st.caption("🚲 Bike Sharing Analytics Dashboard | Data source: Bike Sharing Dataset (2011-2012)")