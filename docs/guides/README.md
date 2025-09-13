# HandyConnect

A Python-based MVP application that automatically converts customer support emails from Outlook into structured tasks, enriched using OpenAI's LLM capabilities, and displayed on a user-friendly frontend for internal teams.

## 🚀 Features

- **Email Integration**: Automatically fetches emails from Outlook using Microsoft Graph API
- **AI-Powered Processing**: Uses OpenAI to categorize, summarize, and prioritize customer emails
- **Task Management**: Convert emails into structured tasks with status tracking
- **Modern UI**: Bootstrap-powered frontend for easy task management
- **Real-time Updates**: Background email polling with live task updates
- **Docker Support**: Fully containerized for easy deployment

## 📋 Prerequisites

- Python 3.11+
- Docker and Docker Compose (for containerized deployment)
- Microsoft Azure App Registration (for Graph API access)
- OpenAI API key

## 🛠 Setup Instructions

### 1. Clone and Setup Environment

```bash
git clone <your-repo-url>
cd HandyConnect
cp env.example .env
```

### 2. Configure Environment Variables

Edit the `.env` file with your credentials:

```env
# Microsoft Graph API Configuration
CLIENT_ID=your_azure_app_client_id
CLIENT_SECRET=your_azure_app_client_secret
TENANT_ID=your_azure_tenant_id
SCOPE=https://graph.microsoft.com/.default

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

# Data Storage Configuration
DATA_DIR=data
TASKS_FILE=data/tasks.json

# Email Polling Configuration
POLL_INTERVAL_MINUTES=5
SUPPORT_EMAIL_FOLDER=Inbox
```

### 3. Azure App Registration Setup

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to "Azure Active Directory" > "App registrations"
3. Click "New registration"
4. Configure:
   - Name: HandyConnect
   - Supported account types: Accounts in this organizational directory only
   - Redirect URI: Not needed for this app
5. After creation, note down:
   - Application (client) ID
   - Directory (tenant) ID
6. Go to "Certificates & secrets" > "New client secret"
7. Note down the client secret value
8. Go to "API permissions" > "Add a permission"
9. Select "Microsoft Graph" > "Application permissions"
10. Add these permissions:
    - Mail.Read
    - User.Read.All
11. Click "Grant admin consent"

## 🐳 Docker Deployment

### Development Environment

```bash
# Build and run in development mode
docker-compose -f docker-compose.dev.yml up --build

# Or run in background
docker-compose -f docker-compose.dev.yml up -d --build
```

### Production Environment

```bash
# Build and run in production mode
docker-compose up --build

# Run with nginx reverse proxy
docker-compose --profile production up --build
```

### Docker Commands

```bash
# Build only
docker build -t handyconnect .

# Run container directly
docker run -d \
  --name handyconnect \
  -p 5000:5000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  handyconnect

# View logs
docker-compose logs -f handyconnect

# Stop services
docker-compose down
```

## 🔧 Local Development

### Without Docker

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Run application
python app.py
```

The application will be available at `http://localhost:5000`

## 📁 Project Structure

```
HandyConnect/
├── app.py                 # Main Flask application
├── email_service.py       # Microsoft Graph API integration
├── llm_service.py         # OpenAI integration
├── task_service.py        # Task management logic
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Production Docker Compose
├── docker-compose.dev.yml # Development Docker Compose
├── nginx.conf            # Nginx configuration
├── start.sh              # Application startup script
├── env.example           # Environment variables template
├── features/             # Functional components (modular architecture)
│   ├── outlook_email_api/        # Microsoft Graph API integration
│   ├── llm_prompt_design/        # Prompt engineering and evaluation
│   ├── task_structure_metadata/  # Task schema and metadata
│   ├── email_response_automation/ # Automated email responses
│   ├── lightweight_ui/           # Performance-optimized UI
│   ├── performance_reporting/    # Analytics and reporting
│   └── case_id_generation/       # Unique ID generation
├── templates/            # Flask HTML templates
│   ├── base.html
│   └── index.html
├── static/               # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── data/                 # JSON data files (created at runtime)
└── logs/                 # Application logs (created at runtime)
```

## 🏗️ Modular Features Architecture

HandyConnect is built with a modular architecture that allows for progressive development of features:

### Core Features (Phase 1)
- **outlook_email_api**: Microsoft Graph API integration for email polling and management
- **llm_prompt_design**: AI prompt engineering and evaluation framework
- **task_structure_metadata**: Task schema definition and metadata management

### Enhanced Features (Phase 2)
- **email_response_automation**: Automated email response generation and sending
- **lightweight_ui**: Performance-optimized UI components and interfaces

### Advanced Features (Phase 3)
- **performance_reporting**: Comprehensive analytics and reporting capabilities
- **case_id_generation**: Advanced case ID generation and management strategies

Each feature module is independently developable and can be built progressively. See the [Features Overview](features/README.md) for detailed information about each component.

For detailed development planning and timelines, see the [Comprehensive Roadmap](ROADMAP.md) which includes both 2-week sprint and 12-phase detailed development approaches.

For team-specific development with Tanuj, Swetha, and Sunayana, see the [Developer-Specific Roadmap](DEVELOPER_ROADMAP.md) which outlines individual lanes, research topics, and convergence strategies.

## 🔄 How It Works

1. **Email Polling**: The application polls Outlook every 5 minutes (configurable) for new emails
2. **AI Processing**: Each email is processed by OpenAI to extract:
   - Summary of the customer's request
   - Category (Technical Issue, Billing, etc.)
   - Priority level (Low, Medium, High, Urgent)
   - Sentiment analysis
3. **Task Creation**: Processed emails become tasks in the database
4. **Task Management**: Team members can:
   - View all tasks in a dashboard
   - Update task status
   - Add notes and comments
   - Filter and search tasks
   - Assign tasks to team members

## 🎯 API Endpoints

- `GET /` - Main dashboard
- `GET /api/tasks` - Get all tasks
- `PUT /api/tasks/<id>` - Update task
- `DELETE /api/tasks/<id>` - Delete task
- `POST /api/poll-emails` - Manual email polling

## 🔐 Security Considerations

- All sensitive credentials should be stored in environment variables
- The application uses Flask's built-in security features
- Database is SQLite for simplicity (consider PostgreSQL for production)
- API endpoints should be protected with authentication in production

## 📈 Monitoring and Maintenance

### Health Checks

The application includes health check endpoints:
- Docker health check on port 5000
- Nginx health check on `/health`

### Logs

Logs are stored in the `logs/` directory and can be viewed with:

```bash
# Docker logs
docker-compose logs -f

# Local logs
tail -f logs/app.log
```

### Database Backup

```bash
# Backup SQLite database
cp data/handyconnect.db data/backup_$(date +%Y%m%d_%H%M%S).db

# In Docker
docker-compose exec handyconnect cp /app/data/handyconnect.db /app/data/backup.db
```

## 🚀 Production Deployment

### Recommended Setup

1. Use a proper web server (nginx) as reverse proxy
2. Set up SSL certificates
3. Use environment-specific configuration
4. Set up monitoring and alerting
5. Configure log rotation
6. Set up database backups

### Environment Variables for Production

```env
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@localhost/handyconnect  # Consider PostgreSQL
SECRET_KEY=your_very_secure_secret_key
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Authentication Errors**: Verify Azure app registration and permissions
2. **OpenAI API Errors**: Check API key and rate limits
3. **Email Not Polling**: Verify Graph API permissions and credentials
4. **Database Issues**: Ensure data directory has write permissions

### Debug Mode

Enable debug mode for detailed error messages:

```env
FLASK_ENV=development
FLASK_DEBUG=1
```

### Support

For issues and questions, please create an issue in the repository or contact the development team.

---

**HandyConnect** - Streamlining customer support with AI-powered email processing 🚀
