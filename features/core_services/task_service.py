from datetime import datetime
import json
import os
from .category_tree import property_categories

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
    
    def assign_task(self, task_id, assignee):
        """Assign task to a team member"""
        tasks = self.load_tasks()
        task = next((t for t in tasks if t.get('id') == task_id), None)
        if task:
            task['assigned_to'] = assignee
            task['updated_at'] = datetime.utcnow().isoformat()
            self.save_tasks(tasks)
            return task
        return None
    
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
