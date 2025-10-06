"""
Case Models for HandyConnect
Data models for case management functionality
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from enum import Enum
from .base_models import BaseModel, TimestampMixin, UserMixin


class CaseStatus(Enum):
    """Case status enumeration"""
    NEW = "New"
    IN_PROGRESS = "In Progress"
    AWAITING_CUSTOMER = "Awaiting Customer"
    AWAITING_VENDOR = "Awaiting Vendor"
    AWAITING_APPROVAL = "Awaiting Approval"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    ESCALATED = "Escalated"


class CaseType(Enum):
    """Case type enumeration"""
    COMPLAINT = "Complaint"
    REQUEST = "Request"
    QUERY = "Query"
    FEEDBACK = "Feedback"
    SUGGESTION = "Suggestion"
    MAINTENANCE = "Maintenance"
    BILLING = "Billing"
    SECURITY = "Security"
    GENERAL = "General"


class CasePriority(Enum):
    """Case priority enumeration"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"
    CRITICAL = "Critical"


class SLAPriority(Enum):
    """SLA priority levels with time limits (in hours)"""
    CRITICAL = 2
    URGENT = 4
    HIGH = 8
    MEDIUM = 24
    LOW = 72


class CustomerType(Enum):
    """Customer type enumeration"""
    TENANT = "tenant"
    OWNER = "owner"
    CONTRACTOR = "contractor"
    VISITOR = "visitor"
    VENDOR = "vendor"


@dataclass
class CustomerInfo:
    """Customer information structure"""
    name: str
    email: str
    phone: Optional[str] = None
    property_id: Optional[str] = None
    property_address: Optional[str] = None
    property_number: Optional[str] = None
    block_number: Optional[str] = None
    customer_type: CustomerType = CustomerType.TENANT
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'property_id': self.property_id,
            'property_address': self.property_address,
            'property_number': self.property_number,
            'block_number': self.block_number,
            'customer_type': self.customer_type.value if hasattr(self.customer_type, 'value') else str(self.customer_type)
        }


@dataclass
class TimelineEvent:
    """Timeline event structure"""
    event_id: str
    event_type: str
    timestamp: datetime
    actor: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat(),
            'actor': self.actor,
            'description': self.description,
            'metadata': self.metadata
        }


@dataclass
class CaseMetadata:
    """Case metadata structure"""
    source: str = "email"
    channel: str = "outlook"
    first_contact_date: datetime = field(default_factory=datetime.utcnow)
    last_activity_date: datetime = field(default_factory=datetime.utcnow)
    escalation_count: int = 0
    satisfaction_score: Optional[float] = None
    resolution_time_minutes: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'source': self.source,
            'channel': self.channel,
            'first_contact_date': self.first_contact_date.isoformat(),
            'last_activity_date': self.last_activity_date.isoformat(),
            'escalation_count': self.escalation_count,
            'satisfaction_score': self.satisfaction_score,
            'resolution_time_minutes': self.resolution_time_minutes,
            'tags': self.tags
        }


@dataclass
class Case:
    """Main Case data model"""
    case_id: str
    case_number: str
    case_title: str
    case_type: CaseType
    status: CaseStatus
    priority: CasePriority
    sentiment: str
    sla_due_date: Optional[datetime] = None
    sla_status: str = "On Time"
    assigned_to: Optional[str] = None
    assigned_team: str = "support"
    customer_info: Optional[CustomerInfo] = None
    case_metadata: Optional[CaseMetadata] = None
    threads: List[str] = field(default_factory=list)  # thread_ids
    tasks: List[int] = field(default_factory=list)    # task_ids
    timeline: List[TimelineEvent] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization setup"""
        if self.customer_info is None:
            self.customer_info = CustomerInfo(name="Unknown", email="unknown@example.com")
        
        if self.case_metadata is None:
            self.case_metadata = CaseMetadata()
        
        if not self.sla_due_date:
            self.sla_due_date = self._calculate_sla_due_date()
    
    def _calculate_sla_due_date(self) -> datetime:
        """Calculate SLA due date based on priority"""
        try:
            sla_hours = SLAPriority[self.priority.value.upper()].value
        except (KeyError, AttributeError):
            sla_hours = SLAPriority.MEDIUM.value
        
        return datetime.utcnow() + timedelta(hours=sla_hours)
    
    def add_timeline_event(self, event_type: str, actor: str, description: str, metadata: Dict[str, Any] = None):
        """Add event to case timeline"""
        import uuid
        
        event = TimelineEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=datetime.utcnow(),
            actor=actor,
            description=description,
            metadata=metadata or {}
        )
        
        self.timeline.append(event)
        if self.case_metadata:
            self.case_metadata.last_activity_date = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def update_status(self, new_status: CaseStatus, actor: str = "system"):
        """Update case status"""
        old_status = self.status
        self.status = new_status
        self.add_timeline_event(
            event_type="status_changed",
            actor=actor,
            description=f"Status changed from {old_status.value} to {new_status.value}",
            metadata={"old_status": old_status.value, "new_status": new_status.value}
        )
    
    def assign_case(self, assignee: str, actor: str = "system"):
        """Assign case to agent"""
        old_assignee = self.assigned_to
        self.assigned_to = assignee
        self.add_timeline_event(
            event_type="assigned",
            actor=actor,
            description=f"Case assigned to {assignee}",
            metadata={"old_assignee": old_assignee, "new_assignee": assignee}
        )
    
    def add_task(self, task_id: int):
        """Add task to case"""
        if task_id not in self.tasks:
            self.tasks.append(task_id)
            self.add_timeline_event(
                event_type="task_added",
                actor="system",
                description=f"Task {task_id} added to case",
                metadata={"task_id": task_id}
            )
    
    def add_thread(self, thread_id: str):
        """Add thread to case"""
        if thread_id not in self.threads:
            self.threads.append(thread_id)
            self.add_timeline_event(
                event_type="thread_added",
                actor="system",
                description=f"Thread {thread_id} added to case",
                metadata={"thread_id": thread_id}
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert case to dictionary"""
        return {
            'case_id': self.case_id,
            'case_number': self.case_number,
            'case_title': self.case_title,
            'case_type': self.case_type.value if hasattr(self.case_type, 'value') else str(self.case_type),
            'status': self.status.value if hasattr(self.status, 'value') else str(self.status),
            'priority': self.priority.value if hasattr(self.priority, 'value') else str(self.priority),
            'sentiment': self.sentiment,
            'sla_due_date': self.sla_due_date.isoformat() if self.sla_due_date else None,
            'sla_status': self.sla_status,
            'assigned_to': self.assigned_to,
            'assigned_team': self.assigned_team,
            'customer_info': self.customer_info.to_dict() if self.customer_info else {},
            'case_metadata': self.case_metadata.to_dict() if self.case_metadata else {},
            'threads': self.threads,
            'tasks': self.tasks,
            'timeline': [event.to_dict() for event in self.timeline],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by,
            'updated_by': self.updated_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Case':
        """Create case from dictionary"""
        # Parse enums
        case_type = CaseType(data.get('case_type', 'GENERAL'))
        status = CaseStatus(data.get('status', 'NEW'))
        priority = CasePriority(data.get('priority', 'MEDIUM'))
        
        # Parse customer info
        customer_info_data = data.get('customer_info', {})
        customer_info = CustomerInfo(
            name=customer_info_data.get('name', 'Unknown'),
            email=customer_info_data.get('email', 'unknown@example.com'),
            phone=customer_info_data.get('phone'),
            property_id=customer_info_data.get('property_id'),
            property_address=customer_info_data.get('property_address'),
            customer_type=CustomerType(customer_info_data.get('customer_type', 'tenant'))
        )
        
        # Parse metadata
        metadata_data = data.get('case_metadata', {})
        case_metadata = CaseMetadata(
            source=metadata_data.get('source', 'email'),
            channel=metadata_data.get('channel', 'outlook'),
            first_contact_date=datetime.fromisoformat(metadata_data.get('first_contact_date', datetime.utcnow().isoformat())),
            last_activity_date=datetime.fromisoformat(metadata_data.get('last_activity_date', datetime.utcnow().isoformat())),
            escalation_count=metadata_data.get('escalation_count', 0),
            satisfaction_score=metadata_data.get('satisfaction_score'),
            resolution_time_minutes=metadata_data.get('resolution_time_minutes'),
            tags=metadata_data.get('tags', [])
        )
        
        # Parse timeline events
        timeline = []
        for event_data in data.get('timeline', []):
            timeline.append(TimelineEvent(
                event_id=event_data['event_id'],
                event_type=event_data['event_type'],
                timestamp=datetime.fromisoformat(event_data['timestamp']),
                actor=event_data['actor'],
                description=event_data['description'],
                metadata=event_data.get('metadata', {})
            ))
        
        # Parse dates
        created_at = datetime.fromisoformat(data.get('created_at', datetime.utcnow().isoformat()))
        updated_at = datetime.fromisoformat(data.get('updated_at', datetime.utcnow().isoformat()))
        sla_due_date = datetime.fromisoformat(data['sla_due_date']) if data.get('sla_due_date') else None
        
        return cls(
            case_id=data['case_id'],
            case_number=data['case_number'],
            case_title=data['case_title'],
            case_type=case_type,
            status=status,
            priority=priority,
            sentiment=data['sentiment'],
            sla_due_date=sla_due_date,
            sla_status=data.get('sla_status', 'On Time'),
            assigned_to=data.get('assigned_to'),
            assigned_team=data.get('assigned_team', 'support'),
            customer_info=customer_info,
            case_metadata=case_metadata,
            threads=data.get('threads', []),
            tasks=data.get('tasks', []),
            timeline=timeline,
            created_at=created_at,
            updated_at=updated_at,
            created_by=data.get('created_by'),
            updated_by=data.get('updated_by')
        )
