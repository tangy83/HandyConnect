"""
Data Persistence System Implementation
Handles robust data storage, backup, and recovery for task data.
"""

import json
import os
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path
import gzip
import pickle

from .task_schema import TaskSchema, TaskValidator, SchemaMigrator


class DataPersistenceManager:
    """Manages data persistence with backup and recovery capabilities"""
    
    def __init__(self, data_dir: str = "data", backup_dir: str = "data/backups"):
        self.data_dir = Path(data_dir)
        self.backup_dir = Path(backup_dir)
        self.tasks_file = self.data_dir / "tasks.json"
        self.analytics_file = self.data_dir / "analytics.json"
        self.metadata_file = self.data_dir / "metadata.json"
        
        # Create directories if they don't exist
        self.data_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def save_tasks(self, tasks: List[TaskSchema], create_backup: bool = True) -> bool:
        """Save tasks to JSON file with backup creation"""
        try:
            # Create backup before saving
            if create_backup and self.tasks_file.exists():
                self._create_backup(self.tasks_file)
            
            # Convert tasks to dictionaries
            tasks_data = [task.to_dict() for task in tasks]
            
            # Save to temporary file first (atomic write)
            temp_file = self.tasks_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, indent=2, ensure_ascii=False, default=str)
            
            # Move temp file to final location
            shutil.move(str(temp_file), str(self.tasks_file))
            
            # Update metadata
            self._update_metadata('tasks_saved', len(tasks))
            
            self.logger.info(f"Successfully saved {len(tasks)} tasks to {self.tasks_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving tasks: {e}")
            return False
    
    def load_tasks(self) -> List[TaskSchema]:
        """Load tasks from JSON file with error handling"""
        try:
            if not self.tasks_file.exists():
                self.logger.info("Tasks file not found, returning empty list")
                return []
            
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
            
            # Convert dictionaries to TaskSchema objects
            tasks = []
            for task_data in tasks_data:
                try:
                    task = TaskSchema.from_dict(task_data)
                    tasks.append(task)
                except Exception as e:
                    self.logger.warning(f"Error loading task {task_data.get('id', 'unknown')}: {e}")
                    continue
            
            self.logger.info(f"Successfully loaded {len(tasks)} tasks from {self.tasks_file}")
            return tasks
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            # Try to restore from backup
            return self._restore_from_backup()
        except Exception as e:
            self.logger.error(f"Error loading tasks: {e}")
            return []
    
    def save_analytics_data(self, analytics_data: Dict[str, Any]) -> bool:
        """Save analytics data to JSON file"""
        try:
            # Create backup
            if self.analytics_file.exists():
                self._create_backup(self.analytics_file)
            
            # Save with timestamp
            data_with_timestamp = {
                'timestamp': datetime.utcnow().isoformat(),
                'data': analytics_data
            }
            
            with open(self.analytics_file, 'w', encoding='utf-8') as f:
                json.dump(data_with_timestamp, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Successfully saved analytics data to {self.analytics_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving analytics data: {e}")
            return False
    
    def load_analytics_data(self) -> Optional[Dict[str, Any]]:
        """Load analytics data from JSON file"""
        try:
            if not self.analytics_file.exists():
                return None
            
            with open(self.analytics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data.get('data', {})
            
        except Exception as e:
            self.logger.error(f"Error loading analytics data: {e}")
            return None
    
    def _create_backup(self, file_path: Path) -> bool:
        """Create timestamped backup of a file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            backup_path = self.backup_dir / backup_name
            
            shutil.copy2(file_path, backup_path)
            
            # Compress old backups
            self._compress_old_backups()
            
            self.logger.info(f"Created backup: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            return False
    
    def _compress_old_backups(self) -> None:
        """Compress backups older than 7 days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=7)
            
            for backup_file in self.backup_dir.glob("*.json"):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    # Compress the file
                    compressed_file = backup_file.with_suffix('.json.gz')
                    with open(backup_file, 'rb') as f_in:
                        with gzip.open(compressed_file, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    
                    # Remove original
                    backup_file.unlink()
                    self.logger.info(f"Compressed old backup: {compressed_file}")
                    
        except Exception as e:
            self.logger.error(f"Error compressing backups: {e}")
    
    def _restore_from_backup(self) -> List[TaskSchema]:
        """Restore tasks from the most recent backup"""
        try:
            # Find most recent backup
            backup_files = list(self.backup_dir.glob("tasks_*.json"))
            if not backup_files:
                self.logger.error("No backup files found")
                return []
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            latest_backup = backup_files[0]
            
            self.logger.info(f"Restoring from backup: {latest_backup}")
            
            with open(latest_backup, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
            
            tasks = []
            for task_data in tasks_data:
                try:
                    task = TaskSchema.from_dict(task_data)
                    tasks.append(task)
                except Exception as e:
                    self.logger.warning(f"Error loading task from backup: {e}")
                    continue
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"Error restoring from backup: {e}")
            return []
    
    def _update_metadata(self, operation: str, count: int) -> None:
        """Update metadata file with operation information"""
        try:
            metadata = self.load_metadata()
            metadata['last_operation'] = {
                'operation': operation,
                'count': count,
                'timestamp': datetime.utcnow().isoformat()
            }
            metadata['total_operations'] = metadata.get('total_operations', 0) + 1
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            self.logger.error(f"Error updating metadata: {e}")
    
    def load_metadata(self) -> Dict[str, Any]:
        """Load metadata file"""
        try:
            if not self.metadata_file.exists():
                return {
                    'created_at': datetime.utcnow().isoformat(),
                    'total_operations': 0,
                    'schema_version': 1
                }
            
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Error loading metadata: {e}")
            return {}
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            stats = {
                'data_directory': str(self.data_dir),
                'backup_directory': str(self.backup_dir),
                'files': {},
                'backups': []
            }
            
            # File sizes
            for file_path in [self.tasks_file, self.analytics_file, self.metadata_file]:
                if file_path.exists():
                    stats['files'][file_path.name] = {
                        'size_bytes': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    }
            
            # Backup information
            for backup_file in self.backup_dir.glob("*"):
                stats['backups'].append({
                    'name': backup_file.name,
                    'size_bytes': backup_file.stat().st_size,
                    'created': datetime.fromtimestamp(backup_file.stat().st_ctime).isoformat()
                })
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting storage stats: {e}")
            return {}
    
    def cleanup_old_backups(self, days_to_keep: int = 30) -> int:
        """Clean up backups older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            deleted_count = 0
            
            for backup_file in self.backup_dir.glob("*"):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    backup_file.unlink()
                    deleted_count += 1
                    self.logger.info(f"Deleted old backup: {backup_file}")
            
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up backups: {e}")
            return 0
    
    def export_data(self, export_path: str, include_backups: bool = False) -> bool:
        """Export all data to a specified path"""
        try:
            export_dir = Path(export_path)
            export_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy main data files
            for file_path in [self.tasks_file, self.analytics_file, self.metadata_file]:
                if file_path.exists():
                    shutil.copy2(file_path, export_dir / file_path.name)
            
            # Copy backups if requested
            if include_backups:
                backup_export_dir = export_dir / "backups"
                backup_export_dir.mkdir(exist_ok=True)
                for backup_file in self.backup_dir.glob("*"):
                    shutil.copy2(backup_file, backup_export_dir / backup_file.name)
            
            self.logger.info(f"Data exported to: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            return False
    
    def import_data(self, import_path: str) -> bool:
        """Import data from a specified path"""
        try:
            import_dir = Path(import_path)
            
            if not import_dir.exists():
                self.logger.error(f"Import path does not exist: {import_path}")
                return False
            
            # Create backup before import
            self._create_backup(self.tasks_file)
            
            # Import main data files
            for file_name in ["tasks.json", "analytics.json", "metadata.json"]:
                source_file = import_dir / file_name
                if source_file.exists():
                    dest_file = self.data_dir / file_name
                    shutil.copy2(source_file, dest_file)
                    self.logger.info(f"Imported {file_name}")
            
            self.logger.info(f"Data imported from: {import_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing data: {e}")
            return False


class DataValidator:
    """Validates data integrity and consistency"""
    
    @staticmethod
    def validate_data_integrity(tasks: List[TaskSchema]) -> Dict[str, Any]:
        """Validate data integrity and return validation results"""
        results = {
            'total_tasks': len(tasks),
            'valid_tasks': 0,
            'invalid_tasks': 0,
            'errors': [],
            'warnings': [],
            'duplicate_ids': [],
            'orphaned_threads': []
        }
        
        seen_ids = set()
        
        for task in tasks:
            # Validate individual task
            task_errors = TaskValidator.validate_task(task)
            
            if task_errors:
                results['invalid_tasks'] += 1
                results['errors'].append({
                    'task_id': task.id,
                    'errors': task_errors
                })
            else:
                results['valid_tasks'] += 1
            
            # Check for duplicate IDs
            if task.id in seen_ids:
                results['duplicate_ids'].append(task.id)
            else:
                seen_ids.add(task.id)
            
            # Check for orphaned threads (thread_id without corresponding tasks)
            if task.thread_id:
                thread_tasks = [t for t in tasks if t.thread_id == task.thread_id]
                if len(thread_tasks) == 1:
                    results['orphaned_threads'].append(task.thread_id)
        
        return results
    
    @staticmethod
    def repair_data_issues(tasks: List[TaskSchema]) -> Tuple[List[TaskSchema], List[str]]:
        """Repair common data issues and return repaired tasks"""
        repaired_tasks = []
        repair_log = []
        
        seen_ids = set()
        
        for task in tasks:
            # Fix duplicate IDs
            original_id = task.id
            while task.id in seen_ids:
                task.id = f"{original_id}_duplicate_{len(seen_ids)}"
                repair_log.append(f"Fixed duplicate ID: {original_id} -> {task.id}")
            
            seen_ids.add(task.id)
            
            # Fix missing timestamps
            if not task.metadata.created_at:
                task.metadata.created_at = datetime.utcnow()
                repair_log.append(f"Added missing created_at for task {task.id}")
            
            if not task.metadata.updated_at:
                task.metadata.updated_at = datetime.utcnow()
                repair_log.append(f"Added missing updated_at for task {task.id}")
            
            # Fix invalid status transitions
            if task.status.value == "Completed" and not task.resolved_at:
                task.resolved_at = datetime.utcnow()
                repair_log.append(f"Added missing resolved_at for completed task {task.id}")
            
            repaired_tasks.append(task)
        
        return repaired_tasks, repair_log


# Export main classes
__all__ = ['DataPersistenceManager', 'DataValidator']






