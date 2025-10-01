# HandyConnect Administrator Guide

## 🛠️ System Administration

This guide is designed for system administrators responsible for managing and maintaining the HandyConnect system.

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Installation & Setup](#installation--setup)
3. [User Management](#user-management)
4. [System Configuration](#system-configuration)
5. [Security Management](#security-management)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Backup & Recovery](#backup--recovery)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Configuration](#advanced-configuration)

---

## 🏗️ System Overview

### Architecture Components

HandyConnect consists of several key components:

- **Web Application**: Flask-based Python application
- **Database**: PostgreSQL for data storage
- **Cache**: Redis for session management and caching
- **Email Integration**: Microsoft Graph API
- **AI Processing**: OpenAI GPT for email analysis
- **Real-time Features**: WebSocket and Server-Sent Events
- **Monitoring**: Prometheus, Grafana, ELK Stack

### System Requirements

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 50GB SSD
- Network: 100 Mbps

**Recommended Requirements:**
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 100GB+ SSD
- Network: 1 Gbps

---

## 🚀 Installation & Setup

### Production Deployment

1. **Prepare the Environment**
   ```bash
   # Create deployment directory
   mkdir -p /opt/handyconnect
   cd /opt/handyconnect
   
   # Clone the repository
   git clone https://github.com/your-org/handyconnect.git .
   ```

2. **Configure Environment Variables**
   ```bash
   # Copy environment template
   cp config/environment/env.example .env
   
   # Edit configuration
   nano .env
   ```

3. **Deploy with Docker**
   ```bash
   # Start production services
   docker-compose -f deployment/docker-compose.prod.yml up -d
   
   # Check service status
   docker-compose -f deployment/docker-compose.prod.yml ps
   ```

4. **Initialize Database**
   ```bash
   # Run database migrations
   docker-compose -f deployment/docker-compose.prod.yml exec handyconnect python manage.py migrate
   
   # Create initial admin user
   docker-compose -f deployment/docker-compose.prod.yml exec handyconnect python manage.py create_admin
   ```

### SSL Certificate Setup

1. **Obtain SSL Certificate**
   ```bash
   # Using Let's Encrypt (recommended)
   certbot certonly --standalone -d yourdomain.com
   
   # Copy certificates to deployment directory
   cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem deployment/ssl/cert.pem
   cp /etc/letsencrypt/live/yourdomain.com/privkey.pem deployment/ssl/key.pem
   ```

2. **Configure Auto-Renewal**
   ```bash
   # Add to crontab
   echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
   ```

---

## 👥 User Management

### Creating Users

1. **Via Web Interface**
   - Login as administrator
   - Navigate to Admin → User Management
   - Click "Add New User"
   - Fill in user details and assign roles

2. **Via Command Line**
   ```bash
   # Create user with specific role
   docker-compose exec handyconnect python manage.py create_user \
     --username john.doe \
     --email john@company.com \
     --role support_agent \
     --send-invitation
   ```

### User Roles and Permissions

**System Administrator**
- Full system access
- User management
- System configuration
- Security settings

**Support Manager**
- Team management
- Task assignment
- Analytics access
- User training

**Support Agent**
- Task management
- Customer communication
- Basic reporting
- Personal settings

**Read-Only User**
- View tasks and reports
- No modification permissions
- Limited system access

### Managing User Sessions

1. **View Active Sessions**
   ```bash
   # Check active sessions
   docker-compose exec handyconnect python manage.py list_sessions
   ```

2. **Terminate User Sessions**
   ```bash
   # Terminate specific user session
   docker-compose exec handyconnect python manage.py terminate_session --user-id 123
   ```

---

## ⚙️ System Configuration

### Email Integration Settings

1. **Microsoft Graph API Configuration**
   ```yaml
   # In .env file
   CLIENT_ID=your_client_id
   CLIENT_SECRET=your_client_secret
   TENANT_ID=your_tenant_id
   EMAIL_POLL_INTERVAL=300  # 5 minutes
   ```

2. **Email Processing Rules**
   ```python
   # Configure in admin panel
   EMAIL_RULES = {
       'auto_categorize': True,
       'auto_priority': True,
       'auto_response': True,
       'business_hours_only': False
   }
   ```

### AI Configuration

1. **OpenAI Settings**
   ```yaml
   # In .env file
   OPENAI_API_KEY=your_openai_key
   OPENAI_MODEL=gpt-3.5-turbo
   AI_CONFIDENCE_THRESHOLD=0.8
   ```

2. **Custom AI Prompts**
   ```python
   # Customize AI behavior
   CUSTOM_PROMPTS = {
       'email_analysis': 'Your custom prompt here',
       'priority_detection': 'Your priority prompt here',
       'category_classification': 'Your category prompt here'
   }
   ```

### Performance Tuning

1. **Database Optimization**
   ```sql
   -- Create indexes for better performance
   CREATE INDEX idx_tasks_created_at ON tasks(created_at);
   CREATE INDEX idx_tasks_status ON tasks(status);
   CREATE INDEX idx_tasks_priority ON tasks(priority);
   ```

2. **Cache Configuration**
   ```yaml
   # Redis configuration
   REDIS_MAX_CONNECTIONS=100
   REDIS_TIMEOUT=30
   CACHE_TTL=3600  # 1 hour
   ```

---

## 🔒 Security Management

### Authentication & Authorization

1. **Password Policies**
   ```yaml
   # Configure password requirements
   PASSWORD_MIN_LENGTH=12
   PASSWORD_REQUIRE_UPPERCASE=true
   PASSWORD_REQUIRE_LOWERCASE=true
   PASSWORD_REQUIRE_NUMBERS=true
   PASSWORD_REQUIRE_SPECIAL=true
   PASSWORD_HISTORY_COUNT=5
   ```

2. **Session Management**
   ```yaml
   # Session security settings
   SESSION_TIMEOUT=1800  # 30 minutes
   MAX_LOGIN_ATTEMPTS=5
   LOCKOUT_DURATION=900  # 15 minutes
   ```

### Security Monitoring

1. **Enable Security Logging**
   ```python
   # Configure security event logging
   SECURITY_LOGGING = {
       'enabled': True,
       'log_level': 'WARNING',
       'retention_days': 90,
       'alert_thresholds': {
           'failed_logins': 10,
           'suspicious_activity': 5
       }
   }
   ```

2. **Review Security Events**
   ```bash
   # View recent security events
   docker-compose exec handyconnect python manage.py security_report
   ```

### Network Security

1. **Firewall Configuration**
   ```bash
   # Allow only necessary ports
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw allow 22/tcp
   ufw enable
   ```

2. **SSL/TLS Configuration**
   ```nginx
   # Strong SSL configuration in nginx.conf
   ssl_protocols TLSv1.2 TLSv1.3;
   ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
   ssl_prefer_server_ciphers off;
   ```

---

## 📊 Monitoring & Maintenance

### System Monitoring

1. **Health Checks**
   ```bash
   # Check system health
   curl http://localhost/health
   
   # Check database connectivity
   docker-compose exec postgres pg_isready
   
   # Check Redis connectivity
   docker-compose exec redis redis-cli ping
   ```

2. **Performance Monitoring**
   - Access Grafana dashboard at `http://yourdomain.com:3000`
   - Monitor key metrics:
     - Response times
     - Error rates
     - Resource usage
     - Task processing rates

### Log Management

1. **Centralized Logging**
   - Access Kibana at `http://yourdomain.com:5601`
   - View application logs, errors, and performance data
   - Set up log-based alerts

2. **Log Rotation**
   ```bash
   # Configure logrotate
   cat > /etc/logrotate.d/handyconnect << EOF
   /opt/handyconnect/logs/*.log {
       daily
       rotate 30
       compress
       delaycompress
       missingok
       notifempty
       create 644 appuser appuser
   }
   EOF
   ```

### Regular Maintenance

1. **Database Maintenance**
   ```bash
   # Weekly database maintenance
   docker-compose exec postgres psql -U postgres -d handyconnect -c "VACUUM ANALYZE;"
   
   # Monthly database backup verification
   docker-compose exec postgres psql -U postgres -d handyconnect -c "SELECT pg_database_size('handyconnect');"
   ```

2. **Application Updates**
   ```bash
   # Update application
   git pull origin main
   docker-compose -f deployment/docker-compose.prod.yml build
   docker-compose -f deployment/docker-compose.prod.yml up -d
   ```

---

## 💾 Backup & Recovery

### Automated Backups

1. **Database Backups**
   ```bash
   # Daily automated backup script
   cat > /opt/handyconnect/backup.sh << 'EOF'
   #!/bin/bash
   BACKUP_DIR="/opt/handyconnect/backups"
   DATE=$(date +%Y%m%d_%H%M%S)
   
   docker-compose exec -T postgres pg_dump -U postgres handyconnect > "$BACKUP_DIR/handyconnect_$DATE.sql"
   
   # Keep only last 30 days
   find $BACKUP_DIR -name "handyconnect_*.sql" -mtime +30 -delete
   EOF
   
   chmod +x /opt/handyconnect/backup.sh
   
   # Add to crontab for daily backup at 2 AM
   echo "0 2 * * * /opt/handyconnect/backup.sh" | crontab -
   ```

2. **File System Backups**
   ```bash
   # Backup application data and configuration
   tar -czf /opt/handyconnect/backups/app_data_$(date +%Y%m%d).tar.gz \
     /opt/handyconnect/data \
     /opt/handyconnect/config \
     /opt/handyconnect/ssl
   ```

### Recovery Procedures

1. **Database Recovery**
   ```bash
   # Restore from backup
   docker-compose exec -T postgres psql -U postgres -d handyconnect < backup_file.sql
   ```

2. **Full System Recovery**
   ```bash
   # Restore application data
   tar -xzf app_data_backup.tar.gz -C /
   
   # Restart services
   docker-compose -f deployment/docker-compose.prod.yml up -d
   ```

---

## 🔧 Troubleshooting

### Common Issues

**Service Won't Start**
```bash
# Check service logs
docker-compose -f deployment/docker-compose.prod.yml logs handyconnect

# Check resource usage
docker stats

# Restart services
docker-compose -f deployment/docker-compose.prod.yml restart
```

**Database Connection Issues**
```bash
# Check database status
docker-compose exec postgres pg_isready

# Check database logs
docker-compose logs postgres

# Reset database connection
docker-compose restart postgres
```

**Email Integration Problems**
```bash
# Test email connectivity
docker-compose exec handyconnect python -c "
import requests
response = requests.get('https://graph.microsoft.com/v1.0/me')
print(response.status_code)
"

# Check email service logs
docker-compose logs handyconnect | grep -i email
```

### Performance Issues

1. **Slow Response Times**
   - Check database query performance
   - Monitor resource usage
   - Review application logs for bottlenecks

2. **High Memory Usage**
   - Check for memory leaks
   - Adjust cache settings
   - Monitor Redis memory usage

3. **Database Performance**
   - Analyze slow queries
   - Add missing indexes
   - Consider query optimization

---

## 🎯 Advanced Configuration

### Custom Integrations

1. **API Endpoints**
   ```python
   # Add custom API endpoints
   @app.route('/api/custom/endpoint', methods=['GET'])
   def custom_endpoint():
       # Your custom logic here
       pass
   ```

2. **Webhook Configuration**
   ```python
   # Configure webhooks for external systems
   WEBHOOK_CONFIG = {
       'enabled': True,
       'url': 'https://external-system.com/webhook',
       'events': ['task_created', 'task_completed'],
       'retry_attempts': 3
   }
   ```

### Scaling Considerations

1. **Horizontal Scaling**
   - Use load balancer for multiple app instances
   - Configure database replication
   - Implement Redis clustering

2. **Performance Optimization**
   - Enable application-level caching
   - Optimize database queries
   - Use CDN for static assets

---

## 📞 Support & Resources

### Documentation
- [API Reference](API_REFERENCE.md)
- [Developer Guide](DEVELOPER_GUIDE.md)
- [User Training Materials](USER_TRAINING.md)

### Support Contacts
- **Technical Support**: admin-support@handyconnect.com
- **Emergency Support**: emergency@handyconnect.com
- **System Updates**: updates@handyconnect.com

### Community Resources
- [GitHub Repository](https://github.com/your-org/handyconnect)
- [Issue Tracker](https://github.com/your-org/handyconnect/issues)
- [Community Forum](https://community.handyconnect.com)

---

*Last Updated: December 30, 2024*  
*Version: 1.0*
