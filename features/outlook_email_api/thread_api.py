"""
Thread API endpoints for email conversation management
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from .email_threading import EmailThreadingService
import json

# Create blueprint for thread API
thread_bp = Blueprint('thread_api', __name__, url_prefix='/api/threads')

# Initialize threading service
threading_service = EmailThreadingService()

@thread_bp.route('/', methods=['GET'])
def get_threads():
    """Get all threads with optional filtering"""
    try:
        status = request.args.get('status')
        priority = request.args.get('priority')
        category = request.args.get('category')
        
        threads = threading_service.get_all_threads(
            status=status,
            priority=priority,
            category=category
        )
        
        # Convert threads to serializable format
        thread_data = []
        for thread in threads:
            thread_data.append({
                'thread_id': thread.thread_id,
                'subject': thread.subject,
                'participants': list(thread.participants),
                'email_count': len(thread.emails),
                'created_at': thread.created_at.isoformat(),
                'updated_at': thread.updated_at.isoformat(),
                'status': thread.status,
                'priority': thread.priority,
                'category': thread.category,
                'summary': thread.summary,
                'notes': getattr(thread, 'notes', [])
            })
        
        return jsonify({
            'status': 'success',
            'message': f'Retrieved {len(thread_data)} threads',
            'data': thread_data
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error retrieving threads: {str(e)}'
        }), 500

@thread_bp.route('/<thread_id>', methods=['GET'])
def get_thread(thread_id):
    """Get a specific thread by ID"""
    try:
        thread = threading_service.get_thread(thread_id)
        
        if not thread:
            return jsonify({
                'status': 'error',
                'message': 'Thread not found'
            }), 404
        
        # Convert thread to serializable format with full email details
        thread_data = {
            'thread_id': thread.thread_id,
            'subject': thread.subject,
            'participants': list(thread.participants),
            'emails': thread.emails,
            'created_at': thread.created_at.isoformat(),
            'updated_at': thread.updated_at.isoformat(),
            'status': thread.status,
            'priority': thread.priority,
            'category': thread.category,
            'summary': thread.summary,
            'notes': getattr(thread, 'notes', [])
        }
        
        return jsonify({
            'status': 'success',
            'message': 'Thread retrieved successfully',
            'data': thread_data
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error retrieving thread: {str(e)}'
        }), 500

@thread_bp.route('/<thread_id>/status', methods=['PUT'])
def update_thread_status(thread_id):
    """Update thread status"""
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Status is required'
            }), 400
        
        status = data['status']
        valid_statuses = ['active', 'resolved', 'archived']
        
        if status not in valid_statuses:
            return jsonify({
                'status': 'error',
                'message': f'Invalid status. Must be one of: {valid_statuses}'
            }), 400
        
        success = threading_service.update_thread_status(thread_id, status)
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Thread not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'message': f'Thread status updated to {status}'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error updating thread status: {str(e)}'
        }), 500

@thread_bp.route('/<thread_id>/priority', methods=['PUT'])
def update_thread_priority(thread_id):
    """Update thread priority"""
    try:
        data = request.get_json()
        if not data or 'priority' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Priority is required'
            }), 400
        
        priority = data['priority']
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        
        if priority not in valid_priorities:
            return jsonify({
                'status': 'error',
                'message': f'Invalid priority. Must be one of: {valid_priorities}'
            }), 400
        
        success = threading_service.update_thread_priority(thread_id, priority)
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Thread not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'message': f'Thread priority updated to {priority}'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error updating thread priority: {str(e)}'
        }), 500

@thread_bp.route('/<thread_id>/notes', methods=['POST'])
def add_thread_notes(thread_id):
    """Add notes to thread"""
    try:
        data = request.get_json()
        if not data or 'notes' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Notes content is required'
            }), 400
        
        notes = data['notes']
        success = threading_service.add_thread_notes(thread_id, notes)
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Thread not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Notes added to thread successfully'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error adding notes: {str(e)}'
        }), 500

@thread_bp.route('/stats', methods=['GET'])
def get_thread_stats():
    """Get thread statistics"""
    try:
        stats = threading_service.get_thread_statistics()
        
        return jsonify({
            'status': 'success',
            'message': 'Thread statistics retrieved successfully',
            'data': stats
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error retrieving thread statistics: {str(e)}'
        }), 500

@thread_bp.route('/search', methods=['GET'])
def search_threads():
    """Search threads by content"""
    try:
        query = request.args.get('q')
        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Search query is required'
            }), 400
        
        threads = threading_service.search_threads(query)
        
        # Convert threads to serializable format
        thread_data = []
        for thread in threads:
            thread_data.append({
                'thread_id': thread.thread_id,
                'subject': thread.subject,
                'participants': list(thread.participants),
                'email_count': len(thread.emails),
                'created_at': thread.created_at.isoformat(),
                'updated_at': thread.updated_at.isoformat(),
                'status': thread.status,
                'priority': thread.priority,
                'category': thread.category,
                'summary': thread.summary
            })
        
        return jsonify({
            'status': 'success',
            'message': f'Found {len(thread_data)} threads matching "{query}"',
            'data': thread_data
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error searching threads: {str(e)}'
        }), 500

@thread_bp.route('/<thread_id1>/merge/<thread_id2>', methods=['POST'])
def merge_threads(thread_id1, thread_id2):
    """Merge two threads"""
    try:
        success = threading_service.merge_threads(thread_id1, thread_id2)
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'One or both threads not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'message': f'Threads {thread_id1} and {thread_id2} merged successfully'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error merging threads: {str(e)}'
        }), 500

@thread_bp.route('/email/<email_id>', methods=['GET'])
def get_thread_by_email(email_id):
    """Get thread containing a specific email"""
    try:
        thread = threading_service.get_thread_by_email(email_id)
        
        if not thread:
            return jsonify({
                'status': 'error',
                'message': 'No thread found for this email'
            }), 404
        
        # Convert thread to serializable format
        thread_data = {
            'thread_id': thread.thread_id,
            'subject': thread.subject,
            'participants': list(thread.participants),
            'email_count': len(thread.emails),
            'created_at': thread.created_at.isoformat(),
            'updated_at': thread.updated_at.isoformat(),
            'status': thread.status,
            'priority': thread.priority,
            'category': thread.category,
            'summary': thread.summary
        }
        
        return jsonify({
            'status': 'success',
            'message': 'Thread retrieved successfully',
            'data': thread_data
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error retrieving thread: {str(e)}'
        }), 500
