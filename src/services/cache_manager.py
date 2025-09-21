"""
Caching system for the log classification project.
Implements multiple caching strategies for improved performance.
"""
import hashlib
import pickle
import os
import time
from typing import Dict, Any, Optional, List, Tuple
from functools import wraps
from threading import Lock
from src.utils.logger_config import get_logger
from src.core.config import config

logger = get_logger(__name__)

class InMemoryCache:
    """Thread-safe in-memory cache with TTL support."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize the cache.
        
        Args:
            max_size: Maximum number of items to store
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
        self._lock = Lock()
        logger.info(f"Initialized in-memory cache: max_size={max_size}, ttl={default_ttl}s")
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a cache key from arguments."""
        key_data = f"{args}_{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_expired(self, key: str) -> bool:
        """Check if a cache entry is expired."""
        if key not in self._cache:
            return True
        
        entry = self._cache[key]
        if time.time() - entry['timestamp'] > entry['ttl']:
            return True
        
        return False
    
    def _evict_if_needed(self):
        """Evict least recently used items if cache is full."""
        if len(self._cache) >= self.max_size:
            # Remove expired items first
            expired_keys = [k for k in self._cache.keys() if self._is_expired(k)]
            for key in expired_keys:
                del self._cache[key]
                del self._access_times[key]
            
            # If still full, remove LRU items
            if len(self._cache) >= self.max_size:
                lru_key = min(self._access_times.keys(), key=self._access_times.get)
                del self._cache[lru_key]
                del self._access_times[lru_key]
                logger.debug(f"Evicted LRU cache entry: {lru_key}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            if key in self._cache and not self._is_expired(key):
                self._access_times[key] = time.time()
                return self._cache[key]['value']
            elif key in self._cache:
                # Remove expired entry
                del self._cache[key]
                del self._access_times[key]
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        with self._lock:
            self._evict_if_needed()
            
            ttl = ttl or self.default_ttl
            now = time.time()
            
            self._cache[key] = {
                'value': value,
                'timestamp': now,
                'ttl': ttl
            }
            self._access_times[key] = now
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
            logger.info("Cache cleared")
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            expired_count = sum(1 for k in self._cache.keys() if self._is_expired(k))
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'expired_entries': expired_count,
                'utilization': len(self._cache) / self.max_size * 100
            }

class FileCacheManager:
    """File-based persistent cache for expensive operations."""
    
    def __init__(self, cache_dir: str = "cache"):
        """Initialize file cache manager."""
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        logger.info(f"Initialized file cache: {cache_dir}")
    
    def _get_cache_path(self, key: str) -> str:
        """Get file path for cache key."""
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{safe_key}.pkl")
    
    def get(self, key: str, max_age: int = 3600) -> Optional[Any]:
        """Get value from file cache."""
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            # Check file age
            file_age = time.time() - os.path.getmtime(cache_path)
            if file_age > max_age:
                os.remove(cache_path)
                logger.debug(f"Removed expired cache file: {cache_path}")
                return None
            
            # Load cached data
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
                logger.debug(f"Cache hit: {key}")
                return data
                
        except Exception as e:
            logger.warning(f"Failed to load cache file {cache_path}: {e}")
            # Remove corrupted cache file
            try:
                os.remove(cache_path)
            except:
                pass
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in file cache."""
        cache_path = self._get_cache_path(key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
                logger.debug(f"Cached to file: {key}")
        except Exception as e:
            logger.error(f"Failed to save cache file {cache_path}: {e}")
    
    def clear(self) -> None:
        """Clear all cache files."""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.pkl'):
                    os.remove(os.path.join(self.cache_dir, filename))
            logger.info("File cache cleared")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")

# Global cache instances
memory_cache = InMemoryCache(max_size=1000, default_ttl=1800)  # 30 minutes
file_cache = FileCacheManager("cache")

def cache_result(ttl: int = 1800, use_file_cache: bool = False):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds
        use_file_cache: Whether to use persistent file cache
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}_{memory_cache._generate_key(*args, **kwargs)}"
            
            # Try memory cache first
            result = memory_cache.get(cache_key)
            if result is not None:
                logger.debug(f"Memory cache hit: {func.__name__}")
                return result
            
            # Try file cache if enabled
            if use_file_cache:
                result = file_cache.get(cache_key, max_age=ttl)
                if result is not None:
                    # Store in memory cache for faster access
                    memory_cache.set(cache_key, result, ttl)
                    logger.debug(f"File cache hit: {func.__name__}")
                    return result
            
            # Execute function
            logger.debug(f"Cache miss, executing: {func.__name__}")
            result = func(*args, **kwargs)
            
            # Cache the result
            memory_cache.set(cache_key, result, ttl)
            if use_file_cache:
                file_cache.set(cache_key, result)
            
            return result
        
        return wrapper
    return decorator

def clear_all_caches():
    """Clear all caches."""
    memory_cache.clear()
    file_cache.clear()
    logger.info("All caches cleared")

def get_cache_stats() -> Dict[str, Any]:
    """Get statistics for all caches."""
    return {
        'memory_cache': memory_cache.stats(),
        'file_cache_dir': file_cache.cache_dir,
        'file_cache_exists': os.path.exists(file_cache.cache_dir)
    }