# HandyConnect Deployment Guide

## 🚀 Production Deployment

This guide covers deploying HandyConnect in production environments with Docker, AWS, and manual deployment options.

---

## 📋 Prerequisites

### **System Requirements**
- Python 3.8+
- Docker & Docker Compose (recommended)
- 2GB RAM minimum, 4GB recommended
- 10GB disk space minimum
- Network access to Microsoft Graph API and OpenAI API

### **External Services**
- Microsoft Graph API access
- OpenAI API key
- Email account permissions

---

## 🐳 Docker Deployment (Recommended)

### **1. Docker Compose Setup**
```yaml
# docker-compose.yml
version: '3.8'

services:
  handyconnect:
    build: .
    ports:
      - "5000:5000"
    environment:
      - MICROSOFT_CLIENT_ID=${MICROSOFT_CLIENT_ID}
      - MICROSOFT_CLIENT_SECRET=${MICROSOFT_CLIENT_SECRET}
      - MICROSOFT_TENANT_ID=${MICROSOFT_TENANT_ID}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - FLASK_SECRET_KEY=${FLASK_SECRET_KEY}
      - FLASK_ENV=production
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### **2. Dockerfile**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p data logs

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run application
CMD ["python", "app.py"]
```

### **3. Environment Configuration**
```bash
# .env file
MICROSOFT_CLIENT_ID=your_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret
MICROSOFT_TENANT_ID=your_tenant_id
OPENAI_API_KEY=your_openai_key
FLASK_SECRET_KEY=your_secret_key
FLASK_ENV=production
LOG_LEVEL=INFO
```

### **4. Deployment Commands**
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Update application
docker-compose pull
docker-compose up -d
```

---

## ☁️ AWS Deployment

### **1. EC2 Instance Setup**
```bash
# Launch EC2 instance (Ubuntu 20.04 LTS)
# t3.medium or larger recommended

# Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu

# Clone repository
git clone <repository-url>
cd HandyConnect

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Deploy
docker-compose up -d
```

### **2. AWS Application Load Balancer**
```yaml
# alb-config.yml
resources:
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: handyconnect-alb
      Scheme: internet-facing
      Type: application
      Subnets:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2
      SecurityGroups:
        - !Ref ALBSecurityGroup

  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: handyconnect-targets
      Port: 5000
      Protocol: HTTP
      VpcId: !Ref VPC
      TargetType: instance
      HealthCheckPath: /health
      HealthCheckProtocol: HTTP
      HealthCheckIntervalSeconds: 30
      HealthCheckTimeoutSeconds: 5
      HealthyThresholdCount: 2
      UnhealthyThresholdCount: 3
```

### **3. Auto Scaling Group**
```yaml
# asg-config.yml
resources:
  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      LaunchTemplate:
        LaunchTemplateId: !Ref LaunchTemplate
        Version: !GetAtt LaunchTemplate.LatestVersionNumber
      MinSize: 1
      MaxSize: 10
      DesiredCapacity: 2
      TargetGroupARNs:
        - !Ref TargetGroup
      VPCZoneIdentifier:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
      HealthCheckType: ELB
      HealthCheckGracePeriod: 300
```

---

## 🔧 Manual Deployment

### **1. Server Setup**
```bash
# Ubuntu 20.04 LTS
sudo apt update
sudo apt upgrade -y

# Install Python 3.9
sudo apt install -y python3.9 python3.9-venv python3.9-dev

# Install system dependencies
sudo apt install -y curl git nginx supervisor

# Create application user
sudo useradd -m -s /bin/bash handyconnect
sudo usermod -aG sudo handyconnect
```

### **2. Application Installation**
```bash
# Switch to application user
sudo su - handyconnect

# Clone repository
git clone <repository-url>
cd HandyConnect

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Create directories
mkdir -p data logs

# Test application
python app.py
```

### **3. Nginx Configuration**
```nginx
# /etc/nginx/sites-available/handyconnect
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }
}
```

### **4. Supervisor Configuration**
```ini
# /etc/supervisor/conf.d/handyconnect.conf
[program:handyconnect]
command=/home/handyconnect/HandyConnect/venv/bin/python /home/handyconnect/HandyConnect/app.py
directory=/home/handyconnect/HandyConnect
user=handyconnect
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/handyconnect.log
environment=FLASK_ENV=production
```

### **5. SSL Certificate (Let's Encrypt)**
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 🔍 Health Monitoring

### **1. Health Check Endpoint**
```python
# app.py
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'services': {
            'database': check_database_health(),
            'microsoft_graph': check_microsoft_graph_health(),
            'openai': check_openai_health()
        }
    }
```

### **2. Monitoring Setup**
```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Create monitoring script
cat > /home/handyconnect/monitor.sh << 'EOF'
#!/bin/bash
echo "=== System Status $(date) ==="
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)"
echo "Memory Usage:"
free -h
echo "Disk Usage:"
df -h
echo "Application Status:"
curl -s http://localhost:5000/health | jq .
EOF

chmod +x /home/handyconnect/monitor.sh
```

### **3. Log Rotation**
```bash
# Configure logrotate
sudo cat > /etc/logrotate.d/handyconnect << 'EOF'
/var/log/handyconnect.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF
```

---

## 📊 Performance Tuning

### **1. Application Configuration**
```python
# config.py
class ProductionConfig:
    # Performance settings
    CACHE_TTL = 300  # 5 minutes
    MAX_CACHE_SIZE = 1000
    PERFORMANCE_MONITORING = True
    
    # Database settings
    DATABASE_POOL_SIZE = 10
    DATABASE_MAX_OVERFLOW = 20
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
```

### **2. System Optimization**
```bash
# Increase file limits
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize network settings
echo "net.core.somaxconn = 65536" | sudo tee -a /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65536" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### **3. Nginx Optimization**
```nginx
# /etc/nginx/nginx.conf
worker_processes auto;
worker_connections 1024;

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
}
```

---

## 🔐 Security Configuration

### **1. Firewall Setup**
```bash
# Configure UFW
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 5000/tcp  # Block direct access to Flask app
```

### **2. Application Security**
```python
# Security headers
@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

### **3. Environment Security**
```bash
# Secure environment file
chmod 600 .env
chown handyconnect:handyconnect .env

# Regular security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 📈 Scaling Considerations

### **1. Horizontal Scaling**
```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  handyconnect:
    image: handyconnect:latest
    deploy:
      replicas: 3
    environment:
      - FLASK_ENV=production
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      - nginx

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - handyconnect
```

### **2. Database Scaling**
```python
# Database connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### **3. Caching Strategy**
```python
# Redis caching
import redis
from flask_caching import Cache

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0'
})
```

---

## 🚨 Troubleshooting

### **Common Issues**

1. **Application Won't Start**
   ```bash
   # Check logs
   docker-compose logs handyconnect
   
   # Check environment variables
   docker-compose exec handyconnect env
   
   # Test database connection
   docker-compose exec handyconnect python -c "from app import app; print('OK')"
   ```

2. **Performance Issues**
   ```bash
   # Monitor system resources
   htop
   iotop
   nethogs
   
   # Check application metrics
   curl http://localhost:5000/health
   
   # Analyze logs
   tail -f /var/log/handyconnect.log
   ```

3. **SSL Certificate Issues**
   ```bash
   # Check certificate status
   sudo certbot certificates
   
   # Renew certificate
   sudo certbot renew --dry-run
   
   # Test SSL
   openssl s_client -connect your-domain.com:443
   ```

### **Emergency Procedures**

1. **Application Recovery**
   ```bash
   # Stop all services
   docker-compose down
   
   # Backup data
   cp -r data data.backup.$(date +%Y%m%d)
   
   # Restart services
   docker-compose up -d
   ```

2. **Database Recovery**
   ```bash
   # Backup database
   cp data/cases.json data/cases.json.backup.$(date +%Y%m%d)
   cp data/tasks.json data/tasks.json.backup.$(date +%Y%m%d)
   
   # Restore from backup
   cp data.backup.$(date +%Y%m%d)/cases.json data/cases.json
   ```

---

## 📋 Deployment Checklist

### **Pre-Deployment**
- [ ] Environment variables configured
- [ ] SSL certificates obtained
- [ ] Database backups completed
- [ ] Monitoring setup verified
- [ ] Security configuration reviewed

### **Deployment**
- [ ] Application deployed successfully
- [ ] Health checks passing
- [ ] SSL certificates working
- [ ] Monitoring active
- [ ] Performance metrics normal

### **Post-Deployment**
- [ ] User acceptance testing completed
- [ ] Documentation updated
- [ ] Team training completed
- [ ] Support procedures established
- [ ] Backup procedures verified

---

This deployment guide provides comprehensive instructions for deploying HandyConnect in production environments with proper monitoring, security, and scaling considerations.
