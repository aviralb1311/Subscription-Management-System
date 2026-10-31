from logging.config import fileConfig
import os
import sys
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import all models to ensure they're registered
from app.core.database import Base
from app.core.config import settings
from app.modules.auth import models as auth_models
from app.modules.products import models as product_models
from app.modules.customers import models as customer_models
from app.modules.quotations import models as quotation_models
from app.modules.subscriptions import models as subscriptions_models
from app.modules.invoices import models as invoices_models
from app.modules.payments import models as payments_models

# this is the Alembic Config object
config = context.config

# Use DATABASE_URL_SYNC from environment/config
db_url = settings.database_url_sync
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
