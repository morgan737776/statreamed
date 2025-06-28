import multiprocessing
import os

# Server socket
bind = 'unix:/run/gunicorn.sock'

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
max_requests = 2000
max_requests_jitter = 50
timeout = 120

# Security
user = 'www-data'
group = 'www-data'

# Logging
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
loglevel = 'info'
capture_output = True

# Server mechanics
pidfile = '/tmp/gunicorn.pid'
daemon = False

# Environment variables
raw_env = [
    'DJANGO_SETTINGS_MODULE=rehab_center.settings_prod',
]

# Server hooks
def on_starting(server):
    # Create log directory if it doesn't exist
    log_dir = '/var/log/gunicorn'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, mode=0o755)
        os.chown(log_dir, 0, 0)  # root:root

# Worker processes are forked from the master, so this code runs in each worker
def worker_int(worker):
    worker.log.info('Worker %s received SIGINT or SIGQUIT', worker.pid)

def worker_abort(worker):
    worker.log.warning('Worker %s received SIGABRT', worker.pid)
