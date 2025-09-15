# HandyConnect Developer Setup Guide

## Prerequisites
- Python 3.8 or higher
- Git
- Docker (optional, for containerized development)
- Microsoft Azure account (for Outlook integration)
- OpenAI API key

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/tangy83/HandyConnect.git
cd HandyConnect
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
cp config/environment/env.example .env
```

Edit `.env` file with your configuration:
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

### 5. Create Required Directories
```bash
mkdir -p data logs
```

### 6. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Development Setup

### Running Tests
```bash
# Run all tests
python tests/run_tests.py

# Or using pytest
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_app.py

# Run specific test
pytest tests/test_app.py::TestHandyConnectApp::test_health_check
```

### Code Quality
```bash
# Install development dependencies
pip install flake8 black isort

# Format code
black .
isort .

# Lint code
flake8 .
```

### Docker Development
```bash
# Build and run with Docker Compose
docker-compose -f config/docker/docker-compose.dev.yml up --build

# Or using Makefile
make dev
```

## Project Structure

```
HandyConnect/
├── app.py                 # Main Flask application
├── email_service.py       # Microsoft Graph API integration
├── llm_service.py         # OpenAI integration
├── task_service.py        # Task management logic
├── requirements.txt       # Python dependencies
├── pytest.ini           # Pytest configuration
├── .env                  # Environment variables (create from env.example)
├── data/                 # JSON data storage
│   └── tasks.json       # Tasks data file
├── logs/                 # Application logs
├── tests/                # Test files
│   ├── test_app.py
│   ├── test_email_service.py
│   ├── test_llm_service.py
│   ├── test_task_service.py
│   └── run_tests.py
├── config/               # Configuration files
│   ├── docker/          # Docker configurations
│   ├── environment/     # Environment templates
│   └── nginx/           # Nginx configuration
├── docs/                 # Documentation
│   ├── api/             # API documentation
│   ├── guides/          # Setup and usage guides
│   └── roadmaps/        # Development roadmaps
├── features/             # Feature modules
│   ├── outlook_email_api/
│   ├── llm_prompt_design/
│   ├── task_structure_metadata/
│   ├── email_response_automation/
│   ├── lightweight_ui/
│   ├── performance_reporting/
│   └── case_id_generation/
├── static/               # Static files
│   ├── css/
│   └── js/
└── templates/            # HTML templates
    ├── base.html
    └── index.html
```

## API Endpoints

### Core Endpoints
- `GET /` - Main dashboard
- `GET /api/health` - Health check
- `GET /api/tasks` - Get all tasks (with filters)
- `GET /api/tasks/{id}` - Get specific task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `GET /api/tasks/stats` - Get task statistics
- `POST /api/poll-emails` - Manually poll emails

### Example API Usage
```python
import requests

# Get all tasks
response = requests.get('http://localhost:5000/api/tasks')
print(response.json())

# Update a task
update_data = {
    'status': 'In Progress',
    'assigned_to': 'Jane Smith'
}
response = requests.put(
    'http://localhost:5000/api/tasks/1',
    json=update_data
)
print(response.json())
```

## Configuration

### Environment Variables
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `CLIENT_ID` | Azure app client ID | Yes | - |
| `CLIENT_SECRET` | Azure app client secret | Yes | - |
| `TENANT_ID` | Azure tenant ID | Yes | - |
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `FLASK_ENV` | Flask environment | No | `development` |
| `SECRET_KEY` | Flask secret key | No | `dev-secret-key` |
| `POLL_INTERVAL_MINUTES` | Email polling interval | No | `5` |
| `SUPPORT_EMAIL_FOLDER` | Outlook folder to monitor | No | `Inbox` |

### Data Storage
The application uses JSON files for data storage:
- `data/tasks.json` - Main tasks data
- `data/tasks.json.backup` - Automatic backup file

## Troubleshooting

### Common Issues

1. **Configuration validation failed**
   - Check that all required environment variables are set
   - Verify Azure app registration and permissions
   - Ensure OpenAI API key is valid

2. **Email polling not working**
   - Verify Microsoft Graph API credentials
   - Check network connectivity
   - Review logs for specific error messages

3. **LLM processing errors**
   - Verify OpenAI API key and credits
   - Check API rate limits
   - Review error logs for specific issues

4. **Data storage issues**
   - Ensure `data/` directory exists and is writable
   - Check file permissions
   - Verify JSON file format

### Logs
Application logs are stored in the `logs/` directory:
- `logs/app.log` - Main application log
- Check logs for detailed error information

### Debug Mode
Run the application in debug mode for detailed error information:
```bash
export FLASK_ENV=development
python app.py
```

## Development Workflow

### 1. Feature Development
1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Implement your changes
3. Write tests for new functionality
4. Run tests: `python tests/run_tests.py`
5. Commit changes: `git commit -m "Add your feature"`
6. Push branch: `git push origin feature/your-feature-name`
7. Create pull request

### 2. Testing
- Write unit tests for new functions
- Test API endpoints manually or with automated tests
- Verify email processing and LLM integration
- Test error handling scenarios

### 3. Code Review
- Follow Python PEP 8 style guidelines
- Add docstrings to functions and classes
- Include error handling
- Write clear commit messages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For questions or issues:
1. Check the documentation in `docs/`
2. Review the roadmap in `docs/roadmaps/ROADMAP.md`
3. Check existing issues on GitHub
4. Create a new issue with detailed information

## Next Steps

1. Set up your development environment
2. Review the roadmap for your assigned tasks
3. Start implementing your features
4. Test thoroughly
5. Submit your work for review

