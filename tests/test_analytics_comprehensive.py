"""
Comprehensive tests for the Analytics system
"""
import pytest
import json
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch

from features.analytics.data_schema import (
    TaskAnalytics, ThreadAnalytics, PerformanceMetric, 
    SystemHealth, UserBehavior, DataValidator
)
from features.analytics.data_persistence import AnalyticsDataPersistence
from features.analytics.analytics_framework import AnalyticsFramework, DataAggregator
from features.analytics.performance_metrics import PerformanceMonitor
from features.analytics.data_visualization import DataVisualization

class TestDataSchema:
    """Test data schema validation and data classes"""
    
    @pytest.mark.unit
    @pytest.mark.analytics
    def test_task_analytics_creation(self, sample_task_data):
        """Test TaskAnalytics data class creation"""
        analytics = TaskAnalytics.from_dict(sample_task_data)
        
        assert analytics.task_id == sample_task_data['task_id']
        assert analytics.status == sample_task_data['status']
        assert analytics.priority == sample_task_data['priority']
        assert analytics.category == sample_task_data['category']
        assert analytics.sender_email == sample_task_data['sender_email']
        assert analytics.tags == sample_task_data['tags']
        assert analytics.metadata == sample_task_data['metadata']
    
    @pytest.mark.unit
    @pytest.mark.analytics
    def test_task_analytics_validation(self, sample_task_data):
        """Test TaskAnalytics validation"""
        analytics = TaskAnalytics.from_dict(sample_task_data)
        assert analytics.validate() == True
        
        # Test invalid data
        invalid_data = sample_task_data.copy()
        invalid_data['status'] = 'InvalidStatus'
        invalid_analytics = TaskAnalytics.from_dict(invalid_data)
        assert invalid_analytics.validate() == False
    
    @pytest.mark.unit
    @pytest.mark.analytics
    def test_thread_analytics_creation(self, sample_thread_data):
        """Test ThreadAnalytics data class creation"""
        analytics = ThreadAnalytics.from_dict(sample_thread_data)
        
        assert analytics.thread_id == sample_thread_data['thread_id']
        assert analytics.status == sample_thread_data['status']
        assert analytics.priority == sample_thread_data['priority']
        assert analytics.message_count == sample_thread_data['message_count']
        assert analytics.participant_count == sample_thread_data['participant_count']
    
    @pytest.mark.unit
    @pytest.mark.analytics
    def test_performance_metric_creation(self, sample_performance_metrics):
        """Test PerformanceMetric data class creation"""
        for metric_data in sample_performance_metrics:
            metric = PerformanceMetric.from_dict(metric_data)
            
            assert metric.metric_type == metric_data['metric_type']
            assert metric.value == metric_data['value']
            assert metric.unit == metric_data['unit']
            assert metric.category == metric_data['category']
            assert metric.validate() == True
    
    @pytest.mark.unit
    @pytest.mark.analytics
    def test_system_health_creation(self, sample_system_health):
        """Test SystemHealth data class creation"""
        health = SystemHealth.from_dict(sample_system_health)
        
        assert health.service_name == sample_system_health['service_name']
        assert health.status == sample_system_health['status']
        assert health.response_time_ms == sample_system_health['response_time_ms']
        assert health.cpu_usage == sample_system_health['cpu_usage']
        assert health.validate() == True
    
    @pytest.mark.unit
    @pytest.mark.analytics
    def test_user_behavior_creation(self, sample_user_behavior):
        """Test UserBehavior data class creation"""
        behavior = UserBehavior.from_dict(sample_user_behavior)
        
        assert behavior.user_id == sample_user_behavior['user_id']
        assert behavior.session_id == sample_user_behavior['session_id']
        assert behavior.action == sample_user_behavior['action']
        assert behavior.page == sample_user_behavior['page']
        assert behavior.duration_seconds == sample_user_behavior['duration_seconds']
        assert behavior.validate() == True
    
    @pytest.mark.unit
    @pytest.mark.analytics
    def test_data_validator(self):
        """Test DataValidator utility"""
        # Test valid data
        valid_data = {
            'task_id': '123',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'status': 'New',
            'priority': 'Medium',
            'category': 'General Inquiry',
            'sender_email': 'test@example.com'
        }
        
        is_valid, error = DataValidator.validate_data(valid_data, 'task_analytics')
        assert is_valid == True
        assert error is None
        
        # Test invalid data
        invalid_data = valid_data.copy()
        invalid_data['status'] = 'InvalidStatus'
        
        is_valid, error = DataValidator.validate_data(invalid_data, 'task_analytics')
        assert is_valid == False
        assert error is not None

class TestDataPersistence:
    """Test data persistence functionality"""
    
    @pytest.mark.integration
    @pytest.mark.analytics
    def test_save_and_load_task_analytics(self, analytics_persistence, sample_task_data):
        """Test saving and loading task analytics"""
        from features.analytics.data_schema import TaskAnalytics
        
        # Create analytics object
        analytics = TaskAnalytics.from_dict(sample_task_data)
        
        # Save analytics
        success = analytics_persistence.save_task_analytics(analytics)
        assert success == True
        
        # Load analytics
        loaded_analytics = analytics_persistence.load_task_analytics()
        assert len(loaded_analytics) == 1
        assert loaded_analytics[0].task_id == analytics.task_id
        assert loaded_analytics[0].status == analytics.status
    
    @pytest.mark.integration
    @pytest.mark.analytics
    def test_save_and_load_thread_analytics(self, analytics_persistence, sample_thread_data):
        """Test saving and loading thread analytics"""
        from features.analytics.data_schema import ThreadAnalytics
        
        # Create analytics object
        analytics = ThreadAnalytics.from_dict(sample_thread_data)
        
        # Save analytics
        success = analytics_persistence.save_thread_analytics(analytics)
        assert success == True
        
        # Load analytics
        loaded_analytics = analytics_persistence.load_thread_analytics()
        assert len(loaded_analytics) == 1
        assert loaded_analytics[0].thread_id == analytics.thread_id
        assert loaded_analytics[0].message_count == analytics.message_count
    
    @pytest.mark.integration
    @pytest.mark.analytics
    def test_save_and_load_performance_metrics(self, analytics_persistence, sample_performance_metrics):
        """Test saving and loading performance metrics"""
        from features.analytics.data_schema import PerformanceMetric
        
        # Create metrics objects
        metrics = [PerformanceMetric.from_dict(data) for data in sample_performance_metrics]
        
        # Save metrics
        success = analytics_persistence.save_performance_metrics(metrics)
        assert success == True
        
        # Load metrics
        loaded_metrics = analytics_persistence.load_performance_metrics()
        assert len(loaded_metrics) == len(metrics)
        assert loaded_metrics[0].metric_type == metrics[0].metric_type
    
    @pytest.mark.integration
    @pytest.mark.analytics
    def test_save_and_load_system_health(self, analytics_persistence, sample_system_health):
        """Test saving and loading system health data"""
        from features.analytics.data_schema import SystemHealth
        
        # Create health object
        health = SystemHealth.from_dict(sample_system_health)
        
        # Save health data
        success = analytics_persistence.save_system_health(health)
        assert success == True
        
        # Load health data
        loaded_health = analytics_persistence.load_system_health()
        assert len(loaded_health) == 1
        assert loaded_health[0].service_name == health.service_name
        assert loaded_health[0].status == health.status
    
    @pytest.mark.integration
    @pytest.mark.analytics
    def test_save_and_load_user_behavior(self, analytics_persistence, sample_user_behavior):
        """Test saving and loading user behavior data"""
        from features.analytics.data_schema import UserBehavior
        
        # Create behavior object
        behavior = UserBehavior.from_dict(sample_user_behavior)
        
        # Save behavior data
        success = analytics_persistence.save_user_behavior(behavior)
        assert success == True
        
        # Load behavior data
        loaded_behavior = analytics_persistence.load_user_behavior()
        assert len(loaded_behavior) == 1
        assert loaded_behavior[0].user_id == behavior.user_id
        assert loaded_behavior[0].action == behavior.action
    
    @pytest.mark.integration
    @pytest.mark.analytics
    def test_data_export(self, analytics_persistence, sample_task_data):
        """Test data export functionality"""
        from features.analytics.data_schema import TaskAnalytics
        
        # Create and save analytics
        analytics = TaskAnalytics.from_dict(sample_task_data)
        analytics_persistence.save_task_analytics(analytics)
        
        # Export data
        export_file = analytics_persistence.export_data('tasks')
        assert os.path.exists(export_file)
        
        # Verify exported data
        with open(export_file, 'r') as f:
            exported_data = json.load(f)
        
        assert len(exported_data) == 1
        assert exported_data[0]['task_id'] == sample_task_data['task_id']
    
    @pytest.mark.integration
    @pytest.mark.analytics
    def test_storage_stats(self, analytics_persistence, sample_task_data):
        """Test storage statistics"""
        from features.analytics.data_schema import TaskAnalytics
        
        # Create and save analytics
        analytics = TaskAnalytics.from_dict(sample_task_data)
        analytics_persistence.save_task_analytics(analytics)
        
        # Get storage stats
        stats = analytics_persistence.get_storage_stats()
        
        assert 'total_size_mb' in stats
        assert 'file_counts' in stats
        assert 'tasks' in stats['file_counts']
        assert stats['file_counts']['tasks'] >= 1

class TestAnalyticsFramework:
    """Test analytics framework functionality"""
    
    @pytest.mark.integration
    @pytest.mark.analytics
    def test_analytics_framework_initialization(self, analytics_config, analytics_persistence):
        """Test analytics framework initialization"""
        framework = AnalyticsFramework(analytics_config)
        framework.persistence = analytics_persistence
        
        assert framework.config == analytics_config
        assert framework.persistence == analytics_persistence
        assert framework.collector is not None
        assert framework.aggregator is not None
    
    @pytest.mark.integration
    @pytest.mark.analytics
    def test_task_data_processing(self, analytics_framework, sample_task_data):
        """Test task data processing"""
        success = analytics_framework.process_task_data(sample_task_data)
        assert success == True
        
        # Verify data was saved
        tasks = analytics_framework.persistence.load_task_analytics()
        assert len(tasks) == 1
        assert tasks[0].task_id == sample_task_data['task_id']
    
    @pytest.mark.integration
    @pytest.mark.analytics
    def test_thread_data_processing(self, analytics_framework, sample_thread_data):
        """Test thread data processing"""
        success = analytics_framework.process_thread_data(sample_thread_data)
        assert success == True
        
        # Verify data was saved
        threads = analytics_framework.persistence.load_thread_analytics()
        assert len(threads) == 1
        assert threads[0].thread_id == sample_thread_data['thread_id']
    
    @pytest.mark.integration
    @pytest.mark.analytics
    def test_user_behavior_tracking(self, analytics_framework, sample_user_behavior):
        """Test user behavior tracking"""
        success = analytics_framework.track_user_behavior(
            user_id=sample_user_behavior['user_id'],
            session_id=sample_user_behavior['session_id'],
            action=sample_user_behavior['action'],
            page=sample_user_behavior['page'],
            duration_seconds=sample_user_behavior['duration_seconds']
        )
        assert success == True
        
        # Verify data was saved
        behavior = analytics_framework.persistence.load_user_behavior()
        assert len(behavior) == 1
        assert behavior[0].user_id == sample_user_behavior['user_id']
    
    @pytest.mark.integration
    @pytest.mark.analytics
    def test_analytics_report_generation(self, analytics_framework, sample_task_data, sample_thread_data):
        """Test analytics report generation"""
        # Process some data
        analytics_framework.process_task_data(sample_task_data)
        analytics_framework.process_thread_data(sample_thread_data)
        
        # Generate report
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=1)
        
        report = analytics_framework.get_analytics_report(start_date, end_date)
        
        assert 'task_analytics' in report
        assert 'thread_analytics' in report
        assert 'performance_metrics' in report
        assert 'system_health' in report
        assert 'report_period' in report

class TestDataAggregator:
    """Test data aggregation functionality"""
    
    @pytest.mark.integration
    @pytest.mark.analytics
    def test_task_metrics_aggregation(self, analytics_persistence, sample_task_data):
        """Test task metrics aggregation"""
        from features.analytics.data_schema import TaskAnalytics
        
        # Create and save multiple task analytics
        for i in range(5):
            task_data = sample_task_data.copy()
            task_data['task_id'] = str(i)
            task_data['status'] = 'New' if i % 2 == 0 else 'Completed'
            task_data['priority'] = 'High' if i % 3 == 0 else 'Medium'
            
            analytics = TaskAnalytics.from_dict(task_data)
            analytics_persistence.save_task_analytics(analytics)
        
        # Test aggregation
        aggregator = DataAggregator(analytics_persistence)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=1)
        
        aggregated = aggregator.aggregate_task_metrics(start_date, end_date)
        
        assert aggregated['total_tasks'] == 5
        assert 'status_distribution' in aggregated
        assert 'priority_distribution' in aggregated
        assert aggregated['status_distribution']['New'] == 3
        assert aggregated['status_distribution']['Completed'] == 2
    
    @pytest.mark.integration
    @pytest.mark.analytics
    def test_thread_metrics_aggregation(self, analytics_persistence, sample_thread_data):
        """Test thread metrics aggregation"""
        from features.analytics.data_schema import ThreadAnalytics
        
        # Create and save multiple thread analytics
        for i in range(3):
            thread_data = sample_thread_data.copy()
            thread_data['thread_id'] = str(i)
            thread_data['status'] = 'Active' if i % 2 == 0 else 'Resolved'
            thread_data['message_count'] = i + 1
            
            analytics = ThreadAnalytics.from_dict(thread_data)
            analytics_persistence.save_thread_analytics(analytics)
        
        # Test aggregation
        aggregator = DataAggregator(analytics_persistence)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=1)
        
        aggregated = aggregator.aggregate_thread_metrics(start_date, end_date)
        
        assert aggregated['total_threads'] == 3
        assert aggregated['total_messages'] == 6  # 1+2+3
        assert 'status_distribution' in aggregated
        assert aggregated['status_distribution']['Active'] == 2
        assert aggregated['status_distribution']['Resolved'] == 1

class TestPerformanceMonitor:
    """Test performance monitoring functionality"""
    
    @pytest.mark.integration
    @pytest.mark.performance
    def test_performance_monitor_initialization(self, analytics_persistence):
        """Test performance monitor initialization"""
        monitor = PerformanceMonitor(analytics_persistence)
        
        assert monitor.persistence == analytics_persistence
        assert monitor._thresholds is not None
        assert len(monitor._thresholds) > 0
    
    @pytest.mark.integration
    @pytest.mark.performance
    def test_custom_metric_recording(self, performance_monitor):
        """Test custom metric recording"""
        # Record a custom metric
        performance_monitor.record_custom_metric(
            metric_type='test_metric',
            value=42.5,
            unit='test_units',
            category='test'
        )
        
        # Verify metric was recorded
        assert len(performance_monitor._metrics_buffer) == 1
        metric = performance_monitor._metrics_buffer[0]
        assert metric.metric_type == 'test_metric'
        assert metric.value == 42.5
        assert metric.unit == 'test_units'
    
    @pytest.mark.integration
    @pytest.mark.performance
    def test_threshold_setting(self, performance_monitor):
        """Test threshold setting"""
        # Set a custom threshold
        performance_monitor.set_threshold(
            metric_type='test_metric',
            warning_threshold=50.0,
            critical_threshold=75.0,
            unit='test_units',
            description='Test metric threshold'
        )
        
        # Verify threshold was set
        assert 'test_metric' in performance_monitor._thresholds
        threshold = performance_monitor._thresholds['test_metric']
        assert threshold.warning_threshold == 50.0
        assert threshold.critical_threshold == 75.0
    
    @pytest.mark.integration
    @pytest.mark.performance
    def test_metrics_summary(self, performance_monitor, sample_performance_metrics):
        """Test metrics summary generation"""
        from features.analytics.data_schema import PerformanceMetric
        
        # Add some metrics to the buffer
        for metric_data in sample_performance_metrics:
            metric = PerformanceMetric.from_dict(metric_data)
            performance_monitor._metrics_buffer.append(metric)
        
        # Process metrics buffer
        performance_monitor._process_metrics_buffer()
        
        # Get summary
        summary = performance_monitor.get_metrics_summary(hours=24)
        
        assert 'total_metrics' in summary
        assert 'metrics_by_type' in summary
        assert summary['total_metrics'] >= len(sample_performance_metrics)
    
    @pytest.mark.integration
    @pytest.mark.performance
    def test_current_metrics(self, performance_monitor):
        """Test current metrics retrieval"""
        with patch('psutil.cpu_percent', return_value=45.2), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk:
            
            # Mock memory and disk objects
            mock_memory.return_value.percent = 60.5
            mock_memory.return_value.available = 2 * 1024**3  # 2GB
            mock_disk.return_value.used = 75 * 1024**3  # 75GB
            mock_disk.return_value.total = 100 * 1024**3  # 100GB
            mock_disk.return_value.free = 25 * 1024**3  # 25GB
            
            current_metrics = performance_monitor.get_current_metrics()
            
            assert 'timestamp' in current_metrics
            assert 'system' in current_metrics
            assert 'application' in current_metrics
            assert 'thresholds' in current_metrics
            assert current_metrics['system']['cpu_usage_percent'] == 45.2
            assert current_metrics['system']['memory_usage_percent'] == 60.5

class TestDataVisualization:
    """Test data visualization functionality"""
    
    @pytest.mark.integration
    @pytest.mark.analytics
    def test_data_visualization_initialization(self, analytics_persistence):
        """Test data visualization initialization"""
        visualization = DataVisualization(analytics_persistence)
        
        assert visualization.persistence == analytics_persistence
        assert visualization.aggregator is not None
        assert visualization.color_palettes is not None
    
    @pytest.mark.integration
    @pytest.mark.analytics
    def test_task_status_chart_generation(self, analytics_persistence, sample_task_data):
        """Test task status chart generation"""
        from features.analytics.data_schema import TaskAnalytics
        
        # Create and save task analytics
        analytics = TaskAnalytics.from_dict(sample_task_data)
        analytics_persistence.save_task_analytics(analytics)
        
        # Generate chart
        visualization = DataVisualization(analytics_persistence)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=1)
        
        chart_config = visualization.generate_task_status_chart(start_date, end_date)
        
        assert 'type' in chart_config
        assert 'data' in chart_config
        assert 'options' in chart_config
        assert chart_config['type'] == 'doughnut'
        assert 'labels' in chart_config['data']
        assert 'datasets' in chart_config['data']
    
    @pytest.mark.integration
    @pytest.mark.analytics
    def test_priority_distribution_chart_generation(self, analytics_persistence, sample_task_data):
        """Test priority distribution chart generation"""
        from features.analytics.data_schema import TaskAnalytics
        
        # Create and save task analytics
        analytics = TaskAnalytics.from_dict(sample_task_data)
        analytics_persistence.save_task_analytics(analytics)
        
        # Generate chart
        visualization = DataVisualization(analytics_persistence)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=1)
        
        chart_config = visualization.generate_priority_distribution_chart(start_date, end_date)
        
        assert 'type' in chart_config
        assert chart_config['type'] == 'bar'
        assert 'data' in chart_config
        assert 'options' in chart_config
    
    @pytest.mark.integration
    @pytest.mark.analytics
    def test_dashboard_charts_generation(self, analytics_persistence, sample_task_data):
        """Test dashboard charts generation"""
        from features.analytics.data_schema import TaskAnalytics
        
        # Create and save task analytics
        analytics = TaskAnalytics.from_dict(sample_task_data)
        analytics_persistence.save_task_analytics(analytics)
        
        # Generate all charts
        visualization = DataVisualization(analytics_persistence)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=1)
        
        charts_data = visualization.generate_dashboard_charts(start_date, end_date)
        
        assert 'charts' in charts_data
        assert 'generated_at' in charts_data
        assert 'period' in charts_data
        
        charts = charts_data['charts']
        expected_charts = [
            'task_status', 'priority_distribution', 'response_time_trend',
            'performance_metrics', 'system_health', 'category_breakdown',
            'escalation_trend'
        ]
        
        for chart_name in expected_charts:
            assert chart_name in charts
