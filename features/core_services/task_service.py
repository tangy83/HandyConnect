from datetime import datetime
import json
import os
import logging
from typing import Dict, List, Optional, Any
from .category_tree import property_categories

logger = logging.getLogger(__name__)

class TaskService:
    def __init__(self):
        self.data_file = 'data/tasks.json'
    
    def load_tasks(self):
        """Load tasks from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            return []
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_tasks(self, tasks):
        """Save tasks to JSON file"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(tasks, f, indent=2, default=str)
    
    def create_task(self, task_data: Dict[str, Any]) -> Dict:
        """Create a new task"""
        try:
            tasks = self.load_tasks()
            
            # Generate task ID
            task_id = max([t.get('id', 0) for t in tasks], default=0) + 1
            
            # Create new task
            new_task = {
                'id': task_id,
                'subject': task_data.get('subject', 'New Task'),
                'title': task_data.get('title', task_data.get('subject', 'New Task')),
                'description': task_data.get('description', ''),
                'content': task_data.get('content', task_data.get('description', '')),
                'status': task_data.get('status', 'New'),
                'priority': task_data.get('priority', 'Medium'),
                'category': task_data.get('category', 'General'),
                'assigned_to': task_data.get('assigned_to'),
                'assignee': task_data.get('assigned_to'),
                'case_id': task_data.get('case_id'),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'created_by': task_data.get('created_by', 'system'),
                'sender': task_data.get('sender', ''),
                'sender_email': task_data.get('sender_email', ''),
                'summary': task_data.get('summary', ''),
                'sentiment': task_data.get('sentiment', 'Neutral'),
                'action_required': task_data.get('action_required', 'Review and respond'),
                'notes': task_data.get('notes', []),
                'email_id': task_data.get('email_id'),
                'thread_id': task_data.get('thread_id'),
                'thread_info': task_data.get('thread_info', {})
            }
            
            # Add to tasks list
            tasks.append(new_task)
            self.save_tasks(tasks)
            
            logger.info(f"Created task {task_id}")
            return new_task
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            raise

    def get_task_stats(self):
        """Get task statistics for dashboard"""
        tasks = self.load_tasks()
        
        total_tasks = len(tasks)
        new_tasks = len([t for t in tasks if t.get('status') == 'New'])
        in_progress_tasks = len([t for t in tasks if t.get('status') == 'In Progress'])
        completed_tasks = len([t for t in tasks if t.get('status') == 'Completed'])
        
        # Priority breakdown
        high_priority = len([t for t in tasks if t.get('priority') == 'High'])
        urgent_priority = len([t for t in tasks if t.get('priority') == 'Urgent'])
        
        # Category breakdown
        categories = {}
        for task in tasks:
            category = task.get('category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
        
        # Status distribution
        status_distribution = {
            'New': new_tasks,
            'In Progress': in_progress_tasks,
            'Completed': completed_tasks
        }
        
        # Priority distribution
        priority_distribution = {
            'High': high_priority,
            'Urgent': urgent_priority,
            'Medium': len([t for t in tasks if t.get('priority') == 'Medium']),
            'Low': len([t for t in tasks if t.get('priority') == 'Low'])
        }
        
        return {
            'total_tasks': total_tasks,
            'new': new_tasks,
            'in_progress': in_progress_tasks,
            'completed': completed_tasks,
            'high_priority': high_priority,
            'urgent_priority': urgent_priority,
            'categories': categories,
            'status_distribution': status_distribution,
            'priority_distribution': priority_distribution
        }
    
    def update_task_status(self, task_id, status):
        """Update task status"""
        tasks = self.load_tasks()
        task = next((t for t in tasks if t.get('id') == task_id), None)
        if task:
            task['status'] = status
            task['updated_at'] = datetime.utcnow().isoformat()
            self.save_tasks(tasks)
            return task
        return None
    
    def assign_task(self, task_id: int, assignee_name: str = None, 
                    assignee_email: str = None, assignee_role: str = None) -> Optional[Dict]:
        """
        Assign task to internal team or external contractor
        
        Args:
            task_id: Task ID
            assignee_name: Full name of assignee (backward compatible if only param)
            assignee_email: Email address (optional)
            assignee_role: "Internal" or "External" (optional)
        
        Returns:
            Updated task dict or None
        """
        tasks = self.load_tasks()
        task = next((t for t in tasks if t.get('id') == task_id), None)
        
        if not task:
            logger.warning(f"Task {task_id} not found for assignment")
            return None
        
        # Backward compatibility: if assignee_name is the only param
        if assignee_name and not assignee_email and not assignee_role:
            task['assigned_to'] = assignee_name
        else:
            # New enhanced assignment with email and role
            if assignee_name:
                task['assigned_to'] = assignee_name
            if assignee_email:
                task['assigned_email'] = assignee_email
            if assignee_role:
                task['assigned_role'] = assignee_role
            
            task['status'] = 'Assigned'
            task['assigned_at'] = datetime.utcnow().isoformat()
        
        task['updated_at'] = datetime.utcnow().isoformat()
        
        self.save_tasks(tasks)
        logger.info(f"✅ Assigned task {task_id} to {assignee_name} ({assignee_role or 'N/A'})")
        
        return task
    
    def add_notes(self, task_id, notes):
        """Add notes to a task"""
        tasks = self.load_tasks()
        task = next((t for t in tasks if t.get('id') == task_id), None)
        if task:
            if task.get('notes'):
                task['notes'] += f"\n\n{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}: {notes}"
            else:
                task['notes'] = f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}: {notes}"
            task['updated_at'] = datetime.utcnow().isoformat()
            self.save_tasks(tasks)
            return task
        return None
    
    def get_tasks_by_filter(self, status=None, category=None, priority=None, assigned_to=None):
        """Get tasks with filters"""
        tasks = self.load_tasks()
        filtered_tasks = []
        
        for task in tasks:
            if status and task.get('status') != status:
                continue
            if category and task.get('category') != category:
                continue
            if priority and task.get('priority') != priority:
                continue
            if assigned_to and task.get('assigned_to') != assigned_to:
                continue
            filtered_tasks.append(task)
        
        # Sort by created_at descending
        filtered_tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return filtered_tasks
    
    def create_task_with_hierarchical_category(self, task_data):
        """Create a new task with hierarchical category classification"""
        tasks = self.load_tasks()
        
        # Get next ID
        next_id = max([t.get('id', 0) for t in tasks], default=0) + 1
        
        # Classify the task using the category tree
        email_text = f"{task_data.get('subject', '')} {task_data.get('content', '')}"
        category_name, category_path = property_categories.find_best_category(email_text)
        
        # Create task with hierarchical category information
        task = {
            'id': next_id,
            'subject': task_data.get('subject', ''),
            'sender': task_data.get('sender', ''),
            'sender_email': task_data.get('sender_email', ''),
            'content': task_data.get('content', ''),
            'summary': task_data.get('summary', ''),
            'category': category_name,
            'category_path': category_path,
            'parent_category': property_categories.get_parent_category(category_name),
            'priority': task_data.get('priority', 'Medium'),
            'status': task_data.get('status', 'New'),
            'assigned_to': task_data.get('assigned_to'),
            'notes': task_data.get('notes'),
            'email_id': task_data.get('email_id'),
            'thread_id': task_data.get('thread_id'),
            'sentiment': task_data.get('sentiment', 'Neutral'),
            'action_required': task_data.get('action_required', 'Review and respond'),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        tasks.append(task)
        self.save_tasks(tasks)
        return task
    
    def get_tasks_by_keyword(self, keyword):
        """Get tasks that contain a specific keyword in subject or content"""
        tasks = self.load_tasks()
        keyword_lower = keyword.lower()
        
        filtered_tasks = []
        for task in tasks:
            subject = task.get('subject', '').lower()
            content = task.get('content', '').lower()
            summary = task.get('summary', '').lower()
            
            if (keyword_lower in subject or 
                keyword_lower in content or 
                keyword_lower in summary):
                filtered_tasks.append(task)
        
        # Sort by created_at descending
        filtered_tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return filtered_tasks
    
    def get_category_hierarchy(self):
        """Get the complete category hierarchy for UI"""
        return property_categories.get_category_tree_for_ui()
    
    def get_all_categories_flat(self):
        """Get all categories in a flat list for dropdowns"""
        return list(property_categories.categories.keys())
    
    def get_category_stats(self):
        """Get statistics for all categories"""
        tasks = self.load_tasks()
        category_stats = {}
        
        for task in tasks:
            category = task.get('category', 'Unknown')
            if category not in category_stats:
                category_stats[category] = {
                    'count': 0,
                    'path': property_categories.get_category_path(category),
                    'parent': property_categories.get_parent_category(category)
                }
            category_stats[category]['count'] += 1
        
        return category_stats
    
    def get_tasks_by_case(self, case_id: str) -> List[Dict]:
        """Get all tasks for a specific case"""
        try:
            tasks = self.load_tasks()
            case_tasks = [task for task in tasks if task.get('case_id') == case_id]
            
            logger.info(f"Retrieved {len(case_tasks)} tasks for case {case_id}")
            return case_tasks
            
        except Exception as e:
            logger.error(f"Error getting tasks for case {case_id}: {e}")
            return []
    
    def get_task_with_case_context(self, task_id: int) -> Optional[Dict]:
        """Get task with case context information"""
        try:
            tasks = self.load_tasks()
            task = next((t for t in tasks if t.get('id') == task_id), None)
            
            if not task:
                return None
            
            # Add case context if task has case_id
            if task.get('case_id'):
                case_context = self._get_case_context(task['case_id'])
                if case_context:
                    task['case_context'] = case_context
            
            return task
            
        except Exception as e:
            logger.error(f"Error getting task {task_id} with case context: {e}")
            return None
    
    def update_task_with_case_context(self, task_id: int, updates: Dict[str, Any]) -> Optional[Dict]:
        """Update task and sync with case context"""
        try:
            tasks = self.load_tasks()
            task = next((t for t in tasks if t.get('id') == task_id), None)
            
            if not task:
                return None
            
            # Update task
            for key, value in updates.items():
                task[key] = value
            
            task['updated_at'] = datetime.utcnow().isoformat()
            
            # If task has case_id, update case context
            if task.get('case_id'):
                self._update_case_from_task(task)
            
            # Save updated tasks
            self.save_tasks(tasks)
            
            logger.info(f"Updated task {task_id} with case context sync")
            return task
            
        except Exception as e:
            logger.error(f"Error updating task {task_id} with case context: {e}")
            return None
    
    def create_task_with_case_context(self, task_data: Dict[str, Any], case_id: str = None) -> Dict:
        """Create a new task with case context"""
        try:
            tasks = self.load_tasks()
            
            # Generate task ID
            task_id = max([t.get('id', 0) for t in tasks], default=0) + 1
            
            # Create new task
            new_task = {
                'id': task_id,
                'title': task_data.get('title', 'New Task'),
                'description': task_data.get('description', ''),
                'status': task_data.get('status', 'New'),
                'priority': task_data.get('priority', 'Medium'),
                'category': task_data.get('category', 'General'),
                'assignee': task_data.get('assignee'),
                'case_id': case_id,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'created_by': task_data.get('created_by', 'system')
            }
            
            # Add case context if case_id provided
            if case_id:
                case_context = self._get_case_context(case_id)
                if case_context:
                    new_task['case_context'] = case_context
                    
                    # Add task to case
                    self._add_task_to_case(case_id, task_id)
            
            # Add to tasks list
            tasks.append(new_task)
            self.save_tasks(tasks)
            
            logger.info(f"Created task {task_id} with case context")
            return new_task
            
        except Exception as e:
            logger.error(f"Error creating task with case context: {e}")
            raise
    
    def get_task_by_id(self, task_id: int) -> Optional[Dict]:
        """Get a single task by ID"""
        try:
            tasks = self.load_tasks()
            return next((task for task in tasks if task.get('id') == task_id), None)
        except Exception as e:
            logger.error(f"Error getting task by ID {task_id}: {e}")
            return None

    def update_task(self, task_id: int, updates: Dict[str, Any]) -> Optional[Dict]:
        """Update an existing task"""
        try:
            tasks = self.load_tasks()
            
            for i, task in enumerate(tasks):
                if task.get('id') == task_id:
                    # Update task with new data
                    task.update(updates)
                    task['updated_at'] = datetime.utcnow().isoformat()
                    
                    # Save updated tasks
                    self.save_tasks(tasks)
                    
                    logger.info(f"Updated task {task_id}")
                    return task
            
            logger.warning(f"Task {task_id} not found")
            return None
            
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}")
            return None

    def add_task_note(self, task_id: int, note_data: Dict[str, Any]) -> Optional[Dict]:
        """Add a note to a task"""
        try:
            tasks = self.load_tasks()
            
            for i, task in enumerate(tasks):
                if task.get('id') == task_id:
                    # Initialize notes array if it doesn't exist
                    if 'notes' not in task:
                        task['notes'] = []
                    
                    # Add note
                    note = {
                        'content': note_data.get('content', ''),
                        'created_by': note_data.get('created_by', 'system'),
                        'created_at': note_data.get('created_at', datetime.utcnow().isoformat())
                    }
                    
                    # If notes is a string, convert to array
                    if isinstance(task['notes'], str):
                        task['notes'] = [{'content': task['notes'], 'created_at': task.get('updated_at', datetime.utcnow().isoformat()), 'created_by': 'system'}]
                    
                    task['notes'].append(note)
                    task['updated_at'] = datetime.utcnow().isoformat()
                    
                    # Save updated tasks
                    self.save_tasks(tasks)
                    
                    logger.info(f"Added note to task {task_id}")
                    return task
            
            logger.warning(f"Task {task_id} not found")
            return None
            
        except Exception as e:
            logger.error(f"Error adding note to task {task_id}: {e}")
            return None

    def get_case_task_summary(self, case_id: str) -> Dict[str, Any]:
        """Get summary of tasks for a case"""
        try:
            case_tasks = self.get_tasks_by_case(case_id)
            
            if not case_tasks:
                return {
                    'total_tasks': 0,
                    'completed_tasks': 0,
                    'in_progress_tasks': 0,
                    'new_tasks': 0,
                    'completion_rate': 0
                }
            
            total_tasks = len(case_tasks)
            completed_tasks = len([t for t in case_tasks if t.get('status') == 'Completed'])
            in_progress_tasks = len([t for t in case_tasks if t.get('status') == 'In Progress'])
            new_tasks = len([t for t in case_tasks if t.get('status') == 'New'])
            
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            return {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'in_progress_tasks': in_progress_tasks,
                'new_tasks': new_tasks,
                'completion_rate': round(completion_rate, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting case task summary for {case_id}: {e}")
            return {}
    
    def _get_case_context(self, case_id: str) -> Optional[Dict]:
        """Get case context information"""
        try:
            from .case_service import CaseService
            case_service = CaseService()
            
            case = case_service.get_case_by_id(case_id)
            if case:
                return {
                    'case_id': case.get('case_id'),
                    'case_number': case.get('case_number'),
                    'case_title': case.get('case_title'),
                    'status': case.get('status'),
                    'priority': case.get('priority'),
                    'assigned_to': case.get('assigned_to'),
                    'sla_status': case.get('sla_status')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting case context for {case_id}: {e}")
            return None
    
    def _update_case_from_task(self, task: Dict):
        """Update case based on task changes"""
        try:
            from .case_service import CaseService
            case_service = CaseService()
            
            case_id = task.get('case_id')
            if not case_id:
                return
            
            # Get current case
            case = case_service.get_case_by_id(case_id)
            if not case:
                return
            
            # Update case based on task status
            task_status = task.get('status')
            if task_status == 'Completed':
                # Check if all tasks are completed
                case_tasks = self.get_tasks_by_case(case_id)
                all_completed = all(t.get('status') == 'Completed' for t in case_tasks)
                
                if all_completed and case.get('status') != 'Resolved':
                    case_service.update_case_status(
                        case_id, 'Resolved', 'system', 
                        'All tasks completed'
                    )
            
            logger.info(f"Updated case {case_id} from task {task.get('id')}")
            
        except Exception as e:
            logger.error(f"Error updating case from task: {e}")
    
    def _add_task_to_case(self, case_id: str, task_id: int):
        """Add task to case"""
        try:
            from .case_service import CaseService
            case_service = CaseService()
            
            case_service.add_task_to_case(case_id, task_id)
            logger.info(f"Added task {task_id} to case {case_id}")
            
        except Exception as e:
            logger.error(f"Error adding task {task_id} to case {case_id}: {e}")
