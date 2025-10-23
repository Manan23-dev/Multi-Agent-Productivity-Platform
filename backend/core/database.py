"""
Database configuration and models for FlowAgent
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from backend.core.config import get_settings

settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.debug,
    future=True
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Create base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()

async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        # Import all models here to ensure they're registered
        from backend.models import agent, workflow, task, user
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
