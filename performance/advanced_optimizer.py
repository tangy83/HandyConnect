#!/usr/bin/env python3
"""
Advanced Performance Optimizer for HandyConnect Phase 12
Comprehensive performance optimization across all components
"""

import os
import time
import logging
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import gc
import json

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: datetime
    component: str
    metric_name: str
    value: float
    unit: str
    threshold_warning: float
    threshold_critical: float
    metadata: Dict[str, Any] = None

@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation"""
    id: str
    component: str
    issue_type: str  # memory, cpu, disk, network, database, cache
    severity: str  # low, medium, high, critical
    title: str
    description: str
    current_value: float
    target_value: float
    improvement_potential: float  # Percentage improvement expected
    implementation_effort: str  # low, medium, high
    estimated_impact: str
    recommendations: List[str]
    created_at: datetime

@dataclass
class CacheConfig:
    """Cache configuration for optimization"""
    component: str
    cache_type: str  # memory, redis, disk
    max_size: int
    ttl_seconds: int
    eviction_policy: str  # lru, lfu, ttl
    compression: bool
    serialization: str  # json, pickle, msgpack

class AdvancedPerformanceOptimizer:
    """Advanced performance optimization system"""
    
    def __init__(self):
        self.metrics_history = []
        self.optimization_recommendations = []
        self.cache_configs = {}
        self.performance_baselines = {}
        
        self.is_monitoring = False
        self.monitoring_thread = None
        
        # Performance thresholds
        self.thresholds = {
            'cpu_usage_percent': {'warning': 70, 'critical': 90},
            'memory_usage_percent': {'warning': 80, 'critical': 95},
            'disk_io_wait_percent': {'warning': 20, 'critical': 50},
            'network_latency_ms': {'warning': 100, 'critical': 500},
            'database_query_time_ms': {'warning': 1000, 'critical': 5000},
            'api_response_time_ms': {'warning': 2000, 'critical': 10000},
            'cache_hit_ratio_percent': {'warning': 70, 'critical': 50}
        }
        
        logger.info("Advanced Performance Optimizer initialized")
    
    def start_monitoring(self, interval_seconds: int = 30):
        """Start continuous performance monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_worker,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitoring_thread.start()
        
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Performance monitoring stopped")
    
    def _monitoring_worker(self, interval_seconds: int):
        """Background worker for performance monitoring"""
        while self.is_monitoring:
            try:
                self._collect_system_metrics()
                self._collect_application_metrics()
                self._collect_database_metrics()
                self._collect_cache_metrics()
                self._collect_network_metrics()
                
                # Analyze metrics and generate recommendations
                self._analyze_performance()
                
                # Clean old metrics (keep last 24 hours)
                cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
                self.metrics_history = [
                    metric for metric in self.metrics_history
                    if metric.timestamp > cutoff_time
                ]
                
                time.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                time.sleep(interval_seconds)
    
    def _collect_system_metrics(self):
        """Collect system-level performance metrics"""
        try:
            now = datetime.now(timezone.utc)
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            self._add_metric('system', 'cpu_usage_percent', cpu_percent, '%', now)
            self._add_metric('system', 'cpu_count', cpu_count, 'cores', now)
            if cpu_freq:
                self._add_metric('system', 'cpu_frequency_mhz', cpu_freq.current, 'MHz', now)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self._add_metric('system', 'memory_usage_percent', memory.percent, '%', now)
            self._add_metric('system', 'memory_available_gb', memory.available / (1024**3), 'GB', now)
            self._add_metric('system', 'memory_used_gb', memory.used / (1024**3), 'GB', now)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            self._add_metric('system', 'disk_usage_percent', (disk.used / disk.total) * 100, '%', now)
            self._add_metric('system', 'disk_free_gb', disk.free / (1024**3), 'GB', now)
            
            # Disk I/O metrics
            disk_io = psutil.disk_io_counters()
            if disk_io:
                self._add_metric('system', 'disk_read_mb', disk_io.read_bytes / (1024**2), 'MB', now)
                self._add_metric('system', 'disk_write_mb', disk_io.write_bytes / (1024**2), 'MB', now)
            
            # Network metrics
            network_io = psutil.net_io_counters()
            if network_io:
                self._add_metric('system', 'network_bytes_sent_mb', network_io.bytes_sent / (1024**2), 'MB', now)
                self._add_metric('system', 'network_bytes_recv_mb', network_io.bytes_recv / (1024**2), 'MB', now)
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def _collect_application_metrics(self):
        """Collect application-level performance metrics"""
        try:
            now = datetime.now(timezone.utc)
            
            # Process metrics
            process = psutil.Process()
            
            # Memory usage
            memory_info = process.memory_info()
            self._add_metric('application', 'process_memory_mb', memory_info.rss / (1024**2), 'MB', now)
            
            # CPU usage
            cpu_percent = process.cpu_percent()
            self._add_metric('application', 'process_cpu_percent', cpu_percent, '%', now)
            
            # Thread count
            thread_count = process.num_threads()
            self._add_metric('application', 'thread_count', thread_count, 'threads', now)
            
            # File descriptors
            try:
                fd_count = process.num_fds()
                self._add_metric('application', 'file_descriptors', fd_count, 'count', now)
            except (AttributeError, psutil.AccessDenied):
                pass  # Not available on all platforms
            
            # Garbage collection metrics
            gc_stats = gc.get_stats()
            total_collections = sum(stat['collections'] for stat in gc_stats)
            self._add_metric('application', 'gc_collections', total_collections, 'count', now)
            
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
    
    def _collect_database_metrics(self):
        """Collect database performance metrics"""
        try:
            now = datetime.now(timezone.utc)
            
            # This would integrate with actual database monitoring
            # For now, simulate some metrics
            
            # Simulate database connection pool metrics
            connection_pool_size = 20  # This would come from actual DB connection pool
            active_connections = 5
            self._add_metric('database', 'connection_pool_size', connection_pool_size, 'connections', now)
            self._add_metric('database', 'active_connections', active_connections, 'connections', now)
            
            # Simulate query performance metrics
            avg_query_time = 150  # milliseconds
            self._add_metric('database', 'avg_query_time_ms', avg_query_time, 'ms', now)
            
            # Simulate cache metrics
            cache_hit_ratio = 85  # percentage
            self._add_metric('database', 'cache_hit_ratio_percent', cache_hit_ratio, '%', now)
            
        except Exception as e:
            logger.error(f"Error collecting database metrics: {e}")
    
    def _collect_cache_metrics(self):
        """Collect cache performance metrics"""
        try:
            now = datetime.now(timezone.utc)
            
            # This would integrate with actual cache monitoring (Redis, etc.)
            # For now, simulate some metrics
            
            # Simulate cache performance
            cache_size_mb = 50
            cache_evictions = 10
            cache_hit_rate = 78
            
            self._add_metric('cache', 'cache_size_mb', cache_size_mb, 'MB', now)
            self._add_metric('cache', 'cache_evictions', cache_evictions, 'count', now)
            self._add_metric('cache', 'cache_hit_rate_percent', cache_hit_rate, '%', now)
            
        except Exception as e:
            logger.error(f"Error collecting cache metrics: {e}")
    
    def _collect_network_metrics(self):
        """Collect network performance metrics"""
        try:
            now = datetime.now(timezone.utc)
            
            # Simulate network latency measurements
            # In a real implementation, this would ping external services
            
            api_response_time = 250  # milliseconds
            self._add_metric('network', 'api_response_time_ms', api_response_time, 'ms', now)
            
            # Simulate external service health
            external_service_latency = 120  # milliseconds
            self._add_metric('network', 'external_service_latency_ms', external_service_latency, 'ms', now)
            
        except Exception as e:
            logger.error(f"Error collecting network metrics: {e}")
    
    def _add_metric(self, component: str, metric_name: str, value: float, unit: str, timestamp: datetime):
        """Add a performance metric to the history"""
        threshold_warning = self.thresholds.get(metric_name, {}).get('warning', 80)
        threshold_critical = self.thresholds.get(metric_name, {}).get('critical', 95)
        
        metric = PerformanceMetrics(
            timestamp=timestamp,
            component=component,
            metric_name=metric_name,
            value=value,
            unit=unit,
            threshold_warning=threshold_warning,
            threshold_critical=threshold_critical
        )
        
        self.metrics_history.append(metric)
    
    def _analyze_performance(self):
        """Analyze performance metrics and generate recommendations"""
        try:
            # Get recent metrics (last hour)
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
            recent_metrics = [
                metric for metric in self.metrics_history
                if metric.timestamp > cutoff_time
            ]
            
            # Group metrics by component
            metrics_by_component = {}
            for metric in recent_metrics:
                if metric.component not in metrics_by_component:
                    metrics_by_component[metric.component] = []
                metrics_by_component[metric.component].append(metric)
            
            # Analyze each component
            for component, metrics in metrics_by_component.items():
                self._analyze_component_performance(component, metrics)
            
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
    
    def _analyze_component_performance(self, component: str, metrics: List[PerformanceMetrics]):
        """Analyze performance for a specific component"""
        try:
            # Check for threshold violations
            for metric in metrics:
                if metric.value >= metric.threshold_critical:
                    self._generate_critical_recommendation(component, metric)
                elif metric.value >= metric.threshold_warning:
                    self._generate_warning_recommendation(component, metric)
            
            # Check for trends
            self._analyze_performance_trends(component, metrics)
            
            # Check for resource optimization opportunities
            self._analyze_optimization_opportunities(component, metrics)
            
        except Exception as e:
            logger.error(f"Error analyzing component {component}: {e}")
    
    def _generate_critical_recommendation(self, component: str, metric: PerformanceMetrics):
        """Generate critical performance recommendation"""
        recommendation = OptimizationRecommendation(
            id=f"critical_{component}_{metric.metric_name}_{int(time.time())}",
            component=component,
            issue_type=self._get_issue_type(metric.metric_name),
            severity='critical',
            title=f"Critical {metric.metric_name} Issue",
            description=f"{metric.metric_name} is at critical levels: {metric.value:.1f}{metric.unit}",
            current_value=metric.value,
            target_value=metric.threshold_warning,
            improvement_potential=self._calculate_improvement_potential(metric),
            implementation_effort='medium',
            estimated_impact='high',
            recommendations=self._get_optimization_recommendations(component, metric),
            created_at=datetime.now(timezone.utc)
        )
        
        self.optimization_recommendations.append(recommendation)
        logger.warning(f"Critical performance issue detected: {recommendation.title}")
    
    def _generate_warning_recommendation(self, component: str, metric: PerformanceMetrics):
        """Generate warning performance recommendation"""
        recommendation = OptimizationRecommendation(
            id=f"warning_{component}_{metric.metric_name}_{int(time.time())}",
            component=component,
            issue_type=self._get_issue_type(metric.metric_name),
            severity='medium',
            title=f"Warning: {metric.metric_name} Approaching Limit",
            description=f"{metric.metric_name} is approaching warning threshold: {metric.value:.1f}{metric.unit}",
            current_value=metric.value,
            target_value=metric.threshold_warning * 0.8,  # Target 20% below warning
            improvement_potential=self._calculate_improvement_potential(metric),
            implementation_effort='low',
            estimated_impact='medium',
            recommendations=self._get_optimization_recommendations(component, metric),
            created_at=datetime.now(timezone.utc)
        )
        
        self.optimization_recommendations.append(recommendation)
        logger.info(f"Performance warning: {recommendation.title}")
    
    def _analyze_performance_trends(self, component: str, metrics: List[PerformanceMetrics]):
        """Analyze performance trends"""
        try:
            # Group metrics by name
            metrics_by_name = {}
            for metric in metrics:
                if metric.metric_name not in metrics_by_name:
                    metrics_by_name[metric.metric_name] = []
                metrics_by_name[metric.metric_name].append(metric)
            
            # Analyze trends for each metric
            for metric_name, metric_list in metrics_by_name.items():
                if len(metric_list) < 3:  # Need at least 3 data points
                    continue
                
                # Sort by timestamp
                metric_list.sort(key=lambda x: x.timestamp)
                
                # Calculate trend
                values = [m.value for m in metric_list]
                trend = self._calculate_trend(values)
                
                # If trend is worsening significantly, generate recommendation
                if trend > 0.1:  # 10% increase per data point
                    self._generate_trend_recommendation(component, metric_name, trend, values[-1])
                
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
    
    def _analyze_optimization_opportunities(self, component: str, metrics: List[PerformanceMetrics]):
        """Analyze optimization opportunities"""
        try:
            # Look for optimization opportunities based on current metrics
            for metric in metrics:
                if metric.metric_name == 'cache_hit_rate_percent' and metric.value < 70:
                    self._generate_cache_optimization_recommendation(component, metric)
                elif metric.metric_name == 'memory_usage_percent' and metric.value > 60:
                    self._generate_memory_optimization_recommendation(component, metric)
                elif metric.metric_name == 'cpu_usage_percent' and metric.value > 50:
                    self._generate_cpu_optimization_recommendation(component, metric)
                
        except Exception as e:
            logger.error(f"Error analyzing optimization opportunities: {e}")
    
    def _get_issue_type(self, metric_name: str) -> str:
        """Determine issue type from metric name"""
        if 'memory' in metric_name or 'ram' in metric_name:
            return 'memory'
        elif 'cpu' in metric_name or 'processor' in metric_name:
            return 'cpu'
        elif 'disk' in metric_name or 'storage' in metric_name:
            return 'disk'
        elif 'network' in metric_name or 'latency' in metric_name:
            return 'network'
        elif 'database' in metric_name or 'query' in metric_name:
            return 'database'
        elif 'cache' in metric_name:
            return 'cache'
        else:
            return 'general'
    
    def _calculate_improvement_potential(self, metric: PerformanceMetrics) -> float:
        """Calculate potential improvement percentage"""
        if metric.value <= metric.threshold_warning:
            return 0
        
        improvement = ((metric.value - metric.threshold_warning) / metric.value) * 100
        return min(improvement, 50)  # Cap at 50% improvement potential
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend direction and magnitude"""
        if len(values) < 2:
            return 0
        
        # Simple linear trend calculation
        n = len(values)
        x = list(range(n))
        y = values
        
        # Calculate slope
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        # Normalize by average value
        avg_value = sum_y / n
        normalized_trend = slope / avg_value if avg_value > 0 else 0
        
        return normalized_trend
    
    def _get_optimization_recommendations(self, component: str, metric: PerformanceMetrics) -> List[str]:
        """Get optimization recommendations for a specific metric"""
        recommendations = []
        
        if 'memory' in metric.metric_name:
            recommendations.extend([
                "Increase available memory",
                "Optimize memory usage in application code",
                "Implement memory caching strategies",
                "Review memory leaks in application"
            ])
        elif 'cpu' in metric.metric_name:
            recommendations.extend([
                "Optimize CPU-intensive operations",
                "Implement multi-threading for parallel processing",
                "Use caching to reduce computational load",
                "Review and optimize algorithms"
            ])
        elif 'disk' in metric.metric_name:
            recommendations.extend([
                "Optimize disk I/O operations",
                "Implement disk caching",
                "Use faster storage (SSD)",
                "Optimize database queries and indexes"
            ])
        elif 'network' in metric.metric_name:
            recommendations.extend([
                "Optimize network requests",
                "Implement request batching",
                "Use CDN for static content",
                "Optimize API endpoints"
            ])
        elif 'database' in metric.metric_name:
            recommendations.extend([
                "Optimize database queries",
                "Add appropriate indexes",
                "Implement query caching",
                "Consider database connection pooling"
            ])
        elif 'cache' in metric.metric_name:
            recommendations.extend([
                "Increase cache size",
                "Optimize cache eviction policies",
                "Implement cache warming strategies",
                "Review cache key strategies"
            ])
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _generate_trend_recommendation(self, component: str, metric_name: str, trend: float, current_value: float):
        """Generate recommendation based on performance trend"""
        recommendation = OptimizationRecommendation(
            id=f"trend_{component}_{metric_name}_{int(time.time())}",
            component=component,
            issue_type=self._get_issue_type(metric_name),
            severity='medium' if trend > 0.2 else 'low',
            title=f"Performance Degradation Trend: {metric_name}",
            description=f"{metric_name} is showing a {trend*100:.1f}% increasing trend (current: {current_value:.1f})",
            current_value=current_value,
            target_value=current_value * 0.8,  # Target 20% reduction
            improvement_potential=trend * 100,
            implementation_effort='medium',
            estimated_impact='medium',
            recommendations=[
                "Monitor trend closely",
                "Implement proactive optimization",
                "Consider scaling resources",
                "Review recent changes that might affect performance"
            ],
            created_at=datetime.now(timezone.utc)
        )
        
        self.optimization_recommendations.append(recommendation)
    
    def _generate_cache_optimization_recommendation(self, component: str, metric: PerformanceMetrics):
        """Generate cache optimization recommendation"""
        recommendation = OptimizationRecommendation(
            id=f"cache_opt_{component}_{int(time.time())}",
            component=component,
            issue_type='cache',
            severity='medium',
            title=f"Cache Hit Rate Optimization Needed",
            description=f"Cache hit rate is {metric.value:.1f}%, below optimal threshold of 80%",
            current_value=metric.value,
            target_value=80.0,
            improvement_potential=((80.0 - metric.value) / metric.value) * 100,
            implementation_effort='medium',
            estimated_impact='high',
            recommendations=[
                "Increase cache size",
                "Optimize cache eviction policy",
                "Implement cache warming",
                "Review cache key strategies",
                "Add more cache layers"
            ],
            created_at=datetime.now(timezone.utc)
        )
        
        self.optimization_recommendations.append(recommendation)
    
    def _generate_memory_optimization_recommendation(self, component: str, metric: PerformanceMetrics):
        """Generate memory optimization recommendation"""
        recommendation = OptimizationRecommendation(
            id=f"memory_opt_{component}_{int(time.time())}",
            component=component,
            issue_type='memory',
            severity='medium',
            title=f"Memory Usage Optimization",
            description=f"Memory usage is {metric.value:.1f}%, consider optimization",
            current_value=metric.value,
            target_value=50.0,
            improvement_potential=((metric.value - 50.0) / metric.value) * 100,
            implementation_effort='high',
            estimated_impact='high',
            recommendations=[
                "Optimize memory usage in application code",
                "Implement memory pooling",
                "Review for memory leaks",
                "Use more efficient data structures",
                "Implement garbage collection optimization"
            ],
            created_at=datetime.now(timezone.utc)
        )
        
        self.optimization_recommendations.append(recommendation)
    
    def _generate_cpu_optimization_recommendation(self, component: str, metric: PerformanceMetrics):
        """Generate CPU optimization recommendation"""
        recommendation = OptimizationRecommendation(
            id=f"cpu_opt_{component}_{int(time.time())}",
            component=component,
            issue_type='cpu',
            severity='low',
            title=f"CPU Usage Optimization",
            description=f"CPU usage is {metric.value:.1f}%, consider optimization",
            current_value=metric.value,
            target_value=40.0,
            improvement_potential=((metric.value - 40.0) / metric.value) * 100,
            implementation_effort='medium',
            estimated_impact='medium',
            recommendations=[
                "Optimize CPU-intensive operations",
                "Implement parallel processing",
                "Use caching to reduce computation",
                "Review and optimize algorithms",
                "Consider horizontal scaling"
            ],
            created_at=datetime.now(timezone.utc)
        )
        
        self.optimization_recommendations.append(recommendation)
    
    def get_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            # Filter recent metrics and recommendations
            recent_metrics = [
                metric for metric in self.metrics_history
                if metric.timestamp > cutoff_time
            ]
            
            recent_recommendations = [
                rec for rec in self.optimization_recommendations
                if rec.created_at > cutoff_time
            ]
            
            # Calculate summary statistics
            summary = self._calculate_performance_summary(recent_metrics)
            
            # Group metrics by component
            metrics_by_component = {}
            for metric in recent_metrics:
                if metric.component not in metrics_by_component:
                    metrics_by_component[metric.component] = []
                metrics_by_component[metric.component].append(metric)
            
            # Group recommendations by severity
            recommendations_by_severity = {}
            for rec in recent_recommendations:
                if rec.severity not in recommendations_by_severity:
                    recommendations_by_severity[rec.severity] = []
                recommendations_by_severity[rec.severity].append(rec)
            
            report = {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'report_period_hours': hours,
                'summary': summary,
                'metrics_by_component': {
                    component: [asdict(metric) for metric in metrics]
                    for component, metrics in metrics_by_component.items()
                },
                'recommendations_by_severity': {
                    severity: [asdict(rec) for rec in recommendations]
                    for severity, recommendations in recommendations_by_severity.items()
                },
                'critical_issues': len(recommendations_by_severity.get('critical', [])),
                'warnings': len(recommendations_by_severity.get('medium', [])),
                'optimization_opportunities': len(recommendations_by_severity.get('low', []))
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {'error': str(e)}
    
    def _calculate_performance_summary(self, metrics: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Calculate performance summary statistics"""
        summary = {
            'total_metrics': len(metrics),
            'components_monitored': len(set(m.metric_name for m in metrics)),
            'threshold_violations': 0,
            'critical_issues': 0,
            'average_performance_score': 0
        }
        
        # Calculate threshold violations
        for metric in metrics:
            if metric.value >= metric.threshold_critical:
                summary['critical_issues'] += 1
                summary['threshold_violations'] += 1
            elif metric.value >= metric.threshold_warning:
                summary['threshold_violations'] += 1
        
        # Calculate average performance score (0-100)
        if metrics:
            performance_scores = []
            for metric in metrics:
                # Calculate score based on how close to thresholds
                if metric.value <= metric.threshold_warning:
                    score = 100
                elif metric.value <= metric.threshold_critical:
                    # Linear interpolation between warning and critical
                    ratio = (metric.threshold_critical - metric.value) / (metric.threshold_critical - metric.threshold_warning)
                    score = 50 + (ratio * 50)
                else:
                    # Below critical threshold
                    score = max(0, 50 - ((metric.value - metric.threshold_critical) / metric.threshold_critical) * 50)
                
                performance_scores.append(score)
            
            summary['average_performance_score'] = sum(performance_scores) / len(performance_scores)
        
        return summary
    
    def get_active_recommendations(self) -> List[OptimizationRecommendation]:
        """Get active optimization recommendations"""
        # Filter recommendations created in last 7 days
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=7)
        return [
            rec for rec in self.optimization_recommendations
            if rec.created_at > cutoff_time
        ]
    
    def get_critical_issues(self) -> List[OptimizationRecommendation]:
        """Get critical performance issues"""
        return [
            rec for rec in self.optimization_recommendations
            if rec.severity == 'critical'
        ]
    
    def clear_old_recommendations(self, days: int = 30):
        """Clear old recommendations"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)
        self.optimization_recommendations = [
            rec for rec in self.optimization_recommendations
            if rec.created_at > cutoff_time
        ]
        
        logger.info(f"Cleared recommendations older than {days} days")
    
    def optimize_cache_configuration(self, component: str, config: CacheConfig):
        """Optimize cache configuration for a component"""
        self.cache_configs[component] = config
        logger.info(f"Updated cache configuration for {component}")
    
    def get_cache_configuration(self, component: str) -> Optional[CacheConfig]:
        """Get cache configuration for a component"""
        return self.cache_configs.get(component)
    
    def set_performance_baseline(self, component: str, baseline_metrics: Dict[str, float]):
        """Set performance baseline for a component"""
        self.performance_baselines[component] = {
            'metrics': baseline_metrics,
            'set_at': datetime.now(timezone.utc)
        }
        logger.info(f"Set performance baseline for {component}")
    
    def get_performance_baseline(self, component: str) -> Optional[Dict[str, Any]]:
        """Get performance baseline for a component"""
        return self.performance_baselines.get(component)
