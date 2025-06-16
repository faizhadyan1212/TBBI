# TBBI
tugas besar BI membuat Dashboard untuk supermarket
Proyek ini adalah aplikasi web interaktif yang dibangun dengan Streamlit untuk menganalisis data penjualan supermarket. Aplikasi ini tidak hanya menampilkan visualisasi, tetapi juga mengimplementasikan alur kerja ETL (Extract, Transform, Load) untuk memindahkan data dari file mentah (CSV/Excel) ke dalam sebuah Data Warehouse MySQL dengan skema bintang (Star Schema) sebelum data tersebut divisualisasikan.
Tahap 1: Pengaturan & ETL

Konfigurasi Koneksi: Pengguna memasukkan detail koneksi database MySQL di sidebar.
Unggah File: Pengguna mengunggah file sumber data (.csv atau .xlsx).
Jalankan ETL: Pengguna menekan tombol untuk memulai proses.
Extract: Data dibaca dari file.
Transform: Data dibersihkan, nama kolom distandarisasi, dan tipe data disesuaikan.
Load: Aplikasi terhubung ke MySQL, membuat database & tabel (jika perlu), lalu memuat data yang sudah bersih ke dalam tabel fakta dan dimensi.
Tahap 2: Visualisasi Dashboard

Ambil Data dari DW: Setelah ETL berhasil, aplikasi beralih mode. Sekarang, data diambil langsung dari Data Warehouse MySQL.
Interaksi Pengguna: Pengguna dapat menggunakan filter di sidebar untuk menganalisis data.
Tampilan Analisis: Semua KPI, grafik, dan prediksi ditampilkan berdasarkan data yang ada di Data Warehouse.
Reset: Pengguna dapat kembali ke tahap 1 dengan menekan tombol "Mulai Ulang".
🔧 Prasyarat
Sebelum Anda memulai, pastikan Anda memiliki perangkat lunak berikut:

Python (versi 3.8 atau lebih tinggi)
pip (manajer paket Python)
Server MySQL yang sedang berjalan (misalnya dari XAMPP, WAMP, Docker, atau instalasi mandiri).
