"""
Dashboard Performance Optimization and Caching
Author: Sunayana
Phase 10: Reporting Dashboard

This module provides performance optimization and caching for the real-time dashboard.
"""

import logging
import json
import time
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from functools import wraps
import hashlib
import pickle

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry data structure"""
    key: str
    data: Any
    created_at: datetime
    expires_at: datetime
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return datetime.now(timezone.utc) > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['expires_at'] = self.expires_at.isoformat()
        if self.last_accessed:
            data['last_accessed'] = self.last_accessed.isoformat()
        return data

class DashboardCache:
    """High-performance dashboard caching system"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []
        self._lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'size': 0
        }
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self._cleanup_thread.start()
        
        logger.info(f"Dashboard cache initialized (max_size={max_size}, ttl={default_ttl})")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            if key not in self.cache:
                self.stats['misses'] += 1
                return None
            
            entry = self.cache[key]
            
            if entry.is_expired():
                self._remove_entry(key)
                self.stats['misses'] += 1
                return None
            
            # Update access tracking
            entry.access_count += 1
            entry.last_accessed = datetime.now(timezone.utc)
            self._update_access_order(key)
            
            self.stats['hits'] += 1
            return entry.data
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        with self._lock:
            ttl = ttl or self.default_ttl
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(seconds=ttl)
            
            entry = CacheEntry(
                key=key,
                data=value,
                created_at=now,
                expires_at=expires_at,
                access_count=1,
                last_accessed=now
            )
            
            # Remove existing entry if it exists
            if key in self.cache:
                self._remove_entry(key)
            
            # Check if we need to evict
            if len(self.cache) >= self.max_size:
                self._evict_lru()
            
            self.cache[key] = entry
            self.access_order.append(key)
            self.stats['size'] = len(self.cache)
    
    def delete(self, key: str) -> bool:
        """Delete entry from cache"""
        with self._lock:
            if key in self.cache:
                self._remove_entry(key)
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self.cache.clear()
            self.access_order.clear()
            self.stats['size'] = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self.stats,
                'hit_rate_percent': round(hit_rate, 2),
                'total_requests': total_requests,
                'cache_size': len(self.cache),
                'max_size': self.max_size,
                'utilization_percent': round((len(self.cache) / self.max_size * 100), 2)
            }
    
    def _remove_entry(self, key: str) -> None:
        """Remove entry from cache and access order"""
        if key in self.cache:
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
            self.stats['size'] = len(self.cache)
    
    def _update_access_order(self, key: str) -> None:
        """Update access order for LRU tracking"""
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if self.access_order:
            lru_key = self.access_order.pop(0)
            if lru_key in self.cache:
                del self.cache[lru_key]
                self.stats['evictions'] += 1
                self.stats['size'] = len(self.cache)
                logger.debug(f"Evicted LRU entry: {lru_key}")
    
    def _cleanup_worker(self) -> None:
        """Background worker for cleaning expired entries"""
        while True:
            try:
                time.sleep(60)  # Run every minute
                self._cleanup_expired()
            except Exception as e:
                logger.error(f"Error in cache cleanup worker: {e}")
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries"""
        with self._lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                self._remove_entry(key)
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

class DashboardOptimizer:
    """Dashboard performance optimization utilities"""
    
    def __init__(self, cache: DashboardCache):
        self.cache = cache
        self.query_cache: Dict[str, Any] = {}
        self._query_lock = threading.Lock()
    
    def cache_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        # Sort kwargs for consistent keys
        sorted_kwargs = sorted(kwargs.items())
        key_data = f"{prefix}:{json.dumps(sorted_kwargs, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def cached_query(self, ttl: int = 300):
        """Decorator for caching expensive queries"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self.cache_key(func.__name__, **kwargs)
                
                # Try to get from cache
                cached_result = self.cache.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}: {cache_key}")
                    return cached_result
                
                # Execute function and cache result
                logger.debug(f"Cache miss for {func.__name__}: {cache_key}")
                result = func(*args, **kwargs)
                self.cache.set(cache_key, result, ttl)
                
                return result
            
            return wrapper
        return decorator
    
    def batch_queries(self, queries: List[Tuple[str, Dict]]) -> Dict[str, Any]:
        """Execute multiple queries in batch and cache results"""
        results = {}
        uncached_queries = []
        
        # Check cache for each query
        for query_name, query_params in queries:
            cache_key = self.cache_key(query_name, **query_params)
            cached_result = self.cache.get(cache_key)
            
            if cached_result is not None:
                results[query_name] = cached_result
            else:
                uncached_queries.append((query_name, query_params, cache_key))
        
        # Execute uncached queries
        if uncached_queries:
            logger.debug(f"Executing {len(uncached_queries)} uncached queries")
            # This would be implemented based on specific query types
            # For now, we'll just mark them as needing execution
        
        return results
    
    def preload_dashboard_data(self, time_ranges: List[int]) -> None:
        """Preload dashboard data for common time ranges"""
        logger.info(f"Preloading dashboard data for {len(time_ranges)} time ranges")
        
        for hours in time_ranges:
            try:
                # Generate cache keys for common dashboard queries
                end_time = datetime.now(timezone.utc)
                start_time = end_time - timedelta(hours=hours)
                
                # Preload analytics report
                report_key = self.cache_key(
                    'analytics_report',
                    start_date=start_time.isoformat(),
                    end_date=end_time.isoformat()
                )
                
                # Preload charts data
                charts_key = self.cache_key(
                    'dashboard_charts',
                    start_date=start_time.isoformat(),
                    end_date=end_time.isoformat()
                )
                
                # Preload metrics
                metrics_key = self.cache_key(
                    'performance_metrics',
                    hours=hours
                )
                
                logger.debug(f"Preloaded cache keys for {hours}h range: {report_key}, {charts_key}, {metrics_key}")
                
            except Exception as e:
                logger.error(f"Error preloading data for {hours}h range: {e}")
    
    def optimize_chart_data(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize chart data for better performance"""
        optimized = {}
        
        for chart_name, chart_config in chart_data.items():
            try:
                # Reduce data points for large datasets
                if 'data' in chart_config and 'datasets' in chart_config['data']:
                    for dataset in chart_config['data']['datasets']:
                        if 'data' in dataset and len(dataset['data']) > 100:
                            # Sample data points for large datasets
                            data = dataset['data']
                            if isinstance(data, list):
                                step = len(data) // 100
                                dataset['data'] = data[::max(step, 1)]
                
                # Compress metadata
                if 'metadata' in chart_config:
                    metadata = chart_config['metadata']
                    if isinstance(metadata, dict):
                        # Remove unnecessary metadata fields
                        essential_fields = ['chart_type', 'last_updated', 'data_points']
                        optimized_metadata = {
                            k: v for k, v in metadata.items()
                            if k in essential_fields
                        }
                        chart_config['metadata'] = optimized_metadata
                
                optimized[chart_name] = chart_config
                
            except Exception as e:
                logger.error(f"Error optimizing chart {chart_name}: {e}")
                optimized[chart_name] = chart_config
        
        return optimized
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance optimization statistics"""
        cache_stats = self.cache.get_stats()
        
        return {
            'cache': cache_stats,
            'optimization': {
                'query_cache_size': len(self.query_cache),
                'preload_enabled': True,
                'chart_optimization_enabled': True
            }
        }

class DashboardMetrics:
    """Dashboard performance metrics collection"""
    
    def __init__(self):
        self.metrics = {
            'request_times': {},
            'cache_performance': {},
            'error_counts': {},
            'active_connections': 0,
            'data_throughput': 0
        }
        self._lock = threading.Lock()
    
    def record_request_time(self, endpoint: str, duration_ms: float) -> None:
        """Record request processing time"""
        with self._lock:
            if endpoint not in self.metrics['request_times']:
                self.metrics['request_times'][endpoint] = []
            
            self.metrics['request_times'][endpoint].append({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'duration_ms': duration_ms
            })
            
            # Keep only last 1000 requests per endpoint
            if len(self.metrics['request_times'][endpoint]) > 1000:
                self.metrics['request_times'][endpoint] = self.metrics['request_times'][endpoint][-1000:]
    
    def record_cache_performance(self, cache_stats: Dict[str, Any]) -> None:
        """Record cache performance metrics"""
        with self._lock:
            self.metrics['cache_performance'] = cache_stats
    
    def record_error(self, error_type: str) -> None:
        """Record error occurrence"""
        with self._lock:
            if error_type not in self.metrics['error_counts']:
                self.metrics['error_counts'][error_type] = 0
            self.metrics['error_counts'][error_type] += 1
    
    def update_connections(self, count: int) -> None:
        """Update active connections count"""
        with self._lock:
            self.metrics['active_connections'] = count
    
    def update_throughput(self, bytes_transferred: int) -> None:
        """Update data throughput"""
        with self._lock:
            self.metrics['data_throughput'] += bytes_transferred
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        with self._lock:
            # Calculate average request times
            avg_request_times = {}
            for endpoint, times in self.metrics['request_times'].items():
                if times:
                    avg_time = sum(t['duration_ms'] for t in times) / len(times)
                    avg_request_times[endpoint] = round(avg_time, 2)
            
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'average_request_times': avg_request_times,
                'cache_performance': self.metrics['cache_performance'],
                'error_counts': self.metrics['error_counts'],
                'active_connections': self.metrics['active_connections'],
                'data_throughput_bytes': self.metrics['data_throughput']
            }

# Global instances
_dashboard_cache = None
_dashboard_optimizer = None
_dashboard_metrics = None

def get_dashboard_cache() -> DashboardCache:
    """Get global dashboard cache instance"""
    global _dashboard_cache
    if _dashboard_cache is None:
        _dashboard_cache = DashboardCache(max_size=1000, default_ttl=300)
    return _dashboard_cache

def get_dashboard_optimizer() -> DashboardOptimizer:
    """Get global dashboard optimizer instance"""
    global _dashboard_optimizer
    if _dashboard_optimizer is None:
        cache = get_dashboard_cache()
        _dashboard_optimizer = DashboardOptimizer(cache)
    return _dashboard_optimizer

def get_dashboard_metrics() -> DashboardMetrics:
    """Get global dashboard metrics instance"""
    global _dashboard_metrics
    if _dashboard_metrics is None:
        _dashboard_metrics = DashboardMetrics()
    return _dashboard_metrics

def performance_monitor(endpoint_name: str = None):
    """Decorator for monitoring endpoint performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                # Record error
                metrics = get_dashboard_metrics()
                error_type = f"{endpoint_name or func.__name__}_error"
                metrics.record_error(error_type)
                raise
            finally:
                # Record performance
                duration_ms = (time.time() - start_time) * 1000
                metrics = get_dashboard_metrics()
                metrics.record_request_time(endpoint_name or func.__name__, duration_ms)
        
        return wrapper
    return decorator

# Export
__all__ = [
    'DashboardCache', 'DashboardOptimizer', 'DashboardMetrics',
    'get_dashboard_cache', 'get_dashboard_optimizer', 'get_dashboard_metrics',
    'performance_monitor'
]
