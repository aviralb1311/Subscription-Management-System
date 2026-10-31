import pytest
from app.core.database import Base
from alembic.config import Config
from alembic.script import ScriptDirectory


def test_alembic_heads_single():
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)
    heads = script.get_heads()
    assert len(heads) == 1


def test_base_has_metadata():
    assert Base.metadata is not None
