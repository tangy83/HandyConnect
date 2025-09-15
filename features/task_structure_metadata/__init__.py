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

from .task_schema import TaskSchema
from .metadata_extractor import MetadataExtractor
from .task_validator import TaskValidator
from .schema_migrator import SchemaMigrator

__all__ = [
    'TaskSchema',
    'MetadataExtractor',
    'TaskValidator',
    'SchemaMigrator'
]


