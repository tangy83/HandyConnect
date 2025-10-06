"""
Case API Blueprint for HandyConnect
RESTful API endpoints for case management
"""

from flask import Blueprint, request, jsonify
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from ..core_services.case_service import CaseService
from ..core_services.task_service import TaskService

logger = logging.getLogger(__name__)

# Create blueprint
case_bp = Blueprint('case_api', __name__, url_prefix='/api/cases')

# Initialize services
case_service = CaseService()
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

@case_bp.route('/', methods=['GET'])
def get_cases():
    """Get all cases with optional filtering"""
    try:
        # Get query parameters
        status = request.args.get('status')
        priority = request.args.get('priority')
        case_type = request.args.get('type')
        assigned_to = request.args.get('assigned_to')
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Get filtered cases
        cases = case_service.get_cases_by_filter(
            status=status,
            priority=priority,
            case_type=case_type,
            assigned_to=assigned_to
        )
        
        # Apply pagination
        if limit:
            cases = cases[offset:offset + limit]
        else:
            cases = cases[offset:]
        
        # Get case statistics
        stats = case_service.get_case_stats()
        
        response_data = {
            "cases": cases,
            "total_count": len(case_service.load_cases()),
            "filtered_count": len(cases),
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": len(cases) == limit if limit else False
            },
            "statistics": stats
        }
        
        return success_response(response_data, f"Retrieved {len(cases)} cases")
        
    except Exception as e:
        logger.error(f"Error getting cases: {e}")
        return error_response("Failed to retrieve cases", 500, str(e))

@case_bp.route('/<case_id>', methods=['GET'])
def get_case(case_id: str):
    """Get specific case by ID"""
    try:
        case = case_service.get_case_by_id(case_id)
        
        if not case:
            return error_response("Case not found", 404)
        
        # Get related tasks
        tasks = task_service.load_tasks()
        case_tasks = [task for task in tasks if task.get('case_id') == case_id]
        
        response_data = {
            "case": case,
            "related_tasks": case_tasks,
            "task_count": len(case_tasks)
        }
        
        return success_response(response_data, f"Retrieved case {case.get('case_number', case_id)}")
        
    except Exception as e:
        logger.error(f"Error getting case {case_id}: {e}")
        return error_response("Failed to retrieve case", 500, str(e))

@case_bp.route('/number/<case_number>', methods=['GET'])
def get_case_by_number(case_number: str):
    """Get specific case by case number"""
    try:
        case = case_service.get_case_by_number(case_number)
        
        if not case:
            return error_response("Case not found", 404)
        
        # Get related tasks
        tasks = task_service.load_tasks()
        case_tasks = [task for task in tasks if task.get('case_id') == case['case_id']]
        
        response_data = {
            "case": case,
            "related_tasks": case_tasks,
            "task_count": len(case_tasks)
        }
        
        return success_response(response_data, f"Retrieved case {case_number}")
        
    except Exception as e:
        logger.error(f"Error getting case {case_number}: {e}")
        return error_response("Failed to retrieve case", 500, str(e))

@case_bp.route('/', methods=['POST'])
def create_case():
    """Create a new case"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("No data provided", 400)
        
        # Validate required fields
        required_fields = ['case_title', 'case_type', 'priority', 'customer_info']
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)
        
        # Create case
        case_id = case_service.create_case_from_email(
            email={
                'id': f"manual_{datetime.utcnow().timestamp()}",
                'subject': data['case_title'],
                'sender': data['customer_info'],
                'body': data.get('description', '')
            },
            thread_id=f"manual_thread_{datetime.utcnow().timestamp()}",
            llm_result={
                'summary': data.get('description', ''),
                'category': data.get('category', 'General'),
                'priority': data['priority'],
                'sentiment': data.get('sentiment', 'Neutral'),
                'action_required': data.get('action_required', 'Review and respond')
            }
        )
        
        # Get the created case
        case = case_service.get_case_by_id(case_id['case_id'])
        
        return success_response(case, f"Created case {case['case_number']}", 201)
        
    except Exception as e:
        logger.error(f"Error creating case: {e}")
        return error_response("Failed to create case", 500, str(e))

@case_bp.route('/<case_id>', methods=['PUT', 'PATCH'])
def update_case(case_id: str):
    """Update an existing case"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("No data provided", 400)
        
        # Get existing case
        case = case_service.get_case_by_id(case_id)
        if not case:
            return error_response("Case not found", 404)
        
        # Update case fields
        updatable_fields = [
            'case_title', 'status', 'priority', 'assigned_to', 'assigned_team',
            'sla_status', 'case_type', 'sentiment'
        ]
        
        for field in updatable_fields:
            if field in data:
                case[field] = data[field]
        
        # Handle description update
        if 'description' in data:
            if 'case_metadata' not in case:
                case['case_metadata'] = {}
            case['case_metadata']['description'] = data['description']
        
        # Update customer info if provided
        if 'customer_info' in data:
            case['customer_info'].update(data['customer_info'])
        
        # Update metadata if provided
        if 'case_metadata' in data:
            case['case_metadata'].update(data['case_metadata'])
        
        # Update timestamp
        case['updated_at'] = datetime.utcnow().isoformat()
        case['updated_by'] = data.get('updated_by', 'api')
        
        # Save updated case
        cases = case_service.load_cases()
        for i, c in enumerate(cases):
            if c['case_id'] == case_id:
                cases[i] = case
                break
        
        case_service.save_cases(cases)
        
        return success_response(case, f"Updated case {case['case_number']}")
        
    except Exception as e:
        logger.error(f"Error updating case {case_id}: {e}")
        return error_response("Failed to update case", 500, str(e))

@case_bp.route('/<case_id>/status', methods=['PATCH'])
def update_case_status(case_id: str):
    """Update case status"""
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return error_response("Status is required", 400)
        
        actor = data.get('actor', 'api')
        
        updated_case = case_service.update_case_status(case_id, data['status'], actor)
        
        if not updated_case:
            return error_response("Case not found", 404)
        
        return success_response(updated_case, f"Updated case status to {data['status']}")
        
    except Exception as e:
        logger.error(f"Error updating case status {case_id}: {e}")
        return error_response("Failed to update case status", 500, str(e))

@case_bp.route('/<case_id>/assign', methods=['PATCH'])
def assign_case(case_id: str):
    """Assign case to agent"""
    try:
        data = request.get_json()
        
        if not data or 'assignee' not in data:
            return error_response("Assignee is required", 400)
        
        actor = data.get('actor', 'api')
        
        updated_case = case_service.assign_case(case_id, data['assignee'], actor)
        
        if not updated_case:
            return error_response("Case not found", 404)
        
        return success_response(updated_case, f"Assigned case to {data['assignee']}")
        
    except Exception as e:
        logger.error(f"Error assigning case {case_id}: {e}")
        return error_response("Failed to assign case", 500, str(e))


@case_bp.route('/<case_id>/timeline', methods=['GET'])
def get_case_timeline(case_id: str):
    """Get case timeline events"""
    try:
        case = case_service.get_case_by_id(case_id)
        if not case:
            return error_response("Case not found", 404)
        
        timeline = case.get('timeline', [])
        
        response_data = {
            "case_id": case_id,
            "case_number": case['case_number'],
            "timeline": timeline,
            "event_count": len(timeline)
        }
        
        return success_response(response_data, f"Retrieved {len(timeline)} timeline events")
        
    except Exception as e:
        logger.error(f"Error getting case timeline {case_id}: {e}")
        return error_response("Failed to retrieve case timeline", 500, str(e))

@case_bp.route('/search', methods=['GET'])
def search_cases():
    """Search cases by various criteria"""
    try:
        query = request.args.get('q', '')
        field = request.args.get('field', 'all')  # all, title, customer, number
        
        if not query:
            return error_response("Search query is required", 400)
        
        cases = case_service.load_cases()
        results = []
        
        for case in cases:
            match = False
            
            if field == 'all' or field == 'title':
                if query.lower() in case.get('case_title', '').lower():
                    match = True
            
            if field == 'all' or field == 'customer':
                customer_info = case.get('customer_info', {})
                if (query.lower() in customer_info.get('name', '').lower() or
                    query.lower() in customer_info.get('email', '').lower()):
                    match = True
            
            if field == 'all' or field == 'number':
                if query.lower() in case.get('case_number', '').lower():
                    match = True
            
            if match:
                results.append(case)
        
        response_data = {
            "query": query,
            "field": field,
            "results": results,
            "result_count": len(results)
        }
        
        return success_response(response_data, f"Found {len(results)} matching cases")
        
    except Exception as e:
        logger.error(f"Error searching cases: {e}")
        return error_response("Failed to search cases", 500, str(e))

@case_bp.route('/stats', methods=['GET'])
def get_case_statistics():
    """Get comprehensive case statistics"""
    try:
        stats = case_service.get_case_stats()
        
        # Add additional statistics
        cases = case_service.load_cases()
        
        # Status distribution
        status_distribution = {}
        for case in cases:
            status = case.get('status', 'Unknown')
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        # Priority distribution
        priority_distribution = {}
        for case in cases:
            priority = case.get('priority', 'Unknown')
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
        
        # Type distribution
        type_distribution = {}
        for case in cases:
            case_type = case.get('case_type', 'Unknown')
            type_distribution[case_type] = type_distribution.get(case_type, 0) + 1
        
        # SLA status distribution
        sla_distribution = {}
        for case in cases:
            sla_status = case.get('sla_status', 'Unknown')
            sla_distribution[sla_status] = sla_distribution.get(sla_status, 0) + 1
        
        enhanced_stats = {
            **stats,
            "distributions": {
                "status": status_distribution,
                "priority": priority_distribution,
                "type": type_distribution,
                "sla_status": sla_distribution
            }
        }
        
        return success_response(enhanced_stats, "Retrieved case statistics")
        
    except Exception as e:
        logger.error(f"Error getting case statistics: {e}")
        return error_response("Failed to retrieve case statistics", 500, str(e))

@case_bp.route('/bulk/status', methods=['PATCH'])
def bulk_update_status():
    """Bulk update case statuses"""
    try:
        data = request.get_json()
        
        if not data or 'case_ids' not in data or 'status' not in data:
            return error_response("case_ids and status are required", 400)
        
        case_ids = data['case_ids']
        new_status = data['status']
        actor = data.get('actor', 'api')
        
        updated_cases = []
        failed_cases = []
        
        for case_id in case_ids:
            try:
                updated_case = case_service.update_case_status(case_id, new_status, actor)
                if updated_case:
                    updated_cases.append(updated_case)
                else:
                    failed_cases.append(case_id)
            except Exception as e:
                logger.error(f"Error updating case {case_id}: {e}")
                failed_cases.append(case_id)
        
        response_data = {
            "updated_cases": updated_cases,
            "updated_count": len(updated_cases),
            "failed_cases": failed_cases,
            "failed_count": len(failed_cases)
        }
        
        return success_response(response_data, f"Updated {len(updated_cases)} cases")
        
    except Exception as e:
        logger.error(f"Error in bulk status update: {e}")
        return error_response("Failed to update case statuses", 500, str(e))

@case_bp.route('/bulk/assign', methods=['PATCH'])
def bulk_assign_cases():
    """Bulk assign cases"""
    try:
        data = request.get_json()
        
        if not data or 'case_ids' not in data or 'assignee' not in data:
            return error_response("case_ids and assignee are required", 400)
        
        case_ids = data['case_ids']
        assignee = data['assignee']
        actor = data.get('actor', 'api')
        
        updated_cases = []
        failed_cases = []
        
        for case_id in case_ids:
            try:
                updated_case = case_service.assign_case(case_id, assignee, actor)
                if updated_case:
                    updated_cases.append(updated_case)
                else:
                    failed_cases.append(case_id)
            except Exception as e:
                logger.error(f"Error assigning case {case_id}: {e}")
                failed_cases.append(case_id)
        
        response_data = {
            "updated_cases": updated_cases,
            "updated_count": len(updated_cases),
            "failed_cases": failed_cases,
            "failed_count": len(failed_cases)
        }
        
        return success_response(response_data, f"Assigned {len(updated_cases)} cases to {assignee}")
        
    except Exception as e:
        logger.error(f"Error in bulk assignment: {e}")
        return error_response("Failed to assign cases", 500, str(e))

@case_bp.route('/<case_id>/summary', methods=['GET'])
def get_case_summary(case_id: str):
    """Get AI-generated case summary (with caching)"""
    try:
        case = case_service.get_case_by_id(case_id)
        if not case:
            return error_response("Case not found", 404)
        
        # Check if summary exists in cache
        if case.get('ai_summary') and case.get('ai_summary_generated_at'):
            logger.info(f"Returning cached summary for case {case.get('case_number', case_id)}")
            return success_response(
                data={
                    "summary": case['ai_summary'],
                    "generated_at": case['ai_summary_generated_at'],
                    "cached": True
                },
                message="Case summary retrieved from cache"
            )
        
        # Generate new summary
        logger.info(f"Generating new summary for case {case.get('case_number', case_id)}")
        summary = case_service.generate_case_summary(case)
        
        # Save summary to case
        case_service.regenerate_summary_for_case(case_id)
        
        return success_response(
            data={
                "summary": summary,
                "generated_at": datetime.utcnow().isoformat(),
                "cached": False
            },
            message="Case summary generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating case summary: {e}")
        return error_response("Failed to generate case summary", 500)


@case_bp.route('/send-response', methods=['POST'])
def send_email_response():
    """Send email response to customer via Microsoft Graph API"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['to', 'subject', 'message', 'case_id']):
            return error_response("Missing required fields: to, subject, message, case_id", 400)
        
        # Get case information
        case = case_service.get_case_by_id(data['case_id'])
        if not case:
            return error_response("Case not found", 404)
        
        # Import email service to send emails
        from ..core_services.email_service import EmailService
        email_service = EmailService()
        
        # Check if case details should be included
        include_case_details = data.get('includeCaseDetails', True)
        
        # Send email using Microsoft Graph API (from handymyjob@outlook.com)
        email_sent = email_service.send_email_response(
            case_id=data['case_id'],
            response_text=data['message'],
            recipient_email=data['to'],
            subject=data['subject'],
            include_case_details=include_case_details
        )
        
        if email_sent:
            logger.info(f"✉️ Email sent successfully from handymyjob@outlook.com to {data['to']}: {data['subject']}")
            
            # Add timeline event to case
            timeline_event = {
                'event_id': str(uuid.uuid4()),
                'event_type': 'email_response_sent',
                'timestamp': datetime.utcnow().isoformat(),
                'actor': 'portal_user',
                'description': f"Email response sent to customer: {data['subject']}",
                'metadata': {
                    'recipient': data['to'],
                    'subject': data['subject']
                }
            }
            
            # Update case timeline
            cases = case_service.load_cases()
            for i, c in enumerate(cases):
                if c['case_id'] == data['case_id']:
                    if 'timeline' not in c:
                        c['timeline'] = []
                    c['timeline'].append(timeline_event)
                    c['updated_at'] = datetime.utcnow().isoformat()
                    case_service.save_cases(cases)
                    break
            
            return success_response(
                data={"email_sent": True},
                message="Email response sent successfully from handymyjob@outlook.com"
            )
        else:
            return error_response("Failed to send email", 500)
        
    except Exception as e:
        logger.error(f"Error sending email response: {e}")
        return error_response("Failed to send email response", 500)

@case_bp.route('/<case_id>/threads', methods=['GET'])
def get_case_threads(case_id: str):
    """Get case communication threads"""
    try:
        case = case_service.get_case_by_id(case_id)
        if not case:
            return error_response("Case not found", 404)
        
        # Get related tasks to find threads
        related_tasks = case_service.get_related_tasks(case_id)
        threads = []
        
        # For now, create mock thread data from related tasks
        for task in related_tasks:
            # Handle both task object and string cases
            if isinstance(task, dict):
                threads.append({
                    'subject': task.get('subject', task.get('title', 'Task Communication')),
                    'sender': task.get('sender', {}).get('name', 'System') if isinstance(task.get('sender'), dict) else 'System',
                    'timestamp': task.get('created_at'),
                    'preview': task.get('description', 'No preview available')[:100] + '...'
                })
            else:
                # If task is a string or other type, create basic thread
                threads.append({
                    'subject': 'Task Communication',
                    'sender': 'System',
                    'timestamp': None,
                    'preview': 'No preview available'
                })
        
        return success_response(
            data={"threads": threads},
            message="Communication threads retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting case threads: {e}")
        return error_response("Failed to get case threads", 500)

@case_bp.route('/<case_id>/tasks', methods=['GET'])
def get_case_tasks(case_id: str):
    """Get case tasks and generate new ones using LLM"""
    try:
        case = case_service.get_case_by_id(case_id)
        if not case:
            return error_response("Case not found", 404)
        
        # Get existing related tasks
        related_tasks = case_service.get_related_tasks(case_id)
        
        # Generate context for LLM
        case_context = f"""
        Case Details:
        - Title: {case.get('case_title', 'N/A')}
        - Type: {case.get('case_type', 'N/A')}
        - Priority: {case.get('priority', 'N/A')}
        - Status: {case.get('status', 'N/A')}
        - Customer: {case.get('customer_info', {}).get('name', 'N/A')}
        - Description: {case.get('case_description', 'N/A')}
        """
        
        # Generate LLM tasks
        from ..core_services.llm_service import LLMService
        llm_service = LLMService()
        
        completed_tasks = [task.get('subject', 'Task') for task in related_tasks if task.get('status') == 'Completed']
        generated_tasks = llm_service.generate_case_tasks(case_context, completed_tasks)
        
        # Combine existing and generated tasks
        all_tasks = []
        
        # Add existing tasks
        for task in related_tasks:
            all_tasks.append({
                'id': task.get('id'),
                'title': task.get('subject', 'Task'),
                'description': task.get('description', 'No description'),
                'status': task.get('status', 'New'),
                'priority': task.get('priority', 'Medium'),
                'created_at': task.get('created_at'),
                'type': 'existing'
            })
        
        # Add generated tasks
        for task in generated_tasks:
            all_tasks.append({
                'id': task.get('id', f"generated_{len(all_tasks) + 1}"),
                'title': task.get('title', 'Generated Task'),
                'description': task.get('description', 'Generated task description'),
                'status': 'Pending',
                'priority': task.get('priority', 'Medium'),
                'estimated_time': task.get('estimated_time', 'Unknown'),
                'type': 'generated'
            })
        
        return success_response(
            data={"tasks": all_tasks},
            message="Case tasks retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting case tasks: {e}")
        return error_response("Failed to get case tasks", 500)

@case_bp.route('/<case_id>/timeline-summary', methods=['GET'])
def get_case_timeline_summary(case_id: str):
    """Get LLM-generated timeline summary"""
    try:
        case = case_service.get_case_by_id(case_id)
        if not case:
            return error_response("Case not found", 404)
        
        # Get threads and tasks
        related_tasks = case_service.get_related_tasks(case_id)
        
        # Create mock threads from tasks for now
        threads = []
        for task in related_tasks:
            threads.append({
                'subject': task.get('subject', 'Task Communication'),
                'preview': task.get('description', 'No preview available')[:100] + '...'
            })
        
        # Generate timeline summary using LLM
        from ..core_services.llm_service import LLMService
        llm_service = LLMService()
        
        timeline_summary = llm_service.generate_case_timeline_summary(threads, related_tasks)
        
        return success_response(
            data={"timeline_summary": timeline_summary},
            message="Timeline summary generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating timeline summary: {e}")
        return error_response("Failed to generate timeline summary", 500)

@case_bp.route('/<case_id>/tasks', methods=['POST'])
def create_case_task(case_id: str):
    """Create a new task for a case"""
    try:
        case = case_service.get_case_by_id(case_id)
        if not case:
            return error_response("Case not found", 404)
        
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        # Create task
        task_data = {
            'case_id': case_id,
            'subject': data.get('subject', 'New Task'),
            'description': data.get('description', ''),
            'priority': data.get('priority', 'Medium'),
            'status': data.get('status', 'New'),
            'assigned_to': data.get('assigned_to'),
            'created_by': 'user'  # TODO: Get from session
        }
        
        task = task_service.create_task(task_data)
        
        # Add task to case
        case_service.add_task_to_case(case_id, task['id'])
        
        return success_response(
            data={"task": task},
            message="Task created successfully"
        )
        
    except Exception as e:
        logger.error(f"Error creating case task: {e}")
        return error_response("Failed to create task", 500)


@case_bp.route('/<case_id>/tasks/<int:task_id>/assign', methods=['POST'])
def assign_case_task(case_id: str, task_id: int):
    """Assign a task to internal team or external contractor"""
    try:
        # Verify case exists
        case = case_service.get_case_by_id(case_id)
        if not case:
            return error_response("Case not found", 404)
        
        # Verify task exists
        task = task_service.get_task_by_id(task_id)
        if not task:
            return error_response("Task not found", 404)
        
        # Get assignment data
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        assignee_name = data.get('assignee_name')
        assignee_email = data.get('assignee_email')
        assignee_role = data.get('assignee_role')  # "Internal" or "External"
        
        if not all([assignee_name, assignee_email, assignee_role]):
            return error_response("Missing required fields: assignee_name, assignee_email, assignee_role", 400)
        
        # Use TaskAssignmentService to assign and notify
        from ..core_services.task_assignment_service import TaskAssignmentService
        assignment_service = TaskAssignmentService()
        
        success = assignment_service.assign_and_notify(
            task_id=task_id,
            assignee_name=assignee_name,
            assignee_email=assignee_email,
            assignee_role=assignee_role,
            case_id=case_id
        )
        
        if success:
            # Get updated task
            updated_task = task_service.get_task_by_id(task_id)
            return success_response(
                data={"task": updated_task},
                message=f"Task assigned to {assignee_name} and notification email sent"
            )
        else:
            return error_response("Failed to assign task or send notification", 500)
        
    except Exception as e:
        logger.error(f"Error assigning task: {e}")
        import traceback
        traceback.print_exc()
        return error_response("Failed to assign task", 500)
