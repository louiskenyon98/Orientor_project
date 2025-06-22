"""
Dependency Injection for Career Service

This module provides dependency injection configuration for the Career service,
managing the creation and lifecycle of repositories, use cases, and services.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from functools import lru_cache
import os

from backend.shared.infrastructure.database import get_db
from backend.services.career.domain.repositories.career_repository import CareerRepository
from backend.services.career.infrastructure.persistence.sqlalchemy_career_repo import SQLAlchemyCareerRepository
from backend.services.career.infrastructure.persistence.career_read_repo import SQLAlchemyCareerReadRepository
from backend.services.career.application.use_cases.recommend_career import RecommendCareerUseCase
from backend.services.career.application.services.career_service import CareerService
from backend.services.career.infrastructure.external.openai_adapter import OpenAILLMService
from backend.shared.infrastructure.cache.redis_cache import RedisCacheService


# Repository dependencies
async def get_career_repository(
    session: AsyncSession = Depends(get_db)
) -> CareerRepository:
    """Get Career repository instance"""
    return SQLAlchemyCareerRepository(session)


async def get_career_read_repository(
    session: AsyncSession = Depends(get_db)
) -> SQLAlchemyCareerReadRepository:
    """Get Career read repository instance"""
    return SQLAlchemyCareerReadRepository(session)


# External service dependencies
@lru_cache()
def get_cache_service() -> Optional[RedisCacheService]:
    """Get cache service instance (singleton)"""
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        return RedisCacheService(redis_url)
    return None


@lru_cache()
def get_llm_service() -> Optional[OpenAILLMService]:
    """Get LLM service instance (singleton)"""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        return OpenAILLMService(api_key=openai_api_key)
    return None


# Use case dependencies
async def get_recommend_career_use_case(
    career_repository: CareerRepository = Depends(get_career_repository),
    career_read_repository: SQLAlchemyCareerReadRepository = Depends(get_career_read_repository),
    cache_service: Optional[RedisCacheService] = Depends(get_cache_service),
    llm_service: Optional[OpenAILLMService] = Depends(get_llm_service)
) -> RecommendCareerUseCase:
    """Get RecommendCareer use case instance"""
    return RecommendCareerUseCase(
        career_repository=career_repository,
        career_read_repository=career_read_repository,
        cache_service=cache_service,
        llm_service=llm_service
    )


# Service dependencies
async def get_career_service(
    career_repository: CareerRepository = Depends(get_career_repository),
    recommend_career_use_case: RecommendCareerUseCase = Depends(get_recommend_career_use_case)
) -> CareerService:
    """Get Career service instance"""
    # Event publisher would be injected here if available
    return CareerService(
        career_repository=career_repository,
        recommend_career_use_case=recommend_career_use_case,
        event_publisher=None  # Could inject RabbitMQ/Kafka publisher here
    )


# Configuration settings
class Settings:
    """Service configuration settings"""
    
    service_name: str = "career-service"
    service_version: str = "1.0.0"
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost/orientor")
    
    # Cache
    redis_url: Optional[str] = os.getenv("REDIS_URL")
    cache_ttl: int = int(os.getenv("CACHE_TTL", "3600"))
    
    # External services
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Service discovery
    service_registry_url: Optional[str] = os.getenv("SERVICE_REGISTRY_URL")
    
    # Monitoring
    metrics_enabled: bool = os.getenv("METRICS_ENABLED", "true").lower() == "true"
    tracing_enabled: bool = os.getenv("TRACING_ENABLED", "false").lower() == "true"
    
    # Feature flags
    use_cache: bool = os.getenv("USE_CACHE", "true").lower() == "true"
    use_llm_reasoning: bool = os.getenv("USE_LLM_REASONING", "true").lower() == "true"


@lru_cache()
def get_settings() -> Settings:
    """Get service settings (singleton)"""
    return Settings()