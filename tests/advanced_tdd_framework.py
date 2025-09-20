"""
Advanced TDD Framework for HandyConnect Application
Author: AI Assistant
Date: September 20, 2025

This module provides advanced TDD utilities, fixtures, and base classes
for comprehensive testing across all application phases.
"""

import pytest
import asyncio
import time
import logging
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import json
import tempfile
import os
from pathlib import Path

# Test Data Classes
@dataclass
class TestScenario:
    """Represents a test scenario with setup, execution, and validation"""
    name: str
    description: str
    setup_data: Dict[str, Any]
    expected_result: Any
    validation_func: Optional[Callable] = None
    cleanup_func: Optional[Callable] = None

@dataclass
class PerformanceMetrics:
    """Performance metrics for tests"""
    execution_time: float
    memory_usage: float
    cpu_usage: float
    api_calls: int
    database_queries: int = 0

class AdvancedTestBase:
    """Base class for advanced TDD tests with common utilities"""
    
    def setup_method(self, method):
        """Setup method called before each test"""
        self.start_time = time.time()
        self.test_data = {}
        self.mocks = []
        
    def teardown_method(self, method):
        """Cleanup method called after each test"""
        # Clean up all mocks
        for mock in self.mocks:
            if hasattr(mock, 'stop'):
                mock.stop()
        
        # Log execution time
        execution_time = time.time() - self.start_time
        logging.info(f"Test {method.__name__} completed in {execution_time:.2f}s")
    
    def create_mock(self, target: str, **kwargs) -> Mock:
        """Create and register a mock for automatic cleanup"""
        mock = patch(target, **kwargs)
        self.mocks.append(mock)
        return mock.start()
    
    def assert_performance(self, max_time: float = 1.0, max_memory: float = 100.0):
        """Assert performance metrics"""
        execution_time = time.time() - self.start_time
        assert execution_time < max_time, f"Test took {execution_time:.2f}s, expected < {max_time}s"
    
    def create_test_data(self, data_type: str, **kwargs) -> Dict[str, Any]:
        """Create standardized test data"""
        if data_type == "task":
            return {
                "id": kwargs.get("id", "test-task-1"),
                "task_id": kwargs.get("task_id", "test-task-1"),
                "subject": kwargs.get("subject", "Test Task"),
                "status": kwargs.get("status", "New"),
                "priority": kwargs.get("priority", "Medium"),
                "category": kwargs.get("category", "General Inquiry"),
                "sender_email": kwargs.get("sender_email", "test@example.com"),
                "created_at": kwargs.get("created_at", datetime.now(timezone.utc).isoformat()),
                "updated_at": kwargs.get("updated_at", datetime.now(timezone.utc).isoformat()),
                "tags": kwargs.get("tags", ["test"]),
                "metadata": kwargs.get("metadata", {"source": "test"})
            }
        elif data_type == "thread":
            return {
                "id": kwargs.get("id", "test-thread-1"),
                "thread_id": kwargs.get("thread_id", "test-thread-1"),
                "status": kwargs.get("status", "Active"),
                "priority": kwargs.get("priority", "Medium"),
                "message_count": kwargs.get("message_count", 1),
                "participant_count": kwargs.get("participant_count", 2),
                "created_at": kwargs.get("created_at", datetime.now(timezone.utc).isoformat()),
                "updated_at": kwargs.get("updated_at", datetime.now(timezone.utc).isoformat()),
                "tags": kwargs.get("tags", ["test"])
            }
        elif data_type == "email":
            return {
                "id": kwargs.get("id", "test-email-1"),
                "subject": kwargs.get("subject", "Test Email"),
                "sender": {
                    "name": kwargs.get("sender_name", "Test User"),
                    "email": kwargs.get("sender_email", "test@example.com")
                },
                "body": kwargs.get("body", "This is a test email"),
                "receivedDateTime": kwargs.get("received", datetime.now(timezone.utc).isoformat()),
                "hasAttachments": kwargs.get("has_attachments", False)
            }
        else:
            return kwargs

class AsyncTestBase(AdvancedTestBase):
    """Base class for async tests"""
    
    def setup_method(self, method):
        super().setup_method(method)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def teardown_method(self, method):
        if self.loop and not self.loop.is_closed():
            self.loop.close()
        super().teardown_method(method)
    
    async def run_async_test(self, coro):
        """Run an async test with proper setup"""
        return await coro

class APITestBase(AdvancedTestBase):
    """Base class for API tests with common utilities"""
    
    def setup_method(self, method):
        super().setup_method(method)
        self.client = None
        self.base_url = "http://localhost:5001"
    
    def assert_api_response(self, response, expected_status: int = 200, 
                          expected_keys: List[str] = None):
        """Assert API response format and content"""
        assert response.status_code == expected_status, \
            f"Expected status {expected_status}, got {response.status_code}"
        
        if response.content_type and 'application/json' in response.content_type:
            data = response.get_json()
            if expected_keys:
                for key in expected_keys:
                    assert key in data, f"Missing key '{key}' in response"
            return data
        return response.data
    
    def assert_error_response(self, response, expected_status: int = 400):
        """Assert error response format"""
        assert response.status_code == expected_status
        data = response.get_json()
        assert "error" in data or "message" in data

class PerformanceTestBase(AdvancedTestBase):
    """Base class for performance tests"""
    
    def setup_method(self, method):
        super().setup_method(method)
        self.metrics = []
    
    def measure_performance(self, func: Callable, *args, **kwargs) -> PerformanceMetrics:
        """Measure performance metrics for a function"""
        import psutil
        import gc
        
        # Force garbage collection before measurement
        gc.collect()
        
        # Get initial metrics
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_cpu = process.cpu_percent()
        
        # Execute function
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # Get final metrics
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        final_cpu = process.cpu_percent()
        
        metrics = PerformanceMetrics(
            execution_time=execution_time,
            memory_usage=final_memory - initial_memory,
            cpu_usage=final_cpu - initial_cpu,
            api_calls=0  # To be implemented based on mocking
        )
        
        self.metrics.append(metrics)
        return metrics
    
    def assert_performance_threshold(self, metrics: PerformanceMetrics,
                                   max_time: float = 1.0,
                                   max_memory: float = 50.0,
                                   max_cpu: float = 80.0):
        """Assert performance thresholds"""
        assert metrics.execution_time < max_time, \
            f"Execution time {metrics.execution_time:.2f}s exceeds threshold {max_time}s"
        assert metrics.memory_usage < max_memory, \
            f"Memory usage {metrics.memory_usage:.2f}MB exceeds threshold {max_memory}MB"
        assert metrics.cpu_usage < max_cpu, \
            f"CPU usage {metrics.cpu_usage:.2f}% exceeds threshold {max_cpu}%"

# Advanced Fixtures
@pytest.fixture(scope="session")
def advanced_test_config():
    """Advanced test configuration"""
    return {
        "test_timeout": 30,
        "performance_thresholds": {
            "api_response_time": 1.0,
            "database_query_time": 0.5,
            "memory_usage_mb": 100.0,
            "cpu_usage_percent": 80.0
        },
        "test_data_dir": "tests/data",
        "mock_services": True,
        "coverage_threshold": 90
    }

@pytest.fixture(scope="function")
def test_scenario_factory():
    """Factory for creating test scenarios"""
    def _create_scenario(name: str, description: str, **kwargs) -> TestScenario:
        return TestScenario(
            name=name,
            description=description,
            setup_data=kwargs.get("setup_data", {}),
            expected_result=kwargs.get("expected_result", None),
            validation_func=kwargs.get("validation_func", None),
            cleanup_func=kwargs.get("cleanup_func", None)
        )
    return _create_scenario

@pytest.fixture(scope="function")
def performance_monitor():
    """Performance monitoring fixture"""
    monitor = PerformanceTestBase()
    monitor.setup_method(None)
    yield monitor
    monitor.teardown_method(None)

@pytest.fixture(scope="function")
def mock_factory():
    """Factory for creating mocks with automatic cleanup"""
    mocks = []
    
    def _create_mock(target: str, **kwargs) -> Mock:
        mock = patch(target, **kwargs)
        mocks.append(mock)
        return mock.start()
    
    yield _create_mock
    
    # Cleanup
    for mock in mocks:
        if hasattr(mock, 'stop'):
            mock.stop()

# Test Utilities
def run_test_scenarios(scenarios: List[TestScenario], test_func: Callable):
    """Run multiple test scenarios"""
    results = []
    for scenario in scenarios:
        try:
            # Setup
            if scenario.setup_data:
                test_func.setup_data = scenario.setup_data
            
            # Execute
            result = test_func(scenario)
            
            # Validate
            if scenario.validation_func:
                scenario.validation_func(result)
            
            results.append({"scenario": scenario.name, "status": "PASS", "result": result})
            
        except Exception as e:
            results.append({"scenario": scenario.name, "status": "FAIL", "error": str(e)})
        
        finally:
            # Cleanup
            if scenario.cleanup_func:
                scenario.cleanup_func()
    
    return results

def generate_test_report(test_results: List[Dict], output_file: str = "test_report.json"):
    """Generate detailed test report"""
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_tests": len(test_results),
        "passed": len([r for r in test_results if r["status"] == "PASS"]),
        "failed": len([r for r in test_results if r["status"] == "FAIL"]),
        "results": test_results
    }
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report

# Decorators
def performance_test(max_time: float = 1.0, max_memory: float = 50.0):
    """Decorator for performance tests"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            base = PerformanceTestBase()
            base.setup_method(func)
            
            try:
                metrics = base.measure_performance(func, *args, **kwargs)
                base.assert_performance_threshold(metrics, max_time, max_memory)
                return func(*args, **kwargs)
            finally:
                base.teardown_method(func)
        return wrapper
    return decorator

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry tests on failure"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(delay)
        return wrapper
    return decorator

def skip_if_condition(condition: Callable, reason: str = "Condition not met"):
    """Decorator to skip tests based on condition"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if condition():
                pytest.skip(reason)
            return func(*args, **kwargs)
        return wrapper
    return decorator
