# Setup Database MySQL untuk Projekta

## 1. Install MySQL Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install MySQL server
sudo apt install mysql-server mysql-client -y

# Start dan enable MySQL
sudo systemctl start mysql
sudo systemctl enable mysql

# Secure MySQL installation
sudo mysql_secure_installation
```

## 2. Login ke MySQL

```bash
# Login sebagai root
sudo mysql -u root -p
```

## 3. Buat Database Sesuai settings.py

**Di MySQL prompt, jalankan perintah berikut:**

```sql
-- Buat database rs_pku
CREATE DATABASE rs_pku CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Buat database rs_rekom
CREATE DATABASE rs_rekom CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Cek database yang sudah dibuat
SHOW DATABASES;

-- Exit dari MySQL
EXIT;
```

## 4. Buat User Database (Opsional - Lebih Aman)

```sql
-- Buat user khusus untuk aplikasi
CREATE USER 'projekta_user'@'localhost' IDENTIFIED BY 'your_strong_password';

-- Grant privileges untuk kedua database
GRANT ALL PRIVILEGES ON rs_pku.* TO 'projekta_user'@'localhost';
GRANT ALL PRIVILEGES ON rs_rekom.* TO 'projekta_user'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

-- Exit
EXIT;
```

## 5. Update settings.py (jika menggunakan user baru)

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rs_pku',
        'USER': 'projekta_user',  # Ganti dari root
        'PASSWORD': 'your_strong_password',  # Password user
        'HOST': 'localhost',
        'PORT': '3306',
    },
    'database2': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rs_rekom',
        'USER': 'projekta_user',  # Ganti dari root
        'PASSWORD': 'your_strong_password',  # Password user
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

## 6. Install Python MySQL Connector

```bash
# Install development headers
sudo apt install python3-dev default-libmysqlclient-dev build-essential -y

# Install mysqlclient
pip install mysqlclient
```

## 7. Test Koneksi Database

```bash
# Test koneksi ke database1 (rs_pku)
python manage.py dbshell --database=default

# Test koneksi ke database2 (rs_rekom)
python manage.py dbshell --database=database2
```

## 8. Run Migrations

```bash
# Migrations untuk database default (rs_pku)
python manage.py migrate --database=default

# Migrations untuk database2 (rs_rekom) - jika ada
python manage.py migrate --database=database2

# Create superuser
python manage.py createsuperuser
```

## 9. Verify Database Setup

```bash
# Cek tabel di database rs_pku
mysql -u root -p rs_pku -e "SHOW TABLES;"

# Cek tabel di database rs_rekom
mysql -u root -p rs_rekom -e "SHOW TABLES;"

# Atau login ke MySQL dan cek manual
mysql -u root -p
USE rs_pku;
SHOW TABLES;
USE rs_rekom;
SHOW TABLES;
EXIT;
```

## 10. Database Router Configuration

Pastikan file `main/db_router.py` ada dan dikonfigurasi dengan benar:

```python
# main/db_router.py
class DatabaseRouter:
    def db_for_read(self, model, **hints):
        # Router untuk membaca dari database yang berbeda
        if hasattr(model, '_database'):
            return model._database
        return 'default'

    def db_for_write(self, model, **hints):
        # Router untuk menulis ke database yang berbeda
        if hasattr(model, '_database'):
            return model._database
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        # Allow relation jika kedua objek di database yang sama
        db_set = {'default', 'database2'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Allow migrasi untuk kedua database
        return True
```

## 11. Quick Setup Script

Buat file `setup_database.sh`:

```bash
#!/bin/bash

echo "Setting up MySQL databases for Projekta..."

# Login ke MySQL dan buat database
sudo mysql -u root << EOF
CREATE DATABASE IF NOT EXISTS rs_pku CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS rs_rekom CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'projekta_user'@'localhost' IDENTIFIED BY 'projekta123';
GRANT ALL PRIVILEGES ON rs_pku.* TO 'projekta_user'@'localhost';
GRANT ALL PRIVILEGES ON rs_rekom.* TO 'projekta_user'@'localhost';
FLUSH PRIVILEGES;
EOF

echo "Databases created successfully!"

# Install dependencies
pip install mysqlclient

# Run migrations
echo "Running migrations..."
python manage.py migrate --database=default
python manage.py migrate --database=database2

echo "Setup completed!"
```

```bash
# Make executable
chmod +x setup_database.sh

# Run script
./setup_database.sh
```

## 12. Troubleshooting

**Error "Access denied for user 'root'@'localhost'":**
```bash
# Reset MySQL root password
sudo systemctl stop mysql
sudo mysqld_safe --skip-grant-tables &
mysql -u root
UPDATE mysql.user SET authentication_string = PASSWORD('newpassword') WHERE User = 'root';
FLUSH PRIVILEGES;
EXIT;
sudo systemctl restart mysql
```

**Error "Can't connect to MySQL server":**
```bash
# Cek MySQL status
sudo systemctl status mysql

# Restart MySQL
sudo systemctl restart mysql

# Cek port
sudo netstat -tlnp | grep :3306
```

**Error "mysqlclient installation failed":**
```bash
# Install development headers
sudo apt install python3-dev default-libmysqlclient-dev build-essential -y

# Clean install
pip uninstall mysqlclient
pip install mysqlclient
```

**Error "Database doesn't exist":**
```bash
# Login ke MySQL
mysql -u root -p

# Buat database manual
CREATE DATABASE rs_pku;
CREATE DATABASE rs_rekom;

# Cek lagi
SHOW DATABASES;
```

## 13. Production Configuration

Untuk production, gunakan konfigurasi yang lebih aman:

```python
# settings.py production
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'rs_pku'),
        'USER': os.environ.get('DB_USER', 'projekta_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
    'database2': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB2_NAME', 'rs_rekom'),
        'USER': os.environ.get('DB_USER', 'projekta_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

---

**🎯 Database Setup Complete!**

Setelah mengikuti panduan ini:
- **Database rs_pku** - Untuk data utama aplikasi
- **Database rs_rekom** - Untuk data rekomendasi
- **User projekta_user** - Dengan privileges untuk kedua database
- **Migrations** - Sudah dijalankan untuk kedua database
- **Router** - Sudah dikonfigurasi untuk multi-database

**Database siap digunakan untuk aplikasi Projekta!**
