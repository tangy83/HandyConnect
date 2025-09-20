"""
Test Analytics Framework
Tests for the analytics and reporting functionality.
"""

import unittest
import json
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Import analytics components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.task_structure_metadata.task_schema import TaskSchema, TaskStatus, TaskPriority, TaskCategory, TaskMetadata
from features.task_structure_metadata.data_persistence import DataPersistenceManager, DataValidator
from features.performance_reporting.analytics_framework import (
    MetricsCollector, TaskAnalyticsEngine, PerformanceMonitor, AnalyticsDashboard
)
from features.performance_reporting.data_visualization import DataVisualizer
from features.performance_reporting.analytics_api import AnalyticsAPI


class TestTaskSchema(unittest.TestCase):
    """Test task schema functionality"""
    
    def setUp(self):
        self.task = TaskSchema(
            subject="Test Task",
            content="This is a test task",
            status=TaskStatus.NEW,
            priority=TaskPriority.MEDIUM,
            category=TaskCategory.GENERAL
        )
    
    def test_task_creation(self):
        """Test task creation"""
        self.assertEqual(self.task.subject, "Test Task")
        self.assertEqual(self.task.status, TaskStatus.NEW)
        self.assertEqual(self.task.priority, TaskPriority.MEDIUM)
        self.assertIsNotNone(self.task.id)
    
    def test_task_to_dict(self):
        """Test task to dictionary conversion"""
        task_dict = self.task.to_dict()
        self.assertIn('id', task_dict)
        self.assertIn('subject', task_dict)
        self.assertIn('status', task_dict)
        self.assertEqual(task_dict['subject'], "Test Task")
    
    def test_task_from_dict(self):
        """Test task creation from dictionary"""
        task_dict = self.task.to_dict()
        new_task = TaskSchema.from_dict(task_dict)
        self.assertEqual(new_task.subject, self.task.subject)
        self.assertEqual(new_task.status, self.task.status)


class TestDataPersistence(unittest.TestCase):
    """Test data persistence functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.persistence = DataPersistenceManager(self.temp_dir, os.path.join(self.temp_dir, 'backups'))
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_save_and_load_tasks(self):
        """Test saving and loading tasks"""
        tasks = [
            TaskSchema(subject="Task 1", content="Content 1"),
            TaskSchema(subject="Task 2", content="Content 2")
        ]
        
        # Save tasks
        result = self.persistence.save_tasks(tasks)
        self.assertTrue(result)
        
        # Load tasks
        loaded_tasks = self.persistence.load_tasks()
        self.assertEqual(len(loaded_tasks), 2)
        self.assertEqual(loaded_tasks[0].subject, "Task 1")
    
    def test_backup_creation(self):
        """Test backup creation"""
        tasks = [TaskSchema(subject="Test Task", content="Test Content")]
        
        # Save tasks (should create backup)
        self.persistence.save_tasks(tasks)
        
        # Check if backup was created
        backup_files = list(self.persistence.backup_dir.glob("*.json"))
        self.assertGreater(len(backup_files), 0)


class TestMetricsCollector(unittest.TestCase):
    """Test metrics collection functionality"""
    
    def setUp(self):
        self.collector = MetricsCollector()
    
    def test_record_metric(self):
        """Test recording metrics"""
        self.collector.record_metric("test_metric", 100.0, "gauge")
        self.assertEqual(len(self.collector.metrics), 1)
        self.assertEqual(self.collector.metrics[0].name, "test_metric")
        self.assertEqual(self.collector.metrics[0].value, 100.0)
    
    def test_record_counter(self):
        """Test recording counter metrics"""
        self.collector.record_counter("test_counter", 5.0)
        self.assertEqual(len(self.collector.metrics), 1)
        self.assertEqual(self.collector.metrics[0].metric_type.value, "counter")
    
    def test_get_aggregated_metrics(self):
        """Test getting aggregated metrics"""
        # Record some metrics
        self.collector.record_gauge("test_gauge", 10.0)
        self.collector.record_gauge("test_gauge", 20.0)
        self.collector.record_gauge("test_gauge", 30.0)
        
        # Get aggregated metrics
        aggregated = self.collector.get_aggregated_metrics()
        self.assertIn("test_gauge", aggregated)
        self.assertEqual(aggregated["test_gauge"]["count"], 3)
        self.assertEqual(aggregated["test_gauge"]["avg"], 20.0)


class TestTaskAnalyticsEngine(unittest.TestCase):
    """Test task analytics engine"""
    
    def setUp(self):
        self.collector = MetricsCollector()
        self.engine = TaskAnalyticsEngine(self.collector)
    
    def test_analyze_tasks(self):
        """Test task analysis"""
        tasks = [
            TaskSchema(
                subject="Task 1",
                content="Content 1",
                status=TaskStatus.NEW,
                priority=TaskPriority.HIGH,
                category=TaskCategory.TECHNICAL
            ),
            TaskSchema(
                subject="Task 2",
                content="Content 2",
                status=TaskStatus.COMPLETED,
                priority=TaskPriority.MEDIUM,
                category=TaskCategory.GENERAL,
                resolved_at=datetime.utcnow()
            )
        ]
        
        analytics = self.engine.analyze_tasks(tasks)
        
        self.assertEqual(analytics.total_tasks, 2)
        self.assertEqual(analytics.tasks_by_status["New"], 1)
        self.assertEqual(analytics.tasks_by_status["Completed"], 1)
        self.assertEqual(analytics.tasks_by_priority["High"], 1)
        self.assertEqual(analytics.tasks_by_priority["Medium"], 1)


class TestDataVisualizer(unittest.TestCase):
    """Test data visualization functionality"""
    
    def setUp(self):
        self.visualizer = DataVisualizer()
    
    def test_create_task_status_chart(self):
        """Test creating task status chart"""
        tasks = [
            TaskSchema(subject="Task 1", status=TaskStatus.NEW),
            TaskSchema(subject="Task 2", status=TaskStatus.COMPLETED),
            TaskSchema(subject="Task 3", status=TaskStatus.IN_PROGRESS)
        ]
        
        chart = self.visualizer.create_task_status_chart(tasks)
        
        self.assertEqual(chart.chart_type.value, "pie")
        self.assertEqual(chart.title, "Task Status Distribution")
        self.assertIn("labels", chart.data)
        self.assertIn("datasets", chart.data)
    
    def test_create_priority_chart(self):
        """Test creating priority chart"""
        tasks = [
            TaskSchema(subject="Task 1", priority=TaskPriority.HIGH),
            TaskSchema(subject="Task 2", priority=TaskPriority.MEDIUM),
            TaskSchema(subject="Task 3", priority=TaskPriority.LOW)
        ]
        
        chart = self.visualizer.create_priority_chart(tasks)
        
        self.assertEqual(chart.chart_type.value, "bar")
        self.assertEqual(chart.title, "Task Priority Distribution")
        self.assertIn("labels", chart.data)
    
    def test_generate_dashboard_charts(self):
        """Test generating all dashboard charts"""
        tasks = [
            TaskSchema(subject="Task 1", status=TaskStatus.NEW, priority=TaskPriority.HIGH),
            TaskSchema(subject="Task 2", status=TaskStatus.COMPLETED, priority=TaskPriority.MEDIUM)
        ]
        
        charts = self.visualizer.generate_dashboard_charts(tasks)
        
        expected_charts = [
            'task_status', 'priority_distribution', 'category_distribution',
            'resolution_time_trends', 'sla_compliance', 'task_trends', 'activity_heatmap'
        ]
        
        for chart_name in expected_charts:
            self.assertIn(chart_name, charts)


class TestAnalyticsAPI(unittest.TestCase):
    """Test analytics API functionality"""
    
    def setUp(self):
        self.api = AnalyticsAPI()
    
    def test_api_initialization(self):
        """Test API initialization"""
        self.assertIsNotNone(self.api.blueprint)
        self.assertIsNotNone(self.api.data_persistence)
        self.assertIsNotNone(self.api.metrics_collector)
        self.assertIsNotNone(self.api.task_analytics_engine)
    
    @patch('features.performance_reporting.analytics_api.DataPersistenceManager')
    def test_dashboard_data_generation(self, mock_persistence):
        """Test dashboard data generation"""
        # Mock the data persistence
        mock_persistence.return_value.load_tasks.return_value = [
            TaskSchema(subject="Test Task", content="Test Content")
        ]
        
        # This would test the actual API endpoint if we had a Flask test client
        # For now, we just test the components work together
        self.assertIsNotNone(self.api.analytics_dashboard)


class TestDataValidator(unittest.TestCase):
    """Test data validation functionality"""
    
    def test_validate_data_integrity(self):
        """Test data integrity validation"""
        tasks = [
            TaskSchema(subject="Valid Task", content="Valid content"),
            TaskSchema(subject="", content="Invalid task with empty subject")
        ]
        
        results = DataValidator.validate_data_integrity(tasks)
        
        self.assertEqual(results['total_tasks'], 2)
        self.assertEqual(results['valid_tasks'], 1)
        self.assertEqual(results['invalid_tasks'], 1)
        self.assertGreater(len(results['errors']), 0)
    
    def test_repair_data_issues(self):
        """Test data repair functionality"""
        tasks = [
            TaskSchema(id="duplicate_id", subject="Task 1"),
            TaskSchema(id="duplicate_id", subject="Task 2")  # Duplicate ID
        ]
        
        repaired_tasks, repair_log = DataValidator.repair_data_issues(tasks)
        
        self.assertEqual(len(repaired_tasks), 2)
        self.assertNotEqual(repaired_tasks[0].id, repaired_tasks[1].id)
        self.assertGreater(len(repair_log), 0)


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestTaskSchema,
        TestDataPersistence,
        TestMetricsCollector,
        TestTaskAnalyticsEngine,
        TestDataVisualizer,
        TestAnalyticsAPI,
        TestDataValidator
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Analytics Tests Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")
