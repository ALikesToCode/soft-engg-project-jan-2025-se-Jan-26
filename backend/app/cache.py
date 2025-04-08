import redis.asyncio as redis
import logging
from app.config import settings
import asyncio
import pickle
import time
import json
from typing import Any, Dict, List, Optional, Set, Tuple, TypeVar, Union, cast

# Configure logger for this module
logger = logging.getLogger(__name__)

class RedisClient:
    """
    Redis client wrapper for caching operations
    
    This class provides an interface to interact with Redis for caching, 
    with methods for getting, setting, and deleting cache entries.
    """
    def __init__(self):
        self.redis = None
        self.enabled = settings.REDIS_ENABLED
    
    async def init(self):
        """Initialize Redis connection pool"""
        if not self.enabled:
            logger.info("Redis caching is disabled")
            return
        
        try:
            self.redis = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
            )
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            self.enabled = False
    
    async def get(self, key: str):
        """
        Get a value from cache
        
        Args:
            key: Cache key
        
        Returns:
            The cached value or None if not found
        """
        if not self.enabled or not self.redis:
            return None
        
        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            return None
    
    async def set(self, key: str, value: str):
        """
        Set a value in cache without expiration
        
        Args:
            key: Cache key
            value: Value to cache
        
        Returns:
            bool: Success status
        """
        if not self.enabled or not self.redis:
            return False
        
        try:
            return await self.redis.set(key, value)
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
            return False
    
    async def setex(self, key: str, expires: int, value: str):
        """
        Set a value in cache with expiration
        
        Args:
            key: Cache key
            expires: Expiration time in seconds
            value: Value to cache
        
        Returns:
            bool: Success status
        """
        if not self.enabled or not self.redis:
            return False
        
        try:
            return await self.redis.setex(key, expires, value)
        except Exception as e:
            logger.error(f"Redis setex error: {str(e)}")
            return False
    
    async def delete(self, key: str):
        """
        Delete a value from cache
        
        Args:
            key: Cache key to delete
        
        Returns:
            Number of keys deleted
        """
        if not self.enabled or not self.redis:
            return 0
        
        try:
            return await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {str(e)}")
            return 0
    
    async def delete_pattern(self, pattern: str):
        """
        Delete all keys matching a pattern
        
        Args:
            pattern: Pattern to match (e.g., "user_*")
        
        Returns:
            Number of keys deleted
        """
        if not self.enabled or not self.redis:
            return 0
        
        try:
            # Get all keys matching the pattern
            keys = await self.redis.keys(pattern)
            
            if not keys:
                return 0
            
            # Delete all matched keys
            return await self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Redis delete_pattern error: {str(e)}")
            return 0
    
    async def close(self):
        """Close Redis connection"""
        if self.enabled and self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")

# Create a singleton instance
redis_client = RedisClient() 