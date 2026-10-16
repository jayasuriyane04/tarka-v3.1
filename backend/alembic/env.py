"""Alembic environment; DATABASE_URL comes from validated project settings."""
from alembic import context
from sqlalchemy import create_engine, pool

from app.config import settings
from app.db import Base

config = context.config
target_metadata = Base.metadata
# Commands may explicitly override the URL for offline SQL compilation/tests.
database_url = config.attributes.get('database_url', settings.database_url)


def run_migrations_offline():
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = create_engine(database_url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
