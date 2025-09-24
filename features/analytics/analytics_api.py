"""
Data Analytics Foundation - Analytics API
Author: Sunayana
Phase 9: Data Analytics Foundation

This module provides REST API endpoints for analytics data access,
reporting, and visualization for the HandyConnect system.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from flask import Blueprint, request, jsonify, current_app
import json

from .analytics_framework import AnalyticsFramework, AnalyticsConfig
from .data_visualization import DataVisualization
from .performance_metrics import get_performance_monitor
from .data_persistence import AnalyticsDataPersistence

logger = logging.getLogger(__name__)

# Create analytics blueprint
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

# Global analytics framework instance
_analytics_framework = None
_data_visualization = None
_data_persistence = None

def get_analytics_framework() -> AnalyticsFramework:
    """Get global analytics framework instance"""
    global _analytics_framework
    if _analytics_framework is None:
        config = AnalyticsConfig(
            collection_interval_seconds=60,
            aggregation_interval_minutes=15,
            retention_days=90,
            enable_real_time=True,
            enable_historical=True
        )
        _analytics_framework = AnalyticsFramework(config)
        _analytics_framework.start()
    return _analytics_framework

def get_data_visualization() -> DataVisualization:
    """Get global data visualization instance"""
    global _data_visualization
    if _data_visualization is None:
        persistence = AnalyticsDataPersistence()
        _data_visualization = DataVisualization(persistence)
    return _data_visualization

def get_data_persistence() -> AnalyticsDataPersistence:
    """Get global data persistence instance"""
    global _data_persistence
    if _data_persistence is None:
        _data_persistence = AnalyticsDataPersistence()
    return _data_persistence

def success_response(data: Any, message: str = "Success") -> tuple:
    """Create success response"""
    return jsonify({
        "status": "success",
        "message": message,
        "data": data
    }), 200

def error_response(message: str, status_code: int = 400, error_details: str = None) -> tuple:
    """Create error response"""
    response = {
        "status": "error",
        "message": message
    }
    if error_details:
        response["error_details"] = error_details
    return jsonify(response), status_code

def parse_date_range() -> tuple[datetime, datetime]:
    """Parse date range from request parameters"""
    try:
        # Get date range from query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        else:
            start_date = datetime.now(timezone.utc) - timedelta(days=30)
        
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        else:
            end_date = datetime.now(timezone.utc)
        
        return start_date, end_date
    except Exception as e:
        raise ValueError(f"Invalid date format: {e}")

# ==================== ANALYTICS ENDPOINTS ====================

@analytics_bp.route('/health', methods=['GET'])
def analytics_health():
    """Analytics service health check"""
    try:
        # Lightweight health check - just verify services are available
        framework = get_analytics_framework()
        
        health_data = {
            'service': 'analytics',
            'status': 'healthy',
            'framework_running': framework._running,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return jsonify({
            "status": "success",
            "message": "Analytics service is healthy",
            "data": health_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error in analytics health check: {e}")
        return error_response("Analytics service health check failed", 500, str(e))

@analytics_bp.route('/health/detailed', methods=['GET'])
def analytics_health_detailed():
    """Detailed analytics service health check with metrics"""
    try:
        framework = get_analytics_framework()
        persistence = get_data_persistence()
        
        # Get storage stats
        storage_stats = persistence.get_storage_stats()
        
        # Get current metrics
        monitor = get_performance_monitor()
        current_metrics = monitor.get_current_metrics()
        
        health_data = {
            'service': 'analytics',
            'status': 'healthy',
            'framework_running': framework._running,
            'storage_stats': storage_stats,
            'current_metrics': current_metrics,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return jsonify({
            "status": "success",
            "message": "Analytics service is healthy",
            "data": health_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error in detailed analytics health check: {e}")
        return error_response("Detailed analytics service health check failed", 500, str(e))

@analytics_bp.route('/report', methods=['GET'])
def get_analytics_report():
    """Get comprehensive analytics report"""
    try:
        start_date, end_date = parse_date_range()
        framework = get_analytics_framework()
        
        # Generate comprehensive report
        report = framework.get_analytics_report(start_date, end_date)
        
        return success_response(report, "Analytics report generated successfully")
        
    except ValueError as e:
        return error_response("Invalid date parameters", 400, str(e))
    except Exception as e:
        logger.error(f"Error generating analytics report: {e}")
        return error_response("Failed to generate analytics report", 500, str(e))

@analytics_bp.route('/tasks', methods=['GET'])
def get_task_analytics():
    """Get task analytics data"""
    try:
        start_date, end_date = parse_date_range()
        framework = get_analytics_framework()
        
        # Get task metrics
        task_metrics = framework.aggregator.aggregate_task_metrics(start_date, end_date)
        
        return success_response(task_metrics, "Task analytics retrieved successfully")
        
    except ValueError as e:
        return error_response("Invalid date parameters", 400, str(e))
    except Exception as e:
        logger.error(f"Error getting task analytics: {e}")
        return error_response("Failed to get task analytics", 500, str(e))

@analytics_bp.route('/threads', methods=['GET'])
def get_thread_analytics():
    """Get thread analytics data"""
    try:
        start_date, end_date = parse_date_range()
        framework = get_analytics_framework()
        
        # Get thread metrics
        thread_metrics = framework.aggregator.aggregate_thread_metrics(start_date, end_date)
        
        return success_response(thread_metrics, "Thread analytics retrieved successfully")
        
    except ValueError as e:
        return error_response("Invalid date parameters", 400, str(e))
    except Exception as e:
        logger.error(f"Error getting thread analytics: {e}")
        return error_response("Failed to get thread analytics", 500, str(e))

@analytics_bp.route('/performance', methods=['GET'])
def get_performance_analytics():
    """Get performance analytics data"""
    try:
        start_date, end_date = parse_date_range()
        metric_type = request.args.get('metric_type')
        
        framework = get_analytics_framework()
        
        # Get performance metrics
        performance_metrics = framework.aggregator.aggregate_performance_metrics(
            start_date, end_date, metric_type
        )
        
        return success_response(performance_metrics, "Performance analytics retrieved successfully")
        
    except ValueError as e:
        return error_response("Invalid date parameters", 400, str(e))
    except Exception as e:
        logger.error(f"Error getting performance analytics: {e}")
        return error_response("Failed to get performance analytics", 500, str(e))

@analytics_bp.route('/system-health', methods=['GET'])
def get_system_health_analytics():
    """Get system health analytics data"""
    try:
        start_date, end_date = parse_date_range()
        service_name = request.args.get('service_name')
        
        framework = get_analytics_framework()
        
        # Get system health metrics
        system_health = framework.aggregator.aggregate_system_health(
            start_date, end_date, service_name
        )
        
        return success_response(system_health, "System health analytics retrieved successfully")
        
    except ValueError as e:
        return error_response("Invalid date parameters", 400, str(e))
    except Exception as e:
        logger.error(f"Error getting system health analytics: {e}")
        return error_response("Failed to get system health analytics", 500, str(e))

@analytics_bp.route('/current-metrics', methods=['GET'])
def get_current_metrics_endpoint():
    """Get current system metrics"""
    try:
        monitor = get_performance_monitor()
        current_metrics = monitor.get_current_metrics()
        
        return success_response(current_metrics, "Current metrics retrieved successfully")
        
    except Exception as e:
        logger.error(f"Error getting current metrics: {e}")
        return error_response("Failed to get current metrics", 500, str(e))

# ==================== VISUALIZATION ENDPOINTS ====================

@analytics_bp.route('/charts', methods=['GET'])
def get_dashboard_charts():
    """Get all dashboard charts data"""
    try:
        start_date, end_date = parse_date_range()
        visualization = get_data_visualization()
        
        # Generate all charts
        charts_data = visualization.generate_dashboard_charts(start_date, end_date)
        
        return success_response(charts_data, "Dashboard charts generated successfully")
        
    except ValueError as e:
        return error_response("Invalid date parameters", 400, str(e))
    except Exception as e:
        logger.error(f"Error generating dashboard charts: {e}")
        return error_response("Failed to generate dashboard charts", 500, str(e))

@analytics_bp.route('/charts/task-status', methods=['GET'])
def get_task_status_chart():
    """Get task status distribution chart"""
    try:
        start_date, end_date = parse_date_range()
        visualization = get_data_visualization()
        
        chart_data = visualization.generate_task_status_chart(start_date, end_date)
        
        return success_response(chart_data, "Task status chart generated successfully")
        
    except ValueError as e:
        return error_response("Invalid date parameters", 400, str(e))
    except Exception as e:
        logger.error(f"Error generating task status chart: {e}")
        return error_response("Failed to generate task status chart", 500, str(e))

@analytics_bp.route('/charts/priority-distribution', methods=['GET'])
def get_priority_distribution_chart():
    """Get priority distribution chart"""
    try:
        start_date, end_date = parse_date_range()
        visualization = get_data_visualization()
        
        chart_data = visualization.generate_priority_distribution_chart(start_date, end_date)
        
        return success_response(chart_data, "Priority distribution chart generated successfully")
        
    except ValueError as e:
        return error_response("Invalid date parameters", 400, str(e))
    except Exception as e:
        logger.error(f"Error generating priority distribution chart: {e}")
        return error_response("Failed to generate priority distribution chart", 500, str(e))

@analytics_bp.route('/charts/response-time-trend', methods=['GET'])
def get_response_time_trend_chart():
    """Get response time trend chart"""
    try:
        start_date, end_date = parse_date_range()
        visualization = get_data_visualization()
        
        chart_data = visualization.generate_response_time_trend_chart(start_date, end_date)
        
        return success_response(chart_data, "Response time trend chart generated successfully")
        
    except ValueError as e:
        return error_response("Invalid date parameters", 400, str(e))
    except Exception as e:
        logger.error(f"Error generating response time trend chart: {e}")
        return error_response("Failed to generate response time trend chart", 500, str(e))

@analytics_bp.route('/charts/performance-metrics', methods=['GET'])
def get_performance_metrics_chart():
    """Get performance metrics chart"""
    try:
        start_date, end_date = parse_date_range()
        visualization = get_data_visualization()
        
        chart_data = visualization.generate_performance_metrics_chart(start_date, end_date)
        
        return success_response(chart_data, "Performance metrics chart generated successfully")
        
    except ValueError as e:
        return error_response("Invalid date parameters", 400, str(e))
    except Exception as e:
        logger.error(f"Error generating performance metrics chart: {e}")
        return error_response("Failed to generate performance metrics chart", 500, str(e))

@analytics_bp.route('/charts/system-health', methods=['GET'])
def get_system_health_chart():
    """Get system health chart"""
    try:
        start_date, end_date = parse_date_range()
        visualization = get_data_visualization()
        
        chart_data = visualization.generate_system_health_chart(start_date, end_date)
        
        return success_response(chart_data, "System health chart generated successfully")
        
    except ValueError as e:
        return error_response("Invalid date parameters", 400, str(e))
    except Exception as e:
        logger.error(f"Error generating system health chart: {e}")
        return error_response("Failed to generate system health chart", 500, str(e))

# ==================== DATA COLLECTION ENDPOINTS ====================

@analytics_bp.route('/collect/task', methods=['POST'])
def collect_task_data():
    """Collect task analytics data"""
    try:
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        framework = get_analytics_framework()
        
        # Process task data
        success = framework.process_task_data(data)
        
        if success:
            return success_response({"processed": True}, "Task data collected successfully")
        else:
            return error_response("Failed to process task data", 500)
        
    except Exception as e:
        logger.error(f"Error collecting task data: {e}")
        return error_response("Failed to collect task data", 500, str(e))

@analytics_bp.route('/collect/thread', methods=['POST'])
def collect_thread_data():
    """Collect thread analytics data"""
    try:
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        framework = get_analytics_framework()
        
        # Process thread data
        success = framework.process_thread_data(data)
        
        if success:
            return success_response({"processed": True}, "Thread data collected successfully")
        else:
            return error_response("Failed to process thread data", 500)
        
    except Exception as e:
        logger.error(f"Error collecting thread data: {e}")
        return error_response("Failed to collect thread data", 500, str(e))

@analytics_bp.route('/collect/user-behavior', methods=['POST'])
def collect_user_behavior():
    """Collect user behavior data"""
    try:
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        required_fields = ['user_id', 'session_id', 'action', 'page']
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)
        
        framework = get_analytics_framework()
        
        # Track user behavior
        success = framework.track_user_behavior(
            user_id=data['user_id'],
            session_id=data['session_id'],
            action=data['action'],
            page=data['page'],
            **{k: v for k, v in data.items() if k not in required_fields}
        )
        
        if success:
            return success_response({"tracked": True}, "User behavior tracked successfully")
        else:
            return error_response("Failed to track user behavior", 500)
        
    except Exception as e:
        logger.error(f"Error collecting user behavior: {e}")
        return error_response("Failed to collect user behavior", 500, str(e))

# ==================== ADMIN ENDPOINTS ====================

@analytics_bp.route('/admin/cleanup', methods=['POST'])
def cleanup_old_data():
    """Clean up old analytics data"""
    try:
        framework = get_analytics_framework()
        
        # Clean up old data
        deleted_files = framework.cleanup_old_data()
        
        return success_response(
            {"deleted_files": deleted_files}, 
            f"Cleaned up {deleted_files} old data files"
        )
        
    except Exception as e:
        logger.error(f"Error cleaning up old data: {e}")
        return error_response("Failed to clean up old data", 500, str(e))

@analytics_bp.route('/admin/storage-stats', methods=['GET'])
def get_storage_stats():
    """Get analytics storage statistics"""
    try:
        persistence = get_data_persistence()
        
        # Get storage stats
        storage_stats = persistence.get_storage_stats()
        
        return success_response(storage_stats, "Storage statistics retrieved successfully")
        
    except Exception as e:
        logger.error(f"Error getting storage stats: {e}")
        return error_response("Failed to get storage statistics", 500, str(e))

@analytics_bp.route('/admin/export', methods=['POST'])
def export_analytics_data():
    """Export analytics data"""
    try:
        data = request.get_json()
        if not data:
            return error_response("No export parameters provided", 400)
        
        data_type = data.get('data_type')
        if not data_type:
            return error_response("Missing data_type parameter", 400)
        
        # Parse date range
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        
        start_date = None
        end_date = None
        
        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        
        persistence = get_data_persistence()
        
        # Export data
        output_file = persistence.export_data(data_type, start_date, end_date)
        
        return success_response(
            {"output_file": output_file}, 
            f"Analytics data exported successfully to {output_file}"
        )
        
    except ValueError as e:
        return error_response("Invalid date format", 400, str(e))
    except Exception as e:
        logger.error(f"Error exporting analytics data: {e}")
        return error_response("Failed to export analytics data", 500, str(e))

# ==================== METRICS ENDPOINTS ====================

@analytics_bp.route('/metrics/summary', methods=['GET'])
def get_metrics_summary():
    """Get performance metrics summary"""
    try:
        hours = int(request.args.get('hours', 24))
        monitor = get_performance_monitor()
        
        # Get metrics summary
        summary = monitor.get_metrics_summary(hours)
        
        # Add time_range field to summary
        if isinstance(summary, dict):
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=hours)
            summary['time_range'] = {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'hours': hours
            }
        
        return success_response(summary, "Metrics summary retrieved successfully")
        
    except ValueError as e:
        return error_response("Invalid hours parameter", 400, str(e))
    except Exception as e:
        logger.error(f"Error getting metrics summary: {e}")
        return error_response("Failed to get metrics summary", 500, str(e))

@analytics_bp.route('/metrics/record', methods=['POST'])
def record_custom_metric():
    """Record a custom performance metric"""
    try:
        data = request.get_json()
        if not data:
            return error_response("No metric data provided", 400)
        
        required_fields = ['metric_type', 'value', 'unit']
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)
        
        monitor = get_performance_monitor()
        
        # Record metric
        monitor.record_custom_metric(
            metric_type=data['metric_type'],
            value=data['value'],
            unit=data['unit'],
            category=data.get('category', 'custom'),
            **{k: v for k, v in data.items() if k not in required_fields + ['category']}
        )
        
        return success_response({"recorded": True}, "Custom metric recorded successfully")
        
    except Exception as e:
        logger.error(f"Error recording custom metric: {e}")
        return error_response("Failed to record custom metric", 500, str(e))

# ==================== ERROR HANDLERS ====================

@analytics_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return error_response("Analytics endpoint not found", 404)

@analytics_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return error_response("Method not allowed for this endpoint", 405)

@analytics_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error in analytics API: {error}")
    return error_response("Internal server error", 500)
