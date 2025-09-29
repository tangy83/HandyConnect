"""
Data Analytics Foundation - Analytics Framework
Author: Sunayana
Phase 9: Data Analytics Foundation

This module provides the core analytics framework including
data collection, processing, aggregation, and reporting capabilities.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass
from collections import defaultdict, Counter
import statistics
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .data_schema import (
    TaskAnalytics, ThreadAnalytics, PerformanceMetric, 
    SystemHealth, UserBehavior, create_performance_metric,
    create_system_health, get_current_timestamp
)
from .data_persistence import AnalyticsDataPersistence

logger = logging.getLogger(__name__)

@dataclass
class AnalyticsConfig:
    """Analytics configuration"""
    collection_interval_seconds: int = 60
    aggregation_interval_minutes: int = 15
    retention_days: int = 90
    max_workers: int = 4
    enable_real_time: bool = True
    enable_historical: bool = True
    enable_forecasting: bool = False

class MetricsCollector:
    """Metrics collection and processing"""
    
    def __init__(self, persistence: AnalyticsDataPersistence):
        self.persistence = persistence
        self._metrics_buffer = []
        self._lock = threading.Lock()
        
    def collect_task_metrics(self, task_data: Dict[str, Any]) -> TaskAnalytics:
        """Collect metrics from task data"""
        try:
            # Calculate response time if available
            response_time = 0.0
            if 'first_response_at' in task_data and 'created_at' in task_data:
                created = datetime.fromisoformat(task_data['created_at'].replace('Z', '+00:00'))
                first_response = datetime.fromisoformat(task_data['first_response_at'].replace('Z', '+00:00'))
                response_time = (first_response - created).total_seconds() / 60
            
            # Calculate resolution time if available
            resolution_time = 0.0
            if 'resolved_at' in task_data and 'created_at' in task_data:
                created = datetime.fromisoformat(task_data['created_at'].replace('Z', '+00:00'))
                resolved = datetime.fromisoformat(task_data['resolved_at'].replace('Z', '+00:00'))
                resolution_time = (resolved - created).total_seconds() / 60
            
            # Handle both 'id' and 'task_id' field names for compatibility
            task_id = task_data.get('task_id') or task_data.get('id', '')
            analytics = TaskAnalytics(
                task_id=task_id,
                created_at=task_data.get('created_at', get_current_timestamp()),
                updated_at=task_data.get('updated_at', get_current_timestamp()),
                status=task_data.get('status', 'New'),
                priority=task_data.get('priority', 'Medium'),
                category=task_data.get('category', 'General Inquiry'),
                sender_email=task_data.get('sender_email', ''),
                response_time_minutes=response_time,
                resolution_time_minutes=resolution_time,
                escalation_count=task_data.get('escalation_count', 0),
                satisfaction_score=task_data.get('satisfaction_score'),
                tags=task_data.get('tags', []),
                metadata=task_data.get('metadata', {})
            )
            
            return analytics
        except Exception as e:
            logger.error(f"Error collecting task metrics: {e}")
            return None
    
    def collect_thread_metrics(self, thread_data: Dict[str, Any]) -> ThreadAnalytics:
        """Collect metrics from thread data"""
        try:
            # Calculate response times
            first_response_time = 0.0
            avg_response_time = 0.0
            resolution_time = 0.0
            
            if 'messages' in thread_data and thread_data['messages']:
                messages = thread_data['messages']
                message_count = len(messages)
                
                # Calculate first response time
                if message_count > 1:
                    first_message = messages[0]
                    second_message = messages[1]
                    if 'timestamp' in first_message and 'timestamp' in second_message:
                        first_ts = datetime.fromisoformat(first_message['timestamp'].replace('Z', '+00:00'))
                        second_ts = datetime.fromisoformat(second_message['timestamp'].replace('Z', '+00:00'))
                        first_response_time = (second_ts - first_ts).total_seconds() / 60
                
                # Calculate average response time
                response_times = []
                for i in range(1, len(messages)):
                    prev_ts = datetime.fromisoformat(messages[i-1]['timestamp'].replace('Z', '+00:00'))
                    curr_ts = datetime.fromisoformat(messages[i]['timestamp'].replace('Z', '+00:00'))
                    response_times.append((curr_ts - prev_ts).total_seconds() / 60)
                
                if response_times:
                    avg_response_time = statistics.mean(response_times)
                
                # Calculate resolution time
                if 'resolved_at' in thread_data and 'created_at' in thread_data:
                    created = datetime.fromisoformat(thread_data['created_at'].replace('Z', '+00:00'))
                    resolved = datetime.fromisoformat(thread_data['resolved_at'].replace('Z', '+00:00'))
                    resolution_time = (resolved - created).total_seconds() / 60
            
            # Handle both 'id' and 'thread_id' field names for compatibility
            thread_id = thread_data.get('thread_id') or thread_data.get('id', '')
            analytics = ThreadAnalytics(
                thread_id=thread_id,
                created_at=thread_data.get('created_at', get_current_timestamp()),
                updated_at=thread_data.get('updated_at', get_current_timestamp()),
                status=thread_data.get('status', 'Active'),
                priority=thread_data.get('priority', 'Medium'),
                message_count=thread_data.get('message_count', 0),
                participant_count=thread_data.get('participant_count', 0),
                first_response_time_minutes=first_response_time,
                resolution_time_minutes=resolution_time,
                avg_response_time_minutes=avg_response_time,
                escalation_count=thread_data.get('escalation_count', 0),
                satisfaction_score=thread_data.get('satisfaction_score'),
                tags=thread_data.get('tags', []),
                metadata=thread_data.get('metadata', {})
            )
            
            return analytics
        except Exception as e:
            logger.error(f"Error collecting thread metrics: {e}")
            return None
    
    def collect_system_metrics(self, service_name: str, metrics: Dict[str, Any]) -> SystemHealth:
        """Collect system health metrics"""
        try:
            health = create_system_health(
                service_name=service_name,
                status=metrics.get('status', 'healthy'),
                response_time_ms=metrics.get('response_time_ms', 0.0),
                error_rate=metrics.get('error_rate', 0.0),
                cpu_usage=metrics.get('cpu_usage', 0.0),
                memory_usage=metrics.get('memory_usage', 0.0),
                disk_usage=metrics.get('disk_usage', 0.0),
                active_connections=metrics.get('active_connections', 0),
                metadata=metrics.get('metadata', {})
            )
            
            return health
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return None
    
    def collect_user_behavior(self, user_id: str, session_id: str, 
                            action: str, page: str, **kwargs) -> UserBehavior:
        """Collect user behavior metrics"""
        try:
            behavior = UserBehavior(
                user_id=user_id,
                session_id=session_id,
                timestamp=get_current_timestamp(),
                action=action,
                page=page,
                duration_seconds=kwargs.get('duration_seconds', 0.0),
                user_agent=kwargs.get('user_agent', ''),
                ip_address=kwargs.get('ip_address', ''),
                metadata=kwargs.get('metadata', {})
            )
            
            return behavior
        except Exception as e:
            logger.error(f"Error collecting user behavior: {e}")
            return None

class DataAggregator:
    """Data aggregation and processing"""
    
    def __init__(self, persistence: AnalyticsDataPersistence):
        self.persistence = persistence
    
    def aggregate_task_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Aggregate task metrics for a time period"""
        try:
            tasks = self.persistence.load_task_analytics(start_date, end_date)
            
            if not tasks:
                return self._empty_aggregation()
            
            # Basic counts
            total_tasks = len(tasks)
            status_counts = Counter(task.status for task in tasks)
            priority_counts = Counter(task.priority for task in tasks)
            category_counts = Counter(task.category for task in tasks)
            
            # Response time metrics
            response_times = [task.response_time_minutes for task in tasks if task.response_time_minutes > 0]
            avg_response_time = statistics.mean(response_times) if response_times else 0
            
            # Resolution time metrics
            resolution_times = [task.resolution_time_minutes for task in tasks if task.resolution_time_minutes > 0]
            avg_resolution_time = statistics.mean(resolution_times) if resolution_times else 0
            
            # Escalation metrics
            escalated_tasks = sum(1 for task in tasks if task.escalation_count > 0)
            escalation_rate = (escalated_tasks / total_tasks) * 100 if total_tasks > 0 else 0
            
            # Satisfaction metrics
            satisfaction_scores = [task.satisfaction_score for task in tasks if task.satisfaction_score is not None]
            avg_satisfaction = statistics.mean(satisfaction_scores) if satisfaction_scores else 0
            
            return {
                'total_tasks': total_tasks,
                'status_distribution': dict(status_counts),
                'priority_distribution': dict(priority_counts),
                'category_distribution': dict(category_counts),
                'avg_response_time_minutes': round(avg_response_time, 2),
                'avg_resolution_time_minutes': round(avg_resolution_time, 2),
                'escalation_rate_percent': round(escalation_rate, 2),
                'avg_satisfaction_score': round(avg_satisfaction, 2),
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error aggregating task metrics: {e}")
            return self._empty_aggregation()
    
    def aggregate_thread_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Aggregate thread metrics for a time period"""
        try:
            threads = self.persistence.load_thread_analytics(start_date, end_date)
            
            if not threads:
                return self._empty_aggregation()
            
            # Basic counts
            total_threads = len(threads)
            status_counts = Counter(thread.status for thread in threads)
            priority_counts = Counter(thread.priority for thread in threads)
            
            # Message metrics
            total_messages = sum(thread.message_count for thread in threads)
            avg_messages_per_thread = total_messages / total_threads if total_threads > 0 else 0
            
            # Response time metrics
            first_response_times = [thread.first_response_time_minutes for thread in threads if thread.first_response_time_minutes > 0]
            avg_first_response_time = statistics.mean(first_response_times) if first_response_times else 0
            
            avg_response_times = [thread.avg_response_time_minutes for thread in threads if thread.avg_response_time_minutes > 0]
            overall_avg_response_time = statistics.mean(avg_response_times) if avg_response_times else 0
            
            # Resolution time metrics
            resolution_times = [thread.resolution_time_minutes for thread in threads if thread.resolution_time_minutes > 0]
            avg_resolution_time = statistics.mean(resolution_times) if resolution_times else 0
            
            # Escalation metrics
            escalated_threads = sum(1 for thread in threads if thread.escalation_count > 0)
            escalation_rate = (escalated_threads / total_threads) * 100 if total_threads > 0 else 0
            
            return {
                'total_threads': total_threads,
                'total_messages': total_messages,
                'avg_messages_per_thread': round(avg_messages_per_thread, 2),
                'status_distribution': dict(status_counts),
                'priority_distribution': dict(priority_counts),
                'avg_first_response_time_minutes': round(avg_first_response_time, 2),
                'avg_response_time_minutes': round(overall_avg_response_time, 2),
                'avg_resolution_time_minutes': round(avg_resolution_time, 2),
                'escalation_rate_percent': round(escalation_rate, 2),
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error aggregating thread metrics: {e}")
            return self._empty_aggregation()
    
    def aggregate_performance_metrics(self, start_date: datetime, end_date: datetime, 
                                    metric_type: Optional[str] = None) -> Dict[str, Any]:
        """Aggregate performance metrics for a time period"""
        try:
            metrics = self.persistence.load_performance_metrics(start_date, end_date, metric_type)
            
            if not metrics:
                return self._empty_performance_aggregation()
            
            # Group by metric type
            by_type = defaultdict(list)
            for metric in metrics:
                by_type[metric.metric_type].append(metric.value)
            
            aggregated = {}
            for metric_type, values in by_type.items():
                if values:
                    aggregated[metric_type] = {
                        'count': len(values),
                        'min': min(values),
                        'max': max(values),
                        'avg': round(statistics.mean(values), 2),
                        'median': round(statistics.median(values), 2),
                        'std_dev': round(statistics.stdev(values), 2) if len(values) > 1 else 0
                    }
            
            return {
                'metrics': aggregated,
                'total_metrics': len(metrics),
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error aggregating performance metrics: {e}")
            return self._empty_performance_aggregation()
    
    def aggregate_system_health(self, start_date: datetime, end_date: datetime, 
                              service_name: Optional[str] = None) -> Dict[str, Any]:
        """Aggregate system health metrics for a time period"""
        try:
            health_data = self.persistence.load_system_health(start_date, end_date, service_name)
            
            if not health_data:
                return self._empty_aggregation()
            
            # Group by service
            by_service = defaultdict(list)
            for health in health_data:
                by_service[health.service_name].append(health)
            
            aggregated = {}
            for service, health_records in by_service.items():
                if health_records:
                    # Calculate averages
                    avg_response_time = statistics.mean([h.response_time_ms for h in health_records])
                    avg_error_rate = statistics.mean([h.error_rate for h in health_records])
                    avg_cpu = statistics.mean([h.cpu_usage for h in health_records])
                    avg_memory = statistics.mean([h.memory_usage for h in health_records])
                    avg_disk = statistics.mean([h.disk_usage for h in health_records])
                    
                    # Status distribution
                    status_counts = Counter(h.status for h in health_records)
                    
                    aggregated[service] = {
                        'total_records': len(health_records),
                        'avg_response_time_ms': round(avg_response_time, 2),
                        'avg_error_rate': round(avg_error_rate, 4),
                        'avg_cpu_usage': round(avg_cpu, 2),
                        'avg_memory_usage': round(avg_memory, 2),
                        'avg_disk_usage': round(avg_disk, 2),
                        'status_distribution': dict(status_counts),
                        'uptime_percent': round((status_counts.get('healthy', 0) / len(health_records)) * 100, 2)
                    }
            
            return {
                'services': aggregated,
                'total_records': len(health_data),
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Error aggregating system health: {e}")
            return self._empty_aggregation()
    
    def _empty_aggregation(self) -> Dict[str, Any]:
        """Return empty aggregation structure"""
        return {
            'total_tasks': 0,
            'status_distribution': {},
            'priority_distribution': {},
            'category_distribution': {},
            'avg_response_time_minutes': 0,
            'avg_resolution_time_minutes': 0,
            'escalation_rate_percent': 0,
            'avg_satisfaction_score': 0,
            'services': {},
            'total_records': 0,
            'period': {
                'start': datetime.now(timezone.utc).isoformat(),
                'end': datetime.now(timezone.utc).isoformat()
            }
        }
    
    def _empty_performance_aggregation(self) -> Dict[str, Any]:
        """Return empty performance metrics aggregation structure"""
        return {
            'metrics': {},
            'total_metrics': 0,
            'period': {
                'start': datetime.now(timezone.utc).isoformat(),
                'end': datetime.now(timezone.utc).isoformat()
            }
        }

class AnalyticsFramework:
    """Main analytics framework"""
    
    def __init__(self, config: AnalyticsConfig = None):
        self.config = config or AnalyticsConfig()
        self.persistence = AnalyticsDataPersistence()
        self.collector = MetricsCollector(self.persistence)
        self.aggregator = DataAggregator(self.persistence)
        
        self._running = False
        self._threads = []
        self._executor = ThreadPoolExecutor(max_workers=self.config.max_workers)
        
        logger.info("Analytics framework initialized")
    
    def start(self):
        """Start the analytics framework"""
        if self._running:
            logger.warning("Analytics framework is already running")
            return
        
        self._running = True
        
        if self.config.enable_real_time:
            # Start real-time collection thread
            collection_thread = threading.Thread(target=self._collection_worker, daemon=True)
            collection_thread.start()
            self._threads.append(collection_thread)
            
            # Start aggregation thread
            aggregation_thread = threading.Thread(target=self._aggregation_worker, daemon=True)
            aggregation_thread.start()
            self._threads.append(aggregation_thread)
        
        logger.info("Analytics framework started")
    
    def stop(self):
        """Stop the analytics framework"""
        if not self._running:
            return
        
        self._running = False
        
        # Wait for threads to finish
        for thread in self._threads:
            thread.join(timeout=5)
        
        # Shutdown executor
        self._executor.shutdown(wait=True)
        
        logger.info("Analytics framework stopped")
    
    def _collection_worker(self):
        """Background worker for data collection"""
        while self._running:
            try:
                # Collect system health metrics
                self._collect_system_health()
                
                # Sleep for collection interval
                time.sleep(self.config.collection_interval_seconds)
            except Exception as e:
                logger.error(f"Error in collection worker: {e}")
                time.sleep(60)  # Wait a minute before retrying
    
    def _aggregation_worker(self):
        """Background worker for data aggregation"""
        while self._running:
            try:
                # Perform periodic aggregation
                end_time = datetime.now(timezone.utc)
                start_time = end_time - timedelta(minutes=self.config.aggregation_interval_minutes)
                
                # Aggregate metrics
                self._perform_aggregation(start_time, end_time)
                
                # Sleep for aggregation interval
                time.sleep(self.config.aggregation_interval_minutes * 60)
            except Exception as e:
                logger.error(f"Error in aggregation worker: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying
    
    def _collect_system_health(self):
        """Collect system health metrics"""
        try:
            # Collect basic system metrics
            import psutil
            
            # CPU and memory usage
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Create system health record
            health = self.collector.collect_system_metrics('system', {
                'status': 'healthy' if cpu_usage < 80 and memory.percent < 80 else 'degraded',
                'cpu_usage': cpu_usage,
                'memory_usage': memory.percent,
                'disk_usage': (disk.used / disk.total) * 100,
                'active_connections': len(psutil.net_connections()),
                'metadata': {
                    'memory_total_gb': round(memory.total / (1024**3), 2),
                    'disk_total_gb': round(disk.total / (1024**3), 2)
                }
            })
            
            if health:
                self.persistence.save_system_health(health)
                
        except Exception as e:
            logger.error(f"Error collecting system health: {e}")
    
    def _perform_aggregation(self, start_time: datetime, end_time: datetime):
        """Perform data aggregation for a time period"""
        try:
            # Create performance metrics from aggregated data
            task_metrics = self.aggregator.aggregate_task_metrics(start_time, end_time)
            thread_metrics = self.aggregator.aggregate_thread_metrics(start_time, end_time)
            
            # Save aggregated metrics
            metrics = [
                create_performance_metric('response_time', task_metrics['avg_response_time_minutes'], 'minutes', 'tasks'),
                create_performance_metric('resolution_time', task_metrics['avg_resolution_time_minutes'], 'minutes', 'tasks'),
                create_performance_metric('escalation_rate', task_metrics['escalation_rate_percent'], 'percent', 'tasks'),
                create_performance_metric('satisfaction', task_metrics['avg_satisfaction_score'], 'score', 'tasks'),
                create_performance_metric('thread_response_time', thread_metrics['avg_response_time_minutes'], 'minutes', 'threads'),
                create_performance_metric('thread_resolution_time', thread_metrics['avg_resolution_time_minutes'], 'minutes', 'threads')
            ]
            
            self.persistence.save_performance_metrics(metrics)
            
        except Exception as e:
            logger.error(f"Error performing aggregation: {e}")
    
    def process_task_data(self, task_data: Dict[str, Any]) -> bool:
        """Process task data and collect metrics"""
        try:
            analytics = self.collector.collect_task_metrics(task_data)
            if analytics:
                return self.persistence.save_task_analytics(analytics)
            return False
        except Exception as e:
            logger.error(f"Error processing task data: {e}")
            return False
    
    def process_thread_data(self, thread_data: Dict[str, Any]) -> bool:
        """Process thread data and collect metrics"""
        try:
            analytics = self.collector.collect_thread_metrics(thread_data)
            if analytics:
                return self.persistence.save_thread_analytics(analytics)
            return False
        except Exception as e:
            logger.error(f"Error processing thread data: {e}")
            return False
    
    def track_user_behavior(self, user_id: str, session_id: str, action: str, page: str, **kwargs) -> bool:
        """Track user behavior"""
        try:
            behavior = self.collector.collect_user_behavior(user_id, session_id, action, page, **kwargs)
            if behavior:
                return self.persistence.save_user_behavior(behavior)
            return False
        except Exception as e:
            logger.error(f"Error tracking user behavior: {e}")
            return False
    
    def get_analytics_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        try:
            # Aggregate all metrics
            task_metrics = self.aggregator.aggregate_task_metrics(start_date, end_date)
            thread_metrics = self.aggregator.aggregate_thread_metrics(start_date, end_date)
            performance_metrics = self.aggregator.aggregate_performance_metrics(start_date, end_date)
            system_health = self.aggregator.aggregate_system_health(start_date, end_date)
            
            return {
                'report_period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'duration_days': (end_date - start_date).days
                },
                'task_analytics': task_metrics,
                'thread_analytics': thread_metrics,
                'performance_metrics': performance_metrics,
                'system_health': system_health,
                'generated_at': get_current_timestamp()
            }
        except Exception as e:
            logger.error(f"Error generating analytics report: {e}")
            return {}
    
    def get_user_behavior_analytics(self, user_id: str = None, days: int = 7, action: str = None) -> Dict[str, Any]:
        """Get user behavior analytics"""
        try:
            # Get user behavior data from persistence
            behavior_data = self.persistence.get_user_behavior(
                user_id=user_id,
                days=days,
                action=action
            )
            
            if not behavior_data:
                return {
                    'total_actions': 0,
                    'unique_users': 0,
                    'top_actions': [],
                    'user_activity': [],
                    'session_stats': {},
                    'page_views': {},
                    'action_timeline': []
                }
            
            # Process the data
            total_actions = len(behavior_data)
            unique_users = len(set(item.get('user_id') for item in behavior_data if item.get('user_id')))
            
            # Top actions
            action_counts = {}
            for item in behavior_data:
                action_name = item.get('action', 'unknown')
                action_counts[action_name] = action_counts.get(action_name, 0) + 1
            
            top_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # User activity
            user_activity = {}
            for item in behavior_data:
                uid = item.get('user_id', 'unknown')
                if uid not in user_activity:
                    user_activity[uid] = 0
                user_activity[uid] += 1
            
            # Session stats
            session_stats = {
                'total_sessions': len(set(item.get('session_id') for item in behavior_data if item.get('session_id'))),
                'avg_actions_per_session': total_actions / max(1, len(set(item.get('session_id') for item in behavior_data if item.get('session_id'))))
            }
            
            # Page views
            page_views = {}
            for item in behavior_data:
                page = item.get('page', 'unknown')
                page_views[page] = page_views.get(page, 0) + 1
            
            # Action timeline (last 24 hours)
            from datetime import datetime, timedelta
            now = datetime.now()
            timeline = []
            for hour in range(24):
                hour_start = now - timedelta(hours=hour)
                hour_end = hour_start + timedelta(hours=1)
                count = sum(1 for item in behavior_data 
                           if hour_start <= datetime.fromisoformat(item.get('timestamp', now.isoformat()).replace('Z', '+00:00')).replace(tzinfo=None) <= hour_end)
                timeline.append({'hour': hour_start.strftime('%H:00'), 'count': count})
            
            return {
                'total_actions': total_actions,
                'unique_users': unique_users,
                'top_actions': [{'action': action, 'count': count} for action, count in top_actions],
                'user_activity': [{'user_id': uid, 'action_count': count} for uid, count in user_activity.items()],
                'session_stats': session_stats,
                'page_views': page_views,
                'action_timeline': timeline,
                'period_days': days,
                'filtered_by_user': user_id,
                'filtered_by_action': action
            }
            
        except Exception as e:
            logger.error(f"Error getting user behavior analytics: {e}")
            return {
                'total_actions': 0,
                'unique_users': 0,
                'top_actions': [],
                'user_activity': [],
                'session_stats': {},
                'page_views': {},
                'action_timeline': [],
                'error': str(e)
            }
    
    def cleanup_old_data(self) -> int:
        """Clean up old data"""
        return self.persistence.cleanup_old_data()
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        return self.persistence.get_storage_stats()
