#!/bin/bash

# QFT Course Deployment Script
# Usage: ./deploy.sh

set -e  # Exit on error

PROJECT_DIR="/root/qftcourse"
VENV_DIR="$PROJECT_DIR/venv"
USER="www-data"
GROUP="www-data"
PORT=8000

echo "========================================="
echo "Starting deployment..."
echo "========================================="

# 1. Update code
echo "[1/4] Pulling latest code..."
cd $PROJECT_DIR
git pull origin main

# 2. Update dependencies
echo "[2/4] Updating dependencies..."
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. Initialize database if needed
echo "[3/4] Checking database..."
if [ ! -f instance/gauge_theory.db ]; then
    echo "Initializing database..."
    python init_data.py
fi

# 4. Restart services
echo "[4/4] Restarting services..."
systemctl restart gunicorn-qftcourse
systemctl reload nginx

echo ""
echo "========================================="
echo "Deployment completed successfully!"
echo "========================================="
echo "Website: http://150.158.103.51"
