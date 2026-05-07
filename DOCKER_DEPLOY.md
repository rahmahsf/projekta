# Docker Deployment Guide for Projekta

## Project Overview
- **Framework**: Django 4.2.7
- **Database**: MySQL 8.0 (Multi-database: rs_pku & rs_rekom)
- **Web Server**: Nginx
- **WSGI Server**: Gunicorn
- **Domain**: nasrulfahmi.my.id

## Quick Start

### 1. Clone and Build
```bash
git clone https://github.com/rahmahsf/projekta.git
cd projekta
git checkout rekomendasi
```

### 2. Update Django Settings for Docker
Edit `website/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'rs_pku'),
        'USER': os.environ.get('DB_USER', 'projekta_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'Projek_rekomendasi02'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    },
    'database2': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB2_NAME', 'rs_rekom'),
        'USER': os.environ.get('DB_USER', 'projekta_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'Projek_rekomendasi02'),
        'HOST': os.environ.get('DB_HOST2', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
}

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
```

### 3. Build and Run
```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Access Application
- **Main App**: http://nasrulfahmi.my.id
- **Admin**: http://nasrulfahmi.my.id/admin
- **Health Check**: http://nasrulfahmi.my.id/health

## Services Overview

### Database Services
- **db**: MySQL 8.0 for rs_pku database (port 3306)
- **db2**: MySQL 8.0 for rs_rekom database (port 3307)

### Web Service
- **web**: Django application with Gunicorn
- Auto-migrations on startup
- Auto-seed data on first run
- Static files collection

### Nginx Service
- **nginx**: Reverse proxy and SSL termination
- Serves static files
- HTTPS redirect
- Security headers

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `False` | Django debug mode |
| `SECRET_KEY` | - | Django secret key |
| `DB_HOST` | `db` | Primary database host |
| `DB_HOST2` | `db2` | Secondary database host |
| `DB_USER` | `projekta_user` | Database username |
| `DB_PASSWORD` | `Projek_rekomendasi02` | Database password |
| `DB_NAME` | `rs_pku` | Primary database name |
| `DB2_NAME` | `rs_rekom` | Secondary database name |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Django allowed hosts |

## SSL Setup

### Option 1: Self-signed (Development)
```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/self-signed.key \
    -out ssl/self-signed.crt \
    -subj "/C=ID/ST=State/L=City/O=Organization/CN=nasrulfahmi.my.id"

mkdir -p ssl
docker-compose up --build -d
```

### Option 2: Let's Encrypt (Production)
```bash
# Install certbot on host
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d nasrulfahmi.my.id -d www.nasrulfahmi.my.id

# Copy certificates to docker volume
sudo cp /etc/letsencrypt/live/nasrulfahmi.my.id/fullchain.pem ./ssl/self-signed.crt
sudo cp /etc/letsencrypt/live/nasrulfahmi.my.id/privkey.pem ./ssl/self-signed.key

# Restart nginx
docker-compose restart nginx
```

## Development Workflow

### 1. Make Changes
```bash
# Edit code
vim main/views.py

# Rebuild and restart
docker-compose up --build -d
```

### 2. Database Operations
```bash
# Access primary database
docker exec -it projekta_mysql mysql -u root -p

# Access secondary database
docker exec -it projekta_mysql2 mysql -u root -p

# Run Django commands
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py seed_users
```

### 3. Logs and Debugging
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f nginx

# Access container shell
docker-compose exec web bash
docker-compose exec db bash
```

## Production Deployment

### 1. Server Requirements
- **RAM**: Minimum 2GB
- **CPU**: Minimum 2 cores
- **Storage**: Minimum 20GB
- **OS**: Ubuntu 20.04+ or CentOS 7+

### 2. Install Docker
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose-plugin

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
```

### 3. Deploy Commands
```bash
# Clone repository
git clone https://github.com/rahmahsf/projekta.git
cd projekta
git checkout rekomendasi

# Set environment variables
cp .env.example .env
# Edit .env file with production values

# Build and deploy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

### 4. Production Compose File
Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  web:
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
    restart: always

  nginx:
    volumes:
      - ./nginx.prod.conf:/etc/nginx/conf.d/default.conf
      - /etc/letsencrypt:/etc/letsencrypt
    restart: always
```

## Monitoring and Maintenance

### 1. Health Checks
```bash
# Check service health
docker-compose ps

# Check application health
curl http://nasrulfahmi.my.id/health
```

### 2. Backup Database
```bash
# Backup primary database
docker exec projekta_mysql mysqldump -u root -p rs_pku > backup_rs_pku.sql

# Backup secondary database
docker exec projekta_mysql2 mysqldump -u root -p rs_rekom > backup_rs_rekom.sql
```

### 3. Update Application
```bash
# Pull latest changes
git pull origin rekomendasi

# Rebuild and restart
docker-compose up --build -d

# Run migrations if needed
docker-compose exec web python manage.py migrate
```

### 4. Performance Monitoring
```bash
# Monitor resource usage
docker stats

# Monitor logs
docker-compose logs -f --tail=100
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Error
```bash
# Check database status
docker-compose logs db

# Restart database
docker-compose restart db

# Check network connectivity
docker-compose exec web ping db
```

#### 2. Static Files 404
```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Restart nginx
docker-compose restart nginx
```

#### 3. Migration Issues
```bash
# Reset migrations
docker-compose exec web python manage.py migrate --fake-initial

# Run specific migration
docker-compose exec web python manage.py migrate main --database=database2
```

#### 4. SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in ssl/self-signed.crt -text -noout

# Regenerate certificate
rm ssl/self-signed.*
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/self-signed.key \
    -out ssl/self-signed.crt

# Restart nginx
docker-compose restart nginx
```

## Security Best Practices

1. **Change default passwords** in docker-compose.yml
2. **Use environment variables** for sensitive data
3. **Enable SSL** in production
4. **Regular updates** of Docker images
5. **Backup databases** regularly
6. **Monitor logs** for suspicious activity
7. **Use firewall** to restrict access

## Support

- **Documentation**: Check inline comments in docker-compose.yml
- **Logs**: Use `docker-compose logs` for debugging
- **Health Check**: Access `/health` endpoint
- **Admin Panel**: Access `/admin` for Django admin

---

**🚀 Ready to Deploy!**

This Docker setup provides:
- ✅ Multi-database MySQL support
- ✅ Nginx reverse proxy
- ✅ SSL termination
- ✅ Auto-migrations and seeding
- ✅ Static file serving
- ✅ Production-ready configuration
- ✅ Easy deployment and scaling
