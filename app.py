import streamlit as st
import pandas as pd
import plotly.express as px

# Set konfigurasi halaman
st.set_page_config(page_title="Executive Hotel Report Patradissa", layout="wide")
st.title("🏨 Patradissa Executive Hotel Performance Dashboard")

# Helper function untuk format angka ke Rupiah
def format_rupiah(nilai):
    if pd.isna(nilai):
        return "Rp. 0"
    return f"Rp. {nilai:,.0f}".replace(",", ".")

# 1. Load Data
@st.cache_data
def load_data():
    file_path = 'ArrivalsReport.xlsx'
    df = pd.read_excel(file_path)
    
    # Preprocessing
    df['Check-in date'] = pd.to_datetime(df['Check-in date'], format='%d/%m/%Y, %H:%M')
    df['Check_in_Month'] = df['Check-in date'].dt.strftime('%Y-%m')
    df['Check_in_Date_Only'] = df['Check-in date'].dt.date
    
    # Format Tanggal khusus untuk display hover (contoh: 1 Sep 2026)
    df['Check_in_Date_Formatted'] = df['Check-in date'].dt.strftime('%d %b %Y').str.lstrip('0')
    
    # Rename 'Amount' -> 'Revenue'
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

# CSS Kustom untuk Kartu KPI Responsif
st.markdown("""
<style>
.kpi-container {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.kpi-card {
    flex: 1 1 200px;
    background-color: #f8f9fa;
    padding: 1.2rem;
    border-radius: 10px;
    border: 1px solid #e9ecef;
    box-shadow: 0 2px 4px rgba(0,0,0,0.04);
}
.kpi-title {
    font-size: 0.85rem;
    color: #6c757d;
    margin-bottom: 0.3rem;
    font-weight: 600;
}
.kpi-value {
    font-size: 1.35rem;
    font-weight: 700;
    color: #1f2937;
}
</style>
""", unsafe_allow_html=True)

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
    
    # KPI Metric Card Responsif
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-title">Total Revenue</div>
            <div class="kpi-value">{format_rupiah(df_filtered['Revenue'].sum())}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Total Booking</div>
            <div class="kpi-value">{len(df_filtered)} Transaksi</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Kamar Valid</div>
            <div class="kpi-value">{df_filtered[df_filtered['Room number'] != 'nan']['Room number'].nunique()} Kamar</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Booking Tanpa Kamar (NaN)</div>
            <div class="kpi-value">{df_filtered['Room type'].isna().sum()} Transaksi</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown("**Tren Revenue Bulanan**")
        monthly_totals = df_filtered.groupby('Check_in_Month', as_index=False)['Revenue'].sum()
        
        # Tambahkan label bulan terformat (misal: Mar 2026) dan Revenue terformat
        monthly_totals['Month_Formatted'] = pd.to_datetime(monthly_totals['Check_in_Month']).dt.strftime('%b %Y')
        monthly_totals['Revenue_Formatted'] = monthly_totals['Revenue'].apply(format_rupiah)
        
        fig1 = px.line(
            monthly_totals, 
            x='Check_in_Month', 
            y='Revenue', 
            markers=True, 
            title="Tren Revenue Bulanan",
            labels={'Check_in_Month': 'Bulan', 'Revenue': 'Total Revenue'},
            custom_data=['Month_Formatted', 'Revenue_Formatted']
        )
        fig1.update_traces(
            line_shape='linear', 
            line_width=3,
            hovertemplate="%{customdata[0]}<br>%{customdata[1]}<extra></extra>"
        )
        fig1.update_layout(yaxis=dict(tickprefix="Rp ", tickformat=",.0f"))
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_chart2:
        st.markdown("**Proporsi Revenue per Tipe Kamar**")
        room_totals = df_filtered.groupby('Room type', as_index=False)['Revenue'].sum()
        room_totals['Revenue_Formatted'] = room_totals['Revenue'].apply(format_rupiah)
        
        fig2 = px.pie(
            room_totals, 
            names='Room type', 
            values='Revenue', 
            hole=0.4,
            custom_data=['Revenue_Formatted']
        )
        fig2.update_traces(
            hovertemplate="%{label}<br>%{customdata[0]} (%{percent})<extra></extra>"
        )
        st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------------
# MENU 2: ANALISIS PER TIPE KAMAR (RESPONSIF)
# ---------------------------------------------------------
elif menu_pilihan == "Analisis Per Tipe Kamar":
    st.subheader("📊 Performance per Room Type")
    
    type_summary = (
        df_filtered.groupby('Room type', dropna=False)
        .agg(Total_Booking=('Booking number', 'count'), Total_Revenue=('Revenue', 'sum'))
        .reset_index()
        .sort_values(by='Total_Booking', ascending=False)
    )
    
    type_summary_display = type_summary.copy()
    type_summary_display['Total_Revenue'] = type_summary_display['Total_Revenue'].apply(format_rupiah)
    
    col_tabel, col_chart = st.columns([1, 1])
    
    with col_tabel:
        st.markdown("**Tabel Detail Per Tipe Kamar**")
        st.dataframe(type_summary_display, use_container_width=True)
        
    with col_chart:
        fig_bar = px.bar(
            type_summary, 
            x='Room type', 
            y='Total_Booking', 
            text='Total_Booking', 
            title="Total Booking per Tipe Kamar"
        )
        fig_bar.update_traces(
            hovertemplate="%{x}<br>%{y} Booking<extra></extra>",
            textposition='outside'
        )
        fig_bar.update_layout(margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_bar, use_container_width=True)
        
    st.divider()
    
    st.markdown("**Tren Jumlah Booking Harian per Tipe Kamar**")
    
    daily_type_summary = (
        df_filtered.groupby(['Check_in_Date_Only', 'Check_in_Date_Formatted', 'Room type'])
        .agg(Total_Booking=('Booking number', 'count'))
        .reset_index()
        .sort_values(by='Check_in_Date_Only')
    )
    
    fig_line = px.line(
        daily_type_summary,
        x='Check_in_Date_Only',
        y='Total_Booking',
        color='Room type',
        markers=True,
        title="Tren Harian Booking Berdasarkan Tipe Kamar",
        labels={'Check_in_Date_Only': 'Tanggal Check-in', 'Total_Booking': 'Jumlah Booking'},
        custom_data=['Check_in_Date_Formatted', 'Room type']
    )
    
    fig_line.update_traces(
        hovertemplate="%{customdata[0]}<br>%{customdata[1]}<br>%{y} Booking<extra></extra>"
    )
    
    fig_line.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    
    st.plotly_chart(fig_line, use_container_width=True)

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
    
    room_summary_display = room_summary.copy()
    room_summary_display['Total_Revenue'] = room_summary_display['Total_Revenue'].apply(format_rupiah)
    
    st.dataframe(room_summary_display, use_container_width=True)

# ---------------------------------------------------------
# MENU 4: TREN PER TANGGAL & BULAN
# ---------------------------------------------------------
elif menu_pilihan == "Tren Per Tanggal & Bulan":
    st.subheader("📅 Summary & Tren Berdasarkan Periode Waktu")
    
    df_filtered['Check_in_Date_DT'] = pd.to_datetime(df_filtered['Check_in_Date_Only'])
    df_filtered['Week_Start'] = df_filtered['Check_in_Date_DT'].dt.to_period('W-SUN').dt.start_time
    df_filtered['Check_in_Week'] = df_filtered['Week_Start'].dt.strftime('Minggu %V (%Y)')
    df_filtered['Check_in_Quarter'] = df_filtered['Check_in_Date_DT'].dt.to_period('Q').astype(str)
    df_filtered['Check_in_Year'] = df_filtered['Check_in_Date_DT'].dt.year.astype(str)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Harian", 
        "Mingguan (Senin-Minggu)", 
        "Bulanan", 
        "Kuartalan (Q1-Q4)", 
        "Tahunan"
    ])
    
    # --- TAB 1: HARIAN ---
    with tab1:
        daily_summary = (
            df_filtered.groupby(['Check_in_Date_Only', 'Check_in_Date_Formatted'])
            .agg(Total_Booking=('Booking number', 'count'), Total_Revenue=('Revenue', 'sum'))
            .reset_index()
            .sort_values(by='Check_in_Date_Only')
        )
        
        daily_summary['Revenue_Formatted'] = daily_summary['Total_Revenue'].apply(format_rupiah)
        
        fig_daily = px.line(
            daily_summary, 
            x='Check_in_Date_Only', 
            y='Total_Revenue', 
            markers=True,
            title="Grafik Tren Revenue Harian",
            labels={'Check_in_Date_Only': 'Tanggal', 'Total_Revenue': 'Total Revenue'},
            custom_data=['Check_in_Date_Formatted', 'Revenue_Formatted']
        )
        
        # Hover format: 14 Feb 2026 \n Rp 7.833.406
        fig_daily.update_traces(
            hovertemplate="%{customdata[0]}<br>%{customdata[1]}<extra></extra>"
        )
        
        fig_daily.update_layout(yaxis=dict(tickprefix="Rp ", tickformat=",.0f"))
        st.plotly_chart(fig_daily, use_container_width=True)
        
        daily_summary_display = daily_summary[['Check_in_Date_Only', 'Total_Booking', 'Total_Revenue']].copy()
        daily_summary_display['Total_Revenue'] = daily_summary_display['Total_Revenue'].apply(format_rupiah)
        st.dataframe(daily_summary_display, use_container_width=True)

    # --- TAB 2: MINGGUAN (Senin s/d Minggu) ---
    with tab2:
        weekly_summary = (
            df_filtered.groupby(['Week_Start', 'Check_in_Week'])
            .agg(Total_Booking=('Booking number', 'count'), Total_Revenue=('Revenue', 'sum'))
            .reset_index()
            .sort_values(by='Week_Start')
        )
        
        weekly_summary['Revenue_Formatted'] = weekly_summary['Total_Revenue'].apply(format_rupiah)
        
        fig_weekly = px.line(
            weekly_summary, 
            x='Check_in_Week', 
            y='Total_Revenue', 
            markers=True,
            title="Grafik Tren Revenue Mingguan (Senin - Minggu)",
            labels={'Check_in_Week': 'Minggu Ke-', 'Total_Revenue': 'Total Revenue'},
            custom_data=['Revenue_Formatted']
        )
        
        # Hover format: Minggu 07 (2026) \n Rp 33.130.976
        fig_weekly.update_traces(
            hovertemplate="%{x}<br>%{customdata[0]}<extra></extra>"
        )
        
        fig_weekly.update_layout(yaxis=dict(tickprefix="Rp ", tickformat=",.0f"))
        st.plotly_chart(fig_weekly, use_container_width=True)
        
        weekly_summary_display = weekly_summary[['Check_in_Week', 'Total_Booking', 'Total_Revenue']].copy()
        weekly_summary_display['Total_Revenue'] = weekly_summary_display['Total_Revenue'].apply(format_rupiah)
        st.dataframe(weekly_summary_display, use_container_width=True)
        
    # --- TAB 3: BULANAN ---
    with tab3:
        monthly_summary = (
            df_filtered.groupby('Check_in_Month')
            .agg(Total_Booking=('Booking number', 'count'), Total_Revenue=('Revenue', 'sum'))
            .reset_index()
            .sort_values(by='Check_in_Month')
        )
        
        monthly_summary['Month_Formatted'] = pd.to_datetime(monthly_summary['Check_in_Month']).dt.strftime('%b %Y')
        monthly_summary['Revenue_Formatted'] = monthly_summary['Total_Revenue'].apply(format_rupiah)
        
        fig_monthly = px.line(
            monthly_summary, 
            x='Check_in_Month', 
            y='Total_Revenue', 
            markers=True, 
            title="Grafik Tren Revenue Bulanan",
            labels={'Check_in_Month': 'Bulan', 'Total_Revenue': 'Total Revenue'},
            custom_data=['Month_Formatted', 'Revenue_Formatted']
        )
        
        # Hover format: Mar 2026 \n Rp 111.580.670
        fig_monthly.update_traces(
            hovertemplate="%{customdata[0]}<br>%{customdata[1]}<extra></extra>"
        )
        
        fig_monthly.update_layout(yaxis=dict(tickprefix="Rp ", tickformat=",.0f"))
        st.plotly_chart(fig_monthly, use_container_width=True)
        
        monthly_summary_display = monthly_summary[['Check_in_Month', 'Total_Booking', 'Total_Revenue']].copy()
        monthly_summary_display['Total_Revenue'] = monthly_summary_display['Total_Revenue'].apply(format_rupiah)
        st.dataframe(monthly_summary_display, use_container_width=True)

    # --- TAB 4: KUARTALAN ---
    with tab4:
        df_filtered['Quarter_Label'] = df_filtered['Check_in_Date_DT'].dt.to_period('Q').apply(lambda q: f"Q{q.quarter} {q.year}")
        
        quarterly_summary = (
            df_filtered.groupby('Quarter_Label')
            .agg(Total_Booking=('Booking number', 'count'), Total_Revenue=('Revenue', 'sum'))
            .reset_index()
            .sort_values(by='Quarter_Label')
        )
        quarterly_summary['Revenue_Formatted'] = quarterly_summary['Total_Revenue'].apply(format_rupiah)
        
        fig_quarterly = px.bar(
            quarterly_summary, 
            x='Quarter_Label', 
            y='Total_Revenue', 
            text='Revenue_Formatted',
            title="Grafik Revenue Kuartalan",
            labels={'Quarter_Label': 'Kuartal', 'Total_Revenue': 'Total Revenue'},
            custom_data=['Revenue_Formatted']
        )
        
        fig_quarterly.update_traces(
            hovertemplate="%{x}<br>%{customdata[0]}<extra></extra>",
            textposition='outside'
        )
        
        fig_quarterly.update_layout(yaxis=dict(tickprefix="Rp ", tickformat=",.0f"))
        st.plotly_chart(fig_quarterly, use_container_width=True)
        
        quarterly_summary_display = quarterly_summary[['Quarter_Label', 'Total_Booking', 'Total_Revenue']].copy()
        quarterly_summary_display['Total_Revenue'] = quarterly_summary_display['Total_Revenue'].apply(format_rupiah)
        st.dataframe(quarterly_summary_display, use_container_width=True)

    # --- TAB 5: TAHUNAN ---
    with tab5:
        yearly_summary = (
            df_filtered.groupby('Check_in_Year')
            .agg(Total_Booking=('Booking number', 'count'), Total_Revenue=('Revenue', 'sum'))
            .reset_index()
            .sort_values(by='Check_in_Year')
        )
        yearly_summary['Revenue_Formatted'] = yearly_summary['Total_Revenue'].apply(format_rupiah)
        
        fig_yearly = px.bar(
            yearly_summary, 
            x='Check_in_Year', 
            y='Total_Revenue', 
            text='Revenue_Formatted',
            title="Grafik Revenue Tahunan",
            labels={'Check_in_Year': 'Tahun', 'Total_Revenue': 'Total Revenue'},
            custom_data=['Revenue_Formatted']
        )
        
        fig_yearly.update_traces(
            hovertemplate="Tahun %{x}<br>%{customdata[0]}<extra></extra>",
            textposition='outside'
        )
        
        fig_yearly.update_layout(yaxis=dict(tickprefix="Rp ", tickformat=",.0f"))
        st.plotly_chart(fig_yearly, use_container_width=True)
        
        yearly_summary_display = yearly_summary[['Check_in_Year', 'Total_Booking', 'Total_Revenue']].copy()
        yearly_summary_display['Total_Revenue'] = yearly_summary_display['Total_Revenue'].apply(format_rupiah)
        st.dataframe(yearly_summary_display, use_container_width=True)

# ---------------------------------------------------------
# MENU 5: DATA MENTAH / RAW DATA
# ---------------------------------------------------------
elif menu_pilihan == "Data Mentah / Raw Data":
    st.subheader("📋 Raw Data View")
    st.write(f"Menampilkan {len(df_filtered)} baris data hasil filter.")
    
    raw_data_display = df_filtered.copy()
    raw_data_display['Revenue'] = raw_data_display['Revenue'].apply(format_rupiah)
    st.dataframe(raw_data_display, use_container_width=True)
