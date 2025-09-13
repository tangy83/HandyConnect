from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import os
import json
from dotenv import load_dotenv
from email_service import EmailService
from llm_service import LLMService
from task_service import TaskService
import threading
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Initialize services
email_service = EmailService()
llm_service = LLMService()
task_service = TaskService()

# JSON Data Storage
DATA_FILE = 'data/tasks.json'

def load_tasks():
    """Load tasks from JSON file"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_tasks(tasks):
    """Save tasks to JSON file"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(tasks, f, indent=2, default=str)

def get_next_id(tasks):
    """Get next available ID for new task"""
    if not tasks:
        return 1
    return max(task.get('id', 0) for task in tasks) + 1

# Routes
@app.route('/')
def index():
    tasks = load_tasks()
    # Sort by created_at descending
    tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return render_template('index.html', tasks=tasks)

@app.route('/api/tasks')
def get_tasks():
    tasks = load_tasks()
    # Sort by created_at descending
    tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jsonify(tasks)

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t.get('id') == task_id), None)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    data = request.get_json()
    
    if 'status' in data:
        task['status'] = data['status']
    if 'priority' in data:
        task['priority'] = data['priority']
    if 'assigned_to' in data:
        task['assigned_to'] = data['assigned_to']
    if 'notes' in data:
        task['notes'] = data['notes']
    
    task['updated_at'] = datetime.utcnow().isoformat()
    save_tasks(tasks)
    
    return jsonify(task)

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t.get('id') == task_id), None)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    tasks.remove(task)
    save_tasks(tasks)
    return jsonify({'message': 'Task deleted successfully'})

@app.route('/api/poll-emails', methods=['POST'])
def poll_emails():
    try:
        emails = email_service.get_emails()
        tasks = load_tasks()
        processed_count = 0
        
        for email in emails:
            # Check if email already exists
            existing_task = next((t for t in tasks if t.get('email_id') == email['id']), None)
            if existing_task:
                continue
                
            # Process email with LLM
            llm_result = llm_service.process_email(email)
            
            # Create task
            task = {
                'id': get_next_id(tasks),
                'email_id': email['id'],
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
                'notes': None
            }
            
            tasks.append(task)
            processed_count += 1
        
        save_tasks(tasks)
        return jsonify({'message': f'Processed {processed_count} new emails'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def email_polling_worker():
    """Background worker for email polling"""
    while True:
        try:
            emails = email_service.get_emails()
            tasks = load_tasks()
            updated = False
            
            for email in emails:
                existing_task = next((t for t in tasks if t.get('email_id') == email['id']), None)
                if not existing_task:
                    llm_result = llm_service.process_email(email)
                    task = {
                        'id': get_next_id(tasks),
                        'email_id': email['id'],
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
                        'notes': None
                    }
                    tasks.append(task)
                    updated = True
            
            if updated:
                save_tasks(tasks)
        except Exception as e:
            print(f"Error in email polling: {e}")
        
        # Wait for the configured interval
        time.sleep(int(os.getenv('POLL_INTERVAL_MINUTES', 5)) * 60)

if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Start email polling in background thread
    polling_thread = threading.Thread(target=email_polling_worker, daemon=True)
    polling_thread.start()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
