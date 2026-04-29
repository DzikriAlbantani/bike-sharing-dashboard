import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# Konfigurasi
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")
sns.set(style='dark')

# --- HELPER FUNCTIONS ---
def create_weather_df(df):
    # Agregasi
    weather_df = df.groupby("weathersit")["cnt"].mean().reset_index()
    weather_df.columns = ["condition", "avg_rentals"]
    
    # Mapping Label (Menangani jika data masih angka)
    labels = {1: 'Clear', 2: 'Misty', 3: 'Light Rain/Snow', 4: 'Heavy Rain'}
    # Jika datanya angka, kita ubah ke teks. Jika sudah teks, tetap aman.
    weather_df["condition"] = weather_df["condition"].replace(labels)
    return weather_df

def create_hourly_df(df):
    working_df = df[df["workingday"] == 1]
    if working_df.empty:
        return pd.DataFrame(columns=["hour", "avg_rentals"])
    hourly_df = working_df.groupby("hr")["cnt"].mean().reset_index()
    hourly_df.columns = ["hour", "avg_rentals"]
    return hourly_df

def create_weekday_df(df):
    weekday_df = df.groupby("weekday")["cnt"].mean().reset_index()
    weekday_df.columns = ["day", "avg_rentals"]
    labels = {0:'Sun', 1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat'}
    weekday_df["day"] = weekday_df["day"].replace(labels)
    return weekday_df

# --- LOAD DATA ---
base_dir = os.path.dirname(os.path.abspath(__file__))
path_data = os.path.join(base_dir, "main_data.csv")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df

main_df = load_data(path_data)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    st.title("Bike Sharing Analysis")
    
    min_date, max_date = main_df["dteday"].min().date(), main_df["dteday"].max().date()
    
    # Ambil full range agar grafik langsung muncul
    dates = st.date_input(
        label='Rentang Waktu',
        min_value=min_date, max_value=max_date,
        value=[min_date, max_date]
    )

# Filter Data
if len(dates) == 2:
    start_date, end_date = dates
    filtered_df = main_df[(main_df["dteday"] >= pd.to_datetime(start_date)) & 
                          (main_df["dteday"] <= pd.to_datetime(end_date))]
else:
    filtered_df = main_df

# --- DASHBOARD UI ---
st.title('Dashboard Analisis Bike Sharing')

if not filtered_df.empty:
    # Siapkan Data
    weather_data = create_weather_df(filtered_df)
    hourly_data = create_hourly_df(filtered_df)
    weekday_data = create_weekday_df(filtered_df)

    # Metrics Row
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Peminjaman", f"{filtered_df.cnt.sum():,}")
    c2.metric("Rata-rata/Jam", f"{round(filtered_df.cnt.mean(), 2)}")
    c3.metric("User Registered", f"{filtered_df.registered.sum():,}")

    st.divider()

    # Visualisasi Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Berdasarkan Cuaca")
        fig, ax = plt.subplots(figsize=(10, 6))
        # Gunakan barplot dengan data eksplisit
        sns.barplot(x="condition", y="avg_rentals", data=weather_data, palette="Blues_d", ax=ax)
        st.pyplot(fig)

    with col2:
        st.subheader("Rata-rata Sewa per Hari")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x="day", y="avg_rentals", data=weekday_data, palette="viridis", ax=ax)
        st.pyplot(fig)

    # Visualisasi Row 2
    st.subheader("Tren Jam Sibuk (Hari Kerja)")
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(x="hour", y="avg_rentals", data=hourly_data, marker='o', color="#72BCD4", ax=ax)
    ax.set_xticks(range(0, 24))
    st.pyplot(fig)

else:
    st.warning("Data tidak ditemukan untuk rentang ini.")

st.caption('Copyright (c) Dzikri Albantani 2026')