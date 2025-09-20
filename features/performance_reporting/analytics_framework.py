"""
Analytics Framework Establishment
Comprehensive analytics and performance monitoring system.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import statistics
from enum import Enum

from ..task_structure_metadata.task_schema import TaskSchema, TaskStatus, TaskPriority, TaskCategory


class MetricType(Enum):
    """Types of metrics that can be collected"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class Metric:
    """Individual metric data structure"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Performance metrics collection"""
    response_time_ms: float = 0.0
    throughput_per_minute: float = 0.0
    error_rate: float = 0.0
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    active_connections: int = 0
    queue_size: int = 0


@dataclass
class TaskAnalytics:
    """Task-specific analytics"""
    total_tasks: int = 0
    tasks_by_status: Dict[str, int] = field(default_factory=dict)
    tasks_by_priority: Dict[str, int] = field(default_factory=dict)
    tasks_by_category: Dict[str, int] = field(default_factory=dict)
    average_resolution_time_hours: float = 0.0
    sla_compliance_rate: float = 0.0
    escalation_rate: float = 0.0
    customer_satisfaction_score: float = 0.0


class MetricsCollector:
    """Collects and aggregates performance metrics"""
    
    def __init__(self):
        self.metrics: List[Metric] = []
        self.logger = logging.getLogger(__name__)
    
    def record_metric(self, name: str, value: float, metric_type: MetricType, 
                     tags: Optional[Dict[str, str]] = None, metadata: Optional[Dict[str, Any]] = None):
        """Record a new metric"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            tags=tags or {},
            metadata=metadata or {}
        )
        self.metrics.append(metric)
    
    def record_counter(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None):
        """Record a counter metric"""
        self.record_metric(name, value, MetricType.COUNTER, tags)
    
    def record_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a gauge metric"""
        self.record_metric(name, value, MetricType.GAUGE, tags)
    
    def record_timer(self, name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None):
        """Record a timer metric"""
        self.record_metric(name, duration_ms, MetricType.TIMER, tags)
    
    def get_metrics_by_name(self, name: str, time_range: Optional[Tuple[datetime, datetime]] = None) -> List[Metric]:
        """Get metrics by name within time range"""
        filtered_metrics = [m for m in self.metrics if m.name == name]
        
        if time_range:
            start_time, end_time = time_range
            filtered_metrics = [m for m in filtered_metrics if start_time <= m.timestamp <= end_time]
        
        return filtered_metrics
    
    def get_aggregated_metrics(self, time_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Dict[str, float]]:
        """Get aggregated metrics by name"""
        if time_range:
            start_time, end_time = time_range
            filtered_metrics = [m for m in self.metrics if start_time <= m.timestamp <= end_time]
        else:
            filtered_metrics = self.metrics
        
        aggregated = defaultdict(list)
        for metric in filtered_metrics:
            aggregated[metric.name].append(metric.value)
        
        result = {}
        for name, values in aggregated.items():
            result[name] = {
                'count': len(values),
                'sum': sum(values),
                'avg': statistics.mean(values),
                'min': min(values),
                'max': max(values),
                'median': statistics.median(values)
            }
        
        return result
    
    def clear_old_metrics(self, days_to_keep: int = 30):
        """Clear metrics older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        self.metrics = [m for m in self.metrics if m.timestamp > cutoff_date]
        self.logger.info(f"Cleared metrics older than {days_to_keep} days")


class TaskAnalyticsEngine:
    """Analytics engine for task-related metrics"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.logger = logging.getLogger(__name__)
    
    def analyze_tasks(self, tasks: List[TaskSchema]) -> TaskAnalytics:
        """Analyze tasks and generate analytics"""
        analytics = TaskAnalytics()
        
        if not tasks:
            return analytics
        
        analytics.total_tasks = len(tasks)
        
        # Status distribution
        status_counts = Counter(task.status.value for task in tasks)
        analytics.tasks_by_status = dict(status_counts)
        
        # Priority distribution
        priority_counts = Counter(task.priority.value for task in tasks)
        analytics.tasks_by_priority = dict(priority_counts)
        
        # Category distribution
        category_counts = Counter(task.category.value for task in tasks)
        analytics.tasks_by_category = dict(category_counts)
        
        # Resolution time analysis
        completed_tasks = [task for task in tasks if task.status == TaskStatus.COMPLETED and task.resolved_at]
        if completed_tasks:
            resolution_times = []
            for task in completed_tasks:
                if task.metadata.created_at and task.resolved_at:
                    duration = task.resolved_at - task.metadata.created_at
                    resolution_times.append(duration.total_seconds() / 3600)  # Convert to hours
            
            if resolution_times:
                analytics.average_resolution_time_hours = statistics.mean(resolution_times)
        
        # SLA compliance
        sla_tasks = [task for task in tasks if task.sla_deadline]
        if sla_tasks:
            sla_compliant = 0
            for task in sla_tasks:
                if task.status == TaskStatus.COMPLETED and task.resolved_at:
                    if task.resolved_at <= task.sla_deadline:
                        sla_compliant += 1
                elif task.status != TaskStatus.COMPLETED:
                    # Check if current time is within SLA
                    if datetime.utcnow() <= task.sla_deadline:
                        sla_compliant += 1
            
            analytics.sla_compliance_rate = (sla_compliant / len(sla_tasks)) * 100
        
        # Escalation rate (tasks that changed priority)
        escalated_tasks = 0
        for task in tasks:
            if task.priority in [TaskPriority.HIGH, TaskPriority.URGENT, TaskPriority.CRITICAL]:
                # Check if this was escalated (simplified logic)
                if task.metadata.analytics_data.get('original_priority') != task.priority.value:
                    escalated_tasks += 1
        
        analytics.escalation_rate = (escalated_tasks / analytics.total_tasks) * 100 if analytics.total_tasks > 0 else 0
        
        # Record metrics
        self._record_task_metrics(analytics)
        
        return analytics
    
    def _record_task_metrics(self, analytics: TaskAnalytics):
        """Record task analytics as metrics"""
        self.metrics_collector.record_gauge("tasks.total", analytics.total_tasks)
        self.metrics_collector.record_gauge("tasks.resolution_time_avg_hours", analytics.average_resolution_time_hours)
        self.metrics_collector.record_gauge("tasks.sla_compliance_rate", analytics.sla_compliance_rate)
        self.metrics_collector.record_gauge("tasks.escalation_rate", analytics.escalation_rate)
        
        # Record status distribution
        for status, count in analytics.tasks_by_status.items():
            self.metrics_collector.record_gauge(f"tasks.status.{status.lower()}", count)
        
        # Record priority distribution
        for priority, count in analytics.tasks_by_priority.items():
            self.metrics_collector.record_gauge(f"tasks.priority.{priority.lower()}", count)
        
        # Record category distribution
        for category, count in analytics.tasks_by_category.items():
            self.metrics_collector.record_gauge(f"tasks.category.{category.lower()}", count)


class PerformanceMonitor:
    """Monitors system performance metrics"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.logger = logging.getLogger(__name__)
    
    def collect_system_metrics(self) -> PerformanceMetrics:
        """Collect current system performance metrics"""
        metrics = PerformanceMetrics()
        
        try:
            import psutil
            
            # CPU usage
            metrics.cpu_usage_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            metrics.memory_usage_mb = memory.used / (1024 * 1024)  # Convert to MB
            
            # Record metrics
            self.metrics_collector.record_gauge("system.cpu_usage_percent", metrics.cpu_usage_percent)
            self.metrics_collector.record_gauge("system.memory_usage_mb", metrics.memory_usage_mb)
            
        except ImportError:
            self.logger.warning("psutil not available, skipping system metrics")
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
        
        return metrics
    
    def record_api_performance(self, endpoint: str, response_time_ms: float, status_code: int):
        """Record API performance metrics"""
        tags = {
            'endpoint': endpoint,
            'status_code': str(status_code),
            'status_class': f"{status_code // 100}xx"
        }
        
        self.metrics_collector.record_timer(f"api.response_time", response_time_ms, tags)
        self.metrics_collector.record_counter(f"api.requests", 1, tags)
        
        if status_code >= 400:
            self.metrics_collector.record_counter(f"api.errors", 1, tags)


class AnalyticsDashboard:
    """Generates analytics dashboard data"""
    
    def __init__(self, metrics_collector: MetricsCollector, task_analytics_engine: TaskAnalyticsEngine):
        self.metrics_collector = metrics_collector
        self.task_analytics_engine = task_analytics_engine
        self.logger = logging.getLogger(__name__)
    
    def generate_dashboard_data(self, tasks: List[TaskSchema], time_range_hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive dashboard data"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=time_range_hours)
        
        # Task analytics
        task_analytics = self.task_analytics_engine.analyze_tasks(tasks)
        
        # Performance metrics
        performance_metrics = self.metrics_collector.get_aggregated_metrics((start_time, end_time))
        
        # Trends over time
        trends = self._calculate_trends(tasks, time_range_hours)
        
        # Key performance indicators
        kpis = self._calculate_kpis(task_analytics, performance_metrics)
        
        return {
            'timestamp': end_time.isoformat(),
            'time_range_hours': time_range_hours,
            'task_analytics': {
                'total_tasks': task_analytics.total_tasks,
                'tasks_by_status': task_analytics.tasks_by_status,
                'tasks_by_priority': task_analytics.tasks_by_priority,
                'tasks_by_category': task_analytics.tasks_by_category,
                'average_resolution_time_hours': round(task_analytics.average_resolution_time_hours, 2),
                'sla_compliance_rate': round(task_analytics.sla_compliance_rate, 2),
                'escalation_rate': round(task_analytics.escalation_rate, 2)
            },
            'performance_metrics': performance_metrics,
            'trends': trends,
            'kpis': kpis
        }
    
    def _calculate_trends(self, tasks: List[TaskSchema], time_range_hours: int) -> Dict[str, Any]:
        """Calculate trends over time"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=time_range_hours)
        
        # Group tasks by hour
        hourly_data = defaultdict(lambda: {'created': 0, 'completed': 0, 'escalated': 0})
        
        for task in tasks:
            if task.metadata.created_at and start_time <= task.metadata.created_at <= end_time:
                hour_key = task.metadata.created_at.replace(minute=0, second=0, microsecond=0)
                hourly_data[hour_key]['created'] += 1
            
            if task.resolved_at and start_time <= task.resolved_at <= end_time:
                hour_key = task.resolved_at.replace(minute=0, second=0, microsecond=0)
                hourly_data[hour_key]['completed'] += 1
            
            if task.priority in [TaskPriority.HIGH, TaskPriority.URGENT, TaskPriority.CRITICAL]:
                if task.metadata.analytics_data.get('original_priority') != task.priority.value:
                    if task.metadata.updated_at and start_time <= task.metadata.updated_at <= end_time:
                        hour_key = task.metadata.updated_at.replace(minute=0, second=0, microsecond=0)
                        hourly_data[hour_key]['escalated'] += 1
        
        # Convert to list format for frontend
        trends = []
        for hour in sorted(hourly_data.keys()):
            trends.append({
                'timestamp': hour.isoformat(),
                'created': hourly_data[hour]['created'],
                'completed': hourly_data[hour]['completed'],
                'escalated': hourly_data[hour]['escalated']
            })
        
        return {
            'hourly_trends': trends,
            'total_created': sum(data['created'] for data in hourly_data.values()),
            'total_completed': sum(data['completed'] for data in hourly_data.values()),
            'total_escalated': sum(data['escalated'] for data in hourly_data.values())
        }
    
    def _calculate_kpis(self, task_analytics: TaskAnalytics, performance_metrics: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Calculate key performance indicators"""
        kpis = {
            'task_volume': {
                'value': task_analytics.total_tasks,
                'trend': 'stable',  # Would be calculated based on historical data
                'target': 100,
                'status': 'good' if task_analytics.total_tasks <= 100 else 'warning'
            },
            'resolution_time': {
                'value': round(task_analytics.average_resolution_time_hours, 2),
                'trend': 'improving',
                'target': 24,  # 24 hours target
                'status': 'good' if task_analytics.average_resolution_time_hours <= 24 else 'warning'
            },
            'sla_compliance': {
                'value': round(task_analytics.sla_compliance_rate, 2),
                'trend': 'stable',
                'target': 95,  # 95% target
                'status': 'good' if task_analytics.sla_compliance_rate >= 95 else 'warning'
            },
            'escalation_rate': {
                'value': round(task_analytics.escalation_rate, 2),
                'trend': 'stable',
                'target': 10,  # 10% target (lower is better)
                'status': 'good' if task_analytics.escalation_rate <= 10 else 'warning'
            }
        }
        
        # Add performance KPIs if available
        if 'api.response_time' in performance_metrics:
            avg_response_time = performance_metrics['api.response_time']['avg']
            kpis['api_response_time'] = {
                'value': round(avg_response_time, 2),
                'trend': 'stable',
                'target': 1000,  # 1 second target
                'status': 'good' if avg_response_time <= 1000 else 'warning'
            }
        
        return kpis


# Export main classes
__all__ = [
    'MetricsCollector', 'TaskAnalyticsEngine', 'PerformanceMonitor', 'AnalyticsDashboard',
    'Metric', 'PerformanceMetrics', 'TaskAnalytics', 'MetricType'
]





