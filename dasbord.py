import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.metrics import r2_score, mean_squared_error
import warnings
import mysql.connector
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import time

warnings.filterwarnings("ignore")

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Supermarket Dashboard with ETL",
    page_icon="🏭",
    layout="wide"
)

# --- FUNGSI-FUNGSI INTI ---

# 1. FUNGSI ETL 
def run_etl_process(file, db_config):
    """
    Menjalankan proses ETL lengkap: Extract, Transform, Load ke MySQL dengan chunking.
    """
    # -- EXTRACT --
    progress_bar = st.progress(0, text="Mengekstrak data dari file...")
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file, encoding='utf-8')
        elif file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file)
        else:
            return False, "Format file tidak didukung."
        progress_bar.progress(25, text="Ekstraksi berhasil. Memulai transformasi...")
        time.sleep(1)

        # -- TRANSFORM --
        # Membersihkan nama kolom agar aman untuk SQL
        df.columns = df.columns.str.strip().str.replace(' ', '_').str.lower().str.replace('%', 'p')
        
        if 'gross_income' in df.columns:
            df.rename(columns={'gross_income': 'profit'}, inplace=True)
        
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M').astype(str)
        
        # Membersihkan kolom numerik
        numeric_cols = ['unit_price', 'quantity', 'tax_5p', 'total', 'cogs', 'gross_margin_percentage', 'profit', 'rating']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(subset=numeric_cols, inplace=True)
        progress_bar.progress(50, text="Transformasi data selesai. Menyiapkan database...")
        time.sleep(1)
        
        # -- LOAD --
        # Membuat database jika belum ada
        try:
            conn = mysql.connector.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['password']
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['db_name']}")
            cursor.close()
            conn.close()
            progress_bar.progress(75, text=f"Database '{db_config['db_name']}' siap. Memuat data...")
        except mysql.connector.Error as e:
            return False, f"Gagal terhubung atau membuat database: {e}"
        
        # Memuat data ke tabel menggunakan SQLAlchemy
        try:
            engine = create_engine(f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['db_name']}")
            
            # --- PERBAIKAN UTAMA DI SINI ---
            df.to_sql(
                db_config['table_name'], 
                con=engine, 
                if_exists='replace', 
                index=False, 
                chunksize=1000  # Mengirim 1000 baris per query untuk menghindari error packet size
            )
            
            progress_bar.progress(100, text="✅ Proses ETL Selesai!")
            time.sleep(1)
            return True, "Data berhasil dimuat ke Data Warehouse."
        except SQLAlchemyError as e:
            return False, f"Gagal memuat data ke tabel: {e}"
        
    except Exception as e:
        return False, f"Terjadi kesalahan pada proses ETL: {e}"


# 2. FUNGSI UNTUK MENGAMBIL DATA DARI DATA WAREHOUSE
@st.cache_data(ttl=600)
def fetch_data_from_dw(_db_config):
    """Mengambil data dari tabel penjualan di MySQL."""
    try:
        engine = create_engine(f"mysql+mysqlconnector://{_db_config['user']}:{_db_config['password']}@{_db_config['host']}/{_db_config['db_name']}")
        # Mengambil nama kolom asli dari tabel untuk pemetaan yang benar
        query = f"SELECT * FROM {_db_config['table_name']}"
        data = pd.read_sql(query, con=engine)
        
        # Balikkan nama kolom ke format yang lebih mudah dibaca untuk tampilan dashboard
        column_mapping = {col: col.replace('_', ' ').title() for col in data.columns}
        data.rename(columns=column_mapping, inplace=True)
        
        # Penanganan khusus untuk kolom yang tidak mengikuti pola title case
        data.rename(columns={'Tax 5P': 'Tax 5%', 'Cogs': 'cogs'}, inplace=True, errors='ignore')
        
        return data
    except Exception as e:
        st.error(f"Gagal mengambil data dari Data Warehouse: {e}")
        return None


# 3. FUNGSI PREDIKSI
def train_and_predict_adaptive(df_monthly, target_col, future_periods=6):
    if df_monthly.empty or len(df_monthly) < 2:
        return None, "Data tidak cukup (butuh min. 2 periode)", None, None, 0, 0, None
    df_monthly = df_monthly.copy(); df_monthly['time_index'] = np.arange(len(df_monthly))
    X = df_monthly[['time_index']]; y = df_monthly[target_col]
    if len(df_monthly) < 5: model = LinearRegression(); model_name = "Regresi Linear (Data Terbatas)"
    else: degree = 2; model = make_pipeline(PolynomialFeatures(degree), LinearRegression()); model_name = f"Regresi Polinomial (Degree {degree})"
    model.fit(X, y); historical_predictions = model.predict(X)
    r2 = r2_score(y, historical_predictions); mse = mean_squared_error(y, historical_predictions)
    last_index = df_monthly['time_index'].max(); future_indices = np.arange(last_index + 1, last_index + 1 + future_periods).reshape(-1, 1); future_predictions = model.predict(future_indices)
    last_month_period = pd.to_datetime(df_monthly['Month'].max()).to_period('M'); future_month_labels = [(last_month_period + i).strftime('%Y-%m') for i in range(1, future_periods + 1)]
    future_df = pd.DataFrame({'Month': future_month_labels, 'Prediction': future_predictions})
    return df_monthly, model_name, historical_predictions, future_df, r2, mse, model

# --- LOGIKA UTAMA APLIKASI ---

if 'etl_complete' not in st.session_state:
    st.session_state.etl_complete = False

if st.session_state.etl_complete:
    st.title("💡 Dashboard Analisis Supermarket")
    st.success("Menampilkan data dari Data Warehouse MySQL.")
    
    data = fetch_data_from_dw(st.session_state.db_config)
    
    if data is not None and not data.empty:
        st.sidebar.header("⚙️ Filter Data")
        # Pastikan kolom 'Month' ada dan dalam format string
        if 'Month' not in data.columns and 'Date' in data.columns:
            data['Date'] = pd.to_datetime(data['Date'])
            data['Month'] = data['Date'].dt.to_period('M').astype(str)

        months = sorted(data['Month'].unique())
        selected_months = st.sidebar.multiselect('Pilih Bulan:', months, default=months)
        cities = sorted(data['City'].unique())
        selected_cities = st.sidebar.multiselect('Pilih Kota:', cities, default=cities)
        
        if selected_months and selected_cities:
            temp_filtered_data = data[(data['Month'].isin(selected_months)) & (data['City'].isin(selected_cities))]
            available_branches = sorted(temp_filtered_data['Branch'].unique())
        else:
            available_branches = []
        selected_branches = st.sidebar.multiselect('Pilih Cabang:', available_branches, default=available_branches)
        
        if selected_months and selected_cities and selected_branches:
            filtered_data = data[(data['Month'].isin(selected_months)) & (data['City'].isin(selected_cities)) & (data['Branch'].isin(selected_branches))]
        else:
            filtered_data = pd.DataFrame()
        
        if filtered_data.empty: st.warning("Tidak ada data untuk filter yang dipilih."); st.stop()
        
        st.markdown(f"Menganalisis **{len(filtered_data)}** transaksi dari filter yang Anda pilih.")
        tab1, tab2, tab3 = st.tabs(["🧭 Overview Penjualan", "📊 Analisis Produk & Pelanggan", "📈 Analisis & Prediksi Tren"])

        with tab1:
            st.header("Ringkasan Kinerja Penjualan")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Tren Penjualan Bulanan"); monthly_sales = filtered_data.groupby('Month')['Total'].sum().reset_index(); fig_trend = px.line(monthly_sales, x='Month', y='Total', markers=True); st.plotly_chart(fig_trend, use_container_width=True)
            with col2:
                st.subheader("Preferensi Metode Pembayaran"); payment_counts = filtered_data['Payment'].value_counts().reset_index(); fig_payment = px.pie(payment_counts, names='Payment', values='count', hole=0.4); st.plotly_chart(fig_payment, use_container_width=True)
            st.subheader("Performa Penjualan per Kota dan Cabang"); sales_by_city_branch = filtered_data.groupby(['City', 'Branch'])['Total'].sum().reset_index(); fig_city_branch = px.bar(sales_by_city_branch, x='City', y='Total', color='Branch', barmode='group'); st.plotly_chart(fig_city_branch, use_container_width=True)
        with tab2:
            st.header("Produk dan Pelanggan"); col1, col2 = st.columns(2)
            with col1:
                sales_by_category = filtered_data.groupby('Product Line')['Total'].sum().sort_values().reset_index(); fig_cat = px.bar(sales_by_category, x='Total', y='Product Line', orientation='h', color='Total'); st.plotly_chart(fig_cat, use_container_width=True)
            with col2:
                customer_type_sales = filtered_data.groupby('Customer Type')['Total'].sum().reset_index(); fig_pie_customer = px.pie(customer_type_sales, names='Customer Type', values='Total', hole=0.4); st.plotly_chart(fig_pie_customer, use_container_width=True)
            st.markdown("---"); st.subheader("Segmentasi Pembelian Berdasarkan Gender"); gender_pref = filtered_data.groupby(['Product Line', 'Gender'])['Quantity'].sum().reset_index(); fig_stacked_bar = px.bar(gender_pref, x='Product Line', y='Quantity', color='Gender', barmode='group'); st.plotly_chart(fig_stacked_bar, use_container_width=True)
        with tab3:
            st.header("Analisis Kinerja dan Prediksi Masa Depan"); st.subheader("Key Performance Indicators (KPIs)")
            total_sales = filtered_data['Total'].sum(); total_profit = filtered_data['Profit'].sum(); avg_rating = filtered_data['Rating'].mean()
            monthly_sales_kpi = filtered_data.groupby('Month')['Total'].sum().reset_index(); _, _, _, future_sales_df, _, _, _ = train_and_predict_adaptive(monthly_sales_kpi, 'Total')
            next_month_sales_prediction = future_sales_df['Prediction'][0] if future_sales_df is not None and not future_sales_df.empty else 0
            kpi_r1_c1, kpi_r1_c2 = st.columns(2); kpi_r2_c1, kpi_r2_c2 = st.columns(2)
            with kpi_r1_c1: st.metric(label="💰 Total Penjualan Aktual", value=f"$ {total_sales:,.2f}")
            with kpi_r1_c2: st.metric(label="✅ Total Profit Aktual", value=f"$ {total_profit:,.2f}")
            with kpi_r2_c1: st.metric(label="⭐ Rata-rata Rating", value=f"{avg_rating:.2f}")
            with kpi_r2_c2: st.metric(label="📈 Prediksi Penjualan Bulan Depan", value=f"$ {next_month_sales_prediction:,.2f}")
            st.markdown("---"); st.header("🔮 Analisis Prediktif"); st.subheader("Prediksi Tren Penjualan")
            monthly_sales_pred = filtered_data.groupby('Month')['Total'].sum().reset_index(); actual_df, model_name, hist_preds, future_df, r2, mse, _ = train_and_predict_adaptive(monthly_sales_pred, 'Total')
            if actual_df is not None:
                m_col1, m_col2 = st.columns(2); m_col1.metric(label="Akurasi Model (R-squared)", value=f"{r2:.2%}"); m_col2.metric(label="Error Model (MSE)", value=f"{mse:,.2f}")
                st.info(f"Model: {model_name}"); fig_pred = go.Figure(); fig_pred.add_trace(go.Scatter(x=actual_df['Month'], y=actual_df['Total'], mode='lines+markers', name='Aktual')); fig_pred.add_trace(go.Scatter(x=actual_df['Month'], y=hist_preds, mode='lines', name='Garis Tren', line=dict(dash='dash'))); fig_pred.add_trace(go.Scatter(x=future_df['Month'], y=future_df['Prediction'], mode='lines+markers', name='Prediksi')); st.plotly_chart(fig_pred, use_container_width=True)
            else: st.warning("Butuh minimal 2 bulan data untuk prediksi.")
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🔌 Hapus Data & Mulai Ulang"):
        st.session_state.etl_complete = False
        st.cache_data.clear()
        st.rerun()

else:
    st.title("🏭 Proses ETL & Data Warehouse Supermarket")
    st.markdown("Selamat datang! Aplikasi ini akan memandu Anda melalui proses ETL untuk memuat data penjualan ke dalam data warehouse MySQL sebelum visualisasi.")
    
    st.sidebar.header("🔌 Konfigurasi Database MySQL")
    db_config = {}
    db_config['host'] = st.sidebar.text_input("Host", value="localhost")
    db_config['user'] = st.sidebar.text_input("User", value="root")
    db_config['password'] = st.sidebar.text_input("Password", type="password")
    db_config['db_name'] = st.sidebar.text_input("Nama Database", value="supermarket_dw")
    db_config['table_name'] = st.sidebar.text_input("Nama Tabel", value="sales_data")
    
    st.info("Pastikan server MySQL Anda sedang berjalan sebelum melanjutkan.")

    uploaded_file = st.file_uploader("Langkah 1: Unggah file data penjualan Anda (.csv atau .xlsx)", type=['csv', 'xlsx'])

    if uploaded_file:
        st.markdown("Langkah 2: Jalankan proses ETL untuk memuat data ke Data Warehouse.")
        if st.button("🚀 Jalankan Proses ETL", type="primary"):
            etl_success, etl_message = run_etl_process(uploaded_file, db_config)
            
            if etl_success:
                st.success(etl_message)
                st.session_state.db_config = db_config
                st.session_state.etl_complete = True
                st.balloons()
                time.sleep(2)
                st.rerun()
            else:
                st.error(etl_message)