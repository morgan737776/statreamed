#!/bin/bash

# Exit on error
set -e

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Install required packages
echo "Installing required packages..."
apt update
apt install -y python3-pip python3-venv python3-dev libpq-dev nginx

# Create system user for running the application
if ! id -u www-data > /dev/null 2>&1; then
    useradd --system --no-create-home --shell /bin/false www-data
fi

# Create log directory
mkdir -p /var/log/gunicorn
chown -R www-data:www-data /var/log/gunicorn
chmod -R 755 /var/log/gunicorn

# Create application directory
APP_DIR="/opt/rehab_center"
mkdir -p $APP_DIR

# Copy application files
# Note: You should copy your application files to $APP_DIR
# For example:
# cp -r /path/to/your/app/* $APP_DIR/

# Set permissions
chown -R www-data:www-data $APP_DIR
chmod -R 755 $APP_DIR

# Install Python dependencies
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-prod.txt

# Set up Gunicorn service
cp $APP_DIR/gunicorn.service /etc/systemd/system/

# Enable and start Gunicorn
systemctl daemon-reload
systemctl enable gunicorn.service
systemctl start gunicorn.service

# Check Gunicorn status
systemctl status gunicorn.service

echo "Gunicorn setup complete!"
echo "Make sure to:"
echo "1. Copy your application files to $APP_DIR"
echo "2. Configure your .env file in $APP_DIR"
echo "3. Set up Nginx as a reverse proxy"
echo "4. Run migrations: python manage.py migrate --settings=rehab_center.settings_prod"
echo "5. Collect static files: python manage.py collectstatic --noinput --settings=rehab_center.settings_prod"
