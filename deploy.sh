#!/bin/bash
# Deployment script for AWS EC2 (Ubuntu)

set -e  # Exit on error

echo "========================================="
echo "Brand Loyalty API - AWS Deployment"
echo "========================================="

# Update system
echo "1. Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install Python 3.9+ and pip
echo "2. Installing Python and dependencies..."
sudo apt install -y python3 python3-pip python3-venv git

# Clone or update repository
REPO_URL="https://github.com/akinmoroglu/brand-loyalty-api.git"
APP_DIR="/home/ubuntu/brand-loyalty-api"

if [ -d "$APP_DIR" ]; then
    echo "3. Updating existing repository..."
    cd "$APP_DIR"
    git pull
else
    echo "3. Cloning repository..."
    cd /home/ubuntu
    git clone "$REPO_URL"
    cd "$APP_DIR"
fi

# Create virtual environment
echo "4. Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "5. Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Initialize database
echo "6. Initializing database with seed data..."
python seed_data.py

# Create systemd service
echo "7. Creating systemd service..."
sudo tee /etc/systemd/system/loyalty-api.service > /dev/null <<SERVICE
[Unit]
Description=Brand Loyalty API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

# Reload systemd and start service
echo "8. Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable loyalty-api
sudo systemctl restart loyalty-api

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Service status:"
sudo systemctl status loyalty-api --no-pager
echo ""
echo "API should be running on http://localhost:8000"
echo "To check logs: sudo journalctl -u loyalty-api -f"
echo "To restart: sudo systemctl restart loyalty-api"
echo ""
