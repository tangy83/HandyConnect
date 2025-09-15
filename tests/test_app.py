import unittest
import json
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from app import app, load_tasks, save_tasks, get_next_id, validate_config

class TestHandyConnectApp(unittest.TestCase):
    """Test cases for HandyConnect Flask application"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.original_data_file = app.config.get('DATA_FILE', 'data/tasks.json')
        
        # Mock the data file path for testing
        self.test_data_file = os.path.join(self.test_dir, 'test_tasks.json')
        with patch('app.DATA_FILE', self.test_data_file):
            self.test_data_file = self.test_data_file
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['status'], 'healthy')
        self.assertIn('timestamp', data['data'])
        self.assertEqual(data['data']['version'], '1.0.0')
    
    def test_load_tasks_empty(self):
        """Test loading tasks from non-existent file"""
        with patch('app.DATA_FILE', self.test_data_file):
            tasks = load_tasks()
            self.assertEqual(tasks, [])
    
    def test_load_tasks_with_data(self):
        """Test loading tasks from existing file"""
        test_tasks = [
            {'id': 1, 'subject': 'Test Task 1', 'status': 'New'},
            {'id': 2, 'subject': 'Test Task 2', 'status': 'In Progress'}
        ]
        
        with patch('app.DATA_FILE', self.test_data_file):
            # Create test data file
            os.makedirs(os.path.dirname(self.test_data_file), exist_ok=True)
            with open(self.test_data_file, 'w') as f:
                json.dump(test_tasks, f)
            
            tasks = load_tasks()
            self.assertEqual(len(tasks), 2)
            self.assertEqual(tasks[0]['subject'], 'Test Task 1')
            self.assertEqual(tasks[1]['subject'], 'Test Task 2')
    
    def test_save_tasks(self):
        """Test saving tasks to file"""
        test_tasks = [
            {'id': 1, 'subject': 'Test Task 1', 'status': 'New'},
            {'id': 2, 'subject': 'Test Task 2', 'status': 'In Progress'}
        ]
        
        with patch('app.DATA_FILE', self.test_data_file):
            result = save_tasks(test_tasks)
            self.assertTrue(result)
            
            # Verify file was created and contains correct data
            self.assertTrue(os.path.exists(self.test_data_file))
            with open(self.test_data_file, 'r') as f:
                saved_tasks = json.load(f)
                self.assertEqual(len(saved_tasks), 2)
                self.assertEqual(saved_tasks[0]['subject'], 'Test Task 1')
    
    def test_get_next_id(self):
        """Test getting next available ID"""
        # Test with empty list
        self.assertEqual(get_next_id([]), 1)
        
        # Test with existing tasks
        tasks = [{'id': 1}, {'id': 3}, {'id': 5}]
        self.assertEqual(get_next_id(tasks), 6)
        
        # Test with tasks without IDs
        tasks = [{'name': 'task1'}, {'id': 2}, {'name': 'task2'}]
        self.assertEqual(get_next_id(tasks), 3)
    
    def test_get_tasks_endpoint(self):
        """Test GET /api/tasks endpoint"""
        with patch('app.load_tasks') as mock_load:
            mock_load.return_value = [
                {'id': 1, 'subject': 'Test Task 1', 'status': 'New'},
                {'id': 2, 'subject': 'Test Task 2', 'status': 'In Progress'}
            ]
            
            response = self.client.get('/api/tasks')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(len(data['data']), 2)
    
    def test_get_tasks_with_filters(self):
        """Test GET /api/tasks endpoint with filters"""
        with patch('app.load_tasks') as mock_load:
            mock_load.return_value = [
                {'id': 1, 'subject': 'Test Task 1', 'status': 'New', 'priority': 'High'},
                {'id': 2, 'subject': 'Test Task 2', 'status': 'In Progress', 'priority': 'Low'},
                {'id': 3, 'subject': 'Test Task 3', 'status': 'New', 'priority': 'High'}
            ]
            
            # Test status filter
            response = self.client.get('/api/tasks?status=New')
            data = json.loads(response.data)
            self.assertEqual(len(data['data']), 2)
            
            # Test priority filter
            response = self.client.get('/api/tasks?priority=High')
            data = json.loads(response.data)
            self.assertEqual(len(data['data']), 2)
    
    def test_get_task_by_id(self):
        """Test GET /api/tasks/<id> endpoint"""
        with patch('app.load_tasks') as mock_load:
            mock_load.return_value = [
                {'id': 1, 'subject': 'Test Task 1', 'status': 'New'},
                {'id': 2, 'subject': 'Test Task 2', 'status': 'In Progress'}
            ]
            
            # Test existing task
            response = self.client.get('/api/tasks/1')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['data']['subject'], 'Test Task 1')
            
            # Test non-existing task
            response = self.client.get('/api/tasks/999')
            self.assertEqual(response.status_code, 404)
    
    def test_update_task(self):
        """Test PUT /api/tasks/<id> endpoint"""
        with patch('app.load_tasks') as mock_load, \
             patch('app.save_tasks') as mock_save:
            
            mock_load.return_value = [
                {'id': 1, 'subject': 'Test Task 1', 'status': 'New', 'priority': 'Medium'}
            ]
            mock_save.return_value = True
            
            update_data = {
                'status': 'In Progress',
                'priority': 'High',
                'notes': 'Updated task'
            }
            
            response = self.client.put('/api/tasks/1', 
                                     data=json.dumps(update_data),
                                     content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['data']['status'], 'In Progress')
            self.assertEqual(data['data']['priority'], 'High')
    
    def test_delete_task(self):
        """Test DELETE /api/tasks/<id> endpoint"""
        with patch('app.load_tasks') as mock_load, \
             patch('app.save_tasks') as mock_save:
            
            mock_load.return_value = [
                {'id': 1, 'subject': 'Test Task 1', 'status': 'New'},
                {'id': 2, 'subject': 'Test Task 2', 'status': 'In Progress'}
            ]
            mock_save.return_value = True
            
            response = self.client.delete('/api/tasks/1')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['data']['task_id'], 1)
    
    def test_poll_emails_endpoint(self):
        """Test POST /api/poll-emails endpoint"""
        with patch('app.validate_config', return_value=True), \
             patch('app.email_service') as mock_email_service, \
             patch('app.llm_service') as mock_llm_service, \
             patch('app.load_tasks') as mock_load, \
             patch('app.save_tasks') as mock_save:
            
            # Mock email service
            mock_email_service.get_emails.return_value = [
                {
                    'id': 'email1',
                    'subject': 'Test Email',
                    'sender': {'name': 'Test User', 'email': 'test@example.com'},
                    'body': 'Test email content'
                }
            ]
            
            # Mock LLM service
            mock_llm_service.process_email.return_value = {
                'summary': 'Test summary',
                'category': 'Technical Issue',
                'priority': 'High',
                'sentiment': 'Neutral',
                'action_required': 'Review and respond'
            }
            
            mock_load.return_value = []
            mock_save.return_value = True
            
            response = self.client.post('/api/poll-emails')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['data']['processed_count'], 1)
    
    @patch.dict(os.environ, {
        'CLIENT_ID': 'test_client_id',
        'CLIENT_SECRET': 'test_client_secret',
        'TENANT_ID': 'test_tenant_id',
        'OPENAI_API_KEY': 'test_openai_key'
    })
    def test_validate_config_success(self):
        """Test configuration validation with valid environment"""
        self.assertTrue(validate_config())
    
    @patch.dict(os.environ, {
        'CLIENT_ID': 'test_client_id',
        'CLIENT_SECRET': 'test_client_secret',
        'TENANT_ID': 'test_tenant_id'
        # Missing OPENAI_API_KEY
    })
    def test_validate_config_failure(self):
        """Test configuration validation with missing environment variables"""
        self.assertFalse(validate_config())

if __name__ == '__main__':
    unittest.main()

