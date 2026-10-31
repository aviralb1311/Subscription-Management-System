import pytest
from app.core.database import Base
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, MetaData
from app.core.database import async_engine


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
