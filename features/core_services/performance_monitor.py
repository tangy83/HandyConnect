"""
Performance Monitor Service for HandyConnect
Monitor and optimize system performance across all components
"""

import time
import psutil
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import os

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    timestamp: datetime
    component: str
    operation: str
    duration_ms: float
    success: bool
    memory_usage_mb: float
    cpu_percent: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceAlert:
    """Performance alert data structure"""
    alert_id: str
    timestamp: datetime
    alert_type: str
    severity: str  # low, medium, high, critical
    component: str
    message: str
    threshold: float
    actual_value: float
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class PerformanceMonitor:
    """Service for monitoring and optimizing system performance"""
    
    def __init__(self, max_metrics: int = 10000):
        self.max_metrics = max_metrics
        self.metrics: deque = deque(maxlen=max_metrics)
        self.alerts: List[PerformanceAlert] = []
        
        # Performance thresholds
        self.thresholds = {
            'response_time_ms': {'warning': 500, 'critical': 2000},
            'memory_usage_mb': {'warning': 500, 'critical': 1000},
            'cpu_percent': {'warning': 70, 'critical': 90},
            'error_rate_percent': {'warning': 5, 'critical': 10}
        }
        
        # Performance tracking
        self.component_stats = defaultdict(lambda: {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'total_duration_ms': 0,
            'avg_duration_ms': 0,
            'max_duration_ms': 0,
            'min_duration_ms': float('inf')
        })
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None
        
        logger.info("Performance Monitor initialized")
    
    def start_monitoring(self, interval_seconds: int = 30):
        """Start background performance monitoring"""
        if self.monitoring:
            logger.warning("Performance monitoring already running")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitor_thread.start()
        
        logger.info(f"Performance monitoring started (interval: {interval_seconds}s)")
    
    def stop_monitoring(self):
        """Stop background performance monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info("Performance monitoring stopped")
    
    def record_metric(self, component: str, operation: str, 
                     duration_ms: float, success: bool = True, 
                     metadata: Dict[str, Any] = None) -> None:
        """Record a performance metric"""
        try:
            current_time = datetime.utcnow()
            
            # Get system metrics
            memory_info = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent()
            
            metric = PerformanceMetric(
                timestamp=current_time,
                component=component,
                operation=operation,
                duration_ms=duration_ms,
                success=success,
                memory_usage_mb=memory_info.used / (1024 * 1024),
                cpu_percent=cpu_percent,
                metadata=metadata or {}
            )
            
            # Add to metrics
            self.metrics.append(metric)
            
            # Update component statistics
            self._update_component_stats(component, operation, duration_ms, success)
            
            # Check for performance alerts
            self._check_performance_alerts(metric)
            
        except Exception as e:
            logger.error(f"Error recording performance metric: {e}")
    
    def get_performance_summary(self, component: str = None, 
                              hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for a component or all components"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Filter metrics by time and component
            filtered_metrics = [
                m for m in self.metrics 
                if m.timestamp >= cutoff_time and 
                (component is None or m.component == component)
            ]
            
            if not filtered_metrics:
                return {
                    'total_operations': 0,
                    'success_rate': 0,
                    'avg_response_time_ms': 0,
                    'max_response_time_ms': 0,
                    'min_response_time_ms': 0,
                    'error_rate': 0,
                    'avg_memory_usage_mb': 0,
                    'avg_cpu_percent': 0
                }
            
            # Calculate statistics
            total_operations = len(filtered_metrics)
            successful_operations = len([m for m in filtered_metrics if m.success])
            failed_operations = total_operations - successful_operations
            
            response_times = [m.duration_ms for m in filtered_metrics]
            memory_usage = [m.memory_usage_mb for m in filtered_metrics]
            cpu_usage = [m.cpu_percent for m in filtered_metrics]
            
            return {
                'total_operations': total_operations,
                'successful_operations': successful_operations,
                'failed_operations': failed_operations,
                'success_rate': round((successful_operations / total_operations) * 100, 2),
                'error_rate': round((failed_operations / total_operations) * 100, 2),
                'avg_response_time_ms': round(sum(response_times) / len(response_times), 2),
                'max_response_time_ms': max(response_times),
                'min_response_time_ms': min(response_times),
                'avg_memory_usage_mb': round(sum(memory_usage) / len(memory_usage), 2),
                'avg_cpu_percent': round(sum(cpu_usage) / len(cpu_usage), 2),
                'component': component,
                'period_hours': hours
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {}
    
    def get_component_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics for all components"""
        try:
            component_performance = {}
            
            for component, stats in self.component_stats.items():
                if stats['total_operations'] > 0:
                    component_performance[component] = {
                        'total_operations': stats['total_operations'],
                        'successful_operations': stats['successful_operations'],
                        'failed_operations': stats['failed_operations'],
                        'success_rate': round((stats['successful_operations'] / stats['total_operations']) * 100, 2),
                        'avg_duration_ms': round(stats['avg_duration_ms'], 2),
                        'max_duration_ms': stats['max_duration_ms'],
                        'min_duration_ms': stats['min_duration_ms'] if stats['min_duration_ms'] != float('inf') else 0
                    }
            
            return component_performance
            
        except Exception as e:
            logger.error(f"Error getting component performance: {e}")
            return {}
    
    def get_performance_trends(self, component: str = None, 
                             hours: int = 24) -> Dict[str, List]:
        """Get performance trends over time"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Filter metrics
            filtered_metrics = [
                m for m in self.metrics 
                if m.timestamp >= cutoff_time and 
                (component is None or m.component == component)
            ]
            
            if not filtered_metrics:
                return {
                    'timestamps': [],
                    'response_times': [],
                    'memory_usage': [],
                    'cpu_usage': [],
                    'success_rates': []
                }
            
            # Group metrics by hour
            hourly_data = defaultdict(list)
            for metric in filtered_metrics:
                hour_key = metric.timestamp.replace(minute=0, second=0, microsecond=0)
                hourly_data[hour_key].append(metric)
            
            # Calculate trends
            timestamps = []
            response_times = []
            memory_usage = []
            cpu_usage = []
            success_rates = []
            
            for hour in sorted(hourly_data.keys()):
                metrics_in_hour = hourly_data[hour]
                
                timestamps.append(hour.isoformat())
                response_times.append(round(sum(m.duration_ms for m in metrics_in_hour) / len(metrics_in_hour), 2))
                memory_usage.append(round(sum(m.memory_usage_mb for m in metrics_in_hour) / len(metrics_in_hour), 2))
                cpu_usage.append(round(sum(m.cpu_percent for m in metrics_in_hour) / len(metrics_in_hour), 2))
                
                successful = len([m for m in metrics_in_hour if m.success])
                success_rates.append(round((successful / len(metrics_in_hour)) * 100, 2))
            
            return {
                'timestamps': timestamps,
                'response_times': response_times,
                'memory_usage': memory_usage,
                'cpu_usage': cpu_usage,
                'success_rates': success_rates,
                'component': component,
                'period_hours': hours
            }
            
        except Exception as e:
            logger.error(f"Error getting performance trends: {e}")
            return {}
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active performance alerts"""
        try:
            active_alerts = [alert for alert in self.alerts if not alert.resolved]
            
            return [
                {
                    'alert_id': alert.alert_id,
                    'timestamp': alert.timestamp.isoformat(),
                    'alert_type': alert.alert_type,
                    'severity': alert.severity,
                    'component': alert.component,
                    'message': alert.message,
                    'threshold': alert.threshold,
                    'actual_value': alert.actual_value
                }
                for alert in active_alerts
            ]
            
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return []
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve a performance alert"""
        try:
            for alert in self.alerts:
                if alert.alert_id == alert_id and not alert.resolved:
                    alert.resolved = True
                    alert.resolved_at = datetime.utcnow()
                    logger.info(f"Resolved performance alert: {alert_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error resolving alert {alert_id}: {e}")
            return False
    
    def export_performance_data(self, filepath: str = None) -> str:
        """Export performance data to JSON file"""
        try:
            if not filepath:
                filepath = f"data/performance_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            export_data = {
                'export_timestamp': datetime.utcnow().isoformat(),
                'total_metrics': len(self.metrics),
                'total_alerts': len(self.alerts),
                'active_alerts': len([a for a in self.alerts if not a.resolved]),
                'component_stats': dict(self.component_stats),
                'recent_metrics': [
                    {
                        'timestamp': m.timestamp.isoformat(),
                        'component': m.component,
                        'operation': m.operation,
                        'duration_ms': m.duration_ms,
                        'success': m.success,
                        'memory_usage_mb': m.memory_usage_mb,
                        'cpu_percent': m.cpu_percent,
                        'metadata': m.metadata
                    }
                    for m in list(self.metrics)[-1000:]  # Last 1000 metrics
                ],
                'alerts': [
                    {
                        'alert_id': a.alert_id,
                        'timestamp': a.timestamp.isoformat(),
                        'alert_type': a.alert_type,
                        'severity': a.severity,
                        'component': a.component,
                        'message': a.message,
                        'threshold': a.threshold,
                        'actual_value': a.actual_value,
                        'resolved': a.resolved,
                        'resolved_at': a.resolved_at.isoformat() if a.resolved_at else None
                    }
                    for a in self.alerts
                ]
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Performance data exported to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting performance data: {e}")
            return ""
    
    def _monitor_loop(self, interval_seconds: int):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                # Record system metrics
                memory_info = psutil.virtual_memory()
                cpu_percent = psutil.cpu_percent()
                
                self.record_metric(
                    component="system",
                    operation="health_check",
                    duration_ms=0,
                    success=True,
                    metadata={
                        'memory_percent': memory_info.percent,
                        'disk_usage_percent': psutil.disk_usage('/').percent,
                        'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
                    }
                )
                
                # Clean up old alerts (older than 7 days)
                cutoff_time = datetime.utcnow() - timedelta(days=7)
                self.alerts = [alert for alert in self.alerts if alert.timestamp >= cutoff_time]
                
                time.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval_seconds)
    
    def _update_component_stats(self, component: str, operation: str, 
                              duration_ms: float, success: bool):
        """Update component statistics"""
        try:
            stats = self.component_stats[component]
            stats['total_operations'] += 1
            
            if success:
                stats['successful_operations'] += 1
            else:
                stats['failed_operations'] += 1
            
            stats['total_duration_ms'] += duration_ms
            stats['avg_duration_ms'] = stats['total_duration_ms'] / stats['total_operations']
            stats['max_duration_ms'] = max(stats['max_duration_ms'], duration_ms)
            stats['min_duration_ms'] = min(stats['min_duration_ms'], duration_ms)
            
        except Exception as e:
            logger.error(f"Error updating component stats: {e}")
    
    def _check_performance_alerts(self, metric: PerformanceMetric):
        """Check for performance alerts based on thresholds"""
        try:
            # Check response time
            if metric.duration_ms > self.thresholds['response_time_ms']['critical']:
                self._create_alert(
                    alert_type='response_time',
                    severity='critical',
                    component=metric.component,
                    message=f"Response time {metric.duration_ms:.2f}ms exceeds critical threshold",
                    threshold=self.thresholds['response_time_ms']['critical'],
                    actual_value=metric.duration_ms
                )
            elif metric.duration_ms > self.thresholds['response_time_ms']['warning']:
                self._create_alert(
                    alert_type='response_time',
                    severity='medium',
                    component=metric.component,
                    message=f"Response time {metric.duration_ms:.2f}ms exceeds warning threshold",
                    threshold=self.thresholds['response_time_ms']['warning'],
                    actual_value=metric.duration_ms
                )
            
            # Check memory usage
            if metric.memory_usage_mb > self.thresholds['memory_usage_mb']['critical']:
                self._create_alert(
                    alert_type='memory_usage',
                    severity='critical',
                    component=metric.component,
                    message=f"Memory usage {metric.memory_usage_mb:.2f}MB exceeds critical threshold",
                    threshold=self.thresholds['memory_usage_mb']['critical'],
                    actual_value=metric.memory_usage_mb
                )
            
            # Check CPU usage
            if metric.cpu_percent > self.thresholds['cpu_percent']['critical']:
                self._create_alert(
                    alert_type='cpu_usage',
                    severity='critical',
                    component=metric.component,
                    message=f"CPU usage {metric.cpu_percent:.2f}% exceeds critical threshold",
                    threshold=self.thresholds['cpu_percent']['critical'],
                    actual_value=metric.cpu_percent
                )
            
        except Exception as e:
            logger.error(f"Error checking performance alerts: {e}")
    
    def _create_alert(self, alert_type: str, severity: str, component: str, 
                     message: str, threshold: float, actual_value: float):
        """Create a new performance alert"""
        try:
            import uuid
            
            alert = PerformanceAlert(
                alert_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                alert_type=alert_type,
                severity=severity,
                component=component,
                message=message,
                threshold=threshold,
                actual_value=actual_value
            )
            
            self.alerts.append(alert)
            logger.warning(f"Performance alert created: {alert.alert_id} - {message}")
            
        except Exception as e:
            logger.error(f"Error creating performance alert: {e}")


# Global performance monitor instance
_performance_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def performance_timer(component: str, operation: str):
    """Decorator to measure performance of functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                monitor.record_metric(component, operation, duration_ms, success=True)
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                monitor.record_metric(component, operation, duration_ms, success=False, 
                                    metadata={'error': str(e)})
                raise
        
        return wrapper
    return decorator
