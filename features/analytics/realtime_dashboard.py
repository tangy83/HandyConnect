"""
Real-time Dashboard Implementation
Author: Sunayana
Phase 10: Reporting Dashboard

This module provides real-time dashboard functionality including:
- Live data streaming
- WebSocket support
- Server-Sent Events (SSE)
- Real-time metrics broadcasting
- Live chart updates
"""

import logging
import json
import threading
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from collections import defaultdict
import queue
import uuid

from flask import Blueprint, request, jsonify, Response, current_app
from flask_socketio import SocketIO, emit, join_room, leave_room
import redis

from .analytics_framework import AnalyticsFramework, AnalyticsConfig
from .data_visualization import DataVisualization
from .performance_metrics import get_performance_monitor
from .data_persistence import AnalyticsDataPersistence
from .dashboard_cache import (
    get_dashboard_cache, get_dashboard_optimizer, get_dashboard_metrics,
    performance_monitor
)

logger = logging.getLogger(__name__)

# Real-time dashboard blueprint
realtime_bp = Blueprint('realtime_dashboard', __name__, url_prefix='/api/realtime')

@dataclass
class RealtimeMetric:
    """Real-time metric data structure"""
    id: str
    metric_type: str
    value: Any
    timestamp: datetime
    tags: Dict[str, str] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class DashboardUpdate:
    """Dashboard update message"""
    update_type: str
    data: Dict[str, Any]
    timestamp: datetime
    room: str = 'dashboard'
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class RealtimeBroadcaster:
    """Handles real-time data broadcasting to connected clients"""
    
    def __init__(self):
        self.connected_clients: Set[str] = set()
        self.rooms: Dict[str, Set[str]] = defaultdict(set)
        self.metric_queue = queue.Queue()
        self.update_queue = queue.Queue()
        self.running = False
        self.broadcast_thread = None
        self._lock = threading.Lock()
        
        # Initialize Redis if available
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            self.redis_available = True
            logger.info("Redis connection established for real-time broadcasting")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory broadcasting: {e}")
            self.redis_client = None
            self.redis_available = False
    
    def start(self):
        """Start the real-time broadcaster"""
        if self.running:
            return
        
        self.running = True
        self.broadcast_thread = threading.Thread(target=self._broadcast_worker, daemon=True)
        self.broadcast_thread.start()
        logger.info("Real-time broadcaster started")
    
    def stop(self):
        """Stop the real-time broadcaster"""
        self.running = False
        if self.broadcast_thread:
            self.broadcast_thread.join(timeout=5)
        logger.info("Real-time broadcaster stopped")
    
    def add_client(self, client_id: str, room: str = 'dashboard'):
        """Add a client to the broadcaster"""
        with self._lock:
            self.connected_clients.add(client_id)
            self.rooms[room].add(client_id)
            logger.debug(f"Client {client_id} added to room {room}")
    
    def remove_client(self, client_id: str, room: str = 'dashboard'):
        """Remove a client from the broadcaster"""
        with self._lock:
            self.connected_clients.discard(client_id)
            self.rooms[room].discard(client_id)
            logger.debug(f"Client {client_id} removed from room {room}")
    
    def broadcast_metric(self, metric: RealtimeMetric, room: str = 'dashboard'):
        """Broadcast a real-time metric"""
        update = DashboardUpdate(
            update_type='metric',
            data=metric.to_dict(),
            timestamp=datetime.now(timezone.utc),
            room=room
        )
        self._queue_update(update)
    
    def broadcast_dashboard_update(self, update_type: str, data: Dict[str, Any], room: str = 'dashboard'):
        """Broadcast a dashboard update"""
        update = DashboardUpdate(
            update_type=update_type,
            data=data,
            timestamp=datetime.now(timezone.utc),
            room=room
        )
        self._queue_update(update)
    
    def _queue_update(self, update: DashboardUpdate):
        """Queue an update for broadcasting"""
        try:
            self.update_queue.put_nowait(update)
        except queue.Full:
            logger.warning("Update queue is full, dropping update")
    
    def _broadcast_worker(self):
        """Background worker for broadcasting updates"""
        while self.running:
            try:
                # Process updates with timeout
                update = self.update_queue.get(timeout=1.0)
                self._process_update(update)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in broadcast worker: {e}")
    
    def _process_update(self, update: DashboardUpdate):
        """Process and broadcast an update"""
        try:
            # Broadcast to Redis if available
            if self.redis_available:
                self._broadcast_to_redis(update)
            
            # Broadcast to WebSocket clients
            self._broadcast_to_websocket(update)
            
        except Exception as e:
            logger.error(f"Error processing update: {e}")
    
    def _broadcast_to_redis(self, update: DashboardUpdate):
        """Broadcast update via Redis pub/sub"""
        try:
            channel = f"dashboard:{update.room}"
            message = json.dumps(update.to_dict())
            self.redis_client.publish(channel, message)
        except Exception as e:
            logger.error(f"Error broadcasting to Redis: {e}")
    
    def _broadcast_to_websocket(self, update: DashboardUpdate):
        """Broadcast update via WebSocket"""
        try:
            # This will be handled by SocketIO
            if hasattr(current_app, 'socketio'):
                current_app.socketio.emit('dashboard_update', update.to_dict(), room=update.room)
        except Exception as e:
            logger.error(f"Error broadcasting to WebSocket: {e}")

class RealtimeMetricsCollector:
    """Collects and processes real-time metrics"""
    
    def __init__(self, broadcaster: RealtimeBroadcaster):
        self.broadcaster = broadcaster
        self.running = False
        self.collection_thread = None
        self.last_metrics = {}
        
    def start(self):
        """Start real-time metrics collection"""
        if self.running:
            return
        
        self.running = True
        self.collection_thread = threading.Thread(target=self._collection_worker, daemon=True)
        self.collection_thread.start()
        logger.info("Real-time metrics collector started")
    
    def stop(self):
        """Stop real-time metrics collection"""
        self.running = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        logger.info("Real-time metrics collector stopped")
    
    def _collection_worker(self):
        """Background worker for collecting real-time metrics"""
        while self.running:
            try:
                self._collect_system_metrics()
                self._collect_analytics_metrics()
                self._collect_performance_metrics()
                time.sleep(5)  # Collect every 5 seconds
            except Exception as e:
                logger.error(f"Error in metrics collection worker: {e}")
                time.sleep(10)  # Wait longer on error
    
    def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            metric = RealtimeMetric(
                id=str(uuid.uuid4()),
                metric_type='system_cpu',
                value=cpu_percent,
                timestamp=datetime.now(timezone.utc),
                tags={'component': 'system'},
                metadata={'unit': 'percent', 'threshold': 80}
            )
            self.broadcaster.broadcast_metric(metric)
            
            # Memory usage
            memory = psutil.virtual_memory()
            metric = RealtimeMetric(
                id=str(uuid.uuid4()),
                metric_type='system_memory',
                value=memory.percent,
                timestamp=datetime.now(timezone.utc),
                tags={'component': 'system'},
                metadata={'unit': 'percent', 'available_gb': round(memory.available / (1024**3), 2)}
            )
            self.broadcaster.broadcast_metric(metric)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            metric = RealtimeMetric(
                id=str(uuid.uuid4()),
                metric_type='system_disk',
                value=disk.percent,
                timestamp=datetime.now(timezone.utc),
                tags={'component': 'system'},
                metadata={'unit': 'percent', 'free_gb': round(disk.free / (1024**3), 2)}
            )
            self.broadcaster.broadcast_metric(metric)
            
        except ImportError:
            logger.warning("psutil not available, skipping system metrics")
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def _collect_analytics_metrics(self):
        """Collect analytics metrics"""
        try:
            framework = get_analytics_framework()
            
            # Task count
            tasks = framework.persistence.load_task_analytics()
            task_count = len(tasks)
            
            # Check if task count changed
            if self.last_metrics.get('task_count') != task_count:
                metric = RealtimeMetric(
                    id=str(uuid.uuid4()),
                    metric_type='task_count',
                    value=task_count,
                    timestamp=datetime.now(timezone.utc),
                    tags={'component': 'analytics'},
                    metadata={'change': task_count - self.last_metrics.get('task_count', 0)}
                )
                self.broadcaster.broadcast_metric(metric)
                self.last_metrics['task_count'] = task_count
            
            # New tasks in last minute
            now = datetime.now(timezone.utc)
            one_minute_ago = now - timedelta(minutes=1)
            recent_tasks = [
                task for task in tasks 
                if task.metadata.created_at and task.metadata.created_at >= one_minute_ago
            ]
            
            if recent_tasks:
                metric = RealtimeMetric(
                    id=str(uuid.uuid4()),
                    metric_type='new_tasks_per_minute',
                    value=len(recent_tasks),
                    timestamp=datetime.now(timezone.utc),
                    tags={'component': 'analytics'},
                    metadata={'time_window': '1 minute'}
                )
                self.broadcaster.broadcast_metric(metric)
            
        except Exception as e:
            logger.error(f"Error collecting analytics metrics: {e}")
    
    def _collect_performance_metrics(self):
        """Collect performance metrics"""
        try:
            monitor = get_performance_monitor()
            current_metrics = monitor.get_current_metrics()
            
            # Response time
            if current_metrics.get('response_time_ms'):
                metric = RealtimeMetric(
                    id=str(uuid.uuid4()),
                    metric_type='response_time',
                    value=current_metrics['response_time_ms'],
                    timestamp=datetime.now(timezone.utc),
                    tags={'component': 'performance'},
                    metadata={'unit': 'milliseconds', 'threshold': 1000}
                )
                self.broadcaster.broadcast_metric(metric)
            
            # Error rate
            if current_metrics.get('error_rate'):
                metric = RealtimeMetric(
                    id=str(uuid.uuid4()),
                    metric_type='error_rate',
                    value=current_metrics['error_rate'],
                    timestamp=datetime.now(timezone.utc),
                    tags={'component': 'performance'},
                    metadata={'unit': 'percent', 'threshold': 5}
                )
                self.broadcaster.broadcast_metric(metric)
            
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")

# Global instances
_realtime_broadcaster = None
_realtime_collector = None
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
        persistence = get_data_persistence()
        _data_visualization = DataVisualization(persistence)
    return _data_visualization

def get_data_persistence() -> AnalyticsDataPersistence:
    """Get global data persistence instance"""
    global _data_persistence
    if _data_persistence is None:
        _data_persistence = AnalyticsDataPersistence()
    return _data_persistence

def get_realtime_broadcaster() -> RealtimeBroadcaster:
    """Get global real-time broadcaster instance"""
    global _realtime_broadcaster
    if _realtime_broadcaster is None:
        _realtime_broadcaster = RealtimeBroadcaster()
        _realtime_broadcaster.start()
    return _realtime_broadcaster

def get_realtime_collector() -> RealtimeMetricsCollector:
    """Get global real-time metrics collector instance"""
    global _realtime_collector
    if _realtime_collector is None:
        broadcaster = get_realtime_broadcaster()
        _realtime_collector = RealtimeMetricsCollector(broadcaster)
        _realtime_collector.start()
    return _realtime_collector

# ==================== API ENDPOINTS ====================

@realtime_bp.route('/dashboard/live', methods=['GET'])
@performance_monitor('live_dashboard')
def get_live_dashboard_data():
    """Get live dashboard data with real-time updates"""
    try:
        # Get cache and optimizer
        cache = get_dashboard_cache()
        optimizer = get_dashboard_optimizer()
        
        # Load recent data (last 24 hours)
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=24)
        
        # Generate cache key for this request
        cache_key = optimizer.cache_key(
            'live_dashboard',
            start_date=start_time.isoformat(),
            end_date=end_time.isoformat()
        )
        
        # Try to get from cache first
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.debug("Returning cached live dashboard data")
            return jsonify({
                'status': 'success',
                'message': 'Live dashboard data retrieved successfully (cached)',
                'data': cached_data
            })
        
        # Get current analytics data
        framework = get_analytics_framework()
        persistence = get_data_persistence()
        visualization = get_data_visualization()
        
        # Get analytics report
        report = framework.get_analytics_report(start_time, end_time)
        
        # Get current metrics
        monitor = get_performance_monitor()
        current_metrics = monitor.get_current_metrics()
        
        # Get charts data
        charts_data = visualization.generate_dashboard_charts(start_time, end_time)
        
        # Optimize chart data for performance
        optimized_charts = optimizer.optimize_chart_data(charts_data)
        
        # Combine all data
        live_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'report': report,
            'current_metrics': current_metrics,
            'charts': optimized_charts,
            'real_time_enabled': True,
            'cached': False
        }
        
        # Cache the result for 2 minutes
        cache.set(cache_key, live_data, ttl=120)
        
        return jsonify({
            'status': 'success',
            'message': 'Live dashboard data retrieved successfully',
            'data': live_data
        })
        
    except Exception as e:
        logger.error(f"Error getting live dashboard data: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get live dashboard data',
            'error': str(e)
        }), 500

@realtime_bp.route('/dashboard/stream', methods=['GET'])
def stream_dashboard_updates():
    """Server-Sent Events endpoint for real-time dashboard updates"""
    def generate_updates():
        """Generate SSE updates"""
        client_id = str(uuid.uuid4())
        broadcaster = get_realtime_broadcaster()
        
        try:
            # Add client to broadcaster
            broadcaster.add_client(client_id)
            
            # Send initial data
            initial_data = {
                'type': 'connection',
                'data': {
                    'client_id': client_id,
                    'status': 'connected',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            }
            yield f"data: {json.dumps(initial_data)}\n\n"
            
            # Send periodic updates
            while True:
                try:
                    # Get latest metrics
                    monitor = get_performance_monitor()
                    current_metrics = monitor.get_current_metrics()
                    
                    update_data = {
                        'type': 'metrics_update',
                        'data': {
                            'metrics': current_metrics,
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        }
                    }
                    yield f"data: {json.dumps(update_data)}\n\n"
                    
                    time.sleep(5)  # Update every 5 seconds
                    
                except Exception as e:
                    logger.error(f"Error in SSE stream: {e}")
                    break
                    
        finally:
            # Remove client from broadcaster
            broadcaster.remove_client(client_id)
    
    return Response(
        generate_updates(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control'
        }
    )

@realtime_bp.route('/metrics/live', methods=['GET'])
def get_live_metrics():
    """Get current live metrics"""
    try:
        monitor = get_performance_monitor()
        current_metrics = monitor.get_current_metrics()
        
        # Add system metrics if available
        try:
            import psutil
            system_metrics = {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            }
            current_metrics.update(system_metrics)
        except ImportError:
            pass
        
        return jsonify({
            'status': 'success',
            'message': 'Live metrics retrieved successfully',
            'data': {
                'metrics': current_metrics,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting live metrics: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get live metrics',
            'error': str(e)
        }), 500

@realtime_bp.route('/notifications', methods=['POST'])
def send_notification():
    """Send a real-time notification"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No notification data provided'
            }), 400
        
        notification_type = data.get('type', 'info')
        message = data.get('message', '')
        room = data.get('room', 'dashboard')
        
        # Create notification update
        broadcaster = get_realtime_broadcaster()
        broadcaster.broadcast_dashboard_update(
            update_type='notification',
            data={
                'type': notification_type,
                'message': message,
                'timestamp': datetime.now(timezone.utc).isoformat()
            },
            room=room
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Notification sent successfully'
        })
        
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to send notification',
            'error': str(e)
        }), 500

@realtime_bp.route('/alerts', methods=['GET'])
def get_active_alerts():
    """Get active system alerts"""
    try:
        monitor = get_performance_monitor()
        current_metrics = monitor.get_current_metrics()
        
        alerts = []
        
        # Check for performance alerts
        if current_metrics.get('response_time_ms', 0) > 1000:
            alerts.append({
                'type': 'warning',
                'message': 'High response time detected',
                'value': current_metrics['response_time_ms'],
                'threshold': 1000,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        
        if current_metrics.get('error_rate', 0) > 5:
            alerts.append({
                'type': 'error',
                'message': 'High error rate detected',
                'value': current_metrics['error_rate'],
                'threshold': 5,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        
        # Check system alerts
        try:
            import psutil
            cpu_percent = psutil.cpu_percent()
            if cpu_percent > 80:
                alerts.append({
                    'type': 'warning',
                    'message': 'High CPU usage',
                    'value': cpu_percent,
                    'threshold': 80,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 85:
                alerts.append({
                    'type': 'warning',
                    'message': 'High memory usage',
                    'value': memory_percent,
                    'threshold': 85,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
        except ImportError:
            pass
        
        return jsonify({
            'status': 'success',
            'message': 'Active alerts retrieved successfully',
            'data': {
                'alerts': alerts,
                'count': len(alerts),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting active alerts: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get active alerts',
            'error': str(e)
        }), 500

@realtime_bp.route('/performance/stats', methods=['GET'])
@performance_monitor('performance_stats')
def get_performance_stats():
    """Get dashboard performance statistics"""
    try:
        cache = get_dashboard_cache()
        optimizer = get_dashboard_optimizer()
        metrics = get_dashboard_metrics()
        
        # Get cache statistics
        cache_stats = cache.get_stats()
        
        # Get optimization statistics
        optimization_stats = optimizer.get_performance_stats()
        
        # Get performance metrics
        performance_metrics = metrics.get_metrics()
        
        # Update metrics with cache performance
        metrics.record_cache_performance(cache_stats)
        
        stats_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'cache': cache_stats,
            'optimization': optimization_stats,
            'performance': performance_metrics
        }
        
        return jsonify({
            'status': 'success',
            'message': 'Performance statistics retrieved successfully',
            'data': stats_data
        })
        
    except Exception as e:
        logger.error(f"Error getting performance stats: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get performance statistics',
            'error': str(e)
        }), 500

@realtime_bp.route('/cache/clear', methods=['POST'])
def clear_dashboard_cache():
    """Clear dashboard cache"""
    try:
        cache = get_dashboard_cache()
        cache.clear()
        
        return jsonify({
            'status': 'success',
            'message': 'Dashboard cache cleared successfully'
        })
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to clear dashboard cache',
            'error': str(e)
        }), 500

@realtime_bp.route('/cache/preload', methods=['POST'])
def preload_dashboard_cache():
    """Preload dashboard cache with common data"""
    try:
        optimizer = get_dashboard_optimizer()
        
        # Preload common time ranges
        time_ranges = [1, 6, 24, 72, 168]  # 1h, 6h, 1d, 3d, 1w
        optimizer.preload_dashboard_data(time_ranges)
        
        return jsonify({
            'status': 'success',
            'message': f'Dashboard cache preloaded for {len(time_ranges)} time ranges'
        })
        
    except Exception as e:
        logger.error(f"Error preloading cache: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to preload dashboard cache',
            'error': str(e)
        }), 500

# ==================== WEBSOCKET HANDLERS ====================

def initialize_websocket_handlers(socketio):
    """Initialize WebSocket event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        client_id = str(uuid.uuid4())
        broadcaster = get_realtime_broadcaster()
        broadcaster.add_client(client_id)
        
        emit('connected', {
            'client_id': client_id,
            'status': 'connected',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        logger.info(f"Client {client_id} connected via WebSocket")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        # Note: client_id would need to be stored in session
        logger.info("Client disconnected via WebSocket")
    
    @socketio.on('join_room')
    def handle_join_room(data):
        """Handle client joining a room"""
        room = data.get('room', 'dashboard')
        join_room(room)
        
        emit('joined_room', {
            'room': room,
            'status': 'joined',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        logger.info(f"Client joined room: {room}")
    
    @socketio.on('leave_room')
    def handle_leave_room(data):
        """Handle client leaving a room"""
        room = data.get('room', 'dashboard')
        leave_room(room)
        
        emit('left_room', {
            'room': room,
            'status': 'left',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        logger.info(f"Client left room: {room}")
    
    @socketio.on('request_metrics')
    def handle_request_metrics():
        """Handle request for current metrics"""
        try:
            monitor = get_performance_monitor()
            current_metrics = monitor.get_current_metrics()
            
            emit('metrics_response', {
                'metrics': current_metrics,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error handling metrics request: {e}")
            emit('error', {
                'message': 'Failed to get metrics',
                'error': str(e)
            })

# Export the blueprint
__all__ = ['realtime_bp', 'get_realtime_broadcaster', 'get_realtime_collector', 'initialize_websocket_handlers']
