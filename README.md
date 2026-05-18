# Sistem Pantau Indikator Pelayanan Rumah Sakit (BOR, LOS, GDR)

Sistem Informasi berbasis web (Django) yang dirancang untuk memantau, mengelola, dan menganalisis indikator utama pelayanan pasien, khususnya di rumah sakit atau klinik. Aplikasi ini berfokus pada perhitungan dan evaluasi kinerja berbasis metrik seperti **BOR (Bed Occupancy Rate)**, **LOS (Length of Stay)**, dan **GDR (Gross Death Rate)**.

Dilengkapi dengan sistem rekomendasi berdasarkan analisis kasus (untuk pelayanan medis maupun kepegawaian), aplikasi ini memfasilitasi pengambilan keputusan oleh manajemen dan direksi.

## 🌟 Fitur Utama

- **Dashboard Indikator**: Visualisasi dan ringkasan data indikator (BOR, LOS, GDR) berdasarkan periode (Bulan/Tahun).
- **Manajemen Pasien Rawat Inap**: Pencatatan data masuk dan keluar pasien beserta status pulang (Sembuh, Pindah Kamar, Atas Permintaan Sendiri, Meninggal, dll).
- **Sistem Rekomendasi**: Modul pencatatan rekomendasi kasus untuk divisi **Pelayanan Medis (Yanmed)** dan **Kepegawaian** guna perbaikan strategi layanan ke depan.
- **Role-based Access Control (RBAC)**: Terdapat 3 role (hak akses) utama dengan wewenang berbeda:
  - `Direktur`
  - `Yanmed` (Pelayanan Medis)
  - `Kepegawaian`
- **Manajemen Akun (User Management)**: Pembuatan, pengeditan, dan penghapusan pengguna sesuai role.
- **Notebook Analisis Data**: Terdapat file Jupyter Notebook (`perhitungan_indikator_bor,los,gdr (1).ipynb`) untuk keperluan eksplorasi dan analisis saintifik di luar antarmuka web.

## 🛠️ Teknologi yang Digunakan

- **Backend Framework**: Python (Django)
- **Frontend / UI**: HTML, CSS (Bootstrap 5 via `django-crispy-forms`)
- **Database**: SQLite (Default) atau opsional MySQL (`pymysql`)
- **Data Analysis**: Jupyter Notebook, Pandas (opsional jika menjalankan _notebook_)

## 🚀 Panduan Instalasi & Menjalankan Projek

Ikuti langkah-langkah di bawah ini untuk menjalankan proyek di perangkat lokal (localhost):

### 1. Prasyarat Lingkungan

Pastikan perangkat Anda sudah terinstall:

- **Python 3.x**
- **pip** (Python package installer)

_(Sangat disarankan untuk menggunakan [Virtual Environment](https://docs.python.org/3/tutorial/venv.html) guna mengisolasi library proyek)._

### 2. Instalasi Dependensi (Libraries)

Instal library yang dibutuhkan (Django, Crispy Forms, dan Bootstrap 5 integrasi) menggunakan perintah berikut di terminal/CMD:

```bash
pip install django
python -m pip install django-crispy-forms
pip install crispy-bootstrap5
```

> **Catatan Database (Opsional):**  
> Secara default proyek menggunakan SQLite (`db.sqlite3`). Apabila ingin menggunakan database **MySQL**, Anda harus menyesuaikan konfigurasi `DATABASES` pada file pengaturan (`settings.py`) dan perlu menginstal library konektor:  
> `pip install pymysql`

### 3. Setup Konfigurasi & Database

Setelah semua _library_ terinstall, lakukan migrasi untuk membuat tabel-tabel dalam database.

#### Konfigurasi Database Ganda

Proyek ini menggunakan **2 database**:
- **Database Default** (`rs_pku`): Untuk User, Kasus, Rekomendasi, dan model lainnya
- **Database Kedua** (`rs_rekom`): Khusus untuk model RawatInap

1. **Membuat File Migration**  
   Generate struktur database yang telah dikonfigurasi pada model ke dalam file migrasi.

   ```bash
   python manage.py makemigrations
   ```

   *(Opsional: Jika muncul interaksi pilihan perbaikan *migrations*, pilih angka **1** lalu ketik **'-'** jika diminta nilai default).*

2. **Eksekusi Migrasi Database Default**  
   Simpan struktur tabel ke database default (`rs_pku`).

   ```bash
   python manage.py migrate
   ```

3. **Eksekusi Migrasi Database Kedua**  
   Simpan struktur tabel RawatInap ke database kedua (`rs_rekom`).

   ```bash
   python manage.py migrate main --database=database2
   ```

4. **Setup Database Kedua (Opsional)**  
   Jika database kedua belum ada, buat terlebih dahulu:

   ```bash
   python manage.py setup_database2
   ```

5. **Seeding (Inisialisasi) Akun Default**  
   Dapatkan data pancingan awal, terutama sistem peran atau akun _dummy_ bawaan proyek:
   ```bash
   python manage.py seed_users
   python manage.py seed_kasus
   python manage.py seed_rawat_inap
   python manage.py seed_dummy
   python manage.py seed_rekomendasi
   python manage.py seed_kasus_rekomendasi
   ```

#### Perintah Migrasi Database Kedua

Untuk operasi migrasi pada database kedua (`rs_rekom`), gunakan perintah berikut:

```bash
# Migrasi semua model main ke database2
python manage.py migrate main --database=database2

# Migrasi aplikasi tertentu
python manage.py migrate auth --database=database2

# Cek status migrasi database2
python manage.py showmigrations --database=database2

# Migrasi file spesifik
python manage.py migrate main 0003_create_rawat_inap_table --database=database2
```

#### Routing Database Otomatis

Sistem telah dikonfigurasi dengan database router yang otomatis mengarahkan:
- **RawatInap** → Database `rs_rekom` (database2)
- **User, Kasus, Rekomendasi, dll** → Database `rs_pku` (default)

Tidak perlu menentukan database secara manual saat menggunakan model, router akan mengatasi routing otomatis.

### 4. Menjalankan Server Lokal (Jalankan Projek)

Semuanya sudah siap! Sekarang hidupkan _built-in server_ Django:

```bash
python manage.py runserver
```

Buka web browser dan akses aplikasi melalui alamat:  
**http://127.0.0.1:8000/** atau **http://localhost:8000/**

---

## 🐳 Panduan Deployment Production via Docker Compose (VPS)

Untuk mendeploy aplikasi ini ke server VPS (Production), sangat disarankan menggunakan Docker Compose yang sudah disediakan.

### 1. Prasyarat Server
Pastikan VPS Anda sudah terinstall:
- **Docker**
- **Docker Compose**
- **Git** (untuk mengambil kode dari repositori)

### 2. Langkah Deployment Awal
1. Clone repository project ini ke dalam VPS Anda:
   ```bash
   git clone <URL_REPOSITORY_ANDA>
   cd projekta-1
   ```
2. Pastikan port `80` di VPS sudah dibuka (allow firewall) karena Nginx akan berjalan pada port tersebut.
3. Build dan jalankan container secara background (detached mode):
   ```bash
   docker compose up -d --build
   ```
4. **Selesai!** Aplikasi sudah berjalan dan bisa diakses melalui IP VPS atau domain yang Anda arahkan ke IP VPS. 
   > **Catatan:** Migrasi database (`migrate`), pengumpulan file statis (`collectstatic`), dan _seeding_ data awal (`seed_all`) akan dieksekusi secara **otomatis** oleh script `command` di dalam file `docker-compose.yml` saat container berjalan.

### 3. Cara Melakukan Update Kode di Production
Jika Anda melakukan perubahan kode di komputer lokal, melakukan *push* ke Git, dan ingin menerapkan pembaruan tersebut di VPS, lakukan langkah berikut:

1. Masuk ke direktori project di VPS:
   ```bash
   cd projekta-1
   ```
2. Tarik kode terbaru dari repository Git:
   ```bash
   git pull origin main
   ```
   *(Catatan: Sesuaikan `main` jika menggunakan branch yang berbeda)*
3. Build ulang image dan jalankan ulang container (tanpa menghapus data pada database):
   ```bash
   docker compose up -d --build
   ```
4. Docker Compose akan secara otomatis mendeteksi perubahan, mematikan container yang lama, melakukan build ulang (misalnya jika ada library baru di `requirements.txt`), menjalankan migrasi otomatis, dan menghidupkan container yang baru. Data database tetap aman karena menggunakan Docker Volume (`mysql_data` & `mysql2_data`).

---

_Proyek ini merupakan solusi terintegrasi untuk memaksimalkan efisiensi asuhan keperawatan dan administrasi kesehatan melalui indikator saintifik perumahsakitan._
