import streamlit as st
import pandas as pd
import plotly.express as px

# Set konfigurasi halaman
st.set_page_config(page_title="Executive Hotel Report", layout="wide")

st.title("🏨 Executive Hotel Performance Dashboard")
st.markdown("Ringkasan Performa Pemesanan & Pendapatan")

# 1. Load Data
@st.cache_data
def load_data():
    file_path = 'ArrivalsReport_01_01_2026-31_08_2026 (2).xlsx'
    df = pd.read_excel(file_path)
    
    # Preprocessing
    df['Check-in date'] = pd.to_datetime(df['Check-in date'], format='%d/%m/%Y, %H:%M')
    df['Check_in_Month'] = df['Check-in date'].dt.strftime('%Y-%m')
    
    room_mapping = {
        '1B': 'Economy', '2B': 'Economy', '3B': 'Economy', '4B': 'Economy', '5B': 'Economy',
        '6': 'Standard Room', '7': 'Standard Room', '17': 'Standard Room', 
        '22': 'Standard Room', '25': 'Standard Room', '1A': 'Standard Room',
        '2': 'Deluxe Double', '3': 'Deluxe Double', '4': 'Deluxe Double', '10': 'Deluxe Double',
        '11': 'Deluxe Double', '14': 'Deluxe Double', '21': 'Deluxe Double', 
        '23': 'Deluxe Double', '24': 'Deluxe Double', '26': 'Deluxe Double', '27': 'Deluxe Double',
        '1': 'Deluxe Twin', '12': 'Deluxe Twin',
        '8': 'Suite Double', '9': 'Suite Double', '28': 'Suite Double', '29': 'Suite Double',
        '15': 'Suite Family', '18': 'Suite Family', '19': 'Suite Family'
    }
    df['Room number'] = df['Room number'].astype(str)
    df['Room type'] = df['Room number'].map(room_mapping)
    return df

df = load_data()

# 2. Sidebar Filter
st.sidebar.header("Filter Data")
selected_month = st.sidebar.multiselect(
    "Pilih Bulan:",
    options=sorted(df['Check_in_Month'].dropna().unique()),
    default=sorted(df['Check_in_Month'].dropna().unique())
)

df_filtered = df[df['Check_in_Month'].isin(selected_month)]

# 3. Key Metrics (KPIs)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"IDR {df_filtered['Amount'].sum():,.0f}")
col2.metric("Total Booking", f"{len(df_filtered)} Transaksi")
col3.metric("Kamar Valid", f"{df_filtered[df_filtered['Room number'] != 'nan']['Room number'].nunique()} Kamar")
col4.metric("Booking Tanpa Kamar (NaN)", f"{df_filtered['Room type'].isna().sum()} Transaksi")

st.divider()

# 4. Grafik Interaktif
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Tren Pendapatan Bulanan")
    monthly_totals = df_filtered.groupby('Check_in_Month', as_index=False)['Amount'].sum()
    fig1 = px.bar(monthly_totals, x='Check_in_Month', y='Amount', text_auto='.2s', color='Amount', color_continuous_scale='Blues')
    st.plotly_chart(fig1, use_container_width=True)

with col_chart2:
    st.subheader("Proporsi Revenue per Tipe Kamar")
    room_totals = df_filtered.groupby('Room type', as_index=False)['Amount'].sum()
    fig2 = px.pie(room_totals, names='Room type', values='Amount', hole=0.4)
    st.plotly_chart(fig2, use_container_width=True)

# 5. Tabel Detail Data
st.subheader("Detail Performa Per Kamar")
summary_table = (
    df_filtered.groupby(['Check_in_Month', 'Room type', 'Room number'], dropna=True)
    .agg(Total_Booking=('Booking number', 'count'), Total_Amount=('Amount', 'sum'))
    .reset_index()
    .sort_values(by=['Check_in_Month', 'Total_Amount'], ascending=[True, False])
)
st.dataframe(summary_table, use_container_width=True)
