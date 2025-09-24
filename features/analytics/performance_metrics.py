"""
Data Analytics Foundation - Performance Metrics Collection
Author: Sunayana
Phase 9: Data Analytics Foundation

This module handles performance metrics collection, monitoring,
and alerting for the HandyConnect system.
"""

import time
import logging
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from collections import defaultdict, deque
import statistics
import psutil
import requests
from contextlib import contextmanager

from .data_schema import PerformanceMetric, create_performance_metric, get_current_timestamp
from .data_persistence import AnalyticsDataPersistence

logger = logging.getLogger(__name__)

@dataclass
class MetricThreshold:
    """Metric threshold configuration"""
    metric_type: str
    warning_threshold: float
    critical_threshold: float
    unit: str
    description: str = ""

@dataclass
class Alert:
    """Alert data structure"""
    timestamp: str
    metric_type: str
    value: float
    threshold: float
    severity: str  # 'warning' or 'critical'
    message: str
    metadata: Dict[str, Any] = None

class PerformanceMonitor:
    """Performance monitoring and metrics collection"""
    
    def __init__(self, persistence: AnalyticsDataPersistence):
        self.persistence = persistence
        self._metrics_buffer = deque(maxlen=1000)
        self._thresholds = {}
        self._alert_callbacks = []
        self._running = False
        self._monitor_thread = None
        self._lock = threading.Lock()
        
        # Initialize default thresholds
        self._setup_default_thresholds()
        
        logger.info("Performance monitor initialized")
    
    def _setup_default_thresholds(self):
        """Setup default metric thresholds"""
        default_thresholds = [
            MetricThreshold('response_time', 5.0, 10.0, 'seconds', 'API response time'),
            MetricThreshold('resolution_time', 60.0, 120.0, 'minutes', 'Task resolution time'),
            MetricThreshold('cpu_usage', 70.0, 90.0, 'percent', 'CPU usage'),
            MetricThreshold('memory_usage', 80.0, 95.0, 'percent', 'Memory usage'),
            MetricThreshold('disk_usage', 85.0, 95.0, 'percent', 'Disk usage'),
            MetricThreshold('error_rate', 0.05, 0.10, 'ratio', 'Error rate'),
            MetricThreshold('escalation_rate', 10.0, 20.0, 'percent', 'Task escalation rate'),
            MetricThreshold('satisfaction_score', 3.0, 2.0, 'score', 'Customer satisfaction score')
        ]
        
        for threshold in default_thresholds:
            self._thresholds[threshold.metric_type] = threshold
    
    def start_monitoring(self, interval_seconds: int = 60):
        """Start performance monitoring"""
        if self._running:
            logger.warning("Performance monitoring is already running")
            return
        
        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop, 
            args=(interval_seconds,),
            daemon=True
        )
        self._monitor_thread.start()
        
        logger.info(f"Performance monitoring started with {interval_seconds}s interval")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        if not self._running:
            return
        
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        
        logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self, interval_seconds: int):
        """Main monitoring loop"""
        while self._running:
            try:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Collect application metrics
                self._collect_application_metrics()
                
                # Process buffered metrics
                self._process_metrics_buffer()
                
                # Sleep for interval
                time.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait a minute before retrying
    
    def _collect_system_metrics(self):
        """Collect system-level performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()
            
            # Collect metrics
            metrics = [
                create_performance_metric('cpu_usage', cpu_percent, 'percent', 'system'),
                create_performance_metric('memory_usage', memory.percent, 'percent', 'system'),
                create_performance_metric('memory_available_gb', memory.available / (1024**3), 'gb', 'system'),
                create_performance_metric('disk_usage', (disk.used / disk.total) * 100, 'percent', 'system'),
                create_performance_metric('disk_free_gb', disk.free / (1024**3), 'gb', 'system'),
                create_performance_metric('swap_usage', swap.percent, 'percent', 'system'),
                create_performance_metric('network_bytes_sent', network.bytes_sent, 'bytes', 'system'),
                create_performance_metric('network_bytes_recv', network.bytes_recv, 'bytes', 'system'),
                create_performance_metric('process_memory_mb', process_memory.rss / (1024**2), 'mb', 'application'),
                create_performance_metric('process_cpu', process_cpu, 'percent', 'application')
            ]
            
            # Add to buffer
            with self._lock:
                self._metrics_buffer.extend(metrics)
                
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def _collect_application_metrics(self):
        """Collect application-specific metrics"""
        try:
            # API response time metrics
            self._measure_api_response_times()
            
            # Database connection metrics
            self._measure_database_metrics()
            
            # Email service metrics
            self._measure_email_service_metrics()
            
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
    
    def _measure_api_response_times(self):
        """Measure API response times"""
        try:
            # Test health endpoint
            start_time = time.time()
            response = requests.get('http://localhost:5001/api/health', timeout=5)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            if response.status_code == 200:
                metric = create_performance_metric(
                    'api_response_time', 
                    response_time, 
                    'milliseconds', 
                    'api',
                    metadata={'endpoint': '/api/health', 'status_code': response.status_code}
                )
                
                with self._lock:
                    self._metrics_buffer.append(metric)
            else:
                # Log error rate
                metric = create_performance_metric(
                    'api_error_rate', 
                    1.0, 
                    'count', 
                    'api',
                    metadata={'endpoint': '/api/health', 'status_code': response.status_code}
                )
                
                with self._lock:
                    self._metrics_buffer.append(metric)
                    
        except requests.RequestException as e:
            # Log connection error
            metric = create_performance_metric(
                'api_connection_error', 
                1.0, 
                'count', 
                'api',
                metadata={'endpoint': '/api/health', 'error': str(e)}
            )
            
            with self._lock:
                self._metrics_buffer.append(metric)
        except Exception as e:
            logger.error(f"Error measuring API response times: {e}")
    
    def _measure_database_metrics(self):
        """Measure database performance metrics"""
        try:
            # Simulate database operations
            # In a real implementation, this would measure actual database operations
            
            # File I/O metrics (simulating database operations)
            start_time = time.time()
            
            # Test file operations
            import tempfile
            with tempfile.NamedTemporaryFile(delete=True) as temp_file:
                temp_file.write(b'test data')
                temp_file.flush()
            
            db_response_time = (time.time() - start_time) * 1000
            
            metric = create_performance_metric(
                'database_response_time', 
                db_response_time, 
                'milliseconds', 
                'database'
            )
            
            with self._lock:
                self._metrics_buffer.append(metric)
                
        except Exception as e:
            logger.error(f"Error measuring database metrics: {e}")
    
    def _measure_email_service_metrics(self):
        """Measure email service performance metrics"""
        try:
            # Test email service connectivity
            start_time = time.time()
            
            # Simulate email service check
            # In a real implementation, this would test actual email service connectivity
            time.sleep(0.1)  # Simulate network call
            
            email_response_time = (time.time() - start_time) * 1000
            
            metric = create_performance_metric(
                'email_service_response_time', 
                email_response_time, 
                'milliseconds', 
                'email_service'
            )
            
            with self._lock:
                self._metrics_buffer.append(metric)
                
        except Exception as e:
            logger.error(f"Error measuring email service metrics: {e}")
    
    def _process_metrics_buffer(self):
        """Process buffered metrics and save to persistence"""
        try:
            with self._lock:
                if not self._metrics_buffer:
                    return
                
                # Get all buffered metrics
                metrics = list(self._metrics_buffer)
                self._metrics_buffer.clear()
            
            # Check thresholds and generate alerts
            for metric in metrics:
                self._check_thresholds(metric)
            
            # Save metrics to persistence
            if metrics:
                self.persistence.save_performance_metrics(metrics)
                logger.debug(f"Saved {len(metrics)} performance metrics")
                
        except Exception as e:
            logger.error(f"Error processing metrics buffer: {e}")
    
    def _check_thresholds(self, metric: PerformanceMetric):
        """Check metric against thresholds and generate alerts"""
        try:
            if metric.metric_type not in self._thresholds:
                return
            
            threshold = self._thresholds[metric.metric_type]
            value = metric.value
            
            # Determine severity
            severity = None
            threshold_value = None
            
            if value >= threshold.critical_threshold:
                severity = 'critical'
                threshold_value = threshold.critical_threshold
            elif value >= threshold.warning_threshold:
                severity = 'warning'
                threshold_value = threshold.warning_threshold
            
            if severity:
                # Create alert
                alert = Alert(
                    timestamp=get_current_timestamp(),
                    metric_type=metric.metric_type,
                    value=value,
                    threshold=threshold_value,
                    severity=severity,
                    message=f"{threshold.description} exceeded {severity} threshold: {value} {threshold.unit} (threshold: {threshold_value} {threshold.unit})",
                    metadata=metric.metadata
                )
                
                # Trigger alert callbacks
                self._trigger_alert(alert)
                
        except Exception as e:
            logger.error(f"Error checking thresholds: {e}")
    
    def _trigger_alert(self, alert: Alert):
        """Trigger alert callbacks"""
        try:
            for callback in self._alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Error in alert callback: {e}")
        except Exception as e:
            logger.error(f"Error triggering alerts: {e}")
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Add alert callback function"""
        self._alert_callbacks.append(callback)
    
    def set_threshold(self, metric_type: str, warning_threshold: float, 
                     critical_threshold: float, unit: str, description: str = ""):
        """Set threshold for a metric type"""
        self._thresholds[metric_type] = MetricThreshold(
            metric_type=metric_type,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold,
            unit=unit,
            description=description
        )
        logger.info(f"Set threshold for {metric_type}: warning={warning_threshold}, critical={critical_threshold}")
    
    def record_custom_metric(self, metric_type: str, value: float, unit: str, 
                           category: str = "custom", **metadata):
        """Record a custom performance metric"""
        try:
            metric = create_performance_metric(
                metric_type=metric_type,
                value=value,
                unit=unit,
                category=category
            )
            
            with self._lock:
                self._metrics_buffer.append(metric)
                
        except Exception as e:
            logger.error(f"Error recording custom metric: {e}")
    
    @contextmanager
    def measure_time(self, metric_type: str, category: str = "timing"):
        """Context manager to measure execution time"""
        start_time = time.time()
        try:
            yield
        finally:
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            self.record_custom_metric(metric_type, execution_time, 'milliseconds', category)
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary for the last N hours"""
        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=hours)
            
            metrics = self.persistence.load_performance_metrics(start_time, end_time)
            
            if not metrics:
                return {'total_metrics': 0, 'metrics_by_type': {}}
            
            # Group by metric type
            by_type = defaultdict(list)
            for metric in metrics:
                by_type[metric.metric_type].append(metric.value)
            
            # Calculate statistics
            summary = {
                'total_metrics': len(metrics),
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'hours': hours
                },
                'metrics_by_type': {}
            }
            
            for metric_type, values in by_type.items():
                if values:
                    summary['metrics_by_type'][metric_type] = {
                        'count': len(values),
                        'min': min(values),
                        'max': max(values),
                        'avg': round(statistics.mean(values), 2),
                        'median': round(statistics.median(values), 2),
                        'latest': values[-1] if values else 0
                    }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting metrics summary: {e}")
            return {'error': str(e)}
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            # Get current system state
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            
            return {
                'timestamp': get_current_timestamp(),
                'system': {
                    'cpu_usage_percent': cpu_percent,
                    'memory_usage_percent': memory.percent,
                    'memory_available_gb': round(memory.available / (1024**3), 2),
                    'disk_usage_percent': round((disk.used / disk.total) * 100, 2),
                    'disk_free_gb': round(disk.free / (1024**3), 2)
                },
                'application': {
                    'process_memory_mb': round(process_memory.rss / (1024**2), 2),
                    'process_cpu_percent': process.cpu_percent()
                },
                'thresholds': {
                    metric_type: {
                        'warning': threshold.warning_threshold,
                        'critical': threshold.critical_threshold,
                        'unit': threshold.unit
                    }
                    for metric_type, threshold in self._thresholds.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting current metrics: {e}")
            return {'error': str(e)}

# Global performance monitor instance
_performance_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        persistence = AnalyticsDataPersistence()
        _performance_monitor = PerformanceMonitor(persistence)
    return _performance_monitor

def start_performance_monitoring(interval_seconds: int = 60):
    """Start global performance monitoring"""
    monitor = get_performance_monitor()
    monitor.start_monitoring(interval_seconds)

def stop_performance_monitoring():
    """Stop global performance monitoring"""
    global _performance_monitor
    if _performance_monitor:
        _performance_monitor.stop_monitoring()

def record_metric(metric_type: str, value: float, unit: str, category: str = "custom", **metadata):
    """Record a performance metric"""
    monitor = get_performance_monitor()
    monitor.record_custom_metric(metric_type, value, unit, category, **metadata)

@contextmanager
def measure_time(metric_type: str, category: str = "timing"):
    """Context manager to measure execution time"""
    monitor = get_performance_monitor()
    with monitor.measure_time(metric_type, category):
        yield
