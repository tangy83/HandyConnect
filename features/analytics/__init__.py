"""
Data Analytics Foundation Package
Author: Sunayana
Phase 9: Data Analytics Foundation

This package provides comprehensive analytics capabilities for the HandyConnect system
including data collection, processing, visualization, and reporting.
"""

from .analytics_framework import AnalyticsFramework, AnalyticsConfig
from .data_schema import (
    TaskAnalytics, ThreadAnalytics, PerformanceMetric, 
    SystemHealth, UserBehavior, DataValidator
)
from .data_persistence import AnalyticsDataPersistence
from .data_visualization import DataVisualization
from .performance_metrics import (
    PerformanceMonitor, get_performance_monitor, 
    start_performance_monitoring, stop_performance_monitoring,
    record_metric, measure_time
)
from .analytics_api import analytics_bp

__version__ = "1.0.0"
__author__ = "Sunayana"

__all__ = [
    # Core framework
    'AnalyticsFramework',
    'AnalyticsConfig',
    
    # Data structures
    'TaskAnalytics',
    'ThreadAnalytics', 
    'PerformanceMetric',
    'SystemHealth',
    'UserBehavior',
    'DataValidator',
    
    # Persistence
    'AnalyticsDataPersistence',
    
    # Visualization
    'DataVisualization',
    
    # Performance monitoring
    'PerformanceMonitor',
    'get_performance_monitor',
    'start_performance_monitoring',
    'stop_performance_monitoring',
    'record_metric',
    'measure_time',
    
    # API
    'analytics_bp'
]
