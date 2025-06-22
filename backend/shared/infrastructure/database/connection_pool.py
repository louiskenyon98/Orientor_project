"""Database connection pooling with SQLAlchemy"""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    AsyncSession, 
    AsyncEngine,
    async_sessionmaker
)
from sqlalchemy.pool import NullPool, QueuePool, StaticPool
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

Base = declarative_base()


@dataclass
class PoolConfig:
    """Database pool configuration"""
    # Connection string
    database_url: str
    
    # Pool settings
    pool_size: int = 20
    max_overflow: int = 10
    pool_timeout: float = 30.0
    pool_recycle: int = 3600  # Recycle connections after 1 hour
    pool_pre_ping: bool = True  # Test connections before using
    
    # Engine settings
    echo: bool = False
    echo_pool: bool = False
    future: bool = True
    
    # Pool class
    poolclass: Optional[type] = None
    
    def get_pool_class(self):
        """Get appropriate pool class based on database URL"""
        if self.poolclass:
            return self.poolclass
        
        if "sqlite" in self.database_url:
            # SQLite doesn't support concurrent connections well
            return StaticPool if ":memory:" in self.database_url else NullPool
        else:
            # PostgreSQL, MySQL, etc.
            return QueuePool


class DatabasePool:
    """Manages database connection pooling"""
    
    def __init__(self, config: PoolConfig):
        self.config = config
        self._engine: Optional[AsyncEngine] = None
        self._sessionmaker: Optional[async_sessionmaker] = None
    
    async def initialize(self):
        """Initialize the connection pool"""
        if self._engine is not None:
            return
        
        pool_class = self.config.get_pool_class()
        
        # Create engine with connection pooling
        engine_kwargs = {
            "echo": self.config.echo,
            "echo_pool": self.config.echo_pool,
            "future": self.config.future,
            "poolclass": pool_class,
        }
        
        # Add pool-specific settings for QueuePool
        if pool_class == QueuePool:
            engine_kwargs.update({
                "pool_size": self.config.pool_size,
                "max_overflow": self.config.max_overflow,
                "pool_timeout": self.config.pool_timeout,
                "pool_recycle": self.config.pool_recycle,
                "pool_pre_ping": self.config.pool_pre_ping,
            })
        
        self._engine = create_async_engine(
            self.config.database_url,
            **engine_kwargs
        )
        
        # Create session factory
        self._sessionmaker = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        logger.info(
            f"Database pool initialized: "
            f"pool_size={self.config.pool_size}, "
            f"max_overflow={self.config.max_overflow}"
        )
    
    async def close(self):
        """Close all connections in the pool"""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None
            logger.info("Database pool closed")
    
    @asynccontextmanager
    async def get_session(self):
        """Get a database session from the pool"""
        if not self._sessionmaker:
            await self.initialize()
        
        async with self._sessionmaker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    @property
    def engine(self) -> AsyncEngine:
        """Get the underlying engine"""
        if not self._engine:
            raise RuntimeError("Database pool not initialized")
        return self._engine
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database connection health"""
        try:
            async with self.get_session() as session:
                # Simple query to test connection
                result = await session.execute("SELECT 1")
                result.scalar()
            
            # Get pool statistics
            pool = self._engine.pool
            return {
                "status": "healthy",
                "size": pool.size() if hasattr(pool, 'size') else None,
                "checked_in": pool.checkedin() if hasattr(pool, 'checkedin') else None,
                "overflow": pool.overflow() if hasattr(pool, 'overflow') else None,
                "total": pool.total() if hasattr(pool, 'total') else None,
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }


class MultiDatabasePool:
    """Manages multiple database pools for microservices"""
    
    def __init__(self):
        self.pools: Dict[str, DatabasePool] = {}
    
    def add_pool(self, name: str, config: PoolConfig):
        """Add a named database pool"""
        if name in self.pools:
            raise ValueError(f"Pool {name} already exists")
        
        self.pools[name] = DatabasePool(config)
    
    async def initialize_all(self):
        """Initialize all pools"""
        for name, pool in self.pools.items():
            await pool.initialize()
            logger.info(f"Initialized pool: {name}")
    
    async def close_all(self):
        """Close all pools"""
        for name, pool in self.pools.items():
            await pool.close()
            logger.info(f"Closed pool: {name}")
    
    def get_pool(self, name: str) -> DatabasePool:
        """Get a specific pool"""
        if name not in self.pools:
            raise ValueError(f"Pool {name} not found")
        return self.pools[name]
    
    @asynccontextmanager
    async def get_session(self, pool_name: str):
        """Get a session from a specific pool"""
        pool = self.get_pool(pool_name)
        async with pool.get_session() as session:
            yield session
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all pools"""
        results = {}
        for name, pool in self.pools.items():
            results[name] = await pool.health_check()
        return results


# Service-specific pool configurations
def create_service_pools() -> MultiDatabasePool:
    """Create database pools for all services"""
    multi_pool = MultiDatabasePool()
    
    # Career Service Pool
    multi_pool.add_pool(
        "career",
        PoolConfig(
            database_url="postgresql+asyncpg://user:pass@localhost/career_db",
            pool_size=20,
            max_overflow=10
        )
    )
    
    # Skills Service Pool
    multi_pool.add_pool(
        "skills",
        PoolConfig(
            database_url="postgresql+asyncpg://user:pass@localhost/skills_db",
            pool_size=15,
            max_overflow=5
        )
    )
    
    # User Service Pool
    multi_pool.add_pool(
        "user",
        PoolConfig(
            database_url="postgresql+asyncpg://user:pass@localhost/user_db",
            pool_size=30,  # Higher pool size for user service
            max_overflow=15
        )
    )
    
    # Assessment Service Pool
    multi_pool.add_pool(
        "assessment",
        PoolConfig(
            database_url="postgresql+asyncpg://user:pass@localhost/assessment_db",
            pool_size=10,
            max_overflow=5
        )
    )
    
    # Matching Service Pool
    multi_pool.add_pool(
        "matching",
        PoolConfig(
            database_url="postgresql+asyncpg://user:pass@localhost/matching_db",
            pool_size=25,
            max_overflow=10
        )
    )
    
    return multi_pool


# Global pool manager
pool_manager = create_service_pools()


# Dependency injection for FastAPI
async def get_db_session(service_name: str):
    """Dependency to get database session"""
    async with pool_manager.get_session(service_name) as session:
        yield session