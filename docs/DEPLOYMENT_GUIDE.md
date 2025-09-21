# Production Deployment Guide

## 🚀 Deployment Options

### Option 1: Docker Compose (Recommended)

#### Prerequisites
- Docker & Docker Compose installed
- 4GB+ RAM available
- SSL certificates (for HTTPS)

#### Quick Deployment

```bash
# 1. Clone and prepare
git clone https://github.com/codebasics/project-nlp-log-classification.git
cd project-nlp-log-classification

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings

# 3. Deploy
docker-compose up -d

# 4. Verify deployment
curl http://localhost:8000/api/v1/health
```

#### Production Deployment with NGINX

```bash
# Deploy with load balancer and SSL
docker-compose --profile production up -d

# Access via HTTPS
curl https://your-domain.com/api/v1/health
```

### Option 2: Manual Deployment

#### System Requirements
- Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- Python 3.8+
- 4GB RAM minimum, 8GB recommended
- 10GB disk space
- Internet connectivity

#### Installation Steps

```bash
# 1. Install system dependencies
sudo apt update && sudo apt install -y \
    python3 python3-pip python3-venv \
    nginx redis-server supervisor \
    build-essential curl

# 2. Create application user
sudo useradd --system --shell /bin/bash --home /opt/log-classifier log-classifier

# 3. Setup application
sudo -u log-classifier git clone \
    https://github.com/codebasics/project-nlp-log-classification.git \
    /opt/log-classifier/app

cd /opt/log-classifier/app

# 4. Create virtual environment
sudo -u log-classifier python3 -m venv venv
sudo -u log-classifier ./venv/bin/pip install -r requirements.txt

# 5. Configure environment
sudo -u log-classifier cp .env.example .env
sudo -u log-classifier nano .env  # Edit configuration

# 6. Set permissions
sudo chown -R log-classifier:log-classifier /opt/log-classifier
sudo chmod 755 /opt/log-classifier/app
```

### Option 3: Cloud Deployment

#### AWS ECS/Fargate

```yaml
# ecs-task-definition.json
{
  "family": "log-classifier",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "log-classifier",
      "image": "your-account.dkr.ecr.region.amazonaws.com/log-classifier:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "GROQ_API_KEY",
          "value": "your-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/log-classifier",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Google Cloud Run

```bash
# Build and deploy to Cloud Run
gcloud builds submit --tag gcr.io/PROJECT-ID/log-classifier
gcloud run deploy log-classifier \
    --image gcr.io/PROJECT-ID/log-classifier \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --port 8000
```

#### Azure Container Instances

```bash
# Deploy to Azure
az container create \
    --resource-group myResourceGroup \
    --name log-classifier \
    --image your-registry.azurecr.io/log-classifier:latest \
    --cpu 1 \
    --memory 2 \
    --restart-policy Always \
    --ports 8000 \
    --environment-variables GROQ_API_KEY=your-key
```

## ⚙️ Configuration

### Environment Variables

```bash
# Required
GROQ_API_KEY=your_groq_api_key_here

# Performance
MAX_FILE_SIZE_MB=10
BERT_MODEL_NAME=all-MiniLM-L6-v2
CACHE_TTL_SECONDS=3600

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
WORKERS=4

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,your-domain.com

# Database (optional)
REDIS_URL=redis://redis:6379/0
DATABASE_URL=postgresql://user:pass@host:5432/db
```

### Production Configuration

```python
# config/production.py
import os

class ProductionConfig:
    DEBUG = False
    TESTING = False
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY')
    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
    
    # Performance
    WORKERS = int(os.environ.get('WORKERS', 4))
    MAX_REQUESTS = 1000
    MAX_REQUESTS_JITTER = 100
    
    # Caching
    REDIS_URL = os.environ.get('REDIS_URL')
    CACHE_TTL = int(os.environ.get('CACHE_TTL_SECONDS', 3600))
    
    # Monitoring
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
```

## 🔒 Security Configuration

### Firewall Rules

```bash
# Allow HTTP/HTTPS only
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 8000/tcp  # Block direct API access
sudo ufw enable
```

### SSL/TLS Configuration

```bash
# Using Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# Manual certificate
sudo mkdir -p /etc/nginx/ssl
sudo cp your-certificate.crt /etc/nginx/ssl/cert.pem
sudo cp your-private-key.key /etc/nginx/ssl/key.pem
sudo chmod 600 /etc/nginx/ssl/key.pem
```

### Application Security

```python
# security.py
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
import jwt

security = HTTPBearer()

async def verify_token(request: Request, token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

## 📊 Monitoring & Observability

### Health Checks

```bash
# Application health
curl http://localhost:8000/api/v1/health

# Detailed system status
curl http://localhost:8000/api/v1/performance/stats/

# Docker health
docker-compose ps
docker-compose logs log-classifier
```

### Logging Configuration

```python
# logging.conf
[loggers]
keys=root,app

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter,jsonFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_app]
level=INFO
handlers=consoleHandler,fileHandler
qualname=app
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=jsonFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=jsonFormatter
args=('/var/log/log-classifier/app.log',)

[formatter_jsonFormatter]
format={"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "module": "%(module)s"}
```

### Metrics & Monitoring

#### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'log-classifier'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

#### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Log Classifier Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph", 
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

## 🔧 Maintenance & Operations

### Backup Strategy

```bash
#!/bin/bash
# backup.sh - Daily backup script

BACKUP_DIR="/backups/log-classifier"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# Backup application data
tar -czf "$BACKUP_DIR/$DATE/app-data.tar.gz" \
    /opt/log-classifier/app/cache \
    /opt/log-classifier/app/models \
    /opt/log-classifier/app/resources

# Backup configuration
cp /opt/log-classifier/app/.env "$BACKUP_DIR/$DATE/"
cp /etc/nginx/sites-available/log-classifier "$BACKUP_DIR/$DATE/"

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -type d -mtime +30 -exec rm -rf {} \;

echo "Backup completed: $BACKUP_DIR/$DATE"
```

### Update Procedure

```bash
#!/bin/bash
# update.sh - Rolling update script

echo "Starting update procedure..."

# 1. Backup current version
./backup.sh

# 2. Pull latest code
cd /opt/log-classifier/app
sudo -u log-classifier git pull origin main

# 3. Update dependencies
sudo -u log-classifier ./venv/bin/pip install -r requirements.txt

# 4. Run tests
sudo -u log-classifier ./venv/bin/python test_quick.py

# 5. Restart application
sudo systemctl restart log-classifier
sudo systemctl reload nginx

# 6. Verify deployment
sleep 10
curl -f http://localhost:8000/api/v1/health

echo "Update completed successfully!"
```

### Performance Tuning

#### System Optimization

```bash
# Increase file limits
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Optimize TCP settings
echo "net.core.somaxconn = 65536" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65536" >> /etc/sysctl.conf
sysctl -p
```

#### Application Tuning

```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
preload_app = True
keepalive = 65
```

## 🚨 Troubleshooting

### Common Issues

#### Memory Issues
```bash
# Check memory usage
free -h
docker stats

# Solution: Increase memory or optimize cache
export MAX_CACHE_SIZE=500
docker-compose restart
```

#### Performance Issues
```bash
# Monitor performance
curl http://localhost:8000/api/v1/performance/stats/

# Check slow queries
grep "slow operation" /var/log/log-classifier/app.log

# Solution: Clear cache and restart
curl -X POST http://localhost:8000/api/v1/performance/clear-cache/
```

#### Connection Issues
```bash
# Check service status
systemctl status log-classifier nginx

# Check ports
netstat -tlnp | grep :8000

# Check logs
journalctl -u log-classifier -f
```

### Emergency Procedures

#### Service Recovery
```bash
# Full service restart
docker-compose down && docker-compose up -d

# Database recovery (if using)
docker-compose exec postgres pg_restore /backup/database.sql

# Cache rebuild
curl -X POST http://localhost:8000/api/v1/performance/clear-cache/
```

## 📞 Support & Maintenance

### Monitoring Checklist
- [ ] Application health endpoint responding
- [ ] Error rates below 1%
- [ ] Response times under 500ms
- [ ] Memory usage below 80%
- [ ] Disk usage below 85%
- [ ] Cache hit rate above 70%

### Maintenance Schedule
- **Daily**: Health checks, log rotation
- **Weekly**: Performance review, backup verification
- **Monthly**: Security updates, dependency updates
- **Quarterly**: Capacity planning, disaster recovery testing

### Contact Information
- **Emergency**: ops-emergency@codebasics.io
- **Support**: support@codebasics.io
- **Documentation**: https://docs.codebasics.io/log-classifier