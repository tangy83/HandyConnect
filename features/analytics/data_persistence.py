"""
Data Analytics Foundation - Data Persistence System
Author: Sunayana
Phase 9: Data Analytics Foundation

This module handles data persistence for analytics data including
JSON file storage, data compression, backup, and retrieval.
"""

import json
import os
import gzip
import shutil
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor
import threading

from .data_schema import (
    TaskAnalytics, ThreadAnalytics, PerformanceMetric, 
    SystemHealth, UserBehavior, DataValidator
)

logger = logging.getLogger(__name__)

class AnalyticsDataPersistence:
    """Analytics data persistence manager"""
    
    def __init__(self, data_dir: str = "data/analytics"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different data types
        self.subdirs = {
            'tasks': self.data_dir / 'tasks',
            'threads': self.data_dir / 'threads',
            'performance': self.data_dir / 'performance',
            'system_health': self.data_dir / 'system_health',
            'user_behavior': self.data_dir / 'user_behavior',
            'backups': self.data_dir / 'backups'
        }
        
        for subdir in self.subdirs.values():
            subdir.mkdir(parents=True, exist_ok=True)
        
        # Thread lock for concurrent access
        self._lock = threading.Lock()
        
        # Configuration
        self.compression_enabled = True
        self.backup_enabled = True
        self.max_file_size_mb = 10
        self.retention_days = 90
        
        logger.info(f"Analytics data persistence initialized at {self.data_dir}")

    def _get_file_path(self, data_type: str, date: Optional[datetime] = None) -> Path:
        """Get file path for a specific data type and date"""
        if date is None:
            date = datetime.now(timezone.utc)
        
        date_str = date.strftime("%Y-%m-%d")
        filename = f"{data_type}_{date_str}.json"
        
        if self.compression_enabled:
            filename += ".gz"
        
        return self.subdirs[data_type] / filename

    def _compress_file(self, file_path: Path) -> Path:
        """Compress a JSON file"""
        if not self.compression_enabled or file_path.suffix == '.gz':
            return file_path
        
        compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
        
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remove original file
        file_path.unlink()
        return compressed_path

    def _decompress_file(self, file_path: Path) -> Path:
        """Decompress a gzipped JSON file"""
        if file_path.suffix != '.gz':
            return file_path
        
        decompressed_path = file_path.with_suffix('')
        
        with gzip.open(file_path, 'rt') as f_in:
            with open(decompressed_path, 'w') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        return decompressed_path

    def _load_json_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load data from a JSON file"""
        if not file_path.exists():
            return []
        
        try:
            # Handle compressed files
            if file_path.suffix == '.gz':
                with gzip.open(file_path, 'rt') as f:
                    data = json.load(f)
            else:
                with open(file_path, 'r') as f:
                    data = json.load(f)
            
            return data if isinstance(data, list) else [data]
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading file {file_path}: {e}")
            return []

    def _save_json_file(self, file_path: Path, data: List[Dict[str, Any]]) -> bool:
        """Save data to a JSON file"""
        try:
            # Create backup if enabled
            if self.backup_enabled and file_path.exists():
                self._create_backup(file_path)
            
            # Write data
            if self.compression_enabled:
                with gzip.open(file_path, 'wt') as f:
                    json.dump(data, f, indent=2, default=str)
            else:
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
            
            logger.debug(f"Saved {len(data)} records to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving file {file_path}: {e}")
            return False

    def _create_backup(self, file_path: Path) -> None:
        """Create a backup of a file"""
        try:
            backup_dir = self.subdirs['backups']
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            backup_path = backup_dir / backup_name
            
            shutil.copy2(file_path, backup_path)
            logger.debug(f"Created backup: {backup_path}")
        except Exception as e:
            logger.error(f"Error creating backup for {file_path}: {e}")

    def _check_file_size(self, file_path: Path) -> bool:
        """Check if file size exceeds maximum allowed size"""
        if not file_path.exists():
            return True
        
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        return file_size_mb < self.max_file_size_mb

    def _rotate_file(self, file_path: Path) -> Path:
        """Rotate file when it exceeds maximum size"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rotated_path = file_path.parent / f"{file_path.stem}_{timestamp}{file_path.suffix}"
        
        if file_path.exists():
            shutil.move(str(file_path), str(rotated_path))
            logger.info(f"Rotated file: {file_path} -> {rotated_path}")
        
        return file_path

    # ==================== TASK ANALYTICS ====================

    def save_task_analytics(self, task_analytics: Union[TaskAnalytics, List[TaskAnalytics]]) -> bool:
        """Save task analytics data"""
        with self._lock:
            if isinstance(task_analytics, TaskAnalytics):
                task_analytics = [task_analytics]
            
            # Validate data
            for analytics in task_analytics:
                if not analytics.validate():
                    logger.error(f"Invalid task analytics data: {analytics.task_id}")
                    return False
            
            # Get file path
            file_path = self._get_file_path('tasks')
            
            # Check file size and rotate if necessary
            if not self._check_file_size(file_path):
                file_path = self._rotate_file(file_path)
            
            # Load existing data
            existing_data = self._load_json_file(file_path)
            
            # Add new data
            new_data = [analytics.to_dict() for analytics in task_analytics]
            existing_data.extend(new_data)
            
            # Save data
            return self._save_json_file(file_path, existing_data)

    def load_task_analytics(self, start_date: Optional[datetime] = None, 
                           end_date: Optional[datetime] = None) -> List[TaskAnalytics]:
        """Load task analytics data"""
        with self._lock:
            if start_date is None:
                start_date = datetime.now(timezone.utc) - timedelta(days=30)
            if end_date is None:
                end_date = datetime.now(timezone.utc)
            
            all_data = []
            current_date = start_date.date()
            end_date_only = end_date.date()
            
            while current_date <= end_date_only:
                file_path = self._get_file_path('tasks', datetime.combine(current_date, datetime.min.time()))
                data = self._load_json_file(file_path)
                
                # Filter by date range
                filtered_data = []
                for item in data:
                    item_date = datetime.fromisoformat(item.get('created_at', '')).date()
                    if start_date.date() <= item_date <= end_date.date():
                        filtered_data.append(item)
                
                all_data.extend(filtered_data)
                current_date += timedelta(days=1)
            
            return [TaskAnalytics.from_dict(item) for item in all_data]

    # ==================== THREAD ANALYTICS ====================

    def save_thread_analytics(self, thread_analytics: Union[ThreadAnalytics, List[ThreadAnalytics]]) -> bool:
        """Save thread analytics data"""
        with self._lock:
            if isinstance(thread_analytics, ThreadAnalytics):
                thread_analytics = [thread_analytics]
            
            # Validate data
            for analytics in thread_analytics:
                if not analytics.validate():
                    logger.error(f"Invalid thread analytics data: {analytics.thread_id}")
                    return False
            
            # Get file path
            file_path = self._get_file_path('threads')
            
            # Check file size and rotate if necessary
            if not self._check_file_size(file_path):
                file_path = self._rotate_file(file_path)
            
            # Load existing data
            existing_data = self._load_json_file(file_path)
            
            # Add new data
            new_data = [analytics.to_dict() for analytics in thread_analytics]
            existing_data.extend(new_data)
            
            # Save data
            return self._save_json_file(file_path, existing_data)

    def load_thread_analytics(self, start_date: Optional[datetime] = None, 
                             end_date: Optional[datetime] = None) -> List[ThreadAnalytics]:
        """Load thread analytics data"""
        with self._lock:
            if start_date is None:
                start_date = datetime.now(timezone.utc) - timedelta(days=30)
            if end_date is None:
                end_date = datetime.now(timezone.utc)
            
            all_data = []
            current_date = start_date.date()
            end_date_only = end_date.date()
            
            while current_date <= end_date_only:
                file_path = self._get_file_path('threads', datetime.combine(current_date, datetime.min.time()))
                data = self._load_json_file(file_path)
                
                # Filter by date range
                filtered_data = []
                for item in data:
                    item_date = datetime.fromisoformat(item.get('created_at', '')).date()
                    if start_date.date() <= item_date <= end_date.date():
                        filtered_data.append(item)
                
                all_data.extend(filtered_data)
                current_date += timedelta(days=1)
            
            return [ThreadAnalytics.from_dict(item) for item in all_data]

    # ==================== PERFORMANCE METRICS ====================

    def save_performance_metrics(self, metrics: Union[PerformanceMetric, List[PerformanceMetric]]) -> bool:
        """Save performance metrics data"""
        with self._lock:
            if isinstance(metrics, PerformanceMetric):
                metrics = [metrics]
            
            # Validate data
            for metric in metrics:
                if not metric.validate():
                    logger.error(f"Invalid performance metric data: {metric.metric_type}")
                    return False
            
            # Get file path
            file_path = self._get_file_path('performance')
            
            # Check file size and rotate if necessary
            if not self._check_file_size(file_path):
                file_path = self._rotate_file(file_path)
            
            # Load existing data
            existing_data = self._load_json_file(file_path)
            
            # Add new data
            new_data = [metric.to_dict() for metric in metrics]
            existing_data.extend(new_data)
            
            # Save data
            return self._save_json_file(file_path, existing_data)

    def load_performance_metrics(self, start_date: Optional[datetime] = None, 
                                end_date: Optional[datetime] = None,
                                metric_type: Optional[str] = None) -> List[PerformanceMetric]:
        """Load performance metrics data"""
        with self._lock:
            if start_date is None:
                start_date = datetime.now(timezone.utc) - timedelta(days=7)
            if end_date is None:
                end_date = datetime.now(timezone.utc)
            
            all_data = []
            current_date = start_date.date()
            end_date_only = end_date.date()
            
            while current_date <= end_date_only:
                file_path = self._get_file_path('performance', datetime.combine(current_date, datetime.min.time()))
                data = self._load_json_file(file_path)
                
                # Filter by date range and metric type
                filtered_data = []
                for item in data:
                    item_date = datetime.fromisoformat(item.get('timestamp', '')).date()
                    if (start_date.date() <= item_date <= end_date.date() and
                        (metric_type is None or item.get('metric_type') == metric_type)):
                        filtered_data.append(item)
                
                all_data.extend(filtered_data)
                current_date += timedelta(days=1)
            
            return [PerformanceMetric.from_dict(item) for item in all_data]

    # ==================== SYSTEM HEALTH ====================

    def save_system_health(self, health_data: Union[SystemHealth, List[SystemHealth]]) -> bool:
        """Save system health data"""
        with self._lock:
            if isinstance(health_data, SystemHealth):
                health_data = [health_data]
            
            # Validate data
            for health in health_data:
                if not health.validate():
                    logger.error(f"Invalid system health data: {health.service_name}")
                    return False
            
            # Get file path
            file_path = self._get_file_path('system_health')
            
            # Check file size and rotate if necessary
            if not self._check_file_size(file_path):
                file_path = self._rotate_file(file_path)
            
            # Load existing data
            existing_data = self._load_json_file(file_path)
            
            # Add new data
            new_data = [health.to_dict() for health in health_data]
            existing_data.extend(new_data)
            
            # Save data
            return self._save_json_file(file_path, existing_data)

    def load_system_health(self, start_date: Optional[datetime] = None, 
                          end_date: Optional[datetime] = None,
                          service_name: Optional[str] = None) -> List[SystemHealth]:
        """Load system health data"""
        with self._lock:
            if start_date is None:
                start_date = datetime.now(timezone.utc) - timedelta(days=7)
            if end_date is None:
                end_date = datetime.now(timezone.utc)
            
            all_data = []
            current_date = start_date.date()
            end_date_only = end_date.date()
            
            while current_date <= end_date_only:
                file_path = self._get_file_path('system_health', datetime.combine(current_date, datetime.min.time()))
                data = self._load_json_file(file_path)
                
                # Filter by date range and service name
                filtered_data = []
                for item in data:
                    item_date = datetime.fromisoformat(item.get('timestamp', '')).date()
                    if (start_date.date() <= item_date <= end_date.date() and
                        (service_name is None or item.get('service_name') == service_name)):
                        filtered_data.append(item)
                
                all_data.extend(filtered_data)
                current_date += timedelta(days=1)
            
            return [SystemHealth.from_dict(item) for item in all_data]

    # ==================== USER BEHAVIOR ====================

    def save_user_behavior(self, behavior_data: Union[UserBehavior, List[UserBehavior]]) -> bool:
        """Save user behavior data"""
        with self._lock:
            if isinstance(behavior_data, UserBehavior):
                behavior_data = [behavior_data]
            
            # Validate data
            for behavior in behavior_data:
                if not behavior.validate():
                    logger.error(f"Invalid user behavior data: {behavior.user_id}")
                    return False
            
            # Get file path
            file_path = self._get_file_path('user_behavior')
            
            # Check file size and rotate if necessary
            if not self._check_file_size(file_path):
                file_path = self._rotate_file(file_path)
            
            # Load existing data
            existing_data = self._load_json_file(file_path)
            
            # Add new data
            new_data = [behavior.to_dict() for behavior in behavior_data]
            existing_data.extend(new_data)
            
            # Save data
            return self._save_json_file(file_path, existing_data)

    def load_user_behavior(self, start_date: Optional[datetime] = None, 
                          end_date: Optional[datetime] = None,
                          user_id: Optional[str] = None) -> List[UserBehavior]:
        """Load user behavior data"""
        with self._lock:
            if start_date is None:
                start_date = datetime.now(timezone.utc) - timedelta(days=7)
            if end_date is None:
                end_date = datetime.now(timezone.utc)
            
            all_data = []
            current_date = start_date.date()
            end_date_only = end_date.date()
            
            while current_date <= end_date_only:
                file_path = self._get_file_path('user_behavior', datetime.combine(current_date, datetime.min.time()))
                data = self._load_json_file(file_path)
                
                # Filter by date range and user ID
                filtered_data = []
                for item in data:
                    item_date = datetime.fromisoformat(item.get('timestamp', '')).date()
                    if (start_date.date() <= item_date <= end_date.date() and
                        (user_id is None or item.get('user_id') == user_id)):
                        filtered_data.append(item)
                
                all_data.extend(filtered_data)
                current_date += timedelta(days=1)
            
            return [UserBehavior.from_dict(item) for item in all_data]

    # ==================== UTILITY METHODS ====================

    def cleanup_old_data(self) -> int:
        """Clean up data older than retention period"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
        deleted_files = 0
        
        for data_type in ['tasks', 'threads', 'performance', 'system_health', 'user_behavior']:
            subdir = self.subdirs[data_type]
            
            for file_path in subdir.glob("*.json*"):
                try:
                    # Extract date from filename
                    filename = file_path.stem.replace('.json', '')
                    if '_' in filename:
                        date_part = filename.split('_')[-1]
                        try:
                            file_date = datetime.strptime(date_part, "%Y-%m-%d").date()
                            if file_date < cutoff_date.date():
                                file_path.unlink()
                                deleted_files += 1
                                logger.info(f"Deleted old file: {file_path}")
                        except ValueError:
                            # Skip files that don't match date pattern
                            continue
                except Exception as e:
                    logger.error(f"Error deleting file {file_path}: {e}")
        
        return deleted_files

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        stats = {
            'total_size_mb': 0,
            'file_counts': {},
            'oldest_file': None,
            'newest_file': None
        }
        
        for data_type, subdir in self.subdirs.items():
            if data_type == 'backups':
                continue
                
            file_count = 0
            total_size = 0
            oldest_date = None
            newest_date = None
            
            for file_path in subdir.glob("*.json*"):
                file_count += 1
                total_size += file_path.stat().st_size
                
                # Extract date from filename
                filename = file_path.stem.replace('.json', '')
                if '_' in filename:
                    date_part = filename.split('_')[-1]
                    try:
                        file_date = datetime.strptime(date_part, "%Y-%m-%d").date()
                        if oldest_date is None or file_date < oldest_date:
                            oldest_date = file_date
                        if newest_date is None or file_date > newest_date:
                            newest_date = file_date
                    except ValueError:
                        continue
            
            stats['file_counts'][data_type] = file_count
            stats['total_size_mb'] += total_size / (1024 * 1024)
            
            if oldest_date and (stats['oldest_file'] is None or oldest_date < stats['oldest_file']):
                stats['oldest_file'] = oldest_date
            if newest_date and (stats['newest_file'] is None or newest_date > stats['newest_file']):
                stats['newest_file'] = newest_date
        
        return stats

    def export_data(self, data_type: str, start_date: Optional[datetime] = None, 
                   end_date: Optional[datetime] = None, output_file: Optional[str] = None) -> str:
        """Export data to a single JSON file"""
        if data_type not in ['tasks', 'threads', 'performance', 'system_health', 'user_behavior']:
            raise ValueError(f"Invalid data type: {data_type}")
        
        # Load data
        if data_type == 'tasks':
            data = self.load_task_analytics(start_date, end_date)
        elif data_type == 'threads':
            data = self.load_thread_analytics(start_date, end_date)
        elif data_type == 'performance':
            data = self.load_performance_metrics(start_date, end_date)
        elif data_type == 'system_health':
            data = self.load_system_health(start_date, end_date)
        elif data_type == 'user_behavior':
            data = self.load_user_behavior(start_date, end_date)
        
        # Convert to dict format
        data_dicts = [item.to_dict() for item in data]
        
        # Generate output filename if not provided
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{data_type}_export_{timestamp}.json"
        
        # Save to file
        output_path = self.data_dir / output_file
        with open(output_path, 'w') as f:
            json.dump(data_dicts, f, indent=2, default=str)
        
        logger.info(f"Exported {len(data_dicts)} {data_type} records to {output_path}")
        return str(output_path)
