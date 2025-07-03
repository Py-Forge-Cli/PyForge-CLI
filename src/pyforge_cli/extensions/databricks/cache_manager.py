"""
Databricks Extension Cache Manager

This module provides thread-safe caching functionality for environment detection
results, improving performance by avoiding repeated expensive operations.
"""

import os
import json
import time
import threading
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path
import hashlib


class CacheManager:
    """
    Thread-safe cache manager for Databricks extension.
    
    Provides in-memory and optional disk-based caching with TTL support,
    automatic expiration, and cache invalidation strategies.
    """
    
    def __init__(self, cache_dir: Optional[Path] = None, default_ttl: int = 300):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir: Directory for disk-based cache (optional)
            default_ttl: Default time-to-live in seconds (default: 5 minutes)
        """
        self.logger = logging.getLogger("pyforge.extensions.databricks.cache")
        
        # In-memory cache
        self._memory_cache: Dict[str, Any] = {}
        self._expiry_times: Dict[str, float] = {}
        self._access_counts: Dict[str, int] = {}
        self._lock = threading.RLock()
        
        # Configuration
        self.default_ttl = default_ttl
        self.cache_dir = cache_dir
        self.enable_disk_cache = cache_dir is not None
        
        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        
        # Cache size limits
        self.max_memory_items = 1000
        self.max_item_size = 10 * 1024 * 1024  # 10MB
        
        # Initialize disk cache directory
        if self.enable_disk_cache and not self.cache_dir.exists():
            try:
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Created cache directory: {self.cache_dir}")
            except Exception as e:
                self.logger.warning(f"Failed to create cache directory: {e}")
                self.enable_disk_cache = False
    
    def get(self, key: str, generator: Optional[Callable] = None, ttl: Optional[int] = None) -> Any:
        """
        Get value from cache or generate if not present.
        
        Args:
            key: Cache key
            generator: Function to generate value if not cached
            ttl: Time-to-live for this item (overrides default)
            
        Returns:
            Any: Cached or generated value
        """
        with self._lock:
            # Check memory cache first
            if self._is_valid_in_memory(key):
                self._hits += 1
                self._access_counts[key] = self._access_counts.get(key, 0) + 1
                self.logger.debug(f"Cache hit (memory): {key}")
                return self._memory_cache[key]
            
            # Check disk cache if enabled
            if self.enable_disk_cache:
                disk_value = self._get_from_disk(key)
                if disk_value is not None:
                    self._hits += 1
                    self.logger.debug(f"Cache hit (disk): {key}")
                    # Promote to memory cache
                    self._set_memory_cache(key, disk_value, ttl or self.default_ttl)
                    return disk_value
            
            # Cache miss
            self._misses += 1
            self.logger.debug(f"Cache miss: {key}")
            
            # Generate value if generator provided
            if generator:
                try:
                    value = generator()
                    self.set(key, value, ttl)
                    return value
                except Exception as e:
                    self.logger.error(f"Error generating cache value: {e}")
                    raise
            
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
            
        Returns:
            bool: True if successfully cached
        """
        with self._lock:
            # Check size limit
            try:
                value_size = len(json.dumps(value, default=str))
                if value_size > self.max_item_size:
                    self.logger.warning(f"Value too large to cache: {key} ({value_size} bytes)")
                    return False
            except Exception:
                # If we can't serialize, we can't cache to disk anyway
                pass
            
            # Set in memory cache
            self._set_memory_cache(key, value, ttl or self.default_ttl)
            
            # Set in disk cache if enabled
            if self.enable_disk_cache:
                self._set_disk_cache(key, value, ttl or self.default_ttl)
            
            # Evict old items if necessary
            self._evict_if_needed()
            
            return True
    
    def invalidate(self, key: str) -> bool:
        """
        Invalidate a specific cache entry.
        
        Args:
            key: Cache key to invalidate
            
        Returns:
            bool: True if entry was invalidated
        """
        with self._lock:
            invalidated = False
            
            # Remove from memory cache
            if key in self._memory_cache:
                del self._memory_cache[key]
                del self._expiry_times[key]
                if key in self._access_counts:
                    del self._access_counts[key]
                invalidated = True
                self.logger.debug(f"Invalidated memory cache: {key}")
            
            # Remove from disk cache
            if self.enable_disk_cache:
                cache_file = self._get_cache_file_path(key)
                if cache_file.exists():
                    try:
                        cache_file.unlink()
                        invalidated = True
                        self.logger.debug(f"Invalidated disk cache: {key}")
                    except Exception as e:
                        self.logger.error(f"Failed to remove disk cache: {e}")
            
            return invalidated
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all cache entries matching a pattern.
        
        Args:
            pattern: Pattern to match (simple string matching)
            
        Returns:
            int: Number of entries invalidated
        """
        with self._lock:
            count = 0
            
            # Find matching keys
            keys_to_invalidate = [
                key for key in self._memory_cache.keys()
                if pattern in key
            ]
            
            # Invalidate each key
            for key in keys_to_invalidate:
                if self.invalidate(key):
                    count += 1
            
            self.logger.info(f"Invalidated {count} cache entries matching '{pattern}'")
            return count
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            # Clear memory cache
            self._memory_cache.clear()
            self._expiry_times.clear()
            self._access_counts.clear()
            
            # Clear disk cache
            if self.enable_disk_cache:
                try:
                    for cache_file in self.cache_dir.glob("*.cache"):
                        cache_file.unlink()
                except Exception as e:
                    self.logger.error(f"Error clearing disk cache: {e}")
            
            # Reset statistics
            self._hits = 0
            self._misses = 0
            self._evictions = 0
            
            self.logger.info("Cache cleared")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict[str, Any]: Cache statistics
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0
            
            # Get top accessed keys
            top_keys = sorted(
                self._access_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            return {
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "hit_rate": hit_rate,
                "memory_entries": len(self._memory_cache),
                "disk_enabled": self.enable_disk_cache,
                "top_accessed_keys": top_keys,
                "memory_size_estimate": sum(
                    len(str(v)) for v in self._memory_cache.values()
                )
            }
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.
        
        Returns:
            int: Number of entries removed
        """
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, expiry in self._expiry_times.items()
                if current_time > expiry
            ]
            
            for key in expired_keys:
                self.invalidate(key)
            
            if expired_keys:
                self.logger.debug(f"Cleaned up {len(expired_keys)} expired entries")
            
            return len(expired_keys)
    
    # Private helper methods
    
    def _is_valid_in_memory(self, key: str) -> bool:
        """Check if memory cache entry is valid (exists and not expired)."""
        if key not in self._memory_cache:
            return False
        
        if time.time() > self._expiry_times.get(key, 0):
            # Expired
            del self._memory_cache[key]
            del self._expiry_times[key]
            return False
        
        return True
    
    def _set_memory_cache(self, key: str, value: Any, ttl: int) -> None:
        """Set value in memory cache with TTL."""
        self._memory_cache[key] = value
        self._expiry_times[key] = time.time() + ttl
        self._access_counts[key] = self._access_counts.get(key, 0) + 1
    
    def _get_cache_file_path(self, key: str) -> Path:
        """Get disk cache file path for a key."""
        # Create safe filename from key
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{safe_key}.cache"
    
    def _get_from_disk(self, key: str) -> Optional[Any]:
        """Get value from disk cache."""
        if not self.enable_disk_cache:
            return None
        
        cache_file = self._get_cache_file_path(key)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check expiry
            if time.time() > cache_data.get("expiry", 0):
                # Expired
                cache_file.unlink()
                return None
            
            return cache_data.get("value")
            
        except Exception as e:
            self.logger.error(f"Error reading disk cache: {e}")
            # Remove corrupted cache file
            try:
                cache_file.unlink()
            except Exception:
                pass
            return None
    
    def _set_disk_cache(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in disk cache."""
        if not self.enable_disk_cache:
            return False
        
        cache_file = self._get_cache_file_path(key)
        
        try:
            cache_data = {
                "key": key,
                "value": value,
                "expiry": time.time() + ttl,
                "created": datetime.now().isoformat()
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, default=str, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error writing disk cache: {e}")
            return False
    
    def _evict_if_needed(self) -> None:
        """Evict old entries if cache is too large."""
        if len(self._memory_cache) <= self.max_memory_items:
            return
        
        # Evict least recently accessed items
        # Sort by access count (ascending) and evict 10% of items
        items_to_evict = max(1, len(self._memory_cache) // 10)
        
        sorted_keys = sorted(
            self._access_counts.items(),
            key=lambda x: x[1]
        )
        
        for key, _ in sorted_keys[:items_to_evict]:
            del self._memory_cache[key]
            del self._expiry_times[key]
            del self._access_counts[key]
            self._evictions += 1
        
        self.logger.debug(f"Evicted {items_to_evict} items from cache")
    
    def __repr__(self) -> str:
        """String representation of cache manager."""
        with self._lock:
            return (
                f"CacheManager("
                f"entries={len(self._memory_cache)}, "
                f"hits={self._hits}, "
                f"misses={self._misses}, "
                f"disk={'enabled' if self.enable_disk_cache else 'disabled'})"
            )


# Singleton instance for the extension
_cache_instance: Optional[CacheManager] = None
_cache_lock = threading.Lock()


def get_cache_manager(cache_dir: Optional[Path] = None) -> CacheManager:
    """
    Get singleton cache manager instance.
    
    Args:
        cache_dir: Cache directory (only used on first call)
        
    Returns:
        CacheManager: Singleton cache instance
    """
    global _cache_instance
    
    with _cache_lock:
        if _cache_instance is None:
            # Default cache directory
            if cache_dir is None:
                cache_dir = Path.home() / ".pyforge" / "cache" / "databricks"
            
            _cache_instance = CacheManager(cache_dir=cache_dir)
        
        return _cache_instance