from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import os
import json
import logging
from dotenv import load_dotenv
from features.core_services.email_service import EmailService
from features.core_services.llm_service import LLMService
from features.core_services.task_service import TaskService
from features.core_services.case_service import CaseService
from features.outlook_email_api.email_threading import EmailThreadingService
from features.outlook_email_api.thread_api import thread_bp
from features.outlook_email_api.graph_testing import graph_test_bp
from features.performance_reporting.analytics_api import create_analytics_api
from features.analytics.analytics_api import analytics_bp as new_analytics_bp
from features.analytics.analytics_framework import AnalyticsFramework, AnalyticsConfig
from features.case_management.case_api import case_bp
from features.case_management.case_analytics import case_analytics_bp
from features.case_management.task_api import task_bp
from features.analytics.performance_metrics import start_performance_monitoring
from features.analytics.realtime_dashboard import realtime_bp, get_realtime_broadcaster, get_realtime_collector
from features.analytics.websocket_manager import initialize_websocket_support, WEBSOCKET_AVAILABLE
import threading
import time
from functools import wraps

# Load environment variables
# Explicitly specify .env file path to ensure it's found
import pathlib
env_path = pathlib.Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

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
    case_service = CaseService()
    threading_service = EmailThreadingService()
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
    raise

# Register thread API blueprint
app.register_blueprint(thread_bp)
app.register_blueprint(graph_test_bp)

# Register case management blueprints
app.register_blueprint(case_bp)
app.register_blueprint(case_analytics_bp)
app.register_blueprint(task_bp)

# Register analytics API blueprint
analytics_bp = create_analytics_api()
app.register_blueprint(analytics_bp)

# Register new analytics API blueprint
app.register_blueprint(new_analytics_bp, name='new_analytics')

# Register real-time dashboard blueprint
app.register_blueprint(realtime_bp)

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

def migrate_existing_tasks_to_cases():
    """Migrate existing tasks to have case_id by creating cases for them"""
    try:
        tasks = load_tasks()
        if not tasks:
            logger.info("No existing tasks to migrate")
            return
        
        # Group tasks by customer email or thread_id
        task_groups = {}
        
        for task in tasks:
            # Skip if already has case_id
            if task.get('case_id'):
                continue
                
            # Group by customer email first, then by thread_id
            customer_email = task.get('sender_email', 'unknown@example.com')
            thread_id = task.get('thread_id', 'unknown')
            
            group_key = f"{customer_email}_{thread_id}"
            
            if group_key not in task_groups:
                task_groups[group_key] = {
                    'customer_email': customer_email,
                    'thread_id': thread_id,
                    'tasks': []
                }
            
            task_groups[group_key]['tasks'].append(task)
        
        # Create cases for each group
        cases_created = 0
        for group_key, group_data in task_groups.items():
            try:
                # Create a case for this group
                customer_email = group_data['customer_email']
                thread_id = group_data['thread_id']
                first_task = group_data['tasks'][0]
                
                # Create mock email data for case creation
                mock_email = {
                    'id': f"migrated_{first_task.get('email_id', 'unknown')}",
                    'subject': first_task.get('subject', 'Migrated Task'),
                    'sender': {
                        'name': first_task.get('sender', 'Unknown'),
                        'email': customer_email
                    },
                    'body': first_task.get('content', '')
                }
                
                # Create mock LLM result
                mock_llm_result = {
                    'summary': first_task.get('summary', 'Migrated from existing task'),
                    'category': first_task.get('category', 'General'),
                    'priority': first_task.get('priority', 'Medium'),
                    'sentiment': first_task.get('sentiment', 'Neutral'),
                    'action_required': first_task.get('action_required', 'Review and respond')
                }
                
                # Create case
                case = case_service.create_case_from_email(mock_email, thread_id, mock_llm_result)
                case_id = case['case_id']
                
                # Update all tasks in this group with case_id
                for task in group_data['tasks']:
                    task['case_id'] = case_id
                    # Add task to case
                    case_service.add_task_to_case(case_id, task['id'])
                
                cases_created += 1
                logger.info(f"Migrated {len(group_data['tasks'])} tasks to case {case['case_number']}")
                
            except Exception as e:
                logger.error(f"Error migrating task group {group_key}: {e}")
                continue
        
        # Save updated tasks
        if cases_created > 0:
            save_tasks(tasks)
            logger.info(f"Migration complete: {cases_created} cases created for existing tasks")
        
    except Exception as e:
        logger.error(f"Error during task migration: {e}")
        raise

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
    """Redirect to Cases page as the main dashboard"""
    return redirect(url_for('cases'))

@app.route('/tasks')
def tasks():
    """Tasks page"""
    try:
        tasks = load_tasks()
        
        # Enrich tasks with case_number
        from features.core_services.case_service import CaseService
        case_service = CaseService()
        cases = case_service.load_cases()
        
        # Create case_id to case_number mapping
        case_map = {c['case_id']: c['case_number'] for c in cases}
        
        # Add case_number to each task
        for task in tasks:
            if task.get('case_id'):
                task['case_number'] = case_map.get(task['case_id'], None)
        
        # Sort by created_at descending
        tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return render_template('index.html', tasks=tasks)
    except Exception as e:
        logger.error(f"Error in tasks route: {e}")
        return render_template('index.html', tasks=[], error="Failed to load tasks")

# Threads route removed - threads are now accessed via Communication tab in Case Detail modal
@app.route('/cases')
def cases():
    """Cases page"""
    try:
        cases = case_service.load_cases()
        return render_template('cases.html', cases=cases)
    except Exception as e:
        logger.error(f"Error in cases page: {e}")
        return render_template('cases.html', cases=[])

@app.route('/analytics')
def analytics():
    """Analytics dashboard page"""
    try:
        return render_template('analytics.html')
    except Exception as e:
        logger.error(f"Error in analytics route: {e}")
        return render_template('analytics.html', error="Failed to load analytics dashboard")

# Cache for main health check to improve performance
_health_cache = {}
_health_cache_timeout = 30  # seconds - longer cache for better performance

@app.route('/api/health')
def health_check():
    """Ultra-fast health check endpoint"""
    # Ultra-simple health check - no caching overhead, just return immediately
    return jsonify({
        "service": "HandyConnect API",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }), 200

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
                # Skip emails sent BY HandyConnect (acknowledgment emails, etc.)
                sender_email = email.get('sender', {}).get('email', '').lower()
                if 'handymyjob@outlook.com' in sender_email:
                    logger.info(f"Skipping self-sent email: {email.get('subject', 'No subject')}")
                    continue
                
                # Check if email already exists
                existing_task = next((t for t in tasks if t.get('email_id') == email['id']), None)
                if existing_task:
                    continue
                
                # Create or update thread
                thread_id = threading_service.create_or_update_thread(email)
                thread = threading_service.get_thread(thread_id)
                
                # Check if a task already exists for this thread (reply to existing conversation)
                thread_task = next((t for t in tasks if t.get('thread_id') == thread_id), None)
                
                if thread_task:
                    # Update existing task with new email info instead of creating new task
                    logger.info(f"Adding email to existing thread task: {thread_task['id']}")
                    thread_task['updated_at'] = datetime.utcnow().isoformat()
                    # Update thread info
                    if 'thread_info' in thread_task:
                        thread_task['thread_info']['email_count'] = len(thread.emails)
                        thread_task['thread_info']['participants'] = list(thread.participants)
                    # Add a note about the new reply
                    if not thread_task.get('notes'):
                        thread_task['notes'] = []
                    if isinstance(thread_task['notes'], str):
                        thread_task['notes'] = [thread_task['notes']]
                    thread_task['notes'].append(f"Reply received at {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}: {email.get('body', '')[:100]}")
                    
                    # Update case activity if case_id exists
                    if thread_task.get('case_id'):
                        case = case_service.get_case_by_id(thread_task['case_id'])
                        if case:
                            # Log inbound email to case threads
                            thread_data = {
                                'direction': 'Inbound',
                                'sender_name': email.get('sender', {}).get('name', 'Unknown'),
                                'sender_email': email.get('sender', {}).get('email', ''),
                                'subject': email.get('subject', 'No subject'),
                                'body': email.get('body', ''),
                                'timestamp': email.get('received_time', datetime.utcnow().isoformat()),
                                'message_id': email.get('id', '')
                            }
                            case_service.add_thread_to_case(thread_task['case_id'], thread_data)
                    
                    processed_count += 1
                    continue
                
                # Process email with LLM
                llm_result = llm_service.process_email(email)
                
                # Create or find case for this email/thread
                existing_case = case_service.find_case_by_thread(thread_id)
                if not existing_case:
                    # Try to find existing open case for this customer
                    customer_email = email['sender']['email']
                    existing_case = case_service.find_case_by_customer_email(customer_email)
                
                if existing_case:
                    # Use existing case
                    case_id = existing_case['case_id']
                    logger.info(f"Using existing case {existing_case['case_number']} for email {email['id']}")
                else:
                    # Create new case
                    case = case_service.create_case_from_email(email, thread_id, llm_result)
                    case_id = case['case_id']
                    logger.info(f"Created new case {case['case_number']} for email {email['id']}")
                
                # Create NEW task (first email in thread) with case_id using TaskService
                task_data = {
                    'case_id': case_id,  # NEW: Link to case
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
                    'assigned_to': None,
                    'notes': [],
                    'sentiment': llm_result.get('sentiment', 'Neutral'),
                    'action_required': llm_result.get('action_required', 'Review and respond'),
                    'created_by': 'system',
                    'thread_info': {
                        'thread_id': thread_id,
                        'thread_status': thread.status,
                        'thread_priority': thread.priority,
                        'thread_category': thread.category,
                        'email_count': len(thread.emails),
                        'participants': list(thread.participants)
                    }
                }
                
                # Create task using TaskService
                from features.core_services.task_service import TaskService
                task_service = TaskService()
                task = task_service.create_task(task_data)
                
                # Add task to case
                case_service.add_task_to_case(case_id, task['id'])
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
                    # Skip emails sent BY HandyConnect (acknowledgment emails, etc.)
                    sender_email = email.get('sender', {}).get('email', '').lower()
                    if 'handymyjob@outlook.com' in sender_email:
                        logger.info(f"[Worker] Skipping self-sent email: {email.get('subject', 'No subject')}")
                        continue
                    
                    existing_task = next((t for t in tasks if t.get('email_id') == email['id']), None)
                    if existing_task:
                        continue
                        
                    # Create or update thread
                    thread_id = threading_service.create_or_update_thread(email)
                    thread = threading_service.get_thread(thread_id)
                    
                    # Check if a task already exists for this thread (reply to existing conversation)
                    thread_task = next((t for t in tasks if t.get('thread_id') == thread_id), None)
                    
                    if thread_task:
                        # Update existing task instead of creating new one
                        logger.info(f"Adding email to existing thread task: {thread_task['id']}")
                        thread_task['updated_at'] = datetime.utcnow().isoformat()
                        if 'thread_info' in thread_task:
                            thread_task['thread_info']['email_count'] = len(thread.emails)
                            thread_task['thread_info']['participants'] = list(thread.participants)
                        if not thread_task.get('notes'):
                            thread_task['notes'] = []
                        if isinstance(thread_task['notes'], str):
                            thread_task['notes'] = [thread_task['notes']]
                        thread_task['notes'].append(f"Reply received at {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}: {email.get('body', '')[:100]}")
                        
                        # Update case activity if case_id exists
                        if thread_task.get('case_id'):
                            case = case_service.get_case_by_id(thread_task['case_id'])
                            if case:
                                # Log inbound email to case threads
                                thread_data = {
                                    'direction': 'Inbound',
                                    'sender_name': email.get('sender', {}).get('name', 'Unknown'),
                                    'sender_email': email.get('sender', {}).get('email', ''),
                                    'subject': email.get('subject', 'No subject'),
                                    'body': email.get('body', ''),
                                    'timestamp': email.get('received_time', datetime.utcnow().isoformat()),
                                    'message_id': email.get('id', '')
                                }
                                case_service.add_thread_to_case(thread_task['case_id'], thread_data)
                                # Regenerate AI summary with new email content
                                logger.info(f"Regenerating AI summary for case {thread_task['case_id']} due to new email")
                                case_service.regenerate_summary_for_case(thread_task['case_id'])
                        
                        updated = True
                        continue
                    
                    # Process email with LLM
                    llm_result = llm_service.process_email(email)
                    
                    # Create or find case for this email/thread
                    existing_case = case_service.find_case_by_thread(thread_id)
                    if not existing_case:
                        # Try to find existing open case for this customer
                        customer_email = email['sender']['email']
                        existing_case = case_service.find_case_by_customer_email(customer_email)
                    
                    if existing_case:
                        # Use existing case
                        case_id = existing_case['case_id']
                        logger.info(f"Using existing case {existing_case['case_number']} for email {email['id']}")
                    else:
                        # Create new case
                        case = case_service.create_case_from_email(email, thread_id, llm_result)
                        case_id = case['case_id']
                        logger.info(f"Created new case {case['case_number']} for email {email['id']}")
                    
                    # Create NEW task (first email in thread) with case_id using TaskService
                    task_data = {
                        'case_id': case_id,  # NEW: Link to case
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
                        'assigned_to': None,
                        'notes': [],
                        'sentiment': llm_result.get('sentiment', 'Neutral'),
                        'action_required': llm_result.get('action_required', 'Review and respond'),
                        'created_by': 'system',
                        'thread_info': {
                            'thread_id': thread_id,
                            'thread_status': thread.status,
                            'thread_priority': thread.priority,
                            'thread_category': thread.category,
                            'email_count': len(thread.emails),
                            'participants': list(thread.participants)
                        }
                    }
                    
                    # Create task using TaskService
                    task_service = TaskService()
                    task = task_service.create_task(task_data)
                    
                    # Add task to case
                    case_service.add_task_to_case(case_id, task['id'])
                    updated = True
                    logger.info(f"Created new task from email: {email['subject']} (Thread: {thread_id})")
                    
                    # Regenerate AI summary with new email content
                    logger.info(f"Regenerating AI summary for case {case_id} with new email content")
                    case_service.regenerate_summary_for_case(case_id)
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
            "case_service": "✅ Available",
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

@app.route('/api/migrate/tasks-to-cases', methods=['POST'])
@handle_exceptions
def migrate_tasks_to_cases():
    """Migrate existing tasks to cases"""
    try:
        logger.info("Starting task-to-case migration")
        migrate_existing_tasks_to_cases()
        
        # Get stats after migration
        tasks = load_tasks()
        cases = case_service.load_cases()
        
        response_data = {
            "migration_completed": True,
            "tasks_migrated": len([t for t in tasks if t.get('case_id')]),
            "total_tasks": len(tasks),
            "total_cases": len(cases),
            "tasks_without_cases": len([t for t in tasks if not t.get('case_id')])
        }
        
        return success_response(response_data, "Task migration completed successfully")
        
    except Exception as e:
        logger.error(f"Error in migrate_tasks_to_cases: {e}")
        return error_response("Task migration failed", 500)

if __name__ == '__main__':
    # Ensure data and logs directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
# Validate configuration (skip for demo)
# if not validate_config():
#     logger.error("Configuration validation failed. Please check your environment variables.")
#     exit(1)
    
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
        
        # Initialize WebSocket support
        if WEBSOCKET_AVAILABLE:
            socketio = initialize_websocket_support(app)
            if socketio:
                logger.info("WebSocket support initialized")
            else:
                logger.warning("WebSocket support failed to initialize")
        else:
            logger.warning("WebSocket support not available - Flask-SocketIO not installed")
        
        # Start real-time dashboard services
        try:
            realtime_broadcaster = get_realtime_broadcaster()
            realtime_collector = get_realtime_collector()
            logger.info("Real-time dashboard services started")
        except Exception as e:
            logger.error(f"Failed to start real-time dashboard services: {e}")
        
    except Exception as e:
        logger.error(f"Failed to initialize analytics framework: {e}")
    
    logger.info("Application starting...")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
