"""
Task Structure & Metadata Schema Module

This module defines and manages the structure and metadata for tasks.
Features:
- Task schema definition and validation
- Metadata extraction and enrichment
- Task lifecycle management
- Custom field definitions
- Data migration and versioning
"""

from .task_schema import (
    TaskSchema, TaskMetadata, TaskValidator, SchemaMigrator, MetadataExtractor,
    TaskStatus, TaskPriority, TaskCategory
)
from .data_persistence import DataPersistenceManager, DataValidator

__all__ = [
    'TaskSchema',
    'TaskMetadata',
    'TaskValidator',
    'SchemaMigrator',
    'MetadataExtractor',
    'TaskStatus',
    'TaskPriority', 
    'TaskCategory',
    'DataPersistenceManager',
    'DataValidator'
]





