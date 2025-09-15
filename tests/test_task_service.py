import unittest
import json
import os
import tempfile
import shutil
from unittest.mock import patch
from task_service import TaskService

class TestTaskService(unittest.TestCase):
    """Test cases for TaskService"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.test_data_file = os.path.join(self.test_dir, 'test_tasks.json')
        
        # Create TaskService instance with test data file
        self.task_service = TaskService()
        self.task_service.data_file = self.test_data_file
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_load_tasks_empty(self):
        """Test loading tasks from non-existent file"""
        tasks = self.task_service.load_tasks()
        self.assertEqual(tasks, [])
    
    def test_load_tasks_with_data(self):
        """Test loading tasks from existing file"""
        test_tasks = [
            {'id': 1, 'subject': 'Test Task 1', 'status': 'New'},
            {'id': 2, 'subject': 'Test Task 2', 'status': 'In Progress'}
        ]
        
        # Create test data file
        os.makedirs(os.path.dirname(self.test_data_file), exist_ok=True)
        with open(self.test_data_file, 'w') as f:
            json.dump(test_tasks, f)
        
        tasks = self.task_service.load_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]['subject'], 'Test Task 1')
        self.assertEqual(tasks[1]['subject'], 'Test Task 2')
    
    def test_save_tasks(self):
        """Test saving tasks to file"""
        test_tasks = [
            {'id': 1, 'subject': 'Test Task 1', 'status': 'New'},
            {'id': 2, 'subject': 'Test Task 2', 'status': 'In Progress'}
        ]
        
        self.task_service.save_tasks(test_tasks)
        
        # Verify file was created and contains correct data
        self.assertTrue(os.path.exists(self.test_data_file))
        with open(self.test_data_file, 'r') as f:
            saved_tasks = json.load(f)
            self.assertEqual(len(saved_tasks), 2)
            self.assertEqual(saved_tasks[0]['subject'], 'Test Task 1')
    
    def test_get_task_stats(self):
        """Test getting task statistics"""
        test_tasks = [
            {'id': 1, 'status': 'New', 'priority': 'High', 'category': 'Technical Issue'},
            {'id': 2, 'status': 'In Progress', 'priority': 'Medium', 'category': 'Billing Question'},
            {'id': 3, 'status': 'Completed', 'priority': 'Low', 'category': 'General Inquiry'},
            {'id': 4, 'status': 'New', 'priority': 'Urgent', 'category': 'Technical Issue'},
            {'id': 5, 'status': 'New', 'priority': 'High', 'category': 'Billing Question'}
        ]
        
        self.task_service.save_tasks(test_tasks)
        stats = self.task_service.get_task_stats()
        
        self.assertEqual(stats['total'], 5)
        self.assertEqual(stats['new'], 3)
        self.assertEqual(stats['in_progress'], 1)
        self.assertEqual(stats['completed'], 1)
        self.assertEqual(stats['high_priority'], 2)
        self.assertEqual(stats['urgent_priority'], 1)
        
        # Check category breakdown
        self.assertEqual(stats['categories']['Technical Issue'], 2)
        self.assertEqual(stats['categories']['Billing Question'], 2)
        self.assertEqual(stats['categories']['General Inquiry'], 1)
    
    def test_update_task_status(self):
        """Test updating task status"""
        test_tasks = [
            {'id': 1, 'status': 'New', 'subject': 'Test Task 1'},
            {'id': 2, 'status': 'In Progress', 'subject': 'Test Task 2'}
        ]
        
        self.task_service.save_tasks(test_tasks)
        
        # Update task status
        updated_task = self.task_service.update_task_status(1, 'In Progress')
        
        self.assertIsNotNone(updated_task)
        self.assertEqual(updated_task['status'], 'In Progress')
        self.assertIn('updated_at', updated_task)
        
        # Verify task was saved
        tasks = self.task_service.load_tasks()
        task_1 = next((t for t in tasks if t['id'] == 1), None)
        self.assertEqual(task_1['status'], 'In Progress')
    
    def test_update_task_status_not_found(self):
        """Test updating status of non-existent task"""
        test_tasks = [
            {'id': 1, 'status': 'New', 'subject': 'Test Task 1'}
        ]
        
        self.task_service.save_tasks(test_tasks)
        
        # Try to update non-existent task
        updated_task = self.task_service.update_task_status(999, 'In Progress')
        
        self.assertIsNone(updated_task)
    
    def test_assign_task(self):
        """Test assigning task to team member"""
        test_tasks = [
            {'id': 1, 'status': 'New', 'subject': 'Test Task 1', 'assigned_to': None},
            {'id': 2, 'status': 'In Progress', 'subject': 'Test Task 2', 'assigned_to': 'John'}
        ]
        
        self.task_service.save_tasks(test_tasks)
        
        # Assign task
        updated_task = self.task_service.assign_task(1, 'Jane')
        
        self.assertIsNotNone(updated_task)
        self.assertEqual(updated_task['assigned_to'], 'Jane')
        self.assertIn('updated_at', updated_task)
        
        # Verify task was saved
        tasks = self.task_service.load_tasks()
        task_1 = next((t for t in tasks if t['id'] == 1), None)
        self.assertEqual(task_1['assigned_to'], 'Jane')
    
    def test_assign_task_not_found(self):
        """Test assigning non-existent task"""
        test_tasks = [
            {'id': 1, 'status': 'New', 'subject': 'Test Task 1', 'assigned_to': None}
        ]
        
        self.task_service.save_tasks(test_tasks)
        
        # Try to assign non-existent task
        updated_task = self.task_service.assign_task(999, 'Jane')
        
        self.assertIsNone(updated_task)
    
    def test_add_notes(self):
        """Test adding notes to task"""
        test_tasks = [
            {'id': 1, 'status': 'New', 'subject': 'Test Task 1', 'notes': None},
            {'id': 2, 'status': 'In Progress', 'subject': 'Test Task 2', 'notes': 'Existing note'}
        ]
        
        self.task_service.save_tasks(test_tasks)
        
        # Add notes to task without existing notes
        updated_task = self.task_service.add_notes(1, 'New note added')
        
        self.assertIsNotNone(updated_task)
        self.assertIn('New note added', updated_task['notes'])
        self.assertIn('updated_at', updated_task)
        
        # Add notes to task with existing notes
        updated_task = self.task_service.add_notes(2, 'Additional note')
        
        self.assertIsNotNone(updated_task)
        self.assertIn('Existing note', updated_task['notes'])
        self.assertIn('Additional note', updated_task['notes'])
        
        # Verify tasks were saved
        tasks = self.task_service.load_tasks()
        task_1 = next((t for t in tasks if t['id'] == 1), None)
        task_2 = next((t for t in tasks if t['id'] == 2), None)
        
        self.assertIn('New note added', task_1['notes'])
        self.assertIn('Existing note', task_2['notes'])
        self.assertIn('Additional note', task_2['notes'])
    
    def test_add_notes_not_found(self):
        """Test adding notes to non-existent task"""
        test_tasks = [
            {'id': 1, 'status': 'New', 'subject': 'Test Task 1', 'notes': None}
        ]
        
        self.task_service.save_tasks(test_tasks)
        
        # Try to add notes to non-existent task
        updated_task = self.task_service.add_notes(999, 'New note')
        
        self.assertIsNone(updated_task)
    
    def test_get_tasks_by_filter(self):
        """Test getting tasks with filters"""
        test_tasks = [
            {'id': 1, 'status': 'New', 'category': 'Technical Issue', 'priority': 'High', 'assigned_to': 'John'},
            {'id': 2, 'status': 'In Progress', 'category': 'Billing Question', 'priority': 'Medium', 'assigned_to': 'Jane'},
            {'id': 3, 'status': 'New', 'category': 'Technical Issue', 'priority': 'Low', 'assigned_to': 'John'},
            {'id': 4, 'status': 'Completed', 'category': 'General Inquiry', 'priority': 'High', 'assigned_to': 'Bob'}
        ]
        
        self.task_service.save_tasks(test_tasks)
        
        # Test status filter
        filtered_tasks = self.task_service.get_tasks_by_filter(status='New')
        self.assertEqual(len(filtered_tasks), 2)
        self.assertTrue(all(task['status'] == 'New' for task in filtered_tasks))
        
        # Test category filter
        filtered_tasks = self.task_service.get_tasks_by_filter(category='Technical Issue')
        self.assertEqual(len(filtered_tasks), 2)
        self.assertTrue(all(task['category'] == 'Technical Issue' for task in filtered_tasks))
        
        # Test priority filter
        filtered_tasks = self.task_service.get_tasks_by_filter(priority='High')
        self.assertEqual(len(filtered_tasks), 2)
        self.assertTrue(all(task['priority'] == 'High' for task in filtered_tasks))
        
        # Test assigned_to filter
        filtered_tasks = self.task_service.get_tasks_by_filter(assigned_to='John')
        self.assertEqual(len(filtered_tasks), 2)
        self.assertTrue(all(task['assigned_to'] == 'John' for task in filtered_tasks))
        
        # Test multiple filters
        filtered_tasks = self.task_service.get_tasks_by_filter(
            status='New', 
            category='Technical Issue', 
            assigned_to='John'
        )
        self.assertEqual(len(filtered_tasks), 1)
        self.assertEqual(filtered_tasks[0]['id'], 1)
        
        # Test no filters (should return all tasks)
        filtered_tasks = self.task_service.get_tasks_by_filter()
        self.assertEqual(len(filtered_tasks), 4)
    
    def test_get_tasks_by_filter_sorting(self):
        """Test that filtered tasks are sorted by created_at descending"""
        test_tasks = [
            {'id': 1, 'status': 'New', 'created_at': '2024-01-01T10:00:00Z'},
            {'id': 2, 'status': 'New', 'created_at': '2024-01-01T12:00:00Z'},
            {'id': 3, 'status': 'New', 'created_at': '2024-01-01T11:00:00Z'}
        ]
        
        self.task_service.save_tasks(test_tasks)
        
        filtered_tasks = self.task_service.get_tasks_by_filter(status='New')
        
        # Should be sorted by created_at descending
        self.assertEqual(filtered_tasks[0]['id'], 2)  # 12:00:00
        self.assertEqual(filtered_tasks[1]['id'], 3)  # 11:00:00
        self.assertEqual(filtered_tasks[2]['id'], 1)  # 10:00:00

if __name__ == '__main__':
    unittest.main()

