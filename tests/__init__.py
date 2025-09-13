"""
HandyConnect Test Suite

This package contains all tests for the HandyConnect application, organized by:
- Unit tests: Individual component testing
- Integration tests: Component interaction testing  
- End-to-end tests: Complete workflow testing
- Performance tests: Load and stress testing

Test Structure:
- tests/unit/: Unit tests for individual functions and classes
- tests/integration/: Integration tests for API endpoints and database
- tests/e2e/: End-to-end tests for complete user workflows
- tests/performance/: Performance and load testing
- tests/features/: Feature-specific test suites
"""

import os
import sys
import pytest
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test configuration
TEST_CONFIG = {
    'database_url': 'sqlite:///:memory:',
    'test_timeout': 30,
    'coverage_threshold': 90,
    'max_retries': 3
}

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for component interactions"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests for complete workflows"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and load tests"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer than 5 seconds"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        
        # Mark slow tests
        if "slow" in item.name or "load" in item.name:
            item.add_marker(pytest.mark.slow)
