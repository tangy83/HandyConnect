"""
Pytest configuration and fixtures for HandyConnect application
"""
import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch
from datetime import datetime, timezone
import json

# Add the parent directory to the Python path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from features.core_services.email_service import EmailService
from features.core_services.llm_service import LLMService
from features.core_services.task_service import TaskService
from features.analytics.analytics_framework import AnalyticsFramework, AnalyticsConfig
from features.analytics.data_persistence import AnalyticsDataPersistence
from features.analytics.performance_metrics import PerformanceMonitor

@pytest.fixture(scope="session")
def test_app():
    """Create test Flask application"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        yield client

@pytest.fixture(scope="function")
def temp_data_dir():
    """Create temporary data directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="function")
def mock_env_vars():
    """Mock environment variables for testing"""
    with patch.dict(os.environ, {
        'CLIENT_ID': 'test_client_id',
        'CLIENT_SECRET': 'test_client_secret',
        'TENANT_ID': 'test_tenant_id',
        'OPENAI_API_KEY': 'test_openai_key',
        'SECRET_KEY': 'test_secret_key'
    }):
        yield

@pytest.fixture(scope="function")
def mock_email_service():
    """Mock email service"""
    mock_service = Mock(spec=EmailService)
    mock_service.get_access_token.return_value = "mock_access_token"
    mock_service.get_emails.return_value = []
    return mock_service

@pytest.fixture(scope="function")
def mock_llm_service():
    """Mock LLM service"""
    mock_service = Mock(spec=LLMService)
    mock_service.process_email.return_value = {
        'category': 'General Inquiry',
        'priority': 'Medium',
        'summary': 'Test email summary'
    }
    return mock_service

@pytest.fixture(scope="function")
def mock_task_service():
    """Mock task service"""
    mock_service = Mock(spec=TaskService)
    mock_service.create_task.return_value = {
        'id': 1,
        'subject': 'Test Task',
        'status': 'New',
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    return mock_service

@pytest.fixture(scope="function")
def analytics_config():
    """Create analytics configuration for testing"""
    return AnalyticsConfig(
        collection_interval_seconds=1,
        aggregation_interval_minutes=1,
        retention_days=7,
        max_workers=2,
        enable_real_time=True,
        enable_historical=True
    )

@pytest.fixture(scope="function")
def analytics_persistence(temp_data_dir):
    """Create analytics data persistence for testing"""
    return AnalyticsDataPersistence(data_dir=temp_data_dir)

@pytest.fixture(scope="function")
def analytics_framework(analytics_config, analytics_persistence):
    """Create analytics framework for testing"""
    framework = AnalyticsFramework(analytics_config)
    framework.persistence = analytics_persistence
    return framework

@pytest.fixture(scope="function")
def performance_monitor(analytics_persistence):
    """Create performance monitor for testing"""
    return PerformanceMonitor(analytics_persistence)

@pytest.fixture(scope="function")
def sample_task_data():
    """Sample task data for testing"""
    return {
        'task_id': '1',
        'status': 'New',
        'priority': 'Medium',
        'category': 'General Inquiry',
        'sender_email': 'test@example.com',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'tags': ['test', 'sample'],
        'metadata': {'source': 'test'}
    }

@pytest.fixture(scope="function")
def sample_thread_data():
    """Sample thread data for testing"""
    return {
        'thread_id': '1',
        'status': 'Active',
        'priority': 'High',
        'message_count': 3,
        'participant_count': 2,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'first_response_time_minutes': 5.0,
        'resolution_time_minutes': 30.0,
        'avg_response_time_minutes': 10.0,
        'escalation_count': 0,
        'satisfaction_score': 4.5,
        'tags': ['test', 'thread'],
        'metadata': {'source': 'test'}
    }

@pytest.fixture(scope="function")
def sample_performance_metrics():
    """Sample performance metrics for testing"""
    return [
        {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metric_type': 'response_time',
            'value': 1.5,
            'unit': 'seconds',
            'category': 'api',
            'priority': 'Medium'
        },
        {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metric_type': 'volume',
            'value': 45.2,
            'unit': 'count',
            'category': 'system',
            'priority': 'Low'
        }
    ]

@pytest.fixture(scope="function")
def sample_system_health():
    """Sample system health data for testing"""
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'service_name': 'test_service',
        'status': 'healthy',
        'response_time_ms': 100.0,
        'error_rate': 0.01,
        'cpu_usage': 45.2,
        'memory_usage': 60.5,
        'disk_usage': 75.0,
        'active_connections': 10
    }

@pytest.fixture(scope="function")
def sample_user_behavior():
    """Sample user behavior data for testing"""
    return {
        'user_id': 'test_user_123',
        'session_id': 'test_session_456',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'action': 'page_view',
        'page': '/dashboard',
        'duration_seconds': 30.5,
        'user_agent': 'Mozilla/5.0 (Test Browser)',
        'ip_address': '127.0.0.1'
    }

# Test markers
pytest_plugins = []

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "analytics: Analytics related tests")
    config.addinivalue_line("markers", "performance: Performance related tests")
    config.addinivalue_line("markers", "email: Email service tests")
    config.addinivalue_line("markers", "llm: LLM service tests")
    config.addinivalue_line("markers", "api: API endpoint tests")

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names"""
    for item in items:
        # Add markers based on test file names
        if "test_analytics" in item.nodeid:
            item.add_marker(pytest.mark.analytics)
        if "test_performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)
        if "test_email" in item.nodeid:
            item.add_marker(pytest.mark.email)
        if "test_llm" in item.nodeid:
            item.add_marker(pytest.mark.llm)
        if "test_api" in item.nodeid:
            item.add_marker(pytest.mark.api)
        
        # Add slow marker for tests that take more than 1 second
        if "slow" in item.name or "integration" in item.name:
            item.add_marker(pytest.mark.slow)
