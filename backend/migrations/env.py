"""Alembic environment configuration for multi-database migrations"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Import your models here
from services.career.infrastructure.persistence.models import Base as CareerBase
from services.skills.infrastructure.persistence.models import Base as SkillsBase
from services.user.infrastructure.persistence.models import Base as UserBase
from services.assessment.infrastructure.persistence.models import Base as AssessmentBase
from services.matching.infrastructure.persistence.models import Base as MatchingBase

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Database to Base mapping
DATABASE_MODELS = {
    "career": CareerBase,
    "skills": SkillsBase,
    "user": UserBase,
    "assessment": AssessmentBase,
    "matching": MatchingBase,
}


def get_url(db_name: str):
    """Get database URL from environment or config"""
    # Try environment variable first
    env_var = f"{db_name.upper()}_DATABASE_URL"
    url = os.getenv(env_var)
    
    if url:
        return url
    
    # Fall back to config file
    return config.get_section_option(db_name, "sqlalchemy.url")


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    # Get database name from command line
    db_name = context.get_x_argument(as_dictionary=True).get("db")
    
    if not db_name:
        raise ValueError("Please specify database with -x db=<name>")
    
    if db_name not in DATABASE_MODELS:
        raise ValueError(f"Unknown database: {db_name}")
    
    url = get_url(db_name)
    context.configure(
        url=url,
        target_metadata=DATABASE_MODELS[db_name].metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table=f"alembic_version_{db_name}",
    )
    
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Run migrations with connection"""
    db_name = context.get_x_argument(as_dictionary=True).get("db")
    
    if not db_name:
        raise ValueError("Please specify database with -x db=<name>")
    
    if db_name not in DATABASE_MODELS:
        raise ValueError(f"Unknown database: {db_name}")
    
    context.configure(
        connection=connection,
        target_metadata=DATABASE_MODELS[db_name].metadata,
        version_table=f"alembic_version_{db_name}",
    )
    
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode with async support."""
    db_name = context.get_x_argument(as_dictionary=True).get("db")
    
    if not db_name:
        raise ValueError("Please specify database with -x db=<name>")
    
    if db_name not in DATABASE_MODELS:
        raise ValueError(f"Unknown database: {db_name}")
    
    url = get_url(db_name)
    
    # Create async engine
    connectable = create_async_engine(
        url,
        poolclass=pool.NullPool,
        future=True,
    )
    
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())