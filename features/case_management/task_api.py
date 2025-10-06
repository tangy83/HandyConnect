"""
Task API Blueprint for HandyConnect
RESTful API endpoints for task management
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from ..core_services.task_service import TaskService

logger = logging.getLogger(__name__)

# Create blueprint
task_bp = Blueprint('task_api', __name__, url_prefix='/api/tasks')

# Initialize services
task_service = TaskService()

def success_response(data=None, message="Success", status_code=200):
    """Standard success response format"""
    response = {"status": "success", "message": message}
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code

def error_response(message="Error", status_code=400, error_details=None):
    """Standard error response format"""
    response = {"status": "error", "message": message}
    if error_details:
        response["error"] = error_details
    return jsonify(response), status_code

@task_bp.route('/<task_id>', methods=['GET'])
def get_task(task_id: str):
    """Get a specific task by ID"""
    try:
        task = task_service.get_task_by_id(task_id)
        if not task:
            return error_response("Task not found", 404)
        
        return success_response(
            data={"task": task},
            message="Task retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {e}")
        return error_response("Failed to get task", 500)

@task_bp.route('/<task_id>', methods=['PATCH'])
def update_task(task_id: str):
    """Update a task"""
    try:
        task = task_service.get_task_by_id(task_id)
        if not task:
            return error_response("Task not found", 404)
        
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        # Update task
        updated_task = task_service.update_task(task_id, data)
        
        return success_response(
            data={"task": updated_task},
            message="Task updated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        return error_response("Failed to update task", 500)

@task_bp.route('/<task_id>/complete', methods=['POST'])
def complete_task(task_id: str):
    """Complete a task with completion details"""
    try:
        task = task_service.get_task_by_id(task_id)
        if not task:
            return error_response("Task not found", 404)
        
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        # Prepare completion data
        completion_data = {
            'status': data.get('status', 'Completed'),
            'completion_date': data.get('completion_date'),
            'completion_notes': data.get('completion_notes', ''),
            'time_spent': data.get('time_spent'),
            'completed_by': 'user',  # TODO: Get from session
            'completed_at': datetime.utcnow().isoformat()
        }
        
        # Update task with completion details
        updated_task = task_service.update_task(task_id, completion_data)
        
        # Add completion note if provided
        if completion_data.get('completion_notes'):
            note_data = {
                'task_id': task_id,
                'content': f"Task completed: {completion_data['completion_notes']}",
                'created_by': completion_data['completed_by'],
                'type': 'completion'
            }
            task_service.add_task_note(note_data)
        
        # TODO: Send notification if requested
        if data.get('notify_customer', False):
            # Implement customer notification
            pass
        
        return success_response(
            data={"task": updated_task},
            message="Task completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error completing task {task_id}: {e}")
        return error_response("Failed to complete task", 500)

@task_bp.route('/<task_id>/notes', methods=['GET'])
def get_task_notes(task_id: str):
    """Get notes for a specific task"""
    try:
        task = task_service.get_task_by_id(task_id)
        if not task:
            return error_response("Task not found", 404)
        
        notes = task_service.get_task_notes(task_id)
        
        return success_response(
            data={"notes": notes},
            message="Task notes retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting task notes for {task_id}: {e}")
        return error_response("Failed to get task notes", 500)

@task_bp.route('/<task_id>/notes', methods=['POST'])
def add_task_note(task_id: str):
    """Add a note to a task"""
    try:
        task = task_service.get_task_by_id(task_id)
        if not task:
            return error_response("Task not found", 404)
        
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        note_data = {
            'task_id': task_id,
            'content': data.get('content', ''),
            'created_by': 'user',  # TODO: Get from session
            'type': data.get('type', 'note')
        }
        
        note = task_service.add_task_note(note_data)
        
        return success_response(
            data={"note": note},
            message="Note added successfully"
        )
        
    except Exception as e:
        logger.error(f"Error adding note to task {task_id}: {e}")
        return error_response("Failed to add note", 500)
