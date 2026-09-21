import streamlit as st
import pandas as pd
import plotly.express as px

# Set konfigurasi halaman
st.set_page_config(page_title="Executive Hotel Report", layout="wide")
st.title("🏨 Executive Hotel Performance Dashboard")

# 1. Load Data
@st.cache_data
def load_data():
    file_path = 'ArrivalsReport_01_01_2026-31_08_2026 (2).xlsx'
    df = pd.read_excel(file_path)
    
    # Preprocessing
    df['Check-in date'] = pd.to_datetime(df['Check-in date'], format='%d/%m/%Y, %H:%M')
    df['Check_in_Month'] = df['Check-in date'].dt.strftime('%Y-%m')
    df['Check_in_Date_Only'] = df['Check-in date'].dt.date
    
    # Rename kolom 'Amount' menjadi 'Revenue'
    df = df.rename(columns={'Amount': 'Revenue'})
    
    room_mapping = {
        '1B': 'Economy', '2B': 'Economy', '3B': 'Economy', '4B': 'Economy', '5B': 'Economy',
        '6': 'Standard Room', '7': 'Standard Room', '17': 'Standard Room', '22': 'Standard Room', '25': 'Standard Room', '1A': 'Standard Room',
        '2': 'Deluxe Double', '3': 'Deluxe Double', '4': 'Deluxe Double', '10': 'Deluxe Double', '11': 'Deluxe Double', '14': 'Deluxe Double', 
        '21': 'Deluxe Double', '23': 'Deluxe Double', '24': 'Deluxe Double', '26': 'Deluxe Double', '27': 'Deluxe Double',
        '1': 'Deluxe Twin', '12': 'Deluxe Twin',
        '8': 'Suite Double', '9': 'Suite Double', '28': 'Suite Double', '29': 'Suite Double',
        '15': 'Suite Family', '18': 'Suite Family', '19': 'Suite Family'
    }
    
    df['Room number'] = df['Room number'].astype(str)
    df['Room type'] = df['Room number'].map(room_mapping)
    return df

df = load_data()

# 2. Sidebar Navigation & Filter
st.sidebar.header("Navigasi & Filter")

menu_pilihan = st.sidebar.radio(
    "Pilih Menu Dashboard:",
    [
        "Ringkasan Utama & KPI",
        "Analisis Per Tipe Kamar",
        "Analisis Per Kamar / Room Number",
        "Tren Per Tanggal & Bulan",
        "Data Mentah / Raw Data"
    ]
)

selected_month = st.sidebar.multiselect(
    "Pilih Bulan:",
    options=sorted(df['Check_in_Month'].dropna().unique()),
    default=sorted(df['Check_in_Month'].dropna().unique())
)

df_filtered = df[df['Check_in_Month'].isin(selected_month)]

# ---------------------------------------------------------
# MENU 1: RINGKASAN UTAMA & KPI
# ---------------------------------------------------------
if menu_pilihan == "Ringkasan Utama & KPI":
    st.subheader("📌 Executive Summary & Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"IDR {df_filtered['Revenue'].sum():,.0f}")
    col2.metric("Total Booking", f"{len(df_filtered)} Transaksi")
    col3.metric("Kamar Valid", f"{df_filtered[df_filtered['Room number'] != 'nan']['Room number'].nunique()} Kamar")
    col4.metric("Booking Tanpa Kamar (NaN)", f"{df_filtered['Room type'].isna().sum()} Transaksi")
    
    st.divider()
    
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown("**Tren Revenue Bulanan**")
        monthly_totals = df_filtered.groupby('Check_in_Month', as_index=False)['Revenue'].sum()
        
        # Grafik Garis Tren Revenue
        fig1 = px.line(
            monthly_totals, 
            x='Check_in_Month', 
            y='Revenue', 
            markers=True, 
            title="Tren Revenue Bulanan",
            labels={'Check_in_Month': 'Bulan', 'Revenue': 'Total Revenue (IDR)'}
        )
        fig1.update_traces(line_shape='linear', line_width=3)
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_chart2:
        st.markdown("**Proporsi Revenue per Tipe Kamar**")
        room_totals = df_filtered.groupby('Room type', as_index=False)['Revenue'].sum()
        fig2 = px.pie(room_totals, names='Room type', values='Revenue', hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------------
# MENU 2: ANALISIS PER TIPE KAMAR
# ---------------------------------------------------------
elif menu_pilihan == "Analisis Per Tipe Kamar":
    st.subheader("📊 Performance per Room Type")
    
    type_summary = (
        df_filtered.groupby('Room type', dropna=False)
        .agg(Total_Booking=('Booking number', 'count'), Total_Revenue=('Revenue', 'sum'))
        .reset_index()
        .sort_values(by='Total_Booking', ascending=False)
    )
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.dataframe(type_summary, use_container_width=True)
    with col2:
        fig = px.bar(type_summary, x='Room type', y='Total_Booking', text='Total_Booking', title="Jumlah Booking per Room Type")
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# MENU 3: ANALISIS PER KAMAR / ROOM NUMBER
# ---------------------------------------------------------
elif menu_pilihan == "Analisis Per Kamar / Room Number":
    st.subheader("🛏️ Performance per Room Number & Type")
    
    room_summary = (
        df_filtered.groupby(['Room type', 'Room number'], dropna=True)
        .agg(Total_Booking=('Booking number', 'count'), Total_Revenue=('Revenue', 'sum'))
        .reset_index()
        .sort_values(by='Total_Revenue', ascending=False)
    )
    
    st.dataframe(room_summary, use_container_width=True)

# ---------------------------------------------------------
# MENU 4: TREN PER TANGGAL & BULAN
# ---------------------------------------------------------
elif menu_pilihan == "Tren Per Tanggal & Bulan":
    st.subheader("📅 Summary & Tren Per Tanggal & Bulan")
    
    tab1, tab2 = st.tabs(["Per Tanggal", "Per Bulan"])
    
    with tab1:
        daily_summary = (
            df_filtered.groupby('Check_in_Date_Only')
            .agg(Total_Booking=('Booking number', 'count'), Total_Revenue=('Revenue', 'sum'))
            .reset_index()
            .sort_values(by='Check_in_Date_Only')
        )
        
        # Grafik Garis Tren Harian
        fig_daily = px.line(
            daily_summary, 
            x='Check_in_Date_Only', 
            y='Total_Revenue', 
            title="Grafik Tren Revenue Harian",
            labels={'Check_in_Date_Only': 'Tanggal', 'Total_Revenue': 'Total Revenue (IDR)'}
        )
        st.plotly_chart(fig_daily, use_container_width=True)
        st.dataframe(daily_summary, use_container_width=True)
        
    with tab2:
        monthly_summary = (
            df_filtered.groupby('Check_in_Month')
            .agg(Total_Booking=('Booking number', 'count'), Total_Revenue=('Revenue', 'sum'))
            .reset_index()
            .sort_values(by='Check_in_Month')
        )
        
        # Grafik Garis Tren Bulanan
        fig_monthly = px.line(
            monthly_summary, 
            x='Check_in_Month', 
            y='Total_Revenue', 
            markers=True, 
            title="Grafik Tren Revenue Bulanan",
            labels={'Check_in_Month': 'Bulan', 'Total_Revenue': 'Total Revenue (IDR)'}
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
        st.dataframe(monthly_summary, use_container_width=True)

# ---------------------------------------------------------
# MENU 5: DATA MENTAH / RAW DATA
# ---------------------------------------------------------
elif menu_pilihan == "Data Mentah / Raw Data":
    st.subheader("📋 Raw Data View")
    st.write(f"Menampilkan {len(df_filtered)} baris data hasil filter.")
    st.dataframe(df_filtered, use_container_width=True)
