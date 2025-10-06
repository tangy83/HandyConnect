# HandyConnect

A Python-based MVP application that automatically converts customer support emails from Outlook into structured tasks, enriched using OpenAI's LLM capabilities, and displayed on a user-friendly frontend for internal teams.

## 🚀 Quick Start

```bash
# Clone and setup
git clone <your-repo-url>
cd HandyConnect

# Setup environment
cp config/environment/env.example .env
# Edit .env with your credentials

# Run with Docker (Recommended)
make dev

# Or run locally
python app.py
```

## 📁 Project Structure

```
HandyConnect/
├── README.md                    # This file - Project overview
├── app.py                      # Main Flask application
├── email_service.py            # Microsoft Graph API integration
├── llm_service.py              # OpenAI integration
├── task_service.py             # Task management logic
├── requirements.txt            # Python dependencies
├── docs/                       # 📚 Complete Documentation
│   ├── README.md               # Documentation index
│   ├── COMPLETE_PROJECT_GUIDE.md  # Comprehensive project guide
│   ├── QUICK_START_GUIDE.md    # User quick start
│   ├── ADMINISTRATOR_GUIDE.md  # Admin guide
│   ├── API_REFERENCE.md        # Complete API docs
│   └── [4 more guides]         # Testing, Git, Troubleshooting, etc.
├── config/                     # ⚙️ Configuration
│   ├── docker/                 # Docker configurations
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── docker-compose.dev.yml
│   ├── nginx/                  # Nginx configuration
│   │   └── nginx.conf
│   └── environment/            # Environment templates
│       └── env.example
├── scripts/                    # 🔧 Scripts and utilities
│   ├── setup/                  # Setup scripts
│   │   ├── start.sh
│   │   └── verify_setup.py
│   ├── deployment/             # Deployment scripts
│   └── utilities/              # Utility scripts
│       └── Makefile
├── auth/                       # 🔐 Authentication tools
│   ├── auth_display.py
│   ├── auth_web.py
│   ├── get_auth_code.py
│   └── show_auth_code.py
├── utilities/                  # 🛠️ Development utilities
│   ├── ci_health_check.py
│   ├── performance_optimizer.py
│   └── verify_email_account.py
├── testing/                    # 🧪 Test runners and tools
│   ├── simple_test_runner.py
│   ├── run_all_tests.py
│   └── integration_test.py
└── reports/                    # 📈 Reports and logs
    ├── health_check_report.md
    └── test_report_*.json
├── features/                   # 🏗️ Feature modules
│   ├── outlook_email_api/      # Email integration
│   ├── llm_prompt_design/      # AI prompt engineering
│   ├── task_structure_metadata/ # Task schema
│   ├── email_response_automation/ # Response automation
│   ├── lightweight_ui/         # UI components
│   ├── performance_reporting/  # Analytics
│   └── case_id_generation/     # ID management
├── templates/                  # 🎨 Frontend templates
│   ├── base.html
│   └── index.html
├── static/                     # 📱 Static assets
│   ├── css/style.css
│   └── js/app.js
├── tests/                      # 🧪 Test suites
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   ├── e2e/                    # End-to-end tests
│   ├── performance/            # Performance tests
│   └── features/               # Feature-specific tests
├── data/                       # 💾 Data storage (JSON)
└── logs/                       # 📝 Application logs
```

## 📚 Documentation

**All documentation is now in the [`docs/`](docs/) folder - clean, organized, and comprehensive!**

### 🎯 Start Here
- **[Complete Project Guide](docs/COMPLETE_PROJECT_GUIDE.md)** - Comprehensive guide covering everything about HandyConnect

### 👤 For Users
- **[Quick Start Guide](docs/QUICK_START_GUIDE.md)** - Get started in 5 minutes
- **[Troubleshooting](docs/Troubleshooting.md)** - Common issues and solutions

### 👨‍💼 For Administrators
- **[Administrator Guide](docs/ADMINISTRATOR_GUIDE.md)** - System administration and operations

### 👨‍💻 For Developers
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation (21+ endpoints)
- **[Test-Driven Development](docs/TEST_DRIVEN_DEVELOPMENT.md)** - Testing methodology
- **[Git Setup](docs/GIT_SETUP.md)** - Version control workflow
- **[Microsoft Graph Testing](docs/MICROSOFT_GRAPH_TESTING.md)** - Email integration testing

### 📖 Full Documentation Index
See **[docs/README.md](docs/README.md)** for the complete documentation index and navigation guide.

## 🚀 Features

- **Email Integration**: Automatically fetches emails from Outlook using Microsoft Graph API
- **AI-Powered Processing**: Uses OpenAI to categorize, summarize, and prioritize customer emails
- **Task Management**: Convert emails into structured tasks with status tracking
- **Modern UI**: Bootstrap-powered frontend for easy task management
- **Real-time Updates**: Background email polling with live task updates
- **Docker Support**: Fully containerized for easy deployment
- **JSON Storage**: Lightweight data storage for rapid development

## 👥 Development Team

| Developer | Primary Lane | Research Focus | Responsibilities |
|-----------|--------------|----------------|------------------|
| **Tanuj** | Backend & Integration | Email Processing & AI | Core backend, email integration, AI processing, APIs |
| **Swetha** | Frontend & UX | User Interface & Experience | UI/UX design, frontend development, user workflows |
| **Sunayana** | Data & Analytics | Data Management & Reporting | Data architecture, analytics, reporting, performance |

## 🛠️ Quick Commands

```bash
# Development
make dev                    # Start development environment
make build                  # Build Docker image
make test                   # Run tests
make clean                  # Clean up containers

# Setup
python scripts/setup/verify_setup.py  # Verify project setup
python scripts/setup/start.sh         # Start application

# Docker
docker-compose -f config/docker/docker-compose.dev.yml up  # Development
docker-compose -f config/docker/docker-compose.yml up      # Production
```

## 📋 Prerequisites

- Python 3.11+
- Docker and Docker Compose (for containerized deployment)
- Microsoft Azure App Registration (for Graph API access)
- OpenAI API key

## 🔧 Configuration

1. Copy environment template:
   ```bash
   cp config/environment/env.example .env
   ```

2. Configure your credentials in `.env`:
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

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test types
pytest tests/unit/           # Unit tests
pytest tests/integration/    # Integration tests
pytest tests/e2e/           # End-to-end tests
pytest tests/performance/   # Performance tests
```

## 🚀 Deployment

### Development
```bash
make dev
```

### Production
```bash
make run
```

### With Nginx
```bash
docker-compose --profile production up
```

## 📊 Success Metrics

- **Email Processing**: 95%+ successful email processing rate
- **AI Accuracy**: 85%+ classification accuracy
- **UI Performance**: < 2 seconds page load time
- **Data Integrity**: 99%+ data integrity
- **System Uptime**: 99.9%+ availability

## 🤝 Contributing

1. Choose your development lane based on research interests
2. Follow the [Roadmap](docs/roadmaps/ROADMAP.md)
3. Use Test-Driven Development (TDD) practices
4. Coordinate with other developers through daily standups
5. Follow the convergence strategy for integration

## 📞 Support

- **Documentation**: Check the `docs/` folder for detailed guides
- **Issues**: Create an issue in the repository
- **Development**: Follow the comprehensive roadmap
- **Deployment**: Check the deployment guides in `docs/deployment/`

---

**HandyConnect** - Streamlining customer support with AI-powered email processing 🚀