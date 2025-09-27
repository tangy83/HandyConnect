from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import os
import json
import logging
from dotenv import load_dotenv
from features.core_services.email_service import EmailService
from features.core_services.llm_service import LLMService
from features.core_services.task_service import TaskService
from features.outlook_email_api.email_threading import EmailThreadingService
from features.outlook_email_api.thread_api import thread_bp
from features.outlook_email_api.graph_testing import graph_test_bp
from features.performance_reporting.analytics_api import create_analytics_api
from features.analytics.analytics_api import analytics_bp as new_analytics_bp
from features.analytics.analytics_framework import AnalyticsFramework, AnalyticsConfig
from features.analytics.performance_metrics import start_performance_monitoring
import threading
import time
from functools import wraps

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Configuration validation
def validate_config():
    """Validate required environment variables"""
    # Updated for device flow authentication
    required_vars = ['CLIENT_ID', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        return False
    
    logger.info("Configuration validation passed")
    return True

# Initialize services
try:
    email_service = EmailService()
    llm_service = LLMService()
    task_service = TaskService()
    threading_service = EmailThreadingService()
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
    raise

# Register thread API blueprint
app.register_blueprint(thread_bp)
app.register_blueprint(graph_test_bp)

# Register analytics API blueprint
analytics_bp = create_analytics_api()
app.register_blueprint(analytics_bp)

# Register new analytics API blueprint
app.register_blueprint(new_analytics_bp, name='new_analytics')

# JSON Data Storage
DATA_FILE = 'data/tasks.json'

def load_tasks():
    """Load tasks from JSON file with error handling"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                tasks = json.load(f)
                logger.info(f"Loaded {len(tasks)} tasks from {DATA_FILE}")
                return tasks
        logger.info("No tasks file found, returning empty list")
        return []
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading tasks: {e}")
        return []

def save_tasks(tasks):
    """Save tasks to JSON file with error handling and backup"""
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        
        # Create backup before saving
        if os.path.exists(DATA_FILE):
            backup_file = f"{DATA_FILE}.backup"
            with open(DATA_FILE, 'r') as src, open(backup_file, 'w') as dst:
                dst.write(src.read())
        
        with open(DATA_FILE, 'w') as f:
            json.dump(tasks, f, indent=2, default=str)
        
        logger.info(f"Saved {len(tasks)} tasks to {DATA_FILE}")
        return True
    except Exception as e:
        logger.error(f"Error saving tasks: {e}")
        return False

def get_next_id(tasks):
    """Get next available ID for new task"""
    if not tasks:
        return 1
    return max(task.get('id', 0) for task in tasks) + 1

# API Response Helpers
def success_response(data=None, message="Success", status_code=200):
    """Standard success response format"""
    response = {"status": "success", "message": message}
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code

def error_response(message="Error", status_code=400, details=None):
    """Standard error response format"""
    response = {"status": "error", "message": message}
    if details:
        response["details"] = details
    return jsonify(response), status_code

# API Decorators
def require_json(f):
    """Decorator to require JSON content type"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return error_response("Content-Type must be application/json", 400)
        return f(*args, **kwargs)
    return decorated_function

def handle_exceptions(f):
    """Decorator to handle exceptions gracefully"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {e}")
            return error_response("Internal server error", 500, str(e))
    return decorated_function

# Routes
@app.route('/')
def index():
    """Main dashboard page"""
    try:
        tasks = load_tasks()
        # Sort by created_at descending
        tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return render_template('index.html', tasks=tasks)
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return render_template('index.html', tasks=[], error="Failed to load tasks")

@app.route('/threads')
def threads():
    """Email threads page"""
    try:
        # For now, we'll create mock thread data
        # In a real implementation, this would come from the threading service
        threads = [
            {
                'id': 1,
                'subject': 'Account Access Issue',
                'summary': 'Customer unable to access their account',
                'status': 'Active',
                'priority': 'High',
                'message_count': 5,
                'participants': [
                    {'name': 'John Doe', 'email': 'john@example.com'},
                    {'name': 'Support Agent', 'email': 'support@company.com'}
                ],
                'created_at': '2025-09-20T10:00:00Z',
                'last_activity': '2025-09-20T13:30:00Z'
            },
            {
                'id': 2,
                'subject': 'Billing Question',
                'summary': 'Customer has questions about their recent bill',
                'status': 'Pending',
                'priority': 'Medium',
                'message_count': 3,
                'participants': [
                    {'name': 'Jane Smith', 'email': 'jane@example.com'},
                    {'name': 'Billing Team', 'email': 'billing@company.com'}
                ],
                'created_at': '2025-09-20T11:15:00Z',
                'last_activity': '2025-09-20T12:45:00Z'
            }
        ]
        return render_template('threads.html', threads=threads)
    except Exception as e:
        logger.error(f"Error in threads route: {e}")
        return render_template('threads.html', threads=[], error="Failed to load threads")

@app.route('/analytics')
def analytics():
    """Analytics dashboard page"""
    try:
        return render_template('analytics.html')
    except Exception as e:
        logger.error(f"Error in analytics route: {e}")
        return render_template('analytics.html', error="Failed to load analytics dashboard")

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return success_response({
        "service": "HandyConnect API",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    })

@app.route('/api/tasks')
@handle_exceptions
def get_tasks():
    """Get all tasks with optional filtering"""
    try:
        tasks = load_tasks()
        
        # Apply filters from query parameters
        status_filter = request.args.get('status')
        category_filter = request.args.get('category')
        priority_filter = request.args.get('priority')
        assigned_to_filter = request.args.get('assigned_to')
        
        if status_filter:
            tasks = [t for t in tasks if t.get('status') == status_filter]
        if category_filter:
            tasks = [t for t in tasks if t.get('category') == category_filter]
        if priority_filter:
            tasks = [t for t in tasks if t.get('priority') == priority_filter]
        if assigned_to_filter:
            tasks = [t for t in tasks if t.get('assigned_to') == assigned_to_filter]
        
        # Sort by created_at descending
        tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return success_response(tasks, f"Retrieved {len(tasks)} tasks")
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        return error_response("Failed to retrieve tasks", 500)

@app.route('/api/tasks/<int:task_id>')
@handle_exceptions
def get_task(task_id):
    """Get a specific task by ID"""
    tasks = load_tasks()
    task = next((t for t in tasks if t.get('id') == task_id), None)
    
    if not task:
        return error_response("Task not found", 404)
    
    return success_response(task, "Task retrieved successfully")

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@require_json
@handle_exceptions
def update_task(task_id):
    """Update a specific task"""
    tasks = load_tasks()
    task = next((t for t in tasks if t.get('id') == task_id), None)
    
    if not task:
        return error_response("Task not found", 404)
    
    data = request.get_json()
    
    # Update allowed fields
    allowed_fields = ['status', 'priority', 'assigned_to', 'notes', 'category']
    updated_fields = []
    
    for field in allowed_fields:
        if field in data:
            task[field] = data[field]
            updated_fields.append(field)
    
    task['updated_at'] = datetime.utcnow().isoformat()
    
    if save_tasks(tasks):
        return success_response(task, f"Task updated successfully. Fields updated: {', '.join(updated_fields)}")
    else:
        return error_response("Failed to save task updates", 500)

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@handle_exceptions
def delete_task(task_id):
    """Delete a specific task"""
    tasks = load_tasks()
    task = next((t for t in tasks if t.get('id') == task_id), None)
    
    if not task:
        return error_response("Task not found", 404)
    
    tasks.remove(task)
    
    if save_tasks(tasks):
        return success_response({"task_id": task_id}, "Task deleted successfully")
    else:
        return error_response("Failed to delete task", 500)

@app.route('/api/tasks/stats')
@handle_exceptions
def get_task_stats():
    """Get task statistics for dashboard"""
    try:
        stats = task_service.get_task_stats()
        return success_response(stats, "Task statistics retrieved successfully")
    except Exception as e:
        logger.error(f"Error getting task stats: {e}")
        return error_response("Failed to retrieve task statistics", 500)

@app.route('/api/poll-emails', methods=['POST'])
@handle_exceptions
def poll_emails():
    """Manually trigger email polling"""
    try:
        if not validate_config():
            return error_response("Configuration validation failed", 500)
        
        emails = email_service.get_emails()
        tasks = load_tasks()
        processed_count = 0
        errors = []
        
        for email in emails:
            try:
                # Check if email already exists
                existing_task = next((t for t in tasks if t.get('email_id') == email['id']), None)
                if existing_task:
                    continue
                
                # Create or update thread
                thread_id = threading_service.create_or_update_thread(email)
                thread = threading_service.get_thread(thread_id)
                
                # Process email with LLM
                llm_result = llm_service.process_email(email)
                
                # Create task with thread information
                task = {
                    'id': get_next_id(tasks),
                    'email_id': email['id'],
                    'thread_id': thread_id,
                    'subject': email['subject'],
                    'sender': email['sender']['name'],
                    'sender_email': email['sender']['email'],
                    'content': email['body'],
                    'summary': llm_result.get('summary'),
                    'category': llm_result.get('category'),
                    'priority': llm_result.get('priority', 'Medium'),
                    'status': 'New',
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat(),
                    'assigned_to': None,
                    'notes': None,
                    'sentiment': llm_result.get('sentiment', 'Neutral'),
                    'action_required': llm_result.get('action_required', 'Review and respond'),
                    'thread_info': {
                        'thread_id': thread_id,
                        'thread_status': thread.status,
                        'thread_priority': thread.priority,
                        'thread_category': thread.category,
                        'email_count': len(thread.emails),
                        'participants': list(thread.participants)
                    }
                }
                
                tasks.append(task)
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing email {email.get('id', 'unknown')}: {e}")
                errors.append(f"Email {email.get('id', 'unknown')}: {str(e)}")
        
        if save_tasks(tasks):
            response_data = {
                'processed_count': processed_count,
                'total_emails': len(emails),
                'errors': errors
            }
            return success_response(response_data, f"Processed {processed_count} new emails")
        else:
            return error_response("Failed to save processed tasks", 500)
    
    except Exception as e:
        logger.error(f"Error in poll_emails: {e}")
        return error_response("Failed to poll emails", 500)

def email_polling_worker():
    """Background worker for email polling"""
    logger.info("Email polling worker started")
    while True:
        try:
            if not validate_config():
                logger.warning("Configuration validation failed, skipping email poll")
                time.sleep(60)  # Wait 1 minute before retrying
                continue
            
            emails = email_service.get_emails()
            tasks = load_tasks()
            updated = False
            
            for email in emails:
                try:
                    existing_task = next((t for t in tasks if t.get('email_id') == email['id']), None)
                    if not existing_task:
                        # Create or update thread
                        thread_id = threading_service.create_or_update_thread(email)
                        thread = threading_service.get_thread(thread_id)
                        
                        llm_result = llm_service.process_email(email)
                        task = {
                            'id': get_next_id(tasks),
                            'email_id': email['id'],
                            'thread_id': thread_id,
                            'subject': email['subject'],
                            'sender': email['sender']['name'],
                            'sender_email': email['sender']['email'],
                            'content': email['body'],
                            'summary': llm_result.get('summary'),
                            'category': llm_result.get('category'),
                            'priority': llm_result.get('priority', 'Medium'),
                            'status': 'New',
                            'created_at': datetime.utcnow().isoformat(),
                            'updated_at': datetime.utcnow().isoformat(),
                            'assigned_to': None,
                            'notes': None,
                            'sentiment': llm_result.get('sentiment', 'Neutral'),
                            'action_required': llm_result.get('action_required', 'Review and respond'),
                            'thread_info': {
                                'thread_id': thread_id,
                                'thread_status': thread.status,
                                'thread_priority': thread.priority,
                                'thread_category': thread.category,
                                'email_count': len(thread.emails),
                                'participants': list(thread.participants)
                            }
                        }
                        tasks.append(task)
                        updated = True
                        logger.info(f"Created new task from email: {email['subject']} (Thread: {thread_id})")
                except Exception as e:
                    logger.error(f"Error processing email {email.get('id', 'unknown')} in worker: {e}")
            
            if updated:
                if save_tasks(tasks):
                    logger.info("Tasks updated successfully")
                else:
                    logger.error("Failed to save tasks in worker")
        except Exception as e:
            logger.error(f"Error in email polling worker: {e}")
        
        # Wait for the configured interval
        poll_interval = int(os.getenv('POLL_INTERVAL_MINUTES', 5)) * 60
        logger.info(f"Email polling worker sleeping for {poll_interval} seconds")
        time.sleep(poll_interval)

# Microsoft Graph API Testing Endpoints
@app.route('/api/test/graph-auth', methods=['POST'])
@handle_exceptions
def test_graph_authentication():
    """Test Microsoft Graph API authentication"""
    try:
        token = email_service.get_access_token()
        
        if token:
            return jsonify({
                "status": "success",
                "message": "Microsoft Graph authentication successful",
                "data": {
                    "token_acquired": True,
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "scope": " ".join(email_service.scopes)
                }
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Microsoft Graph authentication failed",
                "data": {
                    "error": "No access token received",
                    "details": "Check your CLIENT_ID, CLIENT_SECRET, and TENANT_ID"
                }
            }), 401
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Microsoft Graph authentication failed",
            "data": {
                "error": str(e),
                "details": "Check your Azure App Registration configuration"
            }
        }), 500

@app.route('/api/test/email-access', methods=['POST'])
@handle_exceptions
def test_email_access():
    """Test email access and permissions"""
    try:
        token = email_service.get_access_token()
        
        if not token:
            return jsonify({
                "status": "error",
                "message": "Authentication required",
                "data": {"error": "No access token available"}
            }), 401
        
        # Test email access
        emails = email_service.get_emails(folder='Inbox', top=5)
        
        if emails and len(emails) > 0:
            sample_email = emails[0] if emails else None
            return jsonify({
                "status": "success",
                "message": "Email access successful",
                "data": {
                    "emails_found": len(emails),
                    "sample_email": {
                        "subject": sample_email.get('subject', 'No subject'),
                        "from": sample_email.get('from', {}).get('emailAddress', {}).get('address', 'Unknown'),
                        "received": sample_email.get('receivedDateTime', 'Unknown')
                    } if sample_email else None,
                    "permissions": ["Mail.Read", "Mail.ReadWrite"]
                }
            })
        else:
            return jsonify({
                "status": "warning",
                "message": "Email access successful but no emails found",
                "data": {
                    "emails_found": 0,
                    "suggestion": "Check if the mailbox has emails or try a different folder"
                }
            })
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Email access failed",
            "data": {
                "error": str(e),
                "details": "Check your API permissions and mailbox access"
            }
        }), 500

@app.route('/api/test/configuration', methods=['GET'])
@handle_exceptions
def test_configuration():
    """Test configuration and environment variables"""
    try:
        config_status = {}
        
        # Check required environment variables
        required_vars = ['CLIENT_ID', 'CLIENT_SECRET', 'TENANT_ID', 'OPENAI_API_KEY', 'SECRET_KEY']
        
        for var in required_vars:
            value = os.getenv(var)
            if value and value != f"your_{var.lower()}_here" and not value.startswith("your_"):
                config_status[var] = "✅ Configured"
            else:
                config_status[var] = "❌ Not configured or using placeholder"
        
        # Check optional variables
        optional_vars = ['SCOPE', 'DATA_DIR', 'TASKS_FILE', 'POLL_INTERVAL_MINUTES']
        for var in optional_vars:
            value = os.getenv(var)
            if value:
                config_status[var] = f"✅ {value}"
            else:
                config_status[var] = f"⚠️ Using default"
        
        # Count configured variables
        configured_count = sum(1 for status in config_status.values() if status.startswith("✅"))
        total_count = len(config_status)
        
        # Check service status
        services_status = {
            "email_service": "✅ Available" if os.getenv('CLIENT_ID') else "❌ Not configured",
            "llm_service": "✅ Available" if os.getenv('OPENAI_API_KEY') else "❌ Not configured",
            "task_service": "✅ Available",
            "analytics_service": "✅ Available"
        }
        
        return jsonify({
            "status": "success",
            "message": f"Configuration check complete ({configured_count}/{total_count} configured)",
            "data": {
                "environment_variables": config_status,
                "services": services_status
            }
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Configuration check failed",
            "data": {"error": str(e)}
        }), 500

if __name__ == '__main__':
    # Ensure data and logs directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Validate configuration
    if not validate_config():
        logger.error("Configuration validation failed. Please check your environment variables.")
        exit(1)
    
    # Start email polling in background thread
    polling_thread = threading.Thread(target=email_polling_worker, daemon=True)
    polling_thread.start()
    
    # Initialize analytics framework
    try:
        analytics_config = AnalyticsConfig(
            collection_interval_seconds=60,
            aggregation_interval_minutes=15,
            retention_days=90,
            enable_real_time=True,
            enable_historical=True
        )
        analytics_framework = AnalyticsFramework(analytics_config)
        analytics_framework.start()
        logger.info("Analytics framework started")
        
        # Start performance monitoring
        start_performance_monitoring(interval_seconds=60)
        logger.info("Performance monitoring started")
        
    except Exception as e:
        logger.error(f"Failed to initialize analytics framework: {e}")
    
    logger.info("Application starting...")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
