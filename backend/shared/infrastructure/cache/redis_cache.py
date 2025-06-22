"""Redis cache implementation for caching layer."""

import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta
import redis.asyncio as redis
from redis.asyncio.client import Redis
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based caching service with async support."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._redis: Optional[Redis] = None
    
    async def connect(self):
        """Connect to Redis."""
        if not self._redis:
            self._redis = await redis.from_url(self.redis_url, decode_responses=False)
            logger.info("Connected to Redis cache")
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self._redis:
            await self._redis.close()
            self._redis = None
            logger.info("Disconnected from Redis cache")
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        try:
            if not self._redis:
                await self.connect()
            
            value = await self._redis.get(key)
            if value is None:
                return default
            
            # Try to deserialize as JSON first, then pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return pickle.loads(value)
                
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return default
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set value in cache with optional TTL."""
        try:
            if not self._redis:
                await self.connect()
            
            # Serialize value
            try:
                serialized = json.dumps(value)
            except (TypeError, ValueError):
                serialized = pickle.dumps(value)
            
            # Convert timedelta to seconds if needed
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            
            # Set with or without TTL
            if ttl:
                await self._redis.setex(key, ttl, serialized)
            else:
                await self._redis.set(key, serialized)
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            if not self._redis:
                await self.connect()
            
            result = await self._redis.delete(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            if not self._redis:
                await self.connect()
            
            return await self._redis.exists(key) > 0
            
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        try:
            if not self._redis:
                await self.connect()
            
            # Find all keys matching pattern
            keys = []
            async for key in self._redis.scan_iter(match=pattern):
                keys.append(key)
            
            # Delete keys if found
            if keys:
                return await self._redis.delete(*keys)
            return 0
            
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
            return 0
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a counter in cache."""
        try:
            if not self._redis:
                await self.connect()
            
            return await self._redis.incrby(key, amount)
            
        except Exception as e:
            logger.error(f"Error incrementing cache key {key}: {e}")
            return None
    
    async def get_ttl(self, key: str) -> Optional[int]:
        """Get TTL (time to live) for a key in seconds."""
        try:
            if not self._redis:
                await self.connect()
            
            ttl = await self._redis.ttl(key)
            return ttl if ttl >= 0 else None
            
        except Exception as e:
            logger.error(f"Error getting TTL for key {key}: {e}")
            return None
    
    async def set_many(self, mapping: dict, ttl: Optional[int] = None) -> bool:
        """Set multiple key-value pairs at once."""
        try:
            if not self._redis:
                await self.connect()
            
            # Serialize all values
            serialized_mapping = {}
            for key, value in mapping.items():
                try:
                    serialized_mapping[key] = json.dumps(value)
                except (TypeError, ValueError):
                    serialized_mapping[key] = pickle.dumps(value)
            
            # Use pipeline for atomic operation
            async with self._redis.pipeline() as pipe:
                for key, value in serialized_mapping.items():
                    if ttl:
                        pipe.setex(key, ttl, value)
                    else:
                        pipe.set(key, value)
                await pipe.execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting multiple cache keys: {e}")
            return False
    
    async def get_many(self, keys: list) -> dict:
        """Get multiple values at once."""
        try:
            if not self._redis:
                await self.connect()
            
            values = await self._redis.mget(keys)
            result = {}
            
            for key, value in zip(keys, values):
                if value is not None:
                    try:
                        result[key] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        result[key] = pickle.loads(value)
                else:
                    result[key] = None
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting multiple cache keys: {e}")
            return {key: None for key in keys}


# Singleton instance
_cache_service: Optional[CacheService] = None


def get_cache_service(redis_url: str = "redis://localhost:6379") -> CacheService:
    """Get or create cache service singleton."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService(redis_url)
    return _cache_service


# Cache key generators for different services
class CacheKeys:
    """Cache key generators for consistent key naming."""
    
    @staticmethod
    def career_recommendation(user_id: str) -> str:
        return f"career:recommendations:{user_id}"
    
    @staticmethod
    def skill_requirements(career_id: str) -> str:
        return f"career:skills:{career_id}"
    
    @staticmethod
    def user_profile(user_id: str) -> str:
        return f"user:profile:{user_id}"
    
    @staticmethod
    def assessment_result(user_id: str, test_type: str) -> str:
        return f"assessment:{test_type}:{user_id}"
    
    @staticmethod
    def skill_vector(skill_id: str) -> str:
        return f"skill:vector:{skill_id}"
    
    @staticmethod
    def matching_result(user_id: str, match_type: str) -> str:
        return f"match:{match_type}:{user_id}"