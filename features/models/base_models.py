"""
Base Models for HandyConnect
Common base classes and mixins for data models
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from abc import ABC


@dataclass
class TimestampMixin:
    """Mixin for timestamp fields"""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UserMixin:
    """Mixin for user tracking fields"""
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


@dataclass
class BaseModel(ABC):
    """Base class for all data models"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create model instance from dictionary"""
        # This would be implemented by subclasses
        raise NotImplementedError("Subclasses must implement from_dict")
    
    def update(self, **kwargs):
        """Update model fields"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Update timestamp
        if hasattr(self, 'updated_at'):
            self.updated_at = datetime.utcnow()
