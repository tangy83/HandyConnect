"""
Comprehensive integration tests for HandyConnect application
"""
import pytest
import json
import time
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch

# Import analytics components
from features.analytics.data_visualization import DataVisualization
from features.analytics.analytics_framework import AnalyticsFramework, AnalyticsConfig
from features.analytics.performance_metrics import PerformanceMonitor
from features.analytics.data_persistence import AnalyticsDataPersistence

class TestEndToEndWorkflow:
    """Test complete end-to-end workflows"""
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_complete_task_lifecycle(self, test_app, sample_task_data):
        """Test complete task lifecycle from creation to analytics"""
        # Step 1: Create a task via API
        response = test_app.post('/api/analytics/collect/task',
                               data=json.dumps(sample_task_data),
                               content_type='application/json')
        assert response.status_code == 200
        
        # Step 2: Verify task appears in analytics
        time.sleep(1)  # Allow for processing
        response = test_app.get('/api/analytics/tasks')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['total_tasks'] >= 1
        
        # Step 3: Generate analytics report
        response = test_app.get('/api/analytics/report')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'task_analytics' in data['data']
        
        # Step 4: Generate charts
        response = test_app.get('/api/analytics/charts')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'charts' in data['data']
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_complete_thread_lifecycle(self, test_app, sample_thread_data):
        """Test complete thread lifecycle from creation to analytics"""
        # Step 1: Create a thread via API
        response = test_app.post('/api/analytics/collect/thread',
                               data=json.dumps(sample_thread_data),
                               content_type='application/json')
        assert response.status_code == 200
        
        # Step 2: Verify thread appears in analytics
        time.sleep(1)  # Allow for processing
        response = test_app.get('/api/analytics/threads')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['total_threads'] >= 1
        
        # Step 3: Generate analytics report
        response = test_app.get('/api/analytics/report')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'thread_analytics' in data['data']
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_user_behavior_tracking_workflow(self, test_app, sample_user_behavior):
        """Test complete user behavior tracking workflow"""
        # Step 1: Track user behavior
        response = test_app.post('/api/analytics/collect/user-behavior',
                               data=json.dumps(sample_user_behavior),
                               content_type='application/json')
        assert response.status_code == 200
        
        # Step 2: Verify behavior is tracked
        time.sleep(1)  # Allow for processing
        response = test_app.get('/api/analytics/report')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'system_health' in data['data']
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_performance_monitoring_workflow(self, test_app):
        """Test performance monitoring workflow"""
        # Step 1: Record custom performance metrics
        metric_data = {
            'metric_type': 'test_integration_metric',
            'value': 99.9,
            'unit': 'test_units',
            'category': 'integration_test'
        }
        
        response = test_app.post('/api/analytics/metrics/record',
                               data=json.dumps(metric_data),
                               content_type='application/json')
        assert response.status_code == 200
        
        # Step 2: Get metrics summary
        time.sleep(1)  # Allow for processing
        response = test_app.get('/api/analytics/metrics/summary')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_metrics' in data['data']
        
        # Step 3: Get current metrics
        response = test_app.get('/api/analytics/current-metrics')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'system' in data['data']
        assert 'application' in data['data']

class TestDataFlowIntegration:
    """Test data flow between different components"""
    
    @pytest.mark.integration
    def test_analytics_framework_data_flow(self, analytics_framework, sample_task_data, sample_thread_data):
        """Test data flow through analytics framework"""
        # Process task data
        success = analytics_framework.process_task_data(sample_task_data)
        assert success == True
        
        # Process thread data
        success = analytics_framework.process_thread_data(sample_thread_data)
        assert success == True
        
        # Generate report
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=1)
        report = analytics_framework.get_analytics_report(start_date, end_date)
        
        assert 'task_analytics' in report
        assert 'thread_analytics' in report
        assert report['task_analytics']['total_tasks'] >= 1
        assert report['thread_analytics']['total_threads'] >= 1
    
    @pytest.mark.integration
    def test_performance_monitor_data_flow(self, performance_monitor):
        """Test data flow through performance monitor"""
        # Record metrics
        performance_monitor.record_custom_metric('test_metric', 50.0, 'units', 'test')
        
        # Process metrics buffer
        performance_monitor._process_metrics_buffer()
        
        # Get summary
        summary = performance_monitor.get_metrics_summary(hours=1)
        assert 'total_metrics' in summary
        assert summary['total_metrics'] >= 1
    
    @pytest.mark.integration
    def test_data_persistence_flow(self, analytics_persistence, sample_task_data, sample_performance_metrics):
        """Test data persistence flow"""
        from features.analytics.data_schema import TaskAnalytics, PerformanceMetric
        
        # Save task analytics
        task_analytics = TaskAnalytics.from_dict(sample_task_data)
        success = analytics_persistence.save_task_analytics(task_analytics)
        assert success == True
        
        # Save performance metrics
        metrics = [PerformanceMetric.from_dict(data) for data in sample_performance_metrics]
        success = analytics_persistence.save_performance_metrics(metrics)
        assert success == True
        
        # Load and verify data
        loaded_tasks = analytics_persistence.load_task_analytics()
        loaded_metrics = analytics_persistence.load_performance_metrics()
        
        assert len(loaded_tasks) == 1
        assert len(loaded_metrics) == len(sample_performance_metrics)
        assert loaded_tasks[0].task_id == sample_task_data['task_id']
        assert loaded_metrics[0].metric_type == sample_performance_metrics[0]['metric_type']
    
    @pytest.mark.integration
    def test_visualization_data_flow(self, analytics_persistence, sample_task_data):
        """Test data visualization flow"""
        from features.analytics.data_schema import TaskAnalytics
        
        # Save task analytics
        task_analytics = TaskAnalytics.from_dict(sample_task_data)
        analytics_persistence.save_task_analytics(task_analytics)
        
        # Generate visualizations
        visualization = DataVisualization(analytics_persistence)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=1)
        
        # Test various chart types
        charts = [
            visualization.generate_task_status_chart(start_date, end_date),
            visualization.generate_priority_distribution_chart(start_date, end_date),
            visualization.generate_response_time_trend_chart(start_date, end_date),
            visualization.generate_performance_metrics_chart(start_date, end_date),
            visualization.generate_system_health_chart(start_date, end_date),
            visualization.generate_category_breakdown_chart(start_date, end_date),
            visualization.generate_escalation_trend_chart(start_date, end_date)
        ]
        
        for chart in charts:
            assert 'type' in chart
            assert 'data' in chart
            assert 'options' in chart

class TestSystemIntegration:
    """Test system-level integration"""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_analytics_framework_start_stop(self, analytics_config, analytics_persistence):
        """Test analytics framework start/stop lifecycle"""
        framework = AnalyticsFramework(analytics_config)
        framework.persistence = analytics_persistence
        
        # Start framework
        framework.start()
        assert framework._running == True
        
        # Wait a bit for background processes
        time.sleep(2)
        
        # Stop framework
        framework.stop()
        assert framework._running == False
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_performance_monitor_start_stop(self, analytics_persistence):
        """Test performance monitor start/stop lifecycle"""
        monitor = PerformanceMonitor(analytics_persistence)
        
        # Start monitoring
        monitor.start_monitoring(interval_seconds=1)
        assert monitor._running == True
        
        # Wait a bit for monitoring
        time.sleep(2)
        
        # Stop monitoring
        monitor.stop_monitoring()
        assert monitor._running == False
    
    @pytest.mark.integration
    def test_data_cleanup_integration(self, analytics_persistence, sample_task_data):
        """Test data cleanup integration"""
        from features.analytics.data_schema import TaskAnalytics
        
        # Save some data
        task_analytics = TaskAnalytics.from_dict(sample_task_data)
        analytics_persistence.save_task_analytics(task_analytics)
        
        # Verify data exists
        tasks = analytics_persistence.load_task_analytics()
        assert len(tasks) == 1
        
        # Test cleanup (should not delete recent data)
        deleted_files = analytics_persistence.cleanup_old_data()
        assert isinstance(deleted_files, int)
        
        # Verify data still exists (not old enough to be cleaned)
        tasks = analytics_persistence.load_task_analytics()
        assert len(tasks) == 1
    
    @pytest.mark.integration
    def test_export_import_integration(self, analytics_persistence, sample_task_data):
        """Test data export/import integration"""
        from features.analytics.data_schema import TaskAnalytics
        
        # Save data
        task_analytics = TaskAnalytics.from_dict(sample_task_data)
        analytics_persistence.save_task_analytics(task_analytics)
        
        # Export data
        export_file = analytics_persistence.export_data('tasks')
        assert export_file is not None
        
        # Verify export file exists and contains data
        import os
        assert os.path.exists(export_file)
        
        with open(export_file, 'r') as f:
            exported_data = json.load(f)
        
        assert len(exported_data) == 1
        assert exported_data[0]['task_id'] == sample_task_data['task_id']

class TestErrorRecoveryIntegration:
    """Test error recovery and resilience"""
    
    @pytest.mark.integration
    def test_invalid_data_handling(self, analytics_framework):
        """Test handling of invalid data"""
        # Test with invalid task data
        invalid_task_data = {
            'task_id': 'invalid',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'status': 'InvalidStatus',  # Invalid status
            'priority': 'InvalidPriority',  # Invalid priority
            'category': 'Test',
            'sender_email': 'invalid-email'  # Invalid email format
        }
        
        # Should handle gracefully
        success = analytics_framework.process_task_data(invalid_task_data)
        # The framework should still return True but log the validation error
        assert success == True
    
    @pytest.mark.integration
    def test_persistence_error_handling(self, temp_data_dir):
        """Test persistence error handling"""
        # Create persistence with invalid directory
        invalid_persistence = AnalyticsDataPersistence(data_dir='/invalid/path/that/does/not/exist')
        
        from features.analytics.data_schema import TaskAnalytics
        
        # Try to save data - should handle gracefully
        task_data = {
            'task_id': '1',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'status': 'New',
            'priority': 'Medium',
            'category': 'Test',
            'sender_email': 'test@example.com'
        }
        
        task_analytics = TaskAnalytics.from_dict(task_data)
        success = invalid_persistence.save_task_analytics(task_analytics)
        
        # Should return False due to invalid path
        assert success == False
    
    @pytest.mark.integration
    def test_network_error_simulation(self, test_app):
        """Test network error simulation"""
        # Test with invalid JSON
        response = test_app.post('/api/analytics/collect/task',
                               data='{"invalid": json}',
                               content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    @pytest.mark.integration
    def test_concurrent_access_handling(self, analytics_persistence, sample_task_data):
        """Test concurrent access handling"""
        import threading
        from features.analytics.data_schema import TaskAnalytics
        
        results = []
        errors = []
        
        def save_task(task_id):
            try:
                task_data = sample_task_data.copy()
                task_data['id'] = task_id
                task_analytics = TaskAnalytics.from_dict(task_data)
                success = analytics_persistence.save_task_analytics(task_analytics)
                results.append(success)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=save_task, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all operations succeeded
        assert len(results) == 5
        assert all(results) == True
        assert len(errors) == 0
        
        # Verify all data was saved
        tasks = analytics_persistence.load_task_analytics()
        assert len(tasks) == 5

class TestPerformanceIntegration:
    """Test performance under load"""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_bulk_data_processing(self, analytics_persistence):
        """Test bulk data processing performance"""
        from features.analytics.data_schema import TaskAnalytics
        
        # Create bulk data
        bulk_tasks = []
        for i in range(100):
            task_data = {
                'task_id': str(i),
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat(),
                'status': 'New',
                'priority': 'Medium',
                'category': 'Test',
                'sender_email': f'test{i}@example.com'
            }
            bulk_tasks.append(TaskAnalytics.from_dict(task_data))
        
        # Measure processing time
        start_time = time.time()
        success = analytics_persistence.save_task_analytics(bulk_tasks)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        assert success == True
        assert processing_time < 5.0  # Should complete within 5 seconds
        
        # Verify all data was saved
        tasks = analytics_persistence.load_task_analytics()
        assert len(tasks) == 100
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_api_response_times(self, test_app, sample_task_data):
        """Test API response times under load"""
        response_times = []
        
        # Make multiple API calls
        for i in range(10):
            start_time = time.time()
            response = test_app.get('/api/analytics/health')
            end_time = time.time()
            
            response_times.append(end_time - start_time)
            assert response.status_code == 200
        
        # Calculate average response time
        avg_response_time = sum(response_times) / len(response_times)
        
        # Should respond within reasonable time
        assert avg_response_time < 1.0  # Less than 1 second average
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_memory_usage_under_load(self, analytics_persistence):
        """Test memory usage under load"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Process large amount of data
        from features.analytics.data_schema import TaskAnalytics
        
        for batch in range(10):  # 10 batches of 50 tasks each
            batch_tasks = []
            for i in range(50):
                task_data = {
                    'task_id': str(batch * 50 + i),
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'updated_at': datetime.now(timezone.utc).isoformat(),
                    'status': 'New',
                    'priority': 'Medium',
                    'category': 'Test',
                    'sender_email': f'test{batch * 50 + i}@example.com'
                }
                batch_tasks.append(TaskAnalytics.from_dict(task_data))
            
            analytics_persistence.save_task_analytics(batch_tasks)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024  # 100MB in bytes
