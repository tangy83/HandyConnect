# HandyConnect - AWS Deployment Guide

**Complete guide for deploying HandyConnect to Amazon Web Services**

---

## 📋 Table of Contents

1. [Deployment Options Overview](#deployment-options-overview)
2. [Prerequisites](#prerequisites)
3. [Option 1: AWS EC2 (Recommended for Start)](#option-1-aws-ec2-recommended)
4. [Option 2: AWS Elastic Beanstalk (Easiest)](#option-2-aws-elastic-beanstalk)
5. [Option 3: AWS ECS with Fargate (Scalable)](#option-3-aws-ecs-with-fargate)
6. [Option 4: AWS App Runner (Simplest)](#option-4-aws-app-runner)
7. [Database & Storage Setup](#database--storage-setup)
8. [Environment Configuration](#environment-configuration)
9. [Security & Networking](#security--networking)
10. [Monitoring & Logging](#monitoring--logging)
11. [Cost Estimation](#cost-estimation)
12. [Troubleshooting](#troubleshooting)

---

## 🎯 Deployment Options Overview

| Option | Best For | Difficulty | Monthly Cost | Scalability |
|--------|----------|------------|--------------|-------------|
| **EC2** | Full control, custom setup | Medium | ~$10-50 | Manual |
| **Elastic Beanstalk** | Quick deployment, managed | Easy | ~$20-60 | Auto |
| **ECS Fargate** | Containerized, scalable | Medium-Hard | ~$30-100 | Auto |
| **App Runner** | Simplest, container-based | Very Easy | ~$25-75 | Auto |

### Recommended Approach: **AWS EC2 + Docker** 
- Full control over environment
- Cost-effective for small-medium workloads
- Easy to monitor and debug
- Scales vertically easily

---

## 📦 Prerequisites

### 1. AWS Account Setup
```bash
# Create AWS account at: https://aws.amazon.com/
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS CLI
aws configure
# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-east-1)
# - Default output format (json)
```

### 2. Required API Keys
- Microsoft Azure Client ID, Secret, Tenant ID (for email integration)
- OpenAI API Key (for AI processing)
- Generate a strong SECRET_KEY for Flask

### 3. Domain Name (Optional but Recommended)
- Register domain through Route 53 or external provider
- Configure DNS to point to AWS

---

## 🚀 Option 1: AWS EC2 (Recommended)

### Step 1: Launch EC2 Instance

1. **Log into AWS Console** → EC2 Dashboard

2. **Launch Instance**:
   ```
   Name: handyconnect-prod
   AMI: Ubuntu Server 22.04 LTS
   Instance Type: t3.small (2 vCPU, 2GB RAM) - $15/month
                  or t3.medium (2 vCPU, 4GB RAM) - $30/month
   Key Pair: Create new or use existing (save .pem file)
   ```

3. **Configure Network**:
   ```
   VPC: Default VPC
   Subnet: Public subnet
   Auto-assign Public IP: Enable
   ```

4. **Configure Security Group**:
   ```
   Name: handyconnect-sg
   
   Inbound Rules:
   - SSH (22) from My IP (for management)
   - HTTP (80) from Anywhere (0.0.0.0/0)
   - HTTPS (443) from Anywhere (0.0.0.0/0)
   - Custom TCP (5001) from Anywhere (for testing, remove in production)
   ```

5. **Configure Storage**:
   ```
   Root Volume: 20 GB GP3 SSD
   ```

6. **Launch Instance**

### Step 2: Connect to EC2 Instance

```bash
# Set permissions on your key file
chmod 400 your-key.pem

# Connect to instance
ssh -i your-key.pem ubuntu@<your-ec2-public-ip>
```

### Step 3: Install Dependencies on EC2

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu

# Install Git
sudo apt install -y git

# Install Nginx (for reverse proxy)
sudo apt install -y nginx

# Re-login to apply docker group
exit
# Then ssh back in
```

### Step 4: Deploy Application

```bash
# Clone your repository
cd /home/ubuntu
git clone https://github.com/tangy83/HandyConnect.git
cd HandyConnect

# Create .env file
nano .env
```

**Add your environment variables:**
```env
# Microsoft Graph API
CLIENT_ID=your_microsoft_client_id
CLIENT_SECRET=your_microsoft_client_secret
TENANT_ID=your_tenant_id

# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Flask Configuration
SECRET_KEY=your_strong_random_secret_key_here
FLASK_ENV=production

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Application
PORT=5001
HOST=0.0.0.0
```

```bash
# Save and exit (Ctrl+X, Y, Enter)

# Set proper permissions
chmod 600 .env

# Build and run with Docker
sudo docker-compose -f deployment/docker-compose.prod.yml up -d

# Or run without Docker
# Install Python dependencies
sudo apt install -y python3-pip python3-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with gunicorn
gunicorn -k eventlet -w 1 -b 0.0.0.0:5001 app:app --daemon
```

### Step 5: Configure Nginx as Reverse Proxy

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/handyconnect
```

**Add configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;  # or use EC2 public IP

    # Redirect HTTP to HTTPS (after SSL setup)
    # return 301 https://$server_name$request_uri;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files
    location /static {
        alias /home/ubuntu/HandyConnect/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/handyconnect /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### Step 6: Setup SSL with Let's Encrypt (Optional but Recommended)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Certbot will automatically configure HTTPS
# Follow the prompts

# Test auto-renewal
sudo certbot renew --dry-run
```

### Step 7: Setup Application as System Service

```bash
# Create systemd service file
sudo nano /etc/systemd/system/handyconnect.service
```

**Add service configuration:**
```ini
[Unit]
Description=HandyConnect Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/HandyConnect
Environment="PATH=/home/ubuntu/HandyConnect/venv/bin"
ExecStart=/home/ubuntu/HandyConnect/venv/bin/gunicorn -k eventlet -w 1 -b 0.0.0.0:5001 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable handyconnect
sudo systemctl start handyconnect

# Check status
sudo systemctl status handyconnect

# View logs
sudo journalctl -u handyconnect -f
```

### Step 8: Verify Deployment

```bash
# Test local access
curl http://localhost:5001/api/health

# Test external access (from your computer)
curl http://<your-ec2-public-ip>/api/health

# Or visit in browser
# http://<your-ec2-public-ip>
```

---

## 🎈 Option 2: AWS Elastic Beanstalk (Easiest)

### Step 1: Install EB CLI

```bash
# On your local machine
pip install awsebcli
```

### Step 2: Initialize Elastic Beanstalk Application

```bash
cd /path/to/HandyConnect

# Initialize EB application
eb init

# Follow prompts:
# - Select region
# - Create new application: HandyConnect
# - Platform: Python
# - Platform version: Python 3.11
# - Setup SSH: Yes
```

### Step 3: Create Configuration Files

Create `.ebextensions/01_packages.config`:
```yaml
packages:
  yum:
    git: []
    
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app:app
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current:$PYTHONPATH"
  aws:elasticbeanstalk:environment:proxy:
    ProxyServer: nginx
```

Create `.ebextensions/02_environment.config`:
```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    FLASK_ENV: production
    # Add other environment variables or use AWS Secrets Manager
```

### Step 4: Deploy to Elastic Beanstalk

```bash
# Create environment and deploy
eb create handyconnect-prod --instance-type t3.small

# This will:
# - Create environment
# - Deploy application
# - Setup load balancer
# - Configure auto-scaling

# Set environment variables
eb setenv CLIENT_ID=your_value CLIENT_SECRET=your_value OPENAI_API_KEY=your_value SECRET_KEY=your_value

# Open application in browser
eb open

# View logs
eb logs

# Check status
eb status
```

### Step 5: Configure HTTPS

```bash
# In AWS Console:
# 1. Go to Elastic Beanstalk → Your Environment
# 2. Configuration → Load Balancer
# 3. Add listener on port 443
# 4. Upload SSL certificate or use ACM certificate
```

---

## 🐳 Option 3: AWS ECS with Fargate (Scalable)

### Step 1: Create ECR Repository

```bash
# Create repository for Docker images
aws ecr create-repository --repository-name handyconnect

# Get login command
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
```

### Step 2: Build and Push Docker Image

```bash
cd /path/to/HandyConnect

# Build image
docker build -f deployment/Dockerfile.prod -t handyconnect:latest .

# Tag image
docker tag handyconnect:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/handyconnect:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/handyconnect:latest
```

### Step 3: Create ECS Task Definition

Create `ecs-task-definition.json`:
```json
{
  "family": "handyconnect",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "handyconnect",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/handyconnect:latest",
      "portMappings": [
        {
          "containerPort": 5001,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "FLASK_ENV",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "CLIENT_ID",
          "valueFrom": "arn:aws:secretsmanager:region:account-id:secret:handyconnect/client-id"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/handyconnect",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Step 4: Create ECS Cluster and Service

```bash
# Create cluster
aws ecs create-cluster --cluster-name handyconnect-cluster

# Register task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create service with load balancer
aws ecs create-service \
  --cluster handyconnect-cluster \
  --service-name handyconnect-service \
  --task-definition handyconnect \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=handyconnect,containerPort=5001"
```

---

## 🏃 Option 4: AWS App Runner (Simplest)

### Step 1: Prepare Source

```bash
# Ensure your code is in GitHub repository
# AWS App Runner will pull directly from GitHub
```

### Step 2: Create App Runner Service

1. **Go to AWS App Runner Console**
2. **Create Service**:
   ```
   Source: GitHub repository
   Repository: tangy83/HandyConnect
   Branch: main
   Deployment: Automatic
   
   Build Settings:
   - Runtime: Python 3.11
   - Build command: pip install -r requirements.txt
   - Start command: gunicorn -k eventlet -w 1 -b 0.0.0.0:8080 app:app
   
   Service Settings:
   - CPU: 1 vCPU
   - Memory: 2 GB
   - Port: 8080
   
   Environment Variables:
   - Add all your environment variables
   ```

3. **Create & Deploy**
   - App Runner will automatically build and deploy
   - Get the App Runner URL

---

## 💾 Database & Storage Setup

### Option A: Use RDS for PostgreSQL (Recommended for Production)

```bash
# Create RDS instance via AWS Console or CLI
aws rds create-db-instance \
  --db-instance-identifier handyconnect-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password your_password \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxx
```

Update your application to use PostgreSQL instead of JSON files.

### Option B: Use S3 for File Storage

```bash
# Create S3 bucket
aws s3 mb s3://handyconnect-data

# Update application to store tasks in S3 instead of local files
```

### Option C: Keep JSON Files (for testing)

For small deployments, you can keep JSON file storage:
```bash
# Ensure data directory persists
# Use EBS volumes on EC2 or EFS for ECS
```

---

## ⚙️ Environment Configuration

### Using AWS Systems Manager Parameter Store

```bash
# Store secrets securely
aws ssm put-parameter --name "/handyconnect/client-id" --value "your-value" --type "SecureString"
aws ssm put-parameter --name "/handyconnect/client-secret" --value "your-value" --type "SecureString"
aws ssm put-parameter --name "/handyconnect/openai-key" --value "your-value" --type "SecureString"
aws ssm put-parameter --name "/handyconnect/secret-key" --value "your-value" --type "SecureString"

# Retrieve in application
import boto3
ssm = boto3.client('ssm')
parameter = ssm.get_parameter(Name='/handyconnect/client-id', WithDecryption=True)
value = parameter['Parameter']['Value']
```

### Using AWS Secrets Manager

```bash
# Create secret
aws secretsmanager create-secret \
  --name handyconnect/credentials \
  --secret-string '{"CLIENT_ID":"xxx","CLIENT_SECRET":"xxx","OPENAI_API_KEY":"xxx"}'

# Retrieve in application
import boto3
import json
secrets = boto3.client('secretsmanager')
response = secrets.get_secret_value(SecretId='handyconnect/credentials')
credentials = json.loads(response['SecretString'])
```

---

## 🔒 Security & Networking

### 1. Security Group Configuration

```
Inbound Rules:
- Port 443 (HTTPS) from 0.0.0.0/0
- Port 80 (HTTP) from 0.0.0.0/0 (redirect to HTTPS)
- Port 22 (SSH) from Your IP only

Outbound Rules:
- All traffic to 0.0.0.0/0 (for API calls)
```

### 2. IAM Roles

Create IAM role for EC2/ECS with permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "ssm:GetParameter",
        "s3:GetObject",
        "s3:PutObject",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

### 3. VPC Configuration

- Use private subnets for application servers
- Use NAT Gateway for outbound internet access
- Use Application Load Balancer in public subnet

---

## 📊 Monitoring & Logging

### CloudWatch Setup

```bash
# Install CloudWatch agent on EC2
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure CloudWatch agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard

# View logs in CloudWatch Console
# Logs → Log groups → /aws/ec2/handyconnect
```

### Set up Alarms

```bash
# CPU Utilization alarm
aws cloudwatch put-metric-alarm \
  --alarm-name handyconnect-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

---

## 💰 Cost Estimation

### EC2 Deployment (Monthly)

| Resource | Specification | Cost |
|----------|--------------|------|
| EC2 Instance | t3.small | $15 |
| EBS Storage | 20 GB GP3 | $2 |
| Data Transfer | 50 GB/month | $5 |
| Elastic IP | 1 IP | $0 |
| **Total** | | **~$22/month** |

### Elastic Beanstalk (Monthly)

| Resource | Specification | Cost |
|----------|--------------|------|
| Load Balancer | ALB | $16 |
| EC2 Instance | t3.small | $15 |
| EBS Storage | 20 GB | $2 |
| **Total** | | **~$33/month** |

### ECS Fargate (Monthly)

| Resource | Specification | Cost |
|----------|--------------|------|
| Fargate | 0.5 vCPU, 1GB | $30 |
| Load Balancer | ALB | $16 |
| Data Transfer | 50 GB | $5 |
| **Total** | | **~$51/month** |

**Note**: Costs vary by region and usage. Add ~$10-20/month for RDS if used.

---

## 🔧 Troubleshooting

### Application won't start

```bash
# Check logs
sudo journalctl -u handyconnect -n 50

# Check if port is in use
sudo netstat -tulpn | grep 5001

# Verify environment variables
cat /home/ubuntu/HandyConnect/.env

# Test application manually
cd /home/ubuntu/HandyConnect
source venv/bin/activate
python app.py
```

### Can't connect to application

```bash
# Check if application is running
sudo systemctl status handyconnect

# Check Nginx status
sudo systemctl status nginx

# Test local connection
curl http://localhost:5001/api/health

# Check security group rules in AWS Console
# Ensure port 80/443 is open

# Check if Nginx is properly forwarding
sudo tail -f /var/log/nginx/error.log
```

### High memory usage

```bash
# Check memory usage
free -h

# Check application memory
ps aux | grep gunicorn

# Consider upgrading instance type or optimizing application
```

---

## 🚀 Quick Start Command Summary

```bash
# 1. Launch EC2 instance (via AWS Console)
# 2. Connect and setup
ssh -i your-key.pem ubuntu@<ec2-ip>
sudo apt update && sudo apt install -y docker.io git nginx
git clone https://github.com/tangy83/HandyConnect.git
cd HandyConnect

# 3. Configure environment
nano .env  # Add your credentials

# 4. Deploy
docker-compose -f deployment/docker-compose.prod.yml up -d

# 5. Setup Nginx
sudo cp deployment/nginx.conf /etc/nginx/sites-available/handyconnect
sudo ln -s /etc/nginx/sites-available/handyconnect /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# 6. Access application
# http://<your-ec2-ip>
```

---

## 📞 Next Steps

1. ✅ Choose deployment option (EC2 recommended)
2. ✅ Setup AWS account and configure CLI
3. ✅ Prepare environment variables and secrets
4. ✅ Follow deployment steps for chosen option
5. ✅ Configure domain and SSL
6. ✅ Setup monitoring and backups
7. ✅ Test application thoroughly
8. ✅ Go live!

---

**Need Help?** 
- AWS Documentation: https://docs.aws.amazon.com/
- HandyConnect Docs: See `docs/COMPLETE_PROJECT_GUIDE.md`
- Troubleshooting: See `docs/Troubleshooting.md`

---

*AWS Deployment Guide - HandyConnect v2.0*  
*Last Updated: October 1, 2025*

