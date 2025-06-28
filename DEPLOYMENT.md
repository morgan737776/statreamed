# Deployment Guide for Rehab Center Application

## Server Requirements

- Ubuntu 20.04/22.04 LTS (recommended)
- Python 3.8+
- PostgreSQL 12+
- Redis (optional, for caching)
- Nginx
- Supervisor or Systemd (for process management)

## 1. Server Setup

1. Update system packages:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. Install required system packages:
   ```bash
   sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx git
   ```

## 2. Database Setup

1. Login to PostgreSQL:
   ```bash
   sudo -u postgres psql
   ```

2. Create database and user:
   ```sql
   CREATE DATABASE rehab_center;
   CREATE USER rehab_user WITH PASSWORD 'your_secure_password';
   ALTER ROLE rehab_user SET client_encoding TO 'utf8';
   ALTER ROLE rehab_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE rehab_user SET timezone TO 'UTC';
   GRANT ALL PRIVILEGES ON DATABASE rehab_center TO rehab_user;
   \q
   ```

## 3. Application Setup

1. Clone the repository:
   ```bash
   git clone <your-repository-url> /opt/rehab_center
   cd /opt/rehab_center
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements-prod.txt
   ```

4. Create .env file:
   ```bash
   cp .env.example .env
   nano .env  # Edit with your configuration
   ```

5. Apply migrations:
   ```bash
   python manage.py migrate --settings=rehab_center.settings_prod
   python manage.py collectstatic --noinput --settings=rehab_center.settings_prod
   python manage.py createsuperuser --settings=rehab_center.settings_prod
   ```

## 4. Gunicorn Setup

1. Create Gunicorn service file at `/etc/systemd/system/gunicorn.service`:
   ```ini
   [Unit]
   Description=gunicorn daemon
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/opt/rehab_center
   ExecStart=/opt/rehab_center/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn.sock rehab_center.wsgi:application --env DJANGO_SETTINGS_MODULE=rehab_center.settings_prod
   
   [Install]
   WantedBy=multi-user.target
   ```

2. Start and enable Gunicorn:
   ```bash
   sudo systemctl start gunicorn
   sudo systemctl enable gunicorn
   ```

## 5. Nginx Configuration

1. Create Nginx config at `/etc/nginx/sites-available/rehab_center`:
   ```nginx
   server {
       listen 80;
       server_name your_domain.com;

       location = /favicon.ico { access_log off; log_not_found off; }
       
       location /static/ {
           root /opt/rehab_center;
       }
       
       location /media/ {
           root /opt/rehab_center;
       }
       
       location / {
           include proxy_params;
           proxy_pass http://unix:/run/gunicorn.sock;
       }
   }
   ```

2. Enable the site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/rehab_center /etc/nginx/sites-enabled
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## 6. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

## 7. Firewall Setup

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow 'OpenSSH'
sudo ufw enable
```

## 8. Monitoring (Optional)

1. Install and configure monitoring tools like:
   - Sentry for error tracking
   - Prometheus + Grafana for system monitoring
   - Logrotate for log management

## 9. Backup Strategy

1. Set up regular database backups:
   ```bash
   # Add to crontab -e
   0 3 * * * pg_dump -U rehab_user -d rehab_center > /backups/rehab_center_$(date +\%Y\%m\%d).sql
   ```

## 10. Maintenance Commands

- Check application logs: `journalctl -u gunicorn -f`
- Check Nginx logs: `tail -f /var/log/nginx/error.log`
- Restart Gunicorn: `sudo systemctl restart gunicorn`
- Restart Nginx: `sudo systemctl restart nginx`

## Security Considerations

1. Keep system packages updated
2. Use strong passwords and SSH keys
3. Configure proper file permissions
4. Regularly backup your database
5. Monitor server resources and logs
6. Implement rate limiting for API endpoints
7. Regularly review and update dependencies
