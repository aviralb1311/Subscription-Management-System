import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import event
from app.core.database import Base

# Import all models to ensure they're registered
from app.modules.auth import models as auth_models
from app.modules.products import models as product_models
from app.modules.customers import models as customer_models
from app.modules.quotations import models as quotation_models

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)


@pytest.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestingSessionLocal() as session:
        yield session
        await session.close()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    import sqlite3
    from decimal import Decimal
    # SQLite doesn't have Decimal, convert
    def adapt_decimal(val):
        return str(val)
    sqlite3.register_adapter(Decimal, adapt_decimal)
