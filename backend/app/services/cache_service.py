import time
from typing import Dict, Any, Optional, Callable, Awaitable
import logging
import asyncio
from functools import wraps
import redis.asyncio as redis
import json
from app.config import settings

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
    if not settings.REDIS_ENABLED:
        return
        
    while True:
        try:
            # Perform cleanup tasks
            logger.debug("Running Redis cache cleanup task")
            # Implement cleanup logic here if needed
            
            # Wait for next cleanup interval
            await asyncio.sleep(3600)  # 1 hour
        except Exception as e:
            logger.error(f"Error in Redis cleanup task: {e}")
            await asyncio.sleep(60)  # Wait and retry on error


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
                if isinstance(v, dict):  # If v is a dictionary
                    # Convert the dictionary to a frozenset of its items
                    cache_key += f"{k}_{hash(frozenset(v.items()))}:"
                elif hasattr(v, "__dict__"):  # If v has a __dict__ attribute
                    # Hash the frozenset of the object's __dict__
                    cache_key += f"{k}_{hash(frozenset(v.__dict__.items()))}:"
                else:
                    # Otherwise, just hash the value
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

class RedisClient:
    """Redis client for caching operations.
    
    This class provides a Redis client for caching operations with methods for
    getting, setting, and deleting cache entries.
    """
    
    def __init__(self):
        """Initialize the Redis client."""
        self._redis = None
        self._initialized = False
        
    async def init(self) -> None:
        """Initialize the Redis connection."""
        if self._initialized:
            return
            
        try:
            if not settings.REDIS_ENABLED:
                logger.info("Redis is disabled, skipping initialization")
                return
                
            # Parse Redis URL or use connection details
            if settings.REDIS_URL:
                self._redis = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=settings.REDIS_MAX_CONNECTIONS
                )
            else:
                self._redis = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    username=settings.REDIS_USERNAME or None,
                    password=settings.REDIS_PASSWORD or None,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=settings.REDIS_MAX_CONNECTIONS
                )
                
            # Test connection
            await self._redis.ping()
            self._initialized = True
            logger.info("Redis client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {e}")
            self._redis = None
            
    async def close(self) -> None:
        """Close the Redis connection."""
        if self._redis:
            await self._redis.close()
            self._initialized = False
            logger.info("Redis connection closed")
            
    async def get(self, key: str) -> Any:
        """Get a value from the cache.
        
        Args:
            key: The cache key.
            
        Returns:
            The cached value or None if the key doesn't exist.
        """
        if not self._redis:
            return None
            
        try:
            value = await self._redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
            
    async def set(self, key: str, value: Any, expire: int = None) -> bool:
        """Set a value in the cache.
        
        Args:
            key: The cache key.
            value: The value to cache.
            expire: Optional expiration time in seconds.
            
        Returns:
            True if the value was set, False otherwise.
        """
        if not self._redis:
            return False
            
        try:
            expire = expire or settings.CACHE_EXPIRY_SECONDS
            serialized = json.dumps(value)
            await self._redis.set(key, serialized, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
            
    async def delete(self, key: str) -> bool:
        """Delete a key from the cache.
        
        Args:
            key: The cache key to delete.
            
        Returns:
            True if the key was deleted, False otherwise.
        """
        if not self._redis:
            return False
            
        try:
            await self._redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
            
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern.
        
        Args:
            pattern: The pattern to match.
            
        Returns:
            The number of keys deleted.
        """
        if not self._redis:
            return 0
            
        try:
            keys = await self._redis.keys(pattern)
            if keys:
                count = await self._redis.delete(*keys)
                return count
            return 0
        except Exception as e:
            logger.error(f"Error deleting keys matching pattern {pattern}: {e}")
            return 0
            
    async def exists(self, key: str) -> bool:
        """Check if a key exists in the cache.
        
        Args:
            key: The cache key.
            
        Returns:
            True if the key exists, False otherwise.
        """
        if not self._redis:
            return False
            
        try:
            return await self._redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking if key {key} exists: {e}")
            return False

# Create a singleton instance
redis_client = RedisClient() 