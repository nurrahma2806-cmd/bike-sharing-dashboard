# dashboard_simple.py - VERSI RINGKAS TANPA KESIMPULAN

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set page config
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

# Load data
@st.cache_data
def load_data():
    day_url = "https://drive.google.com/uc?id=1xnbSgz7CPQlMTZferCj1zaFuIdEBBhcw"
    hour_url = "https://drive.google.com/uc?id=1cvzL-tEa33v_PNuBR84AM1fqoiMG2pxM"
    
    df = pd.read_csv(day_url)
    df_hour = pd.read_csv(hour_url)
    
    df['dteday'] = pd.to_datetime(df['dteday'])
    df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])
    
    cat_cols = ['season', 'yr', 'mnth', 'holiday', 'weekday', 'workingday', 'weathersit']
    for col in cat_cols:
        df[col] = df[col].astype('category')
    
    cat_cols_hour = ['season', 'yr', 'mnth', 'hr', 'holiday', 'weekday', 'workingday', 'weathersit']
    for col in cat_cols_hour:
        df_hour[col] = df_hour[col].astype('category')
    
    df['temp_group'] = pd.cut(df['temp'], bins=5, 
                               labels=['Sangat Dingin', 'Dingin', 'Sedang', 'Hangat', 'Panas'])
    
    return df, df_hour

df, df_hour = load_data()

# ==================== SIDEBAR FILTER ====================
st.sidebar.image("https://img.icons8.com/color/96/000000/bicycle.png", width=80)
st.sidebar.title("🚲 Bike Sharing")
st.sidebar.markdown("---")

years = df['yr'].unique()
year_labels = {0: '2011', 1: '2012'}
selected_years = st.sidebar.multiselect("Tahun", options=years, 
                                          format_func=lambda x: year_labels[x], default=years)

seasons = df['season'].unique()
season_labels = {1: 'Semi', 2: 'Panas', 3: 'Gugur', 4: 'Dingin'}
selected_seasons = st.sidebar.multiselect("Musim", options=seasons,
                                            format_func=lambda x: season_labels[x], default=seasons)

# Filter data
mask = df['yr'].isin(selected_years) & df['season'].isin(selected_seasons)
df_filtered = df[mask]
mask_hour = df_hour['yr'].isin(selected_years) & df_hour['season'].isin(selected_seasons)
df_hour_filtered = df_hour[mask_hour]

# ==================== HEADER ====================
st.title("🚲 Bike Sharing Dashboard")
st.markdown("### Analisis Penyewaan Sepeda (2011-2012)")
st.markdown("---")

# ==================== KEY METRICS ====================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💰 Total Penyewaan", f"{df_filtered['cnt'].sum():,.0f}")
with col2:
    st.metric("📈 Rata-rata per Hari", f"{df_filtered['cnt'].mean():,.0f}")
with col3:
    st.metric("🏆 Penyewaan Tertinggi", f"{df_filtered['cnt'].max():,.0f}")
with col4:
    st.metric("📅 Total Hari", f"{len(df_filtered)}")

st.markdown("---")

# ==================== PERTANYAAN 1: CUACA & SUHU ====================
st.subheader("🌤️ Pengaruh Cuaca dan Suhu terhadap Penyewaan")

col1, col2 = st.columns(2)

with col1:
    weather_data = df_filtered.groupby('weathersit')['cnt'].mean().reset_index()
    weather_labels = {1: 'Cerah', 2: 'Berkabut', 3: 'Hujan Ringan', 4: 'Hujan Lebat'}
    weather_data['weather_label'] = weather_data['weathersit'].map(weather_labels)
    
    fig, ax = plt.subplots()
    colors = ['#2E7D32', '#FFA000', '#F57C00', '#D32F2F']
    ax.bar(weather_data['weather_label'], weather_data['cnt'], color=colors)
    ax.set_xlabel('Kondisi Cuaca')
    ax.set_ylabel('Rata-rata Penyewaan')
    ax.set_title('Rata-rata Penyewaan per Kondisi Cuaca')
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)
    plt.close()

with col2:
    temp_data = df_filtered.groupby('temp_group')['cnt'].mean().reset_index()
    temp_order = ['Sangat Dingin', 'Dingin', 'Sedang', 'Hangat', 'Panas']
    
    fig, ax = plt.subplots()
    colors = ['#1565C0', '#42A5F5', '#FFA000', '#FF6F00', '#D84315']
    ax.bar(temp_data['temp_group'], temp_data['cnt'], color=colors)
    ax.set_xlabel('Kelompok Suhu')
    ax.set_ylabel('Rata-rata Penyewaan')
    ax.set_title('Rata-rata Penyewaan per Kelompok Suhu')
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)
    plt.close()

st.markdown("---")

# ==================== PERTANYAAN 2: HARI KERJA VS LIBUR ====================
st.subheader("📅 Perbandingan Hari Kerja vs Hari Libur")

col1, col2 = st.columns([1, 1])

with col1:
    workingday_data = df_filtered.groupby('workingday')['cnt'].mean().reset_index()
    fig, ax = plt.subplots()
    colors = ['#FF9800', '#2E7D32']
    ax.bar(['Hari Libur', 'Hari Kerja'], workingday_data['cnt'], color=colors)
    ax.set_ylabel('Rata-rata Penyewaan')
    ax.set_title('Rata-rata Penyewaan: Hari Kerja vs Hari Libur')
    st.pyplot(fig)
    plt.close()

with col2:
    diff_pct = ((workingday_data[workingday_data['workingday']==1]['cnt'].values[0] - 
                 workingday_data[workingday_data['workingday']==0]['cnt'].values[0]) / 
                workingday_data[workingday_data['workingday']==0]['cnt'].values[0] * 100)
    
    st.info(f"""
    ### 📈 **{diff_pct:.1f}%** lebih tinggi pada **Hari Kerja**
    
    **Rekomendasi Operasional:**
    - Alokasikan lebih banyak sepeda pada hari kerja
    - Fokus promosi komuter pada pagi & sore
    - Kembangkan paket rekreasi untuk akhir pekan
    """)

st.markdown("---")

# ==================== PERTANYAAN 3: POLA PER JAM ====================
st.subheader("⏰ Pola Penyewaan per Jam")

hourly_working = df_hour_filtered[df_hour_filtered['workingday'] == 1].groupby('hr')['cnt'].mean().reset_index()
hourly_holiday = df_hour_filtered[df_hour_filtered['workingday'] == 0].groupby('hr')['cnt'].mean().reset_index()

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(hourly_working['hr'], hourly_working['cnt'], marker='o', color='#2E7D32', linewidth=2, label='Hari Kerja')
ax.plot(hourly_holiday['hr'], hourly_holiday['cnt'], marker='s', color='#FF9800', linewidth=2, label='Hari Libur')

# Highlight peak hours
ax.axvspan(7, 9, alpha=0.2, color='green', label='Puncak Pagi (Kerja)')
ax.axvspan(16, 18, alpha=0.2, color='green', label='Puncak Sore (Kerja)')
ax.axvspan(11, 15, alpha=0.2, color='orange', label='Puncak Siang (Libur)')

ax.set_xlabel('Jam')
ax.set_ylabel('Rata-rata Penyewaan')
ax.set_title('Pola Penyewaan: Hari Kerja vs Hari Libur')
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)
st.pyplot(fig)
plt.close()

st.markdown("---")
st.caption("🚲 Bike Sharing Analytics Dashboard | Data source: Bike Sharing Dataset (2011-2012)")
