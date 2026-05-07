# Panduan Deploy ke VPS dengan MySQL

## 1. Setup VPS

### Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python dan dependencies
sudo apt install python3 python3-pip python3-venv nginx mysql-server mysql-client libmysqlclient-dev -y

# Install Node.js (untuk build assets)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install build tools
sudo apt install build-essential -y
```

### Setup MySQL
```bash
# Secure MySQL installation
sudo mysql_secure_installation

# Login ke MySQL
sudo mysql -u root -p
```

**Di MySQL prompt:**
```sql
-- Buat database rs_pku (database utama)
CREATE DATABASE rs_pku CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Buat database rs_rekom (database rekomendasi)
CREATE DATABASE rs_rekom CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Buat user database
CREATE USER 'projekta_user'@'localhost' IDENTIFIED BY 'your_password';

-- Grant privileges untuk kedua database
GRANT ALL PRIVILEGES ON rs_pku.* TO 'projekta_user'@'localhost';
GRANT ALL PRIVILEGES ON rs_rekom.* TO 'projekta_user'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

-- Cek database yang sudah dibuat
SHOW DATABASES;

-- Exit
EXIT;
```

## 2. Clone Repository

```bash
# Clone dari GitHub
cd /var/www/
sudo git clone https://github.com/rahmahsf/projekta.git
cd projekta

# Switch ke branch rekomendasi
sudo git checkout rekomendasi

# Setup permissions
sudo chown -R $USER:$USER /var/www/projekta
```

## 3. Setup Python Environment

```bash
# Buat virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install MySQL connector untuk production
pip install mysqlclient gunicorn whitenoise
```

## 4. Update Django Settings untuk MySQL

**Edit settings.py:**
```python
# Ganti database configuration untuk multi-database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rs_pku',  # Database utama
        'USER': 'projekta_user',
        'PASSWORD': 'Projek_rekomendasi02',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
    'database2': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rs_rekom',  # Database rekomendasi
        'USER': 'projekta_user',
        'PASSWORD': 'Projek_rekomendasi02',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Database Router (sudah ada di settings.py)
DATABASE_ROUTERS = ['main.db_router.DatabaseRouter']
```

## 5. Setup Environment Variables

```bash
# Buat .env file
nano .env
```

**Isi .env:**
```env
DEBUG=False
SECRET_KEY=django-insecure-8k%z#2@!q9j3x$7r5w#1n4m6p8f2t%y&h*j@k=l+g9s3v7b
DB_NAME=rs_pku
DB2_NAME=rs_rekom
DB_USER=projekta_user
DB_PASSWORD=MyStr0ngPass123!
DB_HOST=localhost
DB_PORT=3306
ALLOWED_HOSTS=rsindikator.com,www.rsindikator.com,localhost,127.0.0.1
```

## 6. Database Migration

```bash
# Install mysqlclient jika error
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential -y
pip install pymysql
# Run migrations untuk kedua database
python manage.py makemigrations
python manage.py migrate --database=default  # Migrations untuk rs_pku
python manage.py migrate --database=database2  # Migrations untuk rs_rekom

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

## 7. Setup Gunicorn

```bash
# Buat gunicorn service file
sudo nano /etc/systemd/system/gunicorn.service
```

**Isi gunicorn.service:**
```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/projekta
ExecStart=/var/www/projekta/venv/bin/gunicorn --workers 3 --bind unix:/var/www/projekta/projekta.sock projekta.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Enable dan start gunicorn
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

## 8. Setup Nginx

```bash
# Buat nginx config
sudo nano /etc/nginx/sites-available/projekta
```

**Isi projekta:**
```nginx
server {
    listen 80;
    server_name your_domain.com www.your_domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/projekta;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/projekta/projekta.sock;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/projekta /etc/nginx/sites-enabled/

# Test dan restart nginx
sudo nginx -t
sudo systemctl restart nginx
```

## 9. Setup SSL (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your_domain.com -d www.your_domain.com

# Auto-renewal
sudo crontab -e
# Tambahkan: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 10. Setup Firewall

```bash
# Allow Nginx, SSH, dan MySQL
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw allow 3306  # MySQL (jika perlu remote access)
sudo ufw enable
```

## 11. Quick Deploy Script

Buat file `deploy_mysql.sh`:
```bash
#!/bin/bash

# Update dari GitHub
cd /var/www/projekta
git pull origin rekomendasi

# Install dependencies
source venv/bin/activate
pip install -r requirements.txt
pip install mysqlclient

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "Deploy with MySQL completed!"
```

```bash
# Make executable
chmod +x deploy_mysql.sh
```

## 12. MySQL Management Commands

**Backup Database:**
```bash
# Backup database rs_pku
mysqldump -u root -p rs_pku > rs_pku_backup.sql

# Backup database rs_rekom
mysqldump -u root -p rs_rekom > rs_rekom_backup.sql

# Backup dengan user
mysqldump -u projekta_user -p rs_pku > rs_pku_backup.sql
mysqldump -u projekta_user -p rs_rekom > rs_rekom_backup.sql

# Backup kedua database sekaligus
mysqldump -u root -p --databases rs_pku rs_rekom > projekta_full_backup.sql
```

**Restore Database:**
```bash
# Restore rs_pku
mysql -u root -p rs_pku < rs_pku_backup.sql

# Restore rs_rekom
mysql -u root -p rs_rekom < rs_rekom_backup.sql

# Restore dari full backup
mysql -u root -p < projekta_full_backup.sql
```

**Check Database:**
```bash
# Login ke MySQL
mysql -u projekta_user -p

# Cek database rs_pku
USE rs_pku;
SHOW TABLES;

# Cek database rs_rekom
USE rs_rekom;
SHOW TABLES;

# Cek semua database
SHOW DATABASES;

# Exit
EXIT;
```

## 13. Monitoring

```bash
# Cek status services
sudo systemctl status gunicorn
sudo systemctl status nginx
sudo systemctl status mysql

# Cek logs
sudo journalctl -u gunicorn
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/mysql/error.log
```

## 14. Testing

```bash
# Test aplikasi
curl http://localhost:8000

# Test domain
curl -I https://your_domain.com

# Test database connection
python manage.py dbshell --database=default  # rs_pku
python manage.py dbshell --database=database2  # rs_rekom
```

## Commands Summary

**Deploy pertama kali:**
```bash
cd /var/www/
git clone https://github.com/rahmahsf/projekta.git
cd projekta
git checkout rekomendasi
# ... setup environment dengan MySQL
```

**Update berikutnya:**
```bash
cd /var/www/projekta
git pull origin rekomendasi
./deploy_mysql.sh
```

## Troubleshooting MySQL

**Error mysqlclient installation:**
```bash
# Install development headers
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential -y

# Install mysqlclient
pip install mysqlclient
```

**Error connection refused:**
```bash
# Cek MySQL status
sudo systemctl status mysql

# Restart MySQL
sudo systemctl restart mysql

# Cek port
sudo netstat -tlnp | grep :3306
```

**Error access denied:**
```bash
# Reset password MySQL
sudo mysql -u root -p

ALTER USER 'projekta_user'@'localhost' IDENTIFIED BY 'new_password';
FLUSH PRIVILEGES;
```

**Error 2002 connection:**
```bash
# Cek MySQL socket
sudo ls -la /var/run/mysqld/

# Restart MySQL service
sudo systemctl restart mysql
```

## Security Tips untuk MySQL

1. **Remove anonymous users:**
```sql
DELETE FROM mysql.user WHERE User='';
```

2. **Remove remote root access:**
```sql
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
```

3. **Remove test database:**
```sql
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';
```

4. **Regular backups:**
```bash
# Auto backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u projekta_user -p projekta > /backup/projekta_$DATE.sql
```

## Requirements Update

**Update requirements.txt untuk MySQL:**
```txt
Django==4.2.7
mysqlclient==2.2.0
gunicorn==21.2.0
whitenoise==6.6.0
# ... dependencies lainnya
```

---

**🎯 Ready to Deploy with MySQL!**

Setelah mengikuti panduan ini, aplikasi Anda akan berjalan di:
- **HTTP**: http://your_domain.com
- **HTTPS**: https://your_domain.com (dengan SSL)
- **Admin**: https://your_domain.com/admin
- **Database**: MySQL 8.0

**Branch yang digunakan:** `rekomendasi` (dengan 3 grafik terpisah dan full fill)

**Keuntungan MySQL:**
- **Performance** lebih cepat untuk read-heavy applications
- **Compatibility** dengan banyak hosting providers
- **Scalability** yang sudah terbukti
- **Community support** yang besar
