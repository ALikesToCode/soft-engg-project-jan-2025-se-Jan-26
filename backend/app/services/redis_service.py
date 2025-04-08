import redis.asyncio as redis
import logging
from app.config import settings

logger = logging.getLogger(__name__)

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
            
    async def get(self, key: str):
        """Get a value from the cache.
        
        Args:
            key: The cache key.
            
        Returns:
            The cached value or None if the key doesn't exist.
        """
        if not self._initialized or not self._redis:
            return None
            
        try:
            return await self._redis.get(key)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
            
    async def set(self, key: str, value: str, ex: int = None):
        """Set a value in the cache.
        
        Args:
            key: The cache key.
            value: The value to store.
            ex: Optional expiration time in seconds.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self._initialized or not self._redis:
            return False
            
        try:
            return await self._redis.set(key, value, ex=ex)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
            
    async def delete(self, key: str):
        """Delete a value from the cache.
        
        Args:
            key: The cache key to delete.
            
        Returns:
            Number of keys deleted.
        """
        if not self._initialized or not self._redis:
            return 0
            
        try:
            return await self._redis.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return 0
            
    async def keys(self, pattern: str):
        """Get all keys matching a pattern.
        
        Args:
            pattern: Pattern to match (e.g., "user_*")
            
        Returns:
            List of matching keys.
        """
        if not self._initialized or not self._redis:
            return []
            
        try:
            return await self._redis.keys(pattern)
        except Exception as e:
            logger.error(f"Redis keys error: {e}")
            return []
            
# Create a singleton instance
redis_client = RedisClient() 