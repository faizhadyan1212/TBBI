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


1. Persiapan Lingkungan Python
Pastikan telah terpasang Python 3.8 atau versi lebih baru di komputer Anda. Jika belum, unduh dari situs resmi: https://www.python.org/downloads.

Setelah instalasi Python selesai, buka Command Prompt atau Terminal, dan periksa versi Python dengan perintah:

bash
Copy
Edit
python --version
Disarankan untuk menggunakan virtual environment agar proyek tetap terisolasi:

bash
Copy
Edit
python -m venv env
Aktifkan environment:

Windows:

bash
Copy
Edit
env\Scripts\activate
Mac/Linux:

bash
Copy
Edit
source env/bin/activate
2. Instalasi Library Python
Setelah environment aktif, instal semua pustaka yang dibutuhkan dengan perintah berikut:

bash
Copy
Edit
pip install streamlit pandas numpy plotly scikit-learn mysql-connector-python sqlalchemy
Opsional: jika Anda ingin tampilan grafik yang lebih lengkap, Anda juga bisa menambahkan:

bash
Copy
Edit
pip install seaborn matplotlib
3. Persiapan Dataset
Siapkan file dataset penjualan dalam format .csv atau .xlsx (misalnya supermarket_sales.xlsx).

Simpan file dataset tersebut dalam folder yang sama dengan file Python dasbord.py.

4. Instal dan Siapkan MySQL
Unduh dan instal MySQL Server dari: https://dev.mysql.com/downloads/installer/

Pastikan Anda tahu host, user, dan password dari server MySQL Anda.

Tidak perlu membuat database atau tabel secara manual — aplikasi akan membuatnya secara otomatis saat proses ETL.

5. Menjalankan Aplikasi Streamlit
Pastikan Anda berada di direktori tempat file dasbord.py berada.

Jalankan aplikasi menggunakan perintah berikut:

bash
Copy
Edit
streamlit run dasbord.py
Setelah dijalankan, aplikasi akan terbuka di browser (biasanya di alamat: http://localhost:8501).

Ikuti langkah-langkah di layar:

Unggah file dataset

Konfigurasi koneksi database (host, user, password, nama database, dan tabel)

Klik tombol "Jalankan Proses ETL"

Setelah proses selesai, dashboard akan otomatis ditampilkan

6. Catatan Tambahan
Jika koneksi MySQL gagal, pastikan:

Server MySQL sudah berjalan

Port default (biasanya 3306) tidak diblokir firewall

Nama pengguna dan password benar

Jika ingin mengulang dari awal, Anda bisa menghapus cache dan status dengan menekan tombol "Hapus Data & Mulai Ulang" di sidebar aplikasi.
