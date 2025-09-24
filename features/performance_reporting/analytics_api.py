"""
Analytics API Development
RESTful API endpoints for analytics and reporting functionality.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from flask import Blueprint, request, jsonify, current_app
import json

from ..task_structure_metadata.task_schema import TaskSchema
from ..task_structure_metadata.data_persistence import DataPersistenceManager
from .analytics_framework import (
    MetricsCollector, TaskAnalyticsEngine, PerformanceMonitor, AnalyticsDashboard
)
from .data_visualization import DataVisualizer


class AnalyticsAPI:
    """Analytics API endpoints and functionality"""
    
    def __init__(self):
        self.blueprint = Blueprint('analytics', __name__, url_prefix='/api/analytics')
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.data_persistence = DataPersistenceManager()
        self.metrics_collector = MetricsCollector()
        self.task_analytics_engine = TaskAnalyticsEngine(self.metrics_collector)
        self.performance_monitor = PerformanceMonitor(self.metrics_collector)
        self.analytics_dashboard = AnalyticsDashboard(self.metrics_collector, self.task_analytics_engine)
        self.data_visualizer = DataVisualizer()
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register all analytics API routes"""
        
        @self.blueprint.route('/dashboard', methods=['GET'])
        def get_dashboard_data():
            """Get comprehensive dashboard data"""
            try:
                # Get query parameters
                time_range_hours = request.args.get('time_range_hours', 24, type=int)
                
                # Load tasks
                tasks = self.data_persistence.load_tasks()
                
                # Generate dashboard data
                dashboard_data = self.analytics_dashboard.generate_dashboard_data(tasks, time_range_hours)
                
                return jsonify({
                    'success': True,
                    'data': dashboard_data
                })
                
            except Exception as e:
                self.logger.error(f"Error getting dashboard data: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.blueprint.route('/charts', methods=['GET'])
        def get_charts():
            """Get all dashboard charts data"""
            try:
                # Load tasks
                tasks = self.data_persistence.load_tasks()
                
                # Generate charts
                charts = self.data_visualizer.generate_dashboard_charts(tasks)
                
                # Convert to JSON-serializable format
                charts_data = {}
                for chart_name, chart_data in charts.items():
                    charts_data[chart_name] = {
                        'type': chart_data.chart_type.value,
                        'title': chart_data.title,
                        'data': chart_data.data,
                        'options': chart_data.options,
                        'metadata': chart_data.metadata
                    }
                
                return jsonify({
                    'success': True,
                    'data': charts_data
                })
                
            except Exception as e:
                self.logger.error(f"Error getting charts: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.blueprint.route('/metrics', methods=['GET'])
        def get_metrics():
            """Get performance metrics"""
            try:
                # Get query parameters
                time_range_hours = request.args.get('time_range_hours', 24, type=int)
                metric_name = request.args.get('metric_name')
                
                # Calculate time range
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(hours=time_range_hours)
                
                # Get metrics
                if metric_name:
                    metrics = self.metrics_collector.get_metrics_by_name(metric_name, (start_time, end_time))
                    metrics_data = [{
                        'name': m.name,
                        'value': m.value,
                        'type': m.metric_type.value,
                        'timestamp': m.timestamp.isoformat(),
                        'tags': m.tags,
                        'metadata': m.metadata
                    } for m in metrics]
                else:
                    metrics_data = self.metrics_collector.get_aggregated_metrics((start_time, end_time))
                
                return jsonify({
                    'success': True,
                    'data': metrics_data,
                    'time_range': {
                        'start': start_time.isoformat(),
                        'end': end_time.isoformat()
                    }
                })
                
            except Exception as e:
                self.logger.error(f"Error getting metrics: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.blueprint.route('/metrics', methods=['POST'])
        def record_metric():
            """Record a new metric"""
            try:
                data = request.get_json()
                
                if not data or 'name' not in data or 'value' not in data:
                    return jsonify({
                        'success': False,
                        'error': 'Missing required fields: name, value'
                    }), 400
                
                # Record metric
                self.metrics_collector.record_metric(
                    name=data['name'],
                    value=data['value'],
                    metric_type=data.get('type', 'gauge'),
                    tags=data.get('tags'),
                    metadata=data.get('metadata')
                )
                
                return jsonify({
                    'success': True,
                    'message': 'Metric recorded successfully'
                })
                
            except Exception as e:
                self.logger.error(f"Error recording metric: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.blueprint.route('/tasks/analytics', methods=['GET'])
        def get_task_analytics():
            """Get task-specific analytics"""
            try:
                # Load tasks
                tasks = self.data_persistence.load_tasks()
                
                # Generate analytics
                analytics = self.task_analytics_engine.analyze_tasks(tasks)
                
                # Convert to JSON-serializable format
                analytics_data = {
                    'total_tasks': analytics.total_tasks,
                    'tasks_by_status': analytics.tasks_by_status,
                    'tasks_by_priority': analytics.tasks_by_priority,
                    'tasks_by_category': analytics.tasks_by_category,
                    'average_resolution_time_hours': analytics.average_resolution_time_hours,
                    'sla_compliance_rate': analytics.sla_compliance_rate,
                    'escalation_rate': analytics.escalation_rate
                }
                
                return jsonify({
                    'success': True,
                    'data': analytics_data
                })
                
            except Exception as e:
                self.logger.error(f"Error getting task analytics: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.blueprint.route('/performance', methods=['GET'])
        def get_performance_metrics():
            """Get system performance metrics"""
            try:
                # Collect current performance metrics
                performance_metrics = self.performance_monitor.collect_system_metrics()
                
                # Convert to JSON-serializable format
                metrics_data = {
                    'response_time_ms': performance_metrics.response_time_ms,
                    'throughput_per_minute': performance_metrics.throughput_per_minute,
                    'error_rate': performance_metrics.error_rate,
                    'cpu_usage_percent': performance_metrics.cpu_usage_percent,
                    'memory_usage_mb': performance_metrics.memory_usage_mb,
                    'active_connections': performance_metrics.active_connections,
                    'queue_size': performance_metrics.queue_size,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                return jsonify({
                    'success': True,
                    'data': metrics_data
                })
                
            except Exception as e:
                self.logger.error(f"Error getting performance metrics: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.blueprint.route('/reports', methods=['GET'])
        def generate_report():
            """Generate custom analytics report"""
            try:
                # Get query parameters
                report_type = request.args.get('type', 'summary')
                time_range_days = request.args.get('days', 7, type=int)
                format_type = request.args.get('format', 'json')
                
                # Load tasks
                tasks = self.data_persistence.load_tasks()
                
                # Filter tasks by time range
                cutoff_date = datetime.utcnow() - timedelta(days=time_range_days)
                filtered_tasks = [
                    task for task in tasks 
                    if task.metadata.created_at and task.metadata.created_at >= cutoff_date
                ]
                
                # Generate report based on type
                if report_type == 'summary':
                    report_data = self._generate_summary_report(filtered_tasks)
                elif report_type == 'detailed':
                    report_data = self._generate_detailed_report(filtered_tasks)
                elif report_type == 'performance':
                    report_data = self._generate_performance_report(filtered_tasks)
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Unknown report type: {report_type}'
                    }), 400
                
                # Format response
                if format_type == 'json':
                    return jsonify({
                        'success': True,
                        'data': report_data,
                        'metadata': {
                            'report_type': report_type,
                            'time_range_days': time_range_days,
                            'generated_at': datetime.utcnow().isoformat(),
                            'total_tasks_analyzed': len(filtered_tasks)
                        }
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Unsupported format: {format_type}'
                    }), 400
                
            except Exception as e:
                self.logger.error(f"Error generating report: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.blueprint.route('/export', methods=['POST'])
        def export_data():
            """Export analytics data"""
            try:
                data = request.get_json() or {}
                
                export_type = data.get('type', 'all')
                include_charts = data.get('include_charts', False)
                
                # Load tasks
                tasks = self.data_persistence.load_tasks()
                
                export_data = {}
                
                if export_type in ['all', 'tasks']:
                    export_data['tasks'] = [task.to_dict() for task in tasks]
                
                if export_type in ['all', 'analytics']:
                    analytics = self.task_analytics_engine.analyze_tasks(tasks)
                    export_data['analytics'] = {
                        'total_tasks': analytics.total_tasks,
                        'tasks_by_status': analytics.tasks_by_status,
                        'tasks_by_priority': analytics.tasks_by_priority,
                        'tasks_by_category': analytics.tasks_by_category,
                        'average_resolution_time_hours': analytics.average_resolution_time_hours,
                        'sla_compliance_rate': analytics.sla_compliance_rate,
                        'escalation_rate': analytics.escalation_rate
                    }
                
                if export_type in ['all', 'metrics']:
                    export_data['metrics'] = self.metrics_collector.get_aggregated_metrics()
                
                if include_charts:
                    charts = self.data_visualizer.generate_dashboard_charts(tasks)
                    export_data['charts'] = {
                        name: {
                            'type': chart.chart_type.value,
                            'title': chart.title,
                            'data': chart.data,
                            'options': chart.options
                        } for name, chart in charts.items()
                    }
                
                export_data['metadata'] = {
                    'exported_at': datetime.utcnow().isoformat(),
                    'export_type': export_type,
                    'total_tasks': len(tasks)
                }
                
                return jsonify({
                    'success': True,
                    'data': export_data
                })
                
            except Exception as e:
                self.logger.error(f"Error exporting data: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.blueprint.route('/health', methods=['GET'])
        def health_check():
            """Analytics API health check"""
            try:
                # Check if components are working
                tasks = self.data_persistence.load_tasks()
                
                return jsonify({
                    'success': True,
                    'status': 'healthy',
                    'components': {
                        'data_persistence': 'ok',
                        'metrics_collector': 'ok',
                        'task_analytics_engine': 'ok',
                        'data_visualizer': 'ok'
                    },
                    'data': {
                        'total_tasks': len(tasks),
                        'last_updated': datetime.utcnow().isoformat()
                    }
                })
                
            except Exception as e:
                self.logger.error(f"Analytics API health check failed: {e}")
                return jsonify({
                    'success': False,
                    'status': 'unhealthy',
                    'error': str(e)
                }), 500
    
    def _generate_summary_report(self, tasks: List[TaskSchema]) -> Dict[str, Any]:
        """Generate summary report"""
        analytics = self.task_analytics_engine.analyze_tasks(tasks)
        
        return {
            'summary': {
                'total_tasks': analytics.total_tasks,
                'average_resolution_time_hours': round(analytics.average_resolution_time_hours, 2),
                'sla_compliance_rate': round(analytics.sla_compliance_rate, 2),
                'escalation_rate': round(analytics.escalation_rate, 2)
            },
            'distribution': {
                'by_status': analytics.tasks_by_status,
                'by_priority': analytics.tasks_by_priority,
                'by_category': analytics.tasks_by_category
            }
        }
    
    def _generate_detailed_report(self, tasks: List[TaskSchema]) -> Dict[str, Any]:
        """Generate detailed report"""
        analytics = self.task_analytics_engine.analyze_tasks(tasks)
        
        # Additional detailed analysis
        resolution_times = []
        for task in tasks:
            if task.status.value == 'Completed' and task.resolved_at and task.metadata.created_at:
                duration = task.resolved_at - task.metadata.created_at
                resolution_times.append(duration.total_seconds() / 3600)
        
        return {
            'summary': {
                'total_tasks': analytics.total_tasks,
                'average_resolution_time_hours': round(analytics.average_resolution_time_hours, 2),
                'median_resolution_time_hours': round(
                    sorted(resolution_times)[len(resolution_times)//2] if resolution_times else 0, 2
                ),
                'sla_compliance_rate': round(analytics.sla_compliance_rate, 2),
                'escalation_rate': round(analytics.escalation_rate, 2)
            },
            'distribution': {
                'by_status': analytics.tasks_by_status,
                'by_priority': analytics.tasks_by_priority,
                'by_category': analytics.tasks_by_category
            },
            'performance': {
                'fastest_resolution_hours': round(min(resolution_times), 2) if resolution_times else 0,
                'slowest_resolution_hours': round(max(resolution_times), 2) if resolution_times else 0,
                'resolution_time_std_dev': round(
                    (sum((x - analytics.average_resolution_time_hours) ** 2 for x in resolution_times) / len(resolution_times)) ** 0.5, 2
                ) if resolution_times else 0
            }
        }
    
    def _generate_performance_report(self, tasks: List[TaskSchema]) -> Dict[str, Any]:
        """Generate performance report"""
        # Get system performance metrics
        performance_metrics = self.performance_monitor.collect_system_metrics()
        
        # Get aggregated metrics
        aggregated_metrics = self.metrics_collector.get_aggregated_metrics()
        
        return {
            'system_performance': {
                'cpu_usage_percent': performance_metrics.cpu_usage_percent,
                'memory_usage_mb': performance_metrics.memory_usage_mb,
                'response_time_ms': performance_metrics.response_time_ms,
                'error_rate': performance_metrics.error_rate
            },
            'application_metrics': aggregated_metrics,
            'task_performance': {
                'total_tasks': len(tasks),
                'throughput_per_hour': len(tasks) / 24 if tasks else 0  # Simplified calculation
            }
        }


# Export the blueprint for registration
def create_analytics_api() -> Blueprint:
    """Create and return the analytics API blueprint"""
    api = AnalyticsAPI()
    return api.blueprint


# Export main class
__all__ = ['AnalyticsAPI', 'create_analytics_api']






