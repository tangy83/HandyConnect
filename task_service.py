from datetime import datetime
import json
import os

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
        
        return {
            'total': total_tasks,
            'new': new_tasks,
            'in_progress': in_progress_tasks,
            'completed': completed_tasks,
            'high_priority': high_priority,
            'urgent_priority': urgent_priority,
            'categories': categories
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
