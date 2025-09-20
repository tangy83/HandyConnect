"""
Data Analytics Foundation - JSON Schema Definitions
Author: Sunayana
Phase 9: Data Analytics Foundation

This module defines the JSON schemas for analytics data structures,
validation, and data persistence for the HandyConnect system.
"""

import json
import jsonschema
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import uuid

# ==================== CORE DATA SCHEMAS ====================

# Task Analytics Schema
TASK_ANALYTICS_SCHEMA = {
    "type": "object",
    "properties": {
        "task_id": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"},
        "status": {"type": "string", "enum": ["New", "In Progress", "Completed", "On Hold"]},
        "priority": {"type": "string", "enum": ["Low", "Medium", "High", "Urgent"]},
        "category": {"type": "string"},
        "sender_email": {"type": "string", "format": "email"},
        "response_time_minutes": {"type": "number", "minimum": 0},
        "resolution_time_minutes": {"type": "number", "minimum": 0},
        "escalation_count": {"type": "integer", "minimum": 0},
        "satisfaction_score": {"type": ["number", "null"], "minimum": 1, "maximum": 5},
        "tags": {"type": "array", "items": {"type": "string"}},
        "metadata": {"type": "object"}
    },
    "required": ["task_id", "created_at", "status", "priority", "category", "sender_email"]
}

# Thread Analytics Schema
THREAD_ANALYTICS_SCHEMA = {
    "type": "object",
    "properties": {
        "thread_id": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"},
        "status": {"type": "string", "enum": ["Active", "Pending", "Resolved", "Closed"]},
        "priority": {"type": "string", "enum": ["Low", "Medium", "High", "Urgent"]},
        "message_count": {"type": "integer", "minimum": 0},
        "participant_count": {"type": "integer", "minimum": 0},
        "first_response_time_minutes": {"type": "number", "minimum": 0},
        "resolution_time_minutes": {"type": "number", "minimum": 0},
        "avg_response_time_minutes": {"type": "number", "minimum": 0},
        "escalation_count": {"type": "integer", "minimum": 0},
        "satisfaction_score": {"type": ["number", "null"], "minimum": 1, "maximum": 5},
        "tags": {"type": "array", "items": {"type": "string"}},
        "metadata": {"type": "object"}
    },
    "required": ["thread_id", "created_at", "status", "priority", "message_count", "participant_count"]
}

# Performance Metrics Schema
PERFORMANCE_METRICS_SCHEMA = {
    "type": "object",
    "properties": {
        "timestamp": {"type": "string", "format": "date-time"},
        "metric_type": {"type": "string", "enum": ["response_time", "resolution_time", "satisfaction", "volume", "escalation"]},
        "value": {"type": "number"},
        "unit": {"type": "string"},
        "category": {"type": "string"},
        "priority": {"type": "string", "enum": ["Low", "Medium", "High", "Urgent"]},
        "tags": {"type": "array", "items": {"type": "string"}},
        "metadata": {"type": "object"}
    },
    "required": ["timestamp", "metric_type", "value", "unit"]
}

# System Health Schema
SYSTEM_HEALTH_SCHEMA = {
    "type": "object",
    "properties": {
        "timestamp": {"type": "string", "format": "date-time"},
        "service_name": {"type": "string"},
        "status": {"type": "string", "enum": ["healthy", "degraded", "unhealthy"]},
        "response_time_ms": {"type": "number", "minimum": 0},
        "error_rate": {"type": "number", "minimum": 0, "maximum": 1},
        "cpu_usage": {"type": "number", "minimum": 0, "maximum": 100},
        "memory_usage": {"type": "number", "minimum": 0, "maximum": 100},
        "disk_usage": {"type": "number", "minimum": 0, "maximum": 100},
        "active_connections": {"type": "integer", "minimum": 0},
        "metadata": {"type": "object"}
    },
    "required": ["timestamp", "service_name", "status"]
}

# User Behavior Schema
USER_BEHAVIOR_SCHEMA = {
    "type": "object",
    "properties": {
        "user_id": {"type": "string"},
        "session_id": {"type": "string"},
        "timestamp": {"type": "string", "format": "date-time"},
        "action": {"type": "string"},
        "page": {"type": "string"},
        "duration_seconds": {"type": "number", "minimum": 0},
        "user_agent": {"type": "string"},
        "ip_address": {"type": "string"},
        "metadata": {"type": "object"}
    },
    "required": ["user_id", "session_id", "timestamp", "action", "page"]
}

# ==================== DATA CLASSES ====================

@dataclass
class TaskAnalytics:
    """Task analytics data structure"""
    task_id: str
    created_at: str
    updated_at: str
    status: str
    priority: str
    category: str
    sender_email: str
    response_time_minutes: float = 0.0
    resolution_time_minutes: float = 0.0
    escalation_count: int = 0
    satisfaction_score: Optional[float] = None
    tags: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskAnalytics':
        # Handle both 'id' and 'task_id' field names for compatibility
        if 'id' in data and 'task_id' not in data:
            data = data.copy()
            data['task_id'] = data.pop('id')
        return cls(**data)

    def validate(self) -> bool:
        """Validate the task analytics data against schema"""
        try:
            jsonschema.validate(self.to_dict(), TASK_ANALYTICS_SCHEMA)
            return True
        except jsonschema.ValidationError:
            return False

@dataclass
class ThreadAnalytics:
    """Thread analytics data structure"""
    thread_id: str
    created_at: str
    updated_at: str
    status: str
    priority: str
    message_count: int
    participant_count: int
    first_response_time_minutes: float = 0.0
    resolution_time_minutes: float = 0.0
    avg_response_time_minutes: float = 0.0
    escalation_count: int = 0
    satisfaction_score: Optional[float] = None
    tags: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThreadAnalytics':
        # Handle both 'id' and 'thread_id' field names for compatibility
        if 'id' in data and 'thread_id' not in data:
            data = data.copy()
            data['thread_id'] = data.pop('id')
        return cls(**data)

    def validate(self) -> bool:
        """Validate the thread analytics data against schema"""
        try:
            jsonschema.validate(self.to_dict(), THREAD_ANALYTICS_SCHEMA)
            return True
        except jsonschema.ValidationError:
            return False

@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    timestamp: str
    metric_type: str
    value: float
    unit: str
    category: str = ""
    priority: str = ""
    tags: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PerformanceMetric':
        return cls(**data)

    def validate(self) -> bool:
        """Validate the performance metric data against schema"""
        try:
            jsonschema.validate(self.to_dict(), PERFORMANCE_METRICS_SCHEMA)
            return True
        except jsonschema.ValidationError:
            return False

@dataclass
class SystemHealth:
    """System health data structure"""
    timestamp: str
    service_name: str
    status: str
    response_time_ms: float = 0.0
    error_rate: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    active_connections: int = 0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemHealth':
        return cls(**data)

    def validate(self) -> bool:
        """Validate the system health data against schema"""
        try:
            jsonschema.validate(self.to_dict(), SYSTEM_HEALTH_SCHEMA)
            return True
        except jsonschema.ValidationError:
            return False

@dataclass
class UserBehavior:
    """User behavior data structure"""
    user_id: str
    session_id: str
    timestamp: str
    action: str
    page: str
    duration_seconds: float = 0.0
    user_agent: str = ""
    ip_address: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserBehavior':
        return cls(**data)

    def validate(self) -> bool:
        """Validate the user behavior data against schema"""
        try:
            jsonschema.validate(self.to_dict(), USER_BEHAVIOR_SCHEMA)
            return True
        except jsonschema.ValidationError:
            return False

# ==================== VALIDATION UTILITIES ====================

class DataValidator:
    """Data validation utility class"""
    
    SCHEMAS = {
        'task_analytics': TASK_ANALYTICS_SCHEMA,
        'thread_analytics': THREAD_ANALYTICS_SCHEMA,
        'performance_metrics': PERFORMANCE_METRICS_SCHEMA,
        'system_health': SYSTEM_HEALTH_SCHEMA,
        'user_behavior': USER_BEHAVIOR_SCHEMA
    }

    @classmethod
    def validate_data(cls, data: Dict[str, Any], schema_type: str) -> tuple[bool, Optional[str]]:
        """
        Validate data against a specific schema
        
        Args:
            data: Data to validate
            schema_type: Type of schema to validate against
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if schema_type not in cls.SCHEMAS:
            return False, f"Unknown schema type: {schema_type}"
        
        try:
            jsonschema.validate(data, cls.SCHEMAS[schema_type])
            return True, None
        except jsonschema.ValidationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    @classmethod
    def validate_batch(cls, data_list: List[Dict[str, Any]], schema_type: str) -> tuple[List[bool], List[Optional[str]]]:
        """
        Validate a batch of data against a specific schema
        
        Args:
            data_list: List of data to validate
            schema_type: Type of schema to validate against
            
        Returns:
            Tuple of (validation_results, error_messages)
        """
        results = []
        errors = []
        
        for data in data_list:
            is_valid, error = cls.validate_data(data, schema_type)
            results.append(is_valid)
            errors.append(error)
        
        return results, errors

# ==================== UTILITY FUNCTIONS ====================

def generate_analytics_id() -> str:
    """Generate a unique analytics ID"""
    return str(uuid.uuid4())

def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now(timezone.utc).isoformat()

def create_task_analytics_from_task(task_data: Dict[str, Any]) -> TaskAnalytics:
    """Create TaskAnalytics from task data"""
    # Handle both 'id' and 'task_id' field names for compatibility
    task_id = task_data.get('task_id') or task_data.get('id', generate_analytics_id())
    return TaskAnalytics(
        task_id=task_id,
        created_at=task_data.get('created_at', get_current_timestamp()),
        updated_at=task_data.get('updated_at', get_current_timestamp()),
        status=task_data.get('status', 'New'),
        priority=task_data.get('priority', 'Medium'),
        category=task_data.get('category', 'General Inquiry'),
        sender_email=task_data.get('sender_email', ''),
        tags=task_data.get('tags', []),
        metadata=task_data.get('metadata', {})
    )

def create_performance_metric(metric_type: str, value: float, unit: str, 
                            category: str = "", priority: str = "", metadata: dict = None) -> PerformanceMetric:
    """Create a performance metric"""
    if metadata is None:
        metadata = {}
    return PerformanceMetric(
        timestamp=get_current_timestamp(),
        metric_type=metric_type,
        value=value,
        unit=unit,
        category=category,
        priority=priority,
        metadata=metadata
    )

def create_system_health(service_name: str, status: str, **kwargs) -> SystemHealth:
    """Create system health data"""
    return SystemHealth(
        timestamp=get_current_timestamp(),
        service_name=service_name,
        status=status,
        **kwargs
    )

# ==================== EXPORT SCHEMAS ====================

def export_schemas() -> Dict[str, Dict[str, Any]]:
    """Export all schemas for external use"""
    return {
        'task_analytics': TASK_ANALYTICS_SCHEMA,
        'thread_analytics': THREAD_ANALYTICS_SCHEMA,
        'performance_metrics': PERFORMANCE_METRICS_SCHEMA,
        'system_health': SYSTEM_HEALTH_SCHEMA,
        'user_behavior': USER_BEHAVIOR_SCHEMA
    }

def export_data_classes() -> Dict[str, type]:
    """Export all data classes for external use"""
    return {
        'TaskAnalytics': TaskAnalytics,
        'ThreadAnalytics': ThreadAnalytics,
        'PerformanceMetric': PerformanceMetric,
        'SystemHealth': SystemHealth,
        'UserBehavior': UserBehavior
    }
