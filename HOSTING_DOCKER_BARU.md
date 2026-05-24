# 🚀 Panduan Lengkap Deploy Docker di VPS Baru (IP & Domain Berbeda)

Panduan ini menjelaskan langkah demi langkah untuk mendeploy aplikasi **Projekta** ke server VPS baru dengan **IP** dan **Domain** yang berbeda menggunakan Docker.

Aplikasi ini menggunakan arsitektur modern berbasis kontainer:
- **Django (Gunicorn)**: Sebagai application server.
- **MySQL 8.0**: Multi-database (`rs_pku` & `rs_rekom`).
- **Nginx**: Sebagai reverse proxy untuk mengarahkan lalu lintas dan melayani static files secara efisien.

---

## 📂 Bagian 1: Yang Harus Diubah di File Projek (Local Codebase)

Sebelum mengunggah kode ke server VPS baru, Anda perlu menyesuaikan beberapa nilai konfigurasi agar Django dan Nginx mengenali domain atau IP VPS baru Anda.

### 1. File `website/settings.py`
Kami telah memperbarui `settings.py` agar **`CSRF_TRUSTED_ORIGINS`** dapat dibaca secara dinamis melalui environment variable (`CSRF_TRUSTED_ORIGINS`) di file Docker Compose. Dengan begitu, Anda tidak perlu mengubah file kode Python setiap kali domain/IP berubah.

### 2. File `docker-compose.prod.yml`
Buka file `docker-compose.prod.yml` dan sesuaikan variabel lingkungan di bawah layanan `web`:
python -c "import secrets; print(secrets.token_urlsafe(50))"
jalankan di vps untuk membuat secret key baru
Buka file docker-compose.prod.yml Anda.
Ganti nilai setelah SECRET_KEY= dengan kunci acak baru tersebut.
```yaml
  web:
    ...
    environment:
      - DEBUG=False
      - SECRET_KEY=django-insecure-8k%z#2@!q9j3x$7r5w#1n4m6p8f2t%y&h*j@k=l+g9s3v7b # Ganti dengan secret key unik Anda
      - DB_HOST=db
      - DB_HOST2=db2
      - DB_USER=projekta_user
      - DB_PASSWORD=Projek_rekomendasi02 # Gunakan password database yang aman
      - DB_NAME=rs_pku
      - DB2_NAME=rs_rekom
      # ⚠️ UBAH DUA BARIS DI BAWAH INI SESUAI DOMAIN/IP BARU ANDA:
      - ALLOWED_HOSTS=domain-baru-anda.com,www.domain-baru-anda.com,IP_VPS_BARU
      - CSRF_TRUSTED_ORIGINS=https://domain-baru-anda.com,https://www.domain-baru-anda.com,http://localhost:8080
```

### 3. File `default.prod.conf`
Buka file konfigurasi Nginx production ini dan ubah `server_name` pada baris ke-3 menjadi domain baru Anda:

```nginx
server {
    listen 80;
    # ⚠️ UBAH ini menjadi domain baru atau IP VPS Anda:
    server_name domain-baru-anda.com www.domain-baru-anda.com; 
    ...
}
```

---

## 🖥️ Bagian 2: Persiapan di Server VPS Baru

Lakukan koneksi SSH ke VPS baru Anda dan jalankan perintah-perintah berikut untuk mempersiapkan sistem:

### 1. Update Paket Sistem
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Instal Docker & Docker Compose
Pasang Docker Engine dan Docker Compose plugin terbaru:
```bash
# Instal Docker
sudo apt install -y docker.io

# Jalankan & aktifkan Docker saat server booting
sudo systemctl start docker
sudo systemctl enable docker

# Pasang Docker Compose plugin
sudo apt install -y docker-compose-plugin

# Masukkan user Anda ke grup docker agar tidak perlu mengetik 'sudo' terus-menerus
sudo usermod -aG docker $USER
```
*(Catatan: Setelah menjalankan `usermod`, silakan log out dari SSH dan log in kembali agar perubahan grup berlaku).*

### 3. Konfigurasi Firewall (UFW)
Izinkan port penting agar aplikasi dapat diakses dari internet:
```bash
# Izinkan SSH (Sangat penting agar tidak terkunci!)
sudo ufw allow 22/tcp

# Izinkan HTTP (Port 80) & HTTPS (Port 443)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Izinkan port alternatif jika Anda menggunakannya (misalnya 8080)
sudo ufw allow 8080/tcp

# Aktifkan Firewall
sudo ufw enable
```

### 4. Clone Repository di VPS
```bash
git clone <URL_REPOSITORY_ANDA> projekta-1
cd projekta-1
git checkout rekomendasi
```

---

## 🌐 Bagian 3: Pilihan Arsitektur Hosting SSL (HTTPS)

Ada **dua metode terbaik** yang bisa Anda pilih untuk mengaktifkan HTTPS (SSL) pada VPS baru Anda:

### Opsi A: Menggunakan Cloudflare (Sangat Direkomendasikan & Paling Mudah ⭐️)
Metode ini menggunakan Cloudflare sebagai pelindung dan penyedia SSL otomatis, sehingga Nginx di Docker hanya perlu melayani HTTP di port `8080` tanpa perlu pusing mengurus instalasi sertifikat Let's Encrypt di VPS.

1. **Pengaturan DNS Cloudflare:**
   - Masuk ke dashboard Cloudflare Anda.
   - Arahkan domain Anda ke **IP VPS Baru** menggunakan `A Record` (Aktifkan opsi **Proxied** / awan oranye).
2. **Pengaturan SSL/TLS Cloudflare:**
   - Di dashboard Cloudflare, buka menu **SSL/TLS** -> **Overview**.
   - Ubah mode enkripsi menjadi **Flexible**.
3. **Menjalankan Container:**
   - Nginx di Docker akan menerima lalu lintas HTTP terenkripsi dari Cloudflare pada port `8080` (sesuai mapping `ports: - "8080:80"` di `docker-compose.prod.yml`).
   - Aplikasi Anda dapat langsung diakses dengan aman di: **`https://domain-baru-anda.com`**.

---

### Opsi B: Nginx Host VPS + Certbot (Standar & Mandiri)
Jika Anda tidak menggunakan Cloudflare dan ingin mengelola SSL Let's Encrypt secara langsung di server VPS Anda, arsitektur terbaik adalah memasang Nginx langsung di VPS host untuk menangani HTTPS (Port 443), kemudian meneruskan (proxy) lalu lintas ke Docker container yang berjalan di port `8080`.

1. **Instal Nginx & Certbot di VPS Host:**
   ```bash
   sudo apt install -y nginx certbot python3-certbot-nginx
   ```
2. **Buat Konfigurasi Nginx di VPS Host:**
   ```bash
   sudo nano /etc/nginx/sites-available/projekta
   ```
   Masukkan konfigurasi reverse proxy berikut:
   ```nginx
   server {
       listen 80;
       server_name domain-baru-anda.com www.domain-baru-anda.com;

       location / {
           proxy_pass http://127.0.0.1:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```
3. **Aktifkan Konfigurasi & Restart Nginx VPS:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/projekta /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```
4. **Dapatkan Sertifikat SSL Gratis dari Let's Encrypt:**
   Jalankan Certbot untuk mengubah konfigurasi otomatis menjadi HTTPS:
   ```bash
   sudo certbot --nginx -d domain-baru-anda.com -d www.domain-baru-anda.com
   ```
   Certbot akan otomatis membuat sertifikat SSL dan memperbarui file konfigurasi Nginx VPS Anda agar mendukung HTTPS di port 443 serta melakukan redirect otomatis dari HTTP ke HTTPS!

---

### Opsi C: Menggunakan IP VPS Langsung (Tanpa Domain / HTTP saja)
Jika Anda belum membeli domain dan hanya ingin mengakses aplikasi melalui IP VPS langsung untuk keperluan testing:

1. Di file `docker-compose.prod.yml`, atur:
   - `ALLOWED_HOSTS=IP_VPS_ANDA,localhost`
   - `CSRF_TRUSTED_ORIGINS=http://IP_VPS_ANDA:8080,http://localhost:8080`
2. Di file `default.prod.conf`, atur:
   - `server_name IP_VPS_ANDA;`
3. Jalankan container dan akses aplikasi di: **`http://IP_VPS_ANDA:8080`**.

---

## 🚀 Bagian 4: Cara Build & Menjalankan Aplikasi Pertama Kali

Setelah semua konfigurasi disesuaikan, jalankan aplikasi di VPS dengan langkah berikut:

### 1. Build dan Nyalakan Container
```bash
docker compose -f docker-compose.prod.yml up -d --build
```
> Perintah di atas akan:
> - Mengunduh base image MySQL dan Nginx.
> - Membangun container Django dari `Dockerfile`.
> - Melakukan **migrasi database otomatis** untuk database default (`rs_pku`) dan database kedua (`rs_rekom`).
> - Melakukan **seeding otomatis** untuk akun default, data kasus, dan rekomendasi melalui `seed_all` command.
> - Mengumpulkan seluruh static files (`collectstatic`).
> - Menjalankan server web dalam mode background (`-d`).

### 2. Memeriksa Status Container
Pastikan semua container berjalan dengan status `Up`:
```bash
docker compose -f docker-compose.prod.yml ps
```

### 3. Memantau Log Aplikasi (Bila terjadi kendala)
```bash
docker compose -f docker-compose.prod.yml logs -f web
```

---

## 🔄 Bagian 5: Cara Update Aplikasi di Masa Depan (CI/CD Manual)

Jika Anda melakukan perubahan kode di komputer lokal, kemudian melakukan push ke Git, ikuti langkah ini di VPS untuk memperbarui aplikasi tanpa merusak atau kehilangan data database yang sudah ada:

```bash
# 1. Masuk ke direktori projek
cd ~/projekta-1

# 2. Tarik kode terbaru dari Git
git pull origin rekomendasi

# 3. Build ulang image Django & restart container secara aman
docker compose -f docker-compose.prod.yml up -d --build
```
> **Keamanan Data Terjamin:**
> Data database Anda aman dan tidak akan hilang saat rebuild kontainer, karena data MySQL disimpan pada Docker Volume permanen di luar container (`mysql_data_prod` & `mysql2_data_prod`) yang telah dikonfigurasi di file `docker-compose.prod.yml`.
