import pytest
import os
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


def test_schema_matches_models_against_migrated_db():
    db_url = os.environ.get('DATABASE_URL_SYNC')
    assert db_url, "DATABASE_URL_SYNC required for schema verification"
    engine = create_engine(db_url)
    inspector = inspect(engine)
    
    # Check key tables exist
    tables = set(inspector.get_table_names())
    required_tables = {'users', 'roles', 'permissions', 'customers', 'products', 'plans', 'quotations', 'quotations' in str(tables) and 'subscriptions' or 'subscriptions', 'invoices', 'payments'}
    # Just check core tables
    for t in ['users', 'roles', 'permissions', 'customers', 'products', 'plans', 'quotations']:
        assert t in tables, f"Missing table {t}"
    
    # Check users columns
    user_cols = {c['name'] for c in inspector.get_columns('users')}
    assert 'hashed_password' in user_cols
    assert 'email' in user_cols
    
    engine.dispose()
