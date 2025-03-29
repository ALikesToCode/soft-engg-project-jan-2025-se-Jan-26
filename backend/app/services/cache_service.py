import time
from typing import Dict, Any, Optional, Callable, Awaitable
import logging
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)

# Simple in-memory cache
class CacheService:
    """A simple in-memory cache service with TTL for dashboard data"""
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = 60  # Default TTL of 60 seconds
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Set a value in the cache with a TTL"""
        ttl = ttl or self.default_ttl
        expires_at = time.time() + ttl
        self.cache[key] = {
            "value": value,
            "expires_at": expires_at
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache if it exists and hasn't expired"""
        if key not in self.cache:
            return None
        
        cache_entry = self.cache[key]
        if time.time() > cache_entry["expires_at"]:
            # Cache entry has expired
            del self.cache[key]
            return None
        
        return cache_entry["value"]
    
    def delete(self, key: str):
        """Delete a value from the cache"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """Clear the entire cache"""
        self.cache.clear()
        
    def cleanup(self):
        """Clean up expired cache entries"""
        current_time = time.time()
        keys_to_delete = []
        
        for key, entry in self.cache.items():
            if current_time > entry["expires_at"]:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self.cache[key]


# Create a singleton instance
cache_service = CacheService()

# Start a background cleanup task
async def start_cleanup_task():
    """Start a background task to periodically clean up expired cache entries"""
    while True:
        try:
            cache_service.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up cache: {str(e)}")
        
        await asyncio.sleep(30)  # Cleanup every 30 seconds


# Decorator for caching async functions
def async_cache(ttl: int = None, key_prefix: str = ""):
    """Decorator for caching async functions results"""
    
    def decorator(func: Callable[..., Awaitable[Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name, args and kwargs
            cache_key = f"{key_prefix}:{func.__name__}:"
            
            # Add user ID to cache key if present
            if args and hasattr(args[0], "id"):  # Assuming first arg is user
                cache_key += f"user_{args[0].id}:"
            
            for arg in args[1:]:
                if hasattr(arg, "__dict__"):
                    cache_key += f"{hash(frozenset(arg.__dict__.items()))}:"
                else:
                    cache_key += f"{hash(arg)}:"
                    
            for k, v in sorted(kwargs.items()):
                if hasattr(v, "__dict__"):
                    cache_key += f"{k}_{hash(frozenset(v.__dict__.items()))}:"
                else:
                    cache_key += f"{k}_{hash(v)}:"
            
            # Check cache first
            cached_value = cache_service.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value
            
            # If not in cache, call the function
            result = await func(*args, **kwargs)
            
            # Store result in cache
            cache_service.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {cache_key}")
            
            return result
        
        return wrapper
    
    return decorator 