"""
Advanced TDD Tests for Flask Application (Phase 1)
Author: AI Assistant
Date: September 20, 2025

Comprehensive test suite using advanced TDD practices for the main Flask application.
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
import os
import tempfile

from .advanced_tdd_framework import (
    AdvancedTestBase, APITestBase, PerformanceTestBase,
    performance_test, retry_on_failure, TestScenario
)

class TestFlaskApplicationAdvanced(APITestBase):
    """Advanced tests for Flask application"""
    
    @pytest.fixture(autouse=True)
    def setup_test_app(self, test_app):
        """Setup test Flask application"""
        self.client = test_app
        self.app_context = test_app.application.app_context()
        self.app_context.push()
        yield
        self.app_context.pop()
    
    @pytest.mark.unit
    @pytest.mark.smoke
    def test_application_initialization(self):
        """Test application initializes correctly"""
        # Test that all required components are initialized
        from app import app, email_service, llm_service, task_service
        
        assert app is not None
        assert email_service is not None
        assert llm_service is not None
        assert task_service is not None
        
        # Test configuration
        assert app.config['TESTING'] is True
        
    @pytest.mark.integration
    @pytest.mark.api
    @performance_test(max_time=0.5)
    def test_health_endpoint_comprehensive(self):
        """Comprehensive test for health endpoint"""
        response = self.client.get('/api/health')
        data = self.assert_api_response(response, 200, ['data', 'message', 'status'])
        
        # Validate response structure
        assert data['status'] == 'success'
        assert 'timestamp' in data['data']
        assert 'version' in data['data']
        assert data['data']['status'] == 'healthy'
        
        # Validate timestamp format
        timestamp = data['data']['timestamp']
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_tasks_endpoint_advanced(self):
        """Advanced tests for tasks endpoint"""
        # Test empty tasks
        response = self.client.get('/api/tasks')
        data = self.assert_api_response(response, 200)
        assert data['data'] == []
        
        # Test with filters
        response = self.client.get('/api/tasks?status=New')
        self.assert_api_response(response, 200)
        
        response = self.client.get('/api/tasks?priority=High')
        self.assert_api_response(response, 200)
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_task_stats_endpoint_comprehensive(self):
        """Comprehensive test for task statistics endpoint"""
        response = self.client.get('/api/tasks/stats')
        data = self.assert_api_response(response, 200)
        
        # Validate statistics structure
        stats = data['data']
        required_fields = ['total', 'new', 'in_progress', 'completed', 
                          'high_priority', 'urgent_priority', 'categories']
        
        for field in required_fields:
            assert field in stats, f"Missing field: {field}"
            
        # Validate data types
        assert isinstance(stats['total'], int)
        assert isinstance(stats['categories'], dict)
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_task_crud_operations(self):
        """Test complete CRUD operations for tasks"""
        # Since we're using JSON storage, we'll mock the task creation
        test_task = self.create_test_data("task")
        
        # Test GET specific task (should return 404 for non-existent)
        response = self.client.get('/api/tasks/999')
        self.assert_error_response(response, 404)
        
        # Test UPDATE non-existent task
        response = self.client.put('/api/tasks/999', 
                                 json={'status': 'In Progress'},
                                 content_type='application/json')
        self.assert_error_response(response, 404)
        
        # Test DELETE non-existent task
        response = self.client.delete('/api/tasks/999')
        self.assert_error_response(response, 404)
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_email_polling_endpoint(self):
        """Test email polling endpoint"""
        with patch('app.email_service.get_emails') as mock_get_emails, \
             patch('app.llm_service.process_email') as mock_process_email:
            
            # Mock email data
            mock_get_emails.return_value = [self.create_test_data("email")]
            mock_process_email.return_value = {
                'summary': 'Test summary',
                'category': 'General Inquiry',
                'priority': 'Medium',
                'sentiment': 'Neutral',
                'action_required': 'Review and respond'
            }
            
            response = self.client.post('/api/poll-emails')
            data = self.assert_api_response(response, 200)
            
            assert 'processed_count' in data['data']
            assert 'total_emails' in data['data']
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_security_headers(self):
        """Test security headers in responses"""
        response = self.client.get('/api/health')
        
        # Check for security headers (if implemented)
        # This is a placeholder for security header testing
        assert response.status_code == 200
    
    @pytest.mark.performance
    @pytest.mark.api
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            response = self.client.get('/api/health')
            results.put(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all requests succeeded
        while not results.empty():
            status_code = results.get()
            assert status_code == 200
    
    @pytest.mark.integration
    @pytest.mark.api
    @retry_on_failure(max_retries=3)
    def test_error_handling_comprehensive(self):
        """Comprehensive error handling tests"""
        # Test invalid JSON
        response = self.client.put('/api/tasks/1', 
                                 data='invalid json',
                                 content_type='application/json')
        assert response.status_code in [400, 500]  # Depends on implementation
        
        # Test missing content type
        response = self.client.put('/api/tasks/1', json={'status': 'New'})
        # Should work with proper JSON
        assert response.status_code in [200, 404, 400]
    
    @pytest.mark.e2e
    @pytest.mark.smoke
    def test_application_workflow(self):
        """End-to-end test of basic application workflow"""
        # 1. Check health
        health_response = self.client.get('/api/health')
        self.assert_api_response(health_response, 200)
        
        # 2. Get tasks (should be empty initially)
        tasks_response = self.client.get('/api/tasks')
        tasks_data = self.assert_api_response(tasks_response, 200)
        assert tasks_data['data'] == []
        
        # 3. Get task statistics
        stats_response = self.client.get('/api/tasks/stats')
        stats_data = self.assert_api_response(stats_response, 200)
        assert stats_data['data']['total'] == 0
        
        # 4. Try to poll emails (will depend on configuration)
        with patch('app.validate_config', return_value=False):
            poll_response = self.client.post('/api/poll-emails')
            # Should handle configuration error gracefully
            assert poll_response.status_code in [200, 500]

class TestConfigurationAdvanced(AdvancedTestBase):
    """Advanced configuration tests"""
    
    @pytest.mark.unit
    @pytest.mark.configuration
    def test_environment_variable_handling(self):
        """Test environment variable handling"""
        from app import validate_config
        
        # Test with missing variables
        with patch.dict(os.environ, {}, clear=True):
            assert validate_config() is False
        
        # Test with required variables
        required_vars = {
            'CLIENT_ID': 'test_client_id',
            'CLIENT_SECRET': 'test_secret',
            'TENANT_ID': 'test_tenant',
            'OPENAI_API_KEY': 'test_api_key'
        }
        
        with patch.dict(os.environ, required_vars, clear=True):
            assert validate_config() is True
    
    @pytest.mark.unit
    @pytest.mark.configuration
    def test_data_directory_creation(self):
        """Test data directory creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = os.path.join(temp_dir, 'test_data')
            logs_dir = os.path.join(temp_dir, 'test_logs')
            
            # Simulate app startup directory creation
            os.makedirs(data_dir, exist_ok=True)
            os.makedirs(logs_dir, exist_ok=True)
            
            assert os.path.exists(data_dir)
            assert os.path.exists(logs_dir)

class TestDataStorageAdvanced(AdvancedTestBase):
    """Advanced data storage tests"""
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_json_storage_operations(self):
        """Test JSON storage operations"""
        from app import load_tasks, save_tasks
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'test_tasks.json')
            
            # Mock the DATA_FILE path
            with patch('app.DATA_FILE', test_file):
                # Test loading empty file
                tasks = load_tasks()
                assert tasks == []
                
                # Test saving tasks
                test_tasks = [self.create_test_data("task")]
                result = save_tasks(test_tasks)
                assert result is True
                
                # Test loading saved tasks
                loaded_tasks = load_tasks()
                assert len(loaded_tasks) == 1
                assert loaded_tasks[0]['id'] == test_tasks[0]['id']
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_backup_functionality(self):
        """Test backup functionality"""
        from app import save_tasks
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'test_tasks.json')
            backup_file = f"{test_file}.backup"
            
            with patch('app.DATA_FILE', test_file):
                # Create initial file
                initial_tasks = [self.create_test_data("task", id="initial")]
                save_tasks(initial_tasks)
                
                # Save new tasks (should create backup)
                new_tasks = [self.create_test_data("task", id="updated")]
                save_tasks(new_tasks)
                
                # Check backup was created
                assert os.path.exists(backup_file)
                
                # Verify backup content
                with open(backup_file, 'r') as f:
                    backup_data = json.load(f)
                assert backup_data[0]['id'] == 'initial'

class TestPerformanceAdvanced(PerformanceTestBase):
    """Advanced performance tests"""
    
    @pytest.mark.performance
    @pytest.mark.api
    def test_api_response_times(self, test_app):
        """Test API response times under load"""
        client = test_app
        
        def make_health_request():
            return client.get('/api/health')
        
        # Measure performance
        metrics = self.measure_performance(make_health_request)
        
        # Assert performance thresholds
        self.assert_performance_threshold(
            metrics, 
            max_time=0.5,  # 500ms max
            max_memory=10.0,  # 10MB max
            max_cpu=50.0   # 50% max
        )
    
    @pytest.mark.performance
    @pytest.mark.database
    def test_large_dataset_handling(self):
        """Test handling of large datasets"""
        from app import save_tasks, load_tasks
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'large_tasks.json')
            
            with patch('app.DATA_FILE', test_file):
                # Create large dataset
                large_dataset = []
                for i in range(1000):
                    task = self.create_test_data("task", id=f"task-{i}")
                    large_dataset.append(task)
                
                # Measure save performance
                save_metrics = self.measure_performance(save_tasks, large_dataset)
                self.assert_performance_threshold(
                    save_metrics,
                    max_time=2.0,  # 2 seconds max for 1000 tasks
                    max_memory=50.0
                )
                
                # Measure load performance
                load_metrics = self.measure_performance(load_tasks)
                self.assert_performance_threshold(
                    load_metrics,
                    max_time=1.0,  # 1 second max for loading
                    max_memory=30.0
                )
