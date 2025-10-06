"""
Cache Service for HandyConnect
High-performance caching for case management and analytics
"""

import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CacheType(Enum):
    """Cache types"""
    MEMORY = "memory"
    FILE = "file"
    REDIS = "redis"  # Future implementation


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: datetime = None
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def touch(self):
        """Update access statistics"""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()


class CacheService:
    """High-performance caching service"""
    
    def __init__(self, cache_type: CacheType = CacheType.MEMORY, 
                 default_ttl: int = 300, max_size: int = 1000,
                 file_cache_dir: str = 'data/cache'):
        self.cache_type = cache_type
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.file_cache_dir = file_cache_dir
        
        # Memory cache storage
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        
        # Statistics
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expired': 0,
            'total_requests': 0
        }
        
        # Initialize cache directory for file cache
        if cache_type == CacheType.FILE:
            import os
            os.makedirs(file_cache_dir, exist_ok=True)
        
        logger.info(f"CacheService initialized: {cache_type.value}, TTL: {default_ttl}s, Max size: {max_size}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        with self._lock:
            self._stats['total_requests'] += 1
            
            if self.cache_type == CacheType.MEMORY:
                return self._get_memory(key, default)
            elif self.cache_type == CacheType.FILE:
                return self._get_file(key, default)
            else:
                return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        with self._lock:
            ttl = ttl or self.default_ttl
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            
            if self.cache_type == CacheType.MEMORY:
                return self._set_memory(key, value, expires_at)
            elif self.cache_type == CacheType.FILE:
                return self._set_file(key, value, expires_at)
            else:
                return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        with self._lock:
            if self.cache_type == CacheType.MEMORY:
                return self._delete_memory(key)
            elif self.cache_type == CacheType.FILE:
                return self._delete_file(key)
            else:
                return False
    
    def clear(self) -> bool:
        """Clear all cache entries"""
        with self._lock:
            if self.cache_type == CacheType.MEMORY:
                self._memory_cache.clear()
                logger.info("Memory cache cleared")
                return True
            elif self.cache_type == CacheType.FILE:
                import os
                import glob
                try:
                    cache_files = glob.glob(f"{self.file_cache_dir}/*.cache")
                    for cache_file in cache_files:
                        os.remove(cache_file)
                    logger.info(f"File cache cleared: {len(cache_files)} files removed")
                    return True
                except Exception as e:
                    logger.error(f"Error clearing file cache: {e}")
                    return False
            else:
                return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        with self._lock:
            if self.cache_type == CacheType.MEMORY:
                return key in self._memory_cache and not self._memory_cache[key].is_expired()
            elif self.cache_type == CacheType.FILE:
                import os
                cache_file = f"{self.file_cache_dir}/{self._key_to_filename(key)}"
                return os.path.exists(cache_file) and not self._is_file_cache_expired(cache_file)
            else:
                return False
    
    def get_or_set(self, key: str, factory: Callable[[], Any], ttl: Optional[int] = None) -> Any:
        """Get value from cache or set it using factory function"""
        value = self.get(key)
        if value is None:
            value = factory()
            self.set(key, value, ttl)
        return value
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern"""
        with self._lock:
            import fnmatch
            invalidated = 0
            
            if self.cache_type == CacheType.MEMORY:
                keys_to_delete = [k for k in self._memory_cache.keys() if fnmatch.fnmatch(k, pattern)]
                for key in keys_to_delete:
                    if self._delete_memory(key):
                        invalidated += 1
            elif self.cache_type == CacheType.FILE:
                import os
                import glob
                try:
                    cache_files = glob.glob(f"{self.file_cache_dir}/*.cache")
                    for cache_file in cache_files:
                        filename = os.path.basename(cache_file)
                        key = self._filename_to_key(filename)
                        if fnmatch.fnmatch(key, pattern):
                            if self._delete_file(key):
                                invalidated += 1
                except Exception as e:
                    logger.error(f"Error invalidating pattern {pattern}: {e}")
            
            logger.info(f"Invalidated {invalidated} cache entries matching pattern: {pattern}")
            return invalidated
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._stats['total_requests']
            hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            stats = {
                'cache_type': self.cache_type.value,
                'default_ttl': self.default_ttl,
                'max_size': self.max_size,
                'total_requests': total_requests,
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'hit_rate': round(hit_rate, 2),
                'evictions': self._stats['evictions'],
                'expired': self._stats['expired']
            }
            
            if self.cache_type == CacheType.MEMORY:
                stats['current_size'] = len(self._memory_cache)
                stats['memory_usage'] = self._estimate_memory_usage()
            
            return stats
    
    def cleanup_expired(self) -> int:
        """Clean up expired cache entries"""
        with self._lock:
            cleaned = 0
            
            if self.cache_type == CacheType.MEMORY:
                expired_keys = []
                for key, entry in self._memory_cache.items():
                    if entry.is_expired():
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self._memory_cache[key]
                    cleaned += 1
                    self._stats['expired'] += 1
            
            elif self.cache_type == CacheType.FILE:
                import os
                import glob
                try:
                    cache_files = glob.glob(f"{self.file_cache_dir}/*.cache")
                    for cache_file in cache_files:
                        if self._is_file_cache_expired(cache_file):
                            os.remove(cache_file)
                            cleaned += 1
                            self._stats['expired'] += 1
                except Exception as e:
                    logger.error(f"Error cleaning up expired file cache entries: {e}")
            
            if cleaned > 0:
                logger.info(f"Cleaned up {cleaned} expired cache entries")
            
            return cleaned
    
    def _get_memory(self, key: str, default: Any = None) -> Any:
        """Get value from memory cache"""
        if key not in self._memory_cache:
            self._stats['misses'] += 1
            return default
        
        entry = self._memory_cache[key]
        
        if entry.is_expired():
            del self._memory_cache[key]
            self._stats['misses'] += 1
            self._stats['expired'] += 1
            return default
        
        entry.touch()
        self._stats['hits'] += 1
        return entry.value
    
    def _set_memory(self, key: str, value: Any, expires_at: datetime) -> bool:
        """Set value in memory cache"""
        try:
            # Check if we need to evict entries
            if len(self._memory_cache) >= self.max_size and key not in self._memory_cache:
                self._evict_lru()
            
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.utcnow(),
                expires_at=expires_at
            )
            
            self._memory_cache[key] = entry
            return True
            
        except Exception as e:
            logger.error(f"Error setting memory cache entry {key}: {e}")
            return False
    
    def _delete_memory(self, key: str) -> bool:
        """Delete value from memory cache"""
        if key in self._memory_cache:
            del self._memory_cache[key]
            return True
        return False
    
    def _evict_lru(self):
        """Evict least recently used entry"""
        if not self._memory_cache:
            return
        
        # Find LRU entry
        lru_key = min(
            self._memory_cache.keys(),
            key=lambda k: self._memory_cache[k].last_accessed
        )
        
        del self._memory_cache[lru_key]
        self._stats['evictions'] += 1
        logger.debug(f"Evicted LRU cache entry: {lru_key}")
    
    def _get_file(self, key: str, default: Any = None) -> Any:
        """Get value from file cache"""
        try:
            cache_file = f"{self.file_cache_dir}/{self._key_to_filename(key)}"
            
            if not self._file_exists(cache_file):
                self._stats['misses'] += 1
                return default
            
            if self._is_file_cache_expired(cache_file):
                self._delete_file(key)
                self._stats['misses'] += 1
                self._stats['expired'] += 1
                return default
            
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Update access statistics
            cache_data['access_count'] = cache_data.get('access_count', 0) + 1
            cache_data['last_accessed'] = datetime.utcnow().isoformat()
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
            
            self._stats['hits'] += 1
            return cache_data['value']
            
        except Exception as e:
            logger.error(f"Error getting file cache entry {key}: {e}")
            self._stats['misses'] += 1
            return default
    
    def _set_file(self, key: str, value: Any, expires_at: datetime) -> bool:
        """Set value in file cache"""
        try:
            cache_file = f"{self.file_cache_dir}/{self._key_to_filename(key)}"
            
            cache_data = {
                'key': key,
                'value': value,
                'created_at': datetime.utcnow().isoformat(),
                'expires_at': expires_at.isoformat(),
                'access_count': 0,
                'last_accessed': datetime.utcnow().isoformat()
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting file cache entry {key}: {e}")
            return False
    
    def _delete_file(self, key: str) -> bool:
        """Delete value from file cache"""
        try:
            cache_file = f"{self.file_cache_dir}/{self._key_to_filename(key)}"
            if self._file_exists(cache_file):
                import os
                os.remove(cache_file)
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file cache entry {key}: {e}")
            return False
    
    def _is_file_cache_expired(self, cache_file: str) -> bool:
        """Check if file cache entry is expired"""
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            expires_at = datetime.fromisoformat(cache_data.get('expires_at', ''))
            return datetime.utcnow() > expires_at
            
        except Exception:
            return True
    
    def _file_exists(self, filepath: str) -> bool:
        """Check if file exists"""
        import os
        return os.path.exists(filepath)
    
    def _key_to_filename(self, key: str) -> str:
        """Convert cache key to filename"""
        import hashlib
        # Hash the key to create a safe filename
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return f"{hash_key}.cache"
    
    def _filename_to_key(self, filename: str) -> str:
        """Convert filename back to cache key"""
        # This is a limitation - we can't easily reverse the hash
        # For now, we'll store the original key in the cache data
        return "unknown"
    
    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage in bytes"""
        try:
            import sys
            total_size = 0
            for entry in self._memory_cache.values():
                total_size += sys.getsizeof(entry.key)
                total_size += sys.getsizeof(entry.value)
                total_size += sys.getsizeof(entry)
            return total_size
        except Exception:
            return 0


# Global cache instances
_case_cache = None
_analytics_cache = None


def get_case_cache() -> CacheService:
    """Get global case cache instance"""
    global _case_cache
    if _case_cache is None:
        _case_cache = CacheService(
            cache_type=CacheType.MEMORY,
            default_ttl=300,  # 5 minutes
            max_size=500
        )
    return _case_cache


def get_analytics_cache() -> CacheService:
    """Get global analytics cache instance"""
    global _analytics_cache
    if _analytics_cache is None:
        _analytics_cache = CacheService(
            cache_type=CacheType.MEMORY,
            default_ttl=60,  # 1 minute
            max_size=100
        )
    return _analytics_cache


def cache_cases(cache_key: str, cases: List[Dict], ttl: int = 300):
    """Cache cases data"""
    cache = get_case_cache()
    cache.set(cache_key, cases, ttl)


def get_cached_cases(cache_key: str) -> Optional[List[Dict]]:
    """Get cached cases data"""
    cache = get_case_cache()
    return cache.get(cache_key)


def cache_analytics(cache_key: str, analytics: Dict, ttl: int = 60):
    """Cache analytics data"""
    cache = get_analytics_cache()
    cache.set(cache_key, analytics, ttl)


def get_cached_analytics(cache_key: str) -> Optional[Dict]:
    """Get cached analytics data"""
    cache = get_analytics_cache()
    return cache.get(cache_key)


def invalidate_case_cache(pattern: str = "*"):
    """Invalidate case cache entries"""
    cache = get_case_cache()
    return cache.invalidate_pattern(pattern)


def invalidate_analytics_cache(pattern: str = "*"):
    """Invalidate analytics cache entries"""
    cache = get_analytics_cache()
    return cache.invalidate_pattern(pattern)
