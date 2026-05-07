# Panduan Hosting Django Aplikasi Rumah Sakit

## 📋 Prasyarat Hosting

### 1. Requirements Sistem
- **Python**: 3.8+ (rekomendasi 3.9+)
- **Database**: PostgreSQL/MySQL/SQLite
- **RAM**: Minimal 1GB (rekomendasi 2GB+)
- **Storage**: Minimal 10GB
- **OS**: Linux (Ubuntu 20.04+ / CentOS 8+)

### 2. Dependencies
```bash
pip install -r requirements.txt
```

## 🔧 Persiapan Lokal

### 1. Update Settings Django
```python
# settings/production.py
import os
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 2. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 3. Create Requirements File
```bash
pip freeze > requirements.txt
```

## 🚀 Opsi Hosting

### Opsi 1: VPS/Cloud Server (Recommended)

#### Provider Recommendations:
- **DigitalOcean** (Droplets)
- **Linode** (Linodes)
- **Vultr** (Cloud Compute)
- **AWS EC2** (t2.micro atau lebih)

#### Setup Steps:

1. **Setup Server**
```bash
# Update server
sudo apt update && sudo apt upgrade -y

# Install Python & dependencies
sudo apt install python3-pip python3-venv postgresql postgresql-contrib nginx

# Clone project
git clone https://github.com/yourusername/projekta-1.git
cd projekta-1

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Setup Database**
```bash
# PostgreSQL
sudo -u postgres createdb rumahsakit_db
sudo -u postgres createuser rumahsakit_user
sudo -u postgres psql -c "ALTER USER rumahsakit_user PASSWORD 'yourpassword';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE rumahsakit_db TO rumahsakit_user;"
```

3. **Setup Gunicorn**
```bash
# Install gunicorn
pip install gunicorn

# Create gunicorn service
sudo nano /etc/systemd/system/gunicorn.service
```

```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/projekta-1
ExecStart=/path/to/projekta-1/venv/bin/gunicorn --workers 3 --bind unix:/path/to/projekta-1/gunicorn.sock website.wsgi:application

[Install]
WantedBy=multi-user.target
```

4. **Setup Nginx**
```bash
sudo nano /etc/nginx/sites-available/rumahsakit
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /path/to/projekta-1/staticfiles;
        expires max;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/path/to/projekta-1/gunicorn.sock;
        proxy_redirect off;
    }
}
```

5. **Enable Services**
```bash
# Enable gunicorn
sudo systemctl enable gunicorn
sudo systemctl start gunicorn

# Enable nginx
sudo ln -s /etc/nginx/sites-available/rumahsakit /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Opsi 2: PaaS (Platform as a Service)

#### Provider Recommendations:
- **Heroku** (Free tier available)
- **PythonAnywhere** (Django-friendly)
- **Railway** (Modern, simple)
- **Render** (Free tier available)

#### Setup Heroku Example:
```bash
# Install Heroku CLI
npm install -g heroku

# Login
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set DJANGO_SETTINGS_MODULE=website.settings.production
heroku config:set SECRET_KEY=your-secret-key

# Deploy
git push heroku main
```

### Opsi 3: Shared Hosting

#### Provider Recommendations:
- **Hostinger** (Business plan)
- **SiteGround** (GoGeek plan)
- **Bluehost** (Professional plan)

#### Requirements:
- Support Python 3.8+
- SSH access
- PostgreSQL/MySQL database
- .htaccess support

## 🔐 Security Setup

### 1. Environment Variables
```bash
# .env file
SECRET_KEY=your-very-secret-key-here
DB_NAME=rumahsakit_db
DB_USER=rumahsakit_user
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432
```

### 2. SSL Certificate (Let's Encrypt)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring & Maintenance

### 1. Logging Setup
```python
# settings/production.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/django.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### 2. Backup Strategy
```bash
# Database backup
0 2 * * * pg_dump rumahsakit_db > backup_$(date +\%Y\%m\%d).sql

# Files backup
0 3 * * * tar -czf backup_$(date +\%Y\%m\%d).tar.gz /path/to/projekta-1/
```

## 🚨 Troubleshooting

### Common Issues:
1. **500 Internal Server Error**
   - Check `ALLOWED_HOSTS` in settings
   - Verify database connection
   - Check error logs: `sudo journalctl -u gunicorn`

2. **Static Files Not Loading**
   - Run `collectstatic` command
   - Check Nginx static file configuration
   - Verify file permissions

3. **Database Connection Error**
   - Verify database credentials
   - Check if database server is running
   - Test connection manually

## 📱 Deployment Checklist

### Pre-deployment:
- [ ] Update Django to latest version
- [ ] Test all functionality locally
- [ ] Set DEBUG=False in production
- [ ] Configure proper database
- [ ] Set up environment variables
- [ ] Collect static files
- [ ] Test admin panel access

### Post-deployment:
- [ ] Test all user flows
- [ ] Verify file uploads work
- [ ] Check email functionality
- [ ] Test mobile responsiveness
- [ ] Monitor error logs
- [ ] Set up monitoring

## 💰 Cost Estimation

### VPS Monthly Costs:
- **DigitalOcean**: $5-20/month
- **Linode**: $5-20/month  
- **Vultr**: $3.5-20/month
- **AWS EC2**: $8-15/month

### PaaS Monthly Costs:
- **Heroku**: $7-25/month
- **PythonAnywhere**: $10-15/month
- **Railway**: $5-20/month
- **Render**: $7-25/month

## 🎯 Recommendations

### Untuk Production:
1. **Gunakan PostgreSQL** untuk production (lebih robust dari SQLite)
2. **Setup monitoring** (Sentry, New Relic, dll)
3. **Backup otomatis** harian
4. **Gunakan CDN** untuk static files
5. **Setup SSL** wajib untuk production
6. **Monitor performance** dengan APM tools

### Untuk Development:
1. **Gunakan environment variables** untuk sensitive data
2. **Version control dengan Git**
3. **Automated testing** (pytest)
4. **Code review sebelum deploy**
5. **Documentation** yang lengkap

---

## 📞 Support

Jika mengalami masalah saat deployment:
1. Cek error logs: `tail -f /var/log/nginx/error.log`
2. Restart services: `sudo systemctl restart gunicorn nginx`
3. Test database connection manual
4. Verify Django settings configuration

**Catatan**: Panduan ini bersifat umum. Sesuaikan dengan provider hosting yang Anda pilih.
