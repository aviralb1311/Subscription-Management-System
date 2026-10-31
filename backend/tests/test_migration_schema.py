import pytest
import os
import subprocess
import tempfile
from app.core.database import Base
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect


def test_alembic_heads_single():
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)
    heads = script.get_heads()
    assert len(heads) == 1


def test_base_metadata_accessible():
    assert Base.metadata is not None


def test_auth_models_match_expected():
    from app.modules.auth.models import User, Role
    assert hasattr(User, 'hashed_password')
    assert hasattr(User, 'full_name')
    assert hasattr(Role, 'permissions')


def test_products_models_match_expected():
    from app.modules.products.models import Product, ProductVariant
    assert hasattr(Product, 'price_adjustment')
    assert hasattr(ProductVariant, 'price_adjustment')


def test_migration_config_uses_sync_url():
    from app.core.config import settings
    assert settings.database_url_sync is not None


@pytest.mark.skipif(True, reason="Local PostgreSQL not configured with passwordless access; skipped - validation outstanding")
def test_migrations_fresh_postgres():
    pass


@pytest.mark.skipif(True, reason="Local PostgreSQL not configured with passwordless access; skipped - validation outstanding")
def test_migrations_upgrade_from_previous_head():
    pass
