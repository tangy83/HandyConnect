"""
Task Structure & Metadata Schema Module
Defines and manages the structure, validation, and metadata for tasks.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid


class TaskStatus(Enum):
    """Task status enumeration"""
    NEW = "New"
    IN_PROGRESS = "In Progress"
    PENDING = "Pending"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    ON_HOLD = "On Hold"


class TaskPriority(Enum):
    """Task priority enumeration"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"
    CRITICAL = "Critical"


class TaskCategory(Enum):
    """Task category enumeration"""
    TECHNICAL = "Technical"
    BILLING = "Billing"
    GENERAL = "General"
    FEATURE_REQUEST = "Feature Request"
    BUG_REPORT = "Bug Report"
    ACCOUNT = "Account"
    SECURITY = "Security"
    PERFORMANCE = "Performance"


@dataclass
class TaskMetadata:
    """Task metadata structure"""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    version: int = 1
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    analytics_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskSchema:
    """Core task data structure with validation"""
    # Core identification
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    case_id: Optional[str] = None
    
    # Content fields
    subject: str = ""
    content: str = ""
    summary: Optional[str] = None
    
    # Status and classification
    status: TaskStatus = TaskStatus.NEW
    priority: TaskPriority = TaskPriority.MEDIUM
    category: TaskCategory = TaskCategory.GENERAL
    subcategory: Optional[str] = None
    
    # Assignment and ownership
    assigned_to: Optional[str] = None
    assigned_team: Optional[str] = None
    
    # Communication fields
    sender_email: Optional[str] = None
    sender_name: Optional[str] = None
    thread_id: Optional[str] = None
    conversation_id: Optional[str] = None
    
    # Temporal fields
    due_date: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    sla_deadline: Optional[datetime] = None
    
    # AI processing results
    sentiment: Optional[str] = None
    confidence_score: Optional[float] = None
    ai_summary: Optional[str] = None
    suggested_response: Optional[str] = None
    
    # Notes and comments
    notes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    metadata: TaskMetadata = field(default_factory=TaskMetadata)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for JSON serialization"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, Enum):
                result[key] = value.value
            elif isinstance(value, TaskMetadata):
                result[key] = {
                    'created_at': value.created_at.isoformat(),
                    'updated_at': value.updated_at.isoformat(),
                    'created_by': value.created_by,
                    'updated_by': value.updated_by,
                    'version': value.version,
                    'tags': value.tags,
                    'custom_fields': value.custom_fields,
                    'analytics_data': value.analytics_data
                }
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskSchema':
        """Create task from dictionary"""
        # Handle datetime fields
        if 'due_date' in data and data['due_date']:
            data['due_date'] = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        if 'resolved_at' in data and data['resolved_at']:
            data['resolved_at'] = datetime.fromisoformat(data['resolved_at'].replace('Z', '+00:00'))
        if 'sla_deadline' in data and data['sla_deadline']:
            data['sla_deadline'] = datetime.fromisoformat(data['sla_deadline'].replace('Z', '+00:00'))
        
        # Handle enum fields
        if 'status' in data:
            data['status'] = TaskStatus(data['status'])
        if 'priority' in data:
            data['priority'] = TaskPriority(data['priority'])
        if 'category' in data:
            data['category'] = TaskCategory(data['category'])
        
        # Handle metadata
        if 'metadata' in data and isinstance(data['metadata'], dict):
            metadata_data = data['metadata']
            if 'created_at' in metadata_data:
                metadata_data['created_at'] = datetime.fromisoformat(metadata_data['created_at'].replace('Z', '+00:00'))
            if 'updated_at' in metadata_data:
                metadata_data['updated_at'] = datetime.fromisoformat(metadata_data['updated_at'].replace('Z', '+00:00'))
            data['metadata'] = TaskMetadata(**metadata_data)
        
        return cls(**data)


class TaskValidator:
    """Validates task data against schema and business rules"""
    
    @staticmethod
    def validate_task(task: TaskSchema) -> Dict[str, List[str]]:
        """Validate task data and return validation errors"""
        errors = {}
        
        # Required field validation
        if not task.subject or len(task.subject.strip()) == 0:
            errors['subject'] = ['Subject is required and cannot be empty']
        
        if not task.content or len(task.content.strip()) == 0:
            errors['content'] = ['Content is required and cannot be empty']
        
        # Field length validation
        if len(task.subject) > 200:
            errors['subject'] = errors.get('subject', []) + ['Subject cannot exceed 200 characters']
        
        if len(task.content) > 10000:
            errors['content'] = errors.get('content', []) + ['Content cannot exceed 10000 characters']
        
        # Email validation
        if task.sender_email and not TaskValidator._is_valid_email(task.sender_email):
            errors['sender_email'] = ['Invalid email format']
        
        # Date validation
        if task.due_date and task.due_date < datetime.utcnow():
            errors['due_date'] = ['Due date cannot be in the past']
        
        if task.sla_deadline and task.due_date and task.sla_deadline < task.due_date:
            errors['sla_deadline'] = ['SLA deadline cannot be before due date']
        
        # Status transition validation
        if task.status == TaskStatus.COMPLETED and not task.resolved_at:
            errors['resolved_at'] = ['Resolved date is required for completed tasks']
        
        # Priority validation
        if task.priority == TaskPriority.CRITICAL and task.status == TaskStatus.NEW:
            errors['priority'] = ['Critical tasks should not remain in New status']
        
        return errors
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_bulk_tasks(tasks: List[TaskSchema]) -> Dict[str, Dict[str, List[str]]]:
        """Validate multiple tasks and return errors by task ID"""
        results = {}
        for task in tasks:
            errors = TaskValidator.validate_task(task)
            if errors:
                results[task.id] = errors
        return results


class SchemaMigrator:
    """Manages schema migrations and updates"""
    
    @staticmethod
    def migrate_task_data(task_data: Dict[str, Any], from_version: int, to_version: int) -> Dict[str, Any]:
        """Migrate task data between schema versions"""
        if from_version == to_version:
            return task_data
        
        # Version 1 to 2 migration
        if from_version == 1 and to_version == 2:
            task_data = SchemaMigrator._migrate_v1_to_v2(task_data)
        
        # Version 2 to 3 migration
        if from_version == 2 and to_version == 3:
            task_data = SchemaMigrator._migrate_v2_to_v3(task_data)
        
        return task_data
    
    @staticmethod
    def _migrate_v1_to_v2(task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 1 to version 2"""
        # Add metadata structure if missing
        if 'metadata' not in task_data:
            task_data['metadata'] = {
                'created_at': task_data.get('created_at', datetime.utcnow().isoformat()),
                'updated_at': task_data.get('updated_at', datetime.utcnow().isoformat()),
                'version': 2,
                'tags': [],
                'custom_fields': {},
                'analytics_data': {}
            }
        
        # Add analytics data structure
        if 'analytics_data' not in task_data['metadata']:
            task_data['metadata']['analytics_data'] = {}
        
        return task_data
    
    @staticmethod
    def _migrate_v2_to_v3(task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 2 to version 3"""
        # Add new fields for enhanced analytics
        if 'confidence_score' not in task_data:
            task_data['confidence_score'] = None
        
        if 'ai_summary' not in task_data:
            task_data['ai_summary'] = None
        
        # Update metadata version
        if 'metadata' in task_data:
            task_data['metadata']['version'] = 3
        
        return task_data


class MetadataExtractor:
    """Extracts and enriches task metadata"""
    
    @staticmethod
    def extract_analytics_metadata(task: TaskSchema) -> Dict[str, Any]:
        """Extract analytics metadata from task"""
        analytics = {
            'word_count': len(task.content.split()) if task.content else 0,
            'character_count': len(task.content) if task.content else 0,
            'has_attachments': False,  # Placeholder for future implementation
            'response_time_estimate': MetadataExtractor._estimate_response_time(task),
            'complexity_score': MetadataExtractor._calculate_complexity_score(task),
            'urgency_indicators': MetadataExtractor._detect_urgency_indicators(task),
            'category_confidence': MetadataExtractor._calculate_category_confidence(task)
        }
        
        return analytics
    
    @staticmethod
    def _estimate_response_time(task: TaskSchema) -> int:
        """Estimate response time in minutes based on task characteristics"""
        base_time = 30  # Base 30 minutes
        
        # Adjust based on priority
        priority_multipliers = {
            TaskPriority.LOW: 0.5,
            TaskPriority.MEDIUM: 1.0,
            TaskPriority.HIGH: 1.5,
            TaskPriority.URGENT: 2.0,
            TaskPriority.CRITICAL: 3.0
        }
        
        multiplier = priority_multipliers.get(task.priority, 1.0)
        return int(base_time * multiplier)
    
    @staticmethod
    def _calculate_complexity_score(task: TaskSchema) -> float:
        """Calculate complexity score (0-1) based on task characteristics"""
        score = 0.0
        
        # Content length factor
        if task.content:
            word_count = len(task.content.split())
            if word_count > 100:
                score += 0.3
            elif word_count > 50:
                score += 0.2
            else:
                score += 0.1
        
        # Category complexity
        complex_categories = [TaskCategory.TECHNICAL, TaskCategory.SECURITY, TaskCategory.PERFORMANCE]
        if task.category in complex_categories:
            score += 0.3
        
        # Priority factor
        if task.priority in [TaskPriority.HIGH, TaskPriority.URGENT, TaskPriority.CRITICAL]:
            score += 0.2
        
        return min(score, 1.0)
    
    @staticmethod
    def _detect_urgency_indicators(task: TaskSchema) -> List[str]:
        """Detect urgency indicators in task content"""
        urgency_keywords = [
            'urgent', 'asap', 'immediately', 'critical', 'emergency',
            'broken', 'down', 'not working', 'failed', 'error'
        ]
        
        indicators = []
        content_lower = task.content.lower() if task.content else ""
        subject_lower = task.subject.lower() if task.subject else ""
        
        for keyword in urgency_keywords:
            if keyword in content_lower or keyword in subject_lower:
                indicators.append(keyword)
        
        return indicators
    
    @staticmethod
    def _calculate_category_confidence(task: TaskSchema) -> float:
        """Calculate confidence score for category assignment"""
        # This would typically use ML models, for now return a placeholder
        return 0.85


# Export main classes
__all__ = [
    'TaskSchema', 'TaskMetadata', 'TaskValidator', 'SchemaMigrator', 'MetadataExtractor',
    'TaskStatus', 'TaskPriority', 'TaskCategory'
]






