# HandyConnect Configuration

This directory contains all configuration files organized by type.

## 📁 Configuration Structure

```
config/
├── README.md                    # This file - Configuration index
├── docker/                      # Docker configurations
│   ├── Dockerfile              # Main Docker configuration
│   ├── docker-compose.yml      # Production Docker Compose
│   └── docker-compose.dev.yml  # Development Docker Compose
├── nginx/                       # Nginx configuration
│   └── nginx.conf              # Reverse proxy configuration
└── environment/                 # Environment templates
    └── env.example             # Environment variables template
```

## 🐳 Docker Configuration

### [Dockerfile](docker/Dockerfile)
**Main Docker configuration**
- Python 3.11 slim base image
- Application dependencies
- Health checks
- Security hardening

### [docker-compose.yml](docker/docker-compose.yml)
**Production Docker Compose**
- Production environment setup
- Volume mounting for data persistence
- Health checks and restart policies
- Nginx reverse proxy integration

### [docker-compose.dev.yml](docker/docker-compose.dev.yml)
**Development Docker Compose**
- Development environment setup
- Volume mounting for live code changes
- Debug configuration
- Hot reload support

## 🌐 Nginx Configuration

### [nginx.conf](nginx/nginx.conf)
**Reverse proxy configuration**
- Upstream configuration for Flask app
- Security headers
- Health check endpoint
- SSL configuration (commented)

## ⚙️ Environment Configuration

### [env.example](environment/env.example)
**Environment variables template**
- Microsoft Graph API configuration
- OpenAI API configuration
- Flask configuration
- Data storage configuration
- Email polling configuration

## 🚀 Quick Setup

### 1. Copy Environment Template
```bash
cp config/environment/env.example .env
```

### 2. Configure Your Credentials
Edit `.env` with your actual credentials:
```env
# Microsoft Graph API Configuration
CLIENT_ID=your_azure_app_client_id
CLIENT_SECRET=your_azure_app_client_secret
TENANT_ID=your_azure_tenant_id

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Flask Configuration
SECRET_KEY=your_secret_key_here
```

### 3. Run with Docker
```bash
# Development
docker-compose -f config/docker/docker-compose.dev.yml up

# Production
docker-compose -f config/docker/docker-compose.yml up
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CLIENT_ID` | Azure App Client ID | Required |
| `CLIENT_SECRET` | Azure App Client Secret | Required |
| `TENANT_ID` | Azure Tenant ID | Required |
| `OPENAI_API_KEY` | OpenAI API Key | Required |
| `SECRET_KEY` | Flask Secret Key | Required |
| `DATA_DIR` | Data directory path | `data` |
| `TASKS_FILE` | Tasks JSON file path | `data/tasks.json` |
| `POLL_INTERVAL_MINUTES` | Email polling interval | `5` |
| `SUPPORT_EMAIL_FOLDER` | Outlook folder to monitor | `Inbox` |

### Docker Configuration

| Service | Port | Description |
|---------|------|-------------|
| `handyconnect` | 5000 | Main Flask application |
| `nginx` | 80/443 | Reverse proxy (production profile) |

### Nginx Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| `upstream` | `handyconnect:5000` | Flask app upstream |
| `listen` | `80` | HTTP port |
| `health_check` | `/health` | Health check endpoint |

## 🔒 Security Considerations

### Environment Security
- Never commit `.env` files to version control
- Use strong, unique secret keys
- Rotate API keys regularly
- Use environment-specific configurations

### Docker Security
- Run containers as non-root user
- Use minimal base images
- Regular security updates
- Network isolation

### Nginx Security
- Security headers enabled
- SSL/TLS configuration
- Rate limiting (can be added)
- Access logging

## 🚀 Deployment

### Development
```bash
# Using Makefile
make dev

# Direct Docker Compose
docker-compose -f config/docker/docker-compose.dev.yml up
```

### Production
```bash
# Using Makefile
make run

# Direct Docker Compose
docker-compose -f config/docker/docker-compose.yml up

# With Nginx
docker-compose --profile production up
```

## 🔧 Customization

### Adding New Environment Variables
1. Add to `config/environment/env.example`
2. Update application code to use the variable
3. Document the variable in this README
4. Update Docker configuration if needed

### Modifying Docker Configuration
1. Edit the relevant file in `config/docker/`
2. Test with `docker-compose build`
3. Update documentation
4. Commit changes

### Nginx Customization
1. Edit `config/nginx/nginx.conf`
2. Test configuration: `nginx -t`
3. Restart nginx service
4. Update documentation

---

**Last Updated**: $(date)
**Version**: 1.0.0





