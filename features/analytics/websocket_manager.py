"""
WebSocket Manager for Real-time Dashboard
Author: Sunayana
Phase 10: Reporting Dashboard

This module provides WebSocket management for real-time dashboard updates.
"""

import logging
import json
import threading
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Set
import uuid

try:
    from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Flask-SocketIO not available. WebSocket functionality will be disabled.")

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections and real-time communication"""
    
    def __init__(self, app=None):
        self.app = app
        self.socketio = None
        self.connected_clients: Dict[str, Dict] = {}
        self.rooms: Dict[str, Set[str]] = {}
        self.running = False
        self._lock = threading.Lock()
        
        if app and WEBSOCKET_AVAILABLE:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize WebSocket with Flask app"""
        if not WEBSOCKET_AVAILABLE:
            logger.warning("WebSocket support not available - Flask-SocketIO not installed")
            return
        
        try:
            # Configure SocketIO
            self.socketio = SocketIO(
                app, 
                cors_allowed_origins="*",
                logger=True,
                engineio_logger=True,
                async_mode='threading'
            )
            
            # Register event handlers
            self._register_handlers()
            
            logger.info("WebSocket manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize WebSocket manager: {e}")
            self.socketio = None
    
    def _register_handlers(self):
        """Register WebSocket event handlers"""
        if not self.socketio:
            return
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            client_id = str(uuid.uuid4())
            
            with self._lock:
                self.connected_clients[client_id] = {
                    'connected_at': datetime.now(timezone.utc),
                    'rooms': set(),
                    'last_ping': datetime.now(timezone.utc)
                }
            
            emit('connected', {
                'client_id': client_id,
                'status': 'connected',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'features': ['realtime_updates', 'notifications', 'metrics']
            })
            
            logger.info(f"Client {client_id} connected via WebSocket")
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            # Find client by session (this is a simplified approach)
            # In production, you'd want to store client_id in session
            with self._lock:
                for client_id, client_data in list(self.connected_clients.items()):
                    # Remove from all rooms
                    for room in client_data['rooms']:
                        self._remove_from_room(client_id, room)
                    # Remove client
                    del self.connected_clients[client_id]
            
            logger.info("Client disconnected via WebSocket")
        
        @self.socketio.on('join_room')
        def handle_join_room(data):
            """Handle client joining a room"""
            room = data.get('room', 'dashboard')
            client_id = data.get('client_id')
            
            if not client_id:
                emit('error', {'message': 'client_id required'})
                return
            
            success = self._add_to_room(client_id, room)
            
            if success:
                join_room(room)
                emit('joined_room', {
                    'room': room,
                    'status': 'joined',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                logger.info(f"Client {client_id} joined room: {room}")
            else:
                emit('error', {'message': 'Failed to join room'})
        
        @self.socketio.on('leave_room')
        def handle_leave_room(data):
            """Handle client leaving a room"""
            room = data.get('room', 'dashboard')
            client_id = data.get('client_id')
            
            if not client_id:
                emit('error', {'message': 'client_id required'})
                return
            
            success = self._remove_from_room(client_id, room)
            
            if success:
                leave_room(room)
                emit('left_room', {
                    'room': room,
                    'status': 'left',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                logger.info(f"Client {client_id} left room: {room}")
        
        @self.socketio.on('request_metrics')
        def handle_request_metrics(data=None):
            """Handle request for current metrics"""
            try:
                from .performance_metrics import get_performance_monitor
                
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
        
        @self.socketio.on('ping')
        def handle_ping(data=None):
            """Handle ping from client"""
            client_id = data.get('client_id') if data else None
            
            if client_id:
                with self._lock:
                    if client_id in self.connected_clients:
                        self.connected_clients[client_id]['last_ping'] = datetime.now(timezone.utc)
            
            emit('pong', {
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        
        @self.socketio.on('subscribe_to_metrics')
        def handle_subscribe_to_metrics(data):
            """Handle subscription to metrics updates"""
            client_id = data.get('client_id')
            metric_types = data.get('metric_types', ['all'])
            
            if not client_id:
                emit('error', {'message': 'client_id required'})
                return
            
            # Add to metrics room
            self._add_to_room(client_id, 'metrics')
            
            emit('subscribed_to_metrics', {
                'metric_types': metric_types,
                'status': 'subscribed',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            logger.info(f"Client {client_id} subscribed to metrics: {metric_types}")
        
        @self.socketio.on('subscribe_to_alerts')
        def handle_subscribe_to_alerts(data):
            """Handle subscription to alerts"""
            client_id = data.get('client_id')
            alert_types = data.get('alert_types', ['all'])
            
            if not client_id:
                emit('error', {'message': 'client_id required'})
                return
            
            # Add to alerts room
            self._add_to_room(client_id, 'alerts')
            
            emit('subscribed_to_alerts', {
                'alert_types': alert_types,
                'status': 'subscribed',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            logger.info(f"Client {client_id} subscribed to alerts: {alert_types}")
    
    def _add_to_room(self, client_id: str, room: str) -> bool:
        """Add client to a room"""
        try:
            with self._lock:
                if client_id not in self.connected_clients:
                    return False
                
                if room not in self.rooms:
                    self.rooms[room] = set()
                
                self.rooms[room].add(client_id)
                self.connected_clients[client_id]['rooms'].add(room)
                
                return True
        except Exception as e:
            logger.error(f"Error adding client to room: {e}")
            return False
    
    def _remove_from_room(self, client_id: str, room: str) -> bool:
        """Remove client from a room"""
        try:
            with self._lock:
                if room in self.rooms:
                    self.rooms[room].discard(client_id)
                
                if client_id in self.connected_clients:
                    self.connected_clients[client_id]['rooms'].discard(room)
                
                return True
        except Exception as e:
            logger.error(f"Error removing client from room: {e}")
            return False
    
    def broadcast_to_room(self, room: str, event: str, data: Dict[str, Any]):
        """Broadcast data to all clients in a room"""
        if not self.socketio:
            logger.warning("WebSocket not available for broadcasting")
            return
        
        try:
            self.socketio.emit(event, data, room=room)
            logger.debug(f"Broadcasted {event} to room {room}: {len(data)} bytes")
        except Exception as e:
            logger.error(f"Error broadcasting to room {room}: {e}")
    
    def broadcast_to_all(self, event: str, data: Dict[str, Any]):
        """Broadcast data to all connected clients"""
        if not self.socketio:
            logger.warning("WebSocket not available for broadcasting")
            return
        
        try:
            self.socketio.emit(event, data)
            logger.debug(f"Broadcasted {event} to all clients: {len(data)} bytes")
        except Exception as e:
            logger.error(f"Error broadcasting to all clients: {e}")
    
    def send_to_client(self, client_id: str, event: str, data: Dict[str, Any]):
        """Send data to a specific client"""
        if not self.socketio:
            logger.warning("WebSocket not available for sending")
            return
        
        try:
            self.socketio.emit(event, data, room=client_id)
            logger.debug(f"Sent {event} to client {client_id}: {len(data)} bytes")
        except Exception as e:
            logger.error(f"Error sending to client {client_id}: {e}")
    
    def get_connected_clients_count(self) -> int:
        """Get number of connected clients"""
        with self._lock:
            return len(self.connected_clients)
    
    def get_room_clients_count(self, room: str) -> int:
        """Get number of clients in a room"""
        with self._lock:
            return len(self.rooms.get(room, set()))
    
    def get_client_info(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific client"""
        with self._lock:
            if client_id in self.connected_clients:
                client_data = self.connected_clients[client_id].copy()
                client_data['connected_at'] = client_data['connected_at'].isoformat()
                client_data['last_ping'] = client_data['last_ping'].isoformat()
                client_data['rooms'] = list(client_data['rooms'])
                return client_data
            return None
    
    def cleanup_stale_connections(self, timeout_minutes: int = 30):
        """Clean up stale connections"""
        if not self.socketio:
            return
        
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=timeout_minutes)
            stale_clients = []
            
            with self._lock:
                for client_id, client_data in self.connected_clients.items():
                    if client_data['last_ping'] < cutoff_time:
                        stale_clients.append(client_id)
            
            for client_id in stale_clients:
                logger.info(f"Cleaning up stale connection: {client_id}")
                # Remove from all rooms
                if client_id in self.connected_clients:
                    for room in self.connected_clients[client_id]['rooms']:
                        self._remove_from_room(client_id, room)
                    del self.connected_clients[client_id]
                
                # Disconnect client
                self.socketio.emit('disconnect_reason', {
                    'reason': 'stale_connection',
                    'message': 'Connection timed out'
                }, room=client_id)
                
        except Exception as e:
            logger.error(f"Error cleaning up stale connections: {e}")
    
    def start_cleanup_task(self, interval_minutes: int = 10):
        """Start periodic cleanup task"""
        def cleanup_worker():
            while True:
                try:
                    self.cleanup_stale_connections()
                    time.sleep(interval_minutes * 60)
                except Exception as e:
                    logger.error(f"Error in cleanup worker: {e}")
                    time.sleep(60)  # Wait 1 minute on error
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        logger.info("WebSocket cleanup task started")

# Global WebSocket manager instance
_websocket_manager = None

def get_websocket_manager(app=None) -> WebSocketManager:
    """Get global WebSocket manager instance"""
    global _websocket_manager
    if _websocket_manager is None:
        _websocket_manager = WebSocketManager(app)
    return _websocket_manager

def initialize_websocket_support(app):
    """Initialize WebSocket support for the Flask app"""
    if not WEBSOCKET_AVAILABLE:
        logger.warning("WebSocket support not available - Flask-SocketIO not installed")
        return None
    
    try:
        manager = get_websocket_manager(app)
        manager.start_cleanup_task()
        logger.info("WebSocket support initialized successfully")
        return manager.socketio
    except Exception as e:
        logger.error(f"Failed to initialize WebSocket support: {e}")
        return None

# Export
__all__ = ['WebSocketManager', 'get_websocket_manager', 'initialize_websocket_support', 'WEBSOCKET_AVAILABLE']
