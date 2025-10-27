# AWS Deployment Guide

This guide will help you deploy the Brand Loyalty API to an AWS EC2 free-tier instance.

## Prerequisites

1. AWS Account with free-tier eligibility
2. EC2 instance (t2.micro or t3.micro) running Ubuntu 22.04 LTS
3. Security group configured to allow:
   - SSH (port 22) from your IP
   - HTTP (port 8000) from anywhere (or specific IPs)

## Quick Deployment

### Step 1: Connect to Your EC2 Instance

```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### Step 2: Run the One-Command Deployment

```bash
curl -sSL https://raw.githubusercontent.com/akinmoroglu/brand-loyalty-api/main/deploy.sh | bash
```

Or manually:

```bash
# Clone the repository
git clone https://github.com/akinmoroglu/brand-loyalty-api.git
cd brand-loyalty-api

# Run deployment script
chmod +x deploy.sh
./deploy.sh
```

### Step 3: Verify Deployment

```bash
# Check service status
sudo systemctl status loyalty-api

# Check API health
curl http://localhost:8000/

# View logs
sudo journalctl -u loyalty-api -f
```

## Manual Deployment Steps

If you prefer manual control:

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git
```

### 2. Clone Repository

```bash
cd /home/ubuntu
git clone https://github.com/akinmoroglu/brand-loyalty-api.git
cd brand-loyalty-api
```

### 3. Setup Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Initialize Database

```bash
python seed_data.py
```

### 5. Test the Application

```bash
python main.py &
curl http://localhost:8000/
```

### 6. Create Systemd Service

```bash
sudo nano /etc/systemd/system/loyalty-api.service
```

Paste:

```ini
[Unit]
Description=Brand Loyalty API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/brand-loyalty-api
Environment="PATH=/home/ubuntu/brand-loyalty-api/venv/bin"
ExecStart=/home/ubuntu/brand-loyalty-api/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 7. Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable loyalty-api
sudo systemctl start loyalty-api
sudo systemctl status loyalty-api
```

## AWS Security Group Configuration

Your EC2 security group should have these inbound rules:

| Type | Protocol | Port | Source |
|------|----------|------|--------|
| SSH | TCP | 22 | Your IP |
| Custom TCP | TCP | 8000 | 0.0.0.0/0 (or specific IPs) |

## Accessing the API

Once deployed:

- **API Base URL**: `http://your-ec2-public-ip:8000`
- **API Documentation**: `http://your-ec2-public-ip:8000/docs`
- **Health Check**: `http://your-ec2-public-ip:8000/`

Example:
```bash
# From your local machine
curl http://your-ec2-public-ip:8000/

# List brands
curl http://your-ec2-public-ip:8000/brands

# Check customer
curl http://your-ec2-public-ip:8000/brands/brand-001/customers/by-phone/5551234567
```

## Service Management

```bash
# Start service
sudo systemctl start loyalty-api

# Stop service
sudo systemctl stop loyalty-api

# Restart service
sudo systemctl restart loyalty-api

# Check status
sudo systemctl status loyalty-api

# View logs (real-time)
sudo journalctl -u loyalty-api -f

# View last 50 lines of logs
sudo journalctl -u loyalty-api -n 50
```

## Updating the Application

```bash
cd /home/ubuntu/brand-loyalty-api
git pull
sudo systemctl restart loyalty-api
```

## Production Considerations

### 1. Use a Reverse Proxy (Nginx)

For production, use Nginx as a reverse proxy:

```bash
sudo apt install -y nginx

sudo nano /etc/nginx/sites-available/loyalty-api
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/loyalty-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 2. Enable HTTPS with Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. Setup Database Backups

```bash
# Create backup script
cat > /home/ubuntu/backup-db.sh << 'BACKUP'
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)
cp /home/ubuntu/brand-loyalty-api/loyalty.db $BACKUP_DIR/loyalty_$DATE.db
# Keep only last 7 days
find $BACKUP_DIR -name "loyalty_*.db" -mtime +7 -delete
BACKUP

chmod +x /home/ubuntu/backup-db.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /home/ubuntu/backup-db.sh") | crontab -
```

### 4. Enable API Key Authentication

Edit `app/core/config.py` and set:

```python
API_KEY_ENABLED = True
```

Then restart the service.

## Troubleshooting

### Port Already in Use

```bash
sudo lsof -i :8000
sudo kill -9 <PID>
sudo systemctl restart loyalty-api
```

### Permission Issues

```bash
sudo chown -R ubuntu:ubuntu /home/ubuntu/brand-loyalty-api
```

### Database Issues

```bash
cd /home/ubuntu/brand-loyalty-api
source venv/bin/activate
python seed_data.py
```

### View Full Logs

```bash
sudo journalctl -u loyalty-api --since today
```

## Free Tier Optimization

The t2.micro/t3.micro instances have limited resources:
- 1 vCPU
- 1 GB RAM
- SQLite is perfect for this (no extra database server needed)
- The API uses minimal resources (~100 MB RAM)

## Cost Estimation

With AWS Free Tier:
- EC2 t2.micro: 750 hours/month FREE (first 12 months)
- Data Transfer: 15 GB/month FREE
- EBS Storage: 30 GB FREE

**Expected monthly cost after free tier: $5-10/month**

## Support

For issues, check:
- GitHub Issues: https://github.com/akinmoroglu/brand-loyalty-api/issues
- API Logs: `sudo journalctl -u loyalty-api -f`
- System Logs: `/var/log/syslog`
