import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db, async_engine, AsyncSessionLocal, Base


@pytest.mark.asyncio
async def test_get_db_yields_session():
    gen = get_db()
    session = await gen.__anext__()
    assert isinstance(session, AsyncSession)
    await gen.aclose()


def test_async_engine_exists():
    assert async_engine is not None


def test_session_local_exists():
    assert AsyncSessionLocal is not None


def test_base_metadata_has_tables():
    # Just ensure Base.metadata is accessible
    assert Base.metadata is not None
