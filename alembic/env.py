from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from app.core.config import settings
from app.db.base import Base
import app.models

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# Check for the right DB and the mode
def safety_guard(url: str, mode: str) -> None:
    if not url or not mode:
        raise ValueError("DB URL or MODE not provided")
    if "stm_db_test" not in url and mode.translate({32:""}).lower() == "test":
        raise RuntimeError(f"Migration can not be done on non-test DB! DB: {url.split("/")[-1].translate({32:""}).lower()} or the MODE is wrong: {mode}.")
    if mode.translate({32:""}).lower() != "test" and "stm_db_test" in url:
        raise RuntimeError(f"You are not in test mode: {mode}, so you can't use the test DB: {url.split("/")[-1].translate({32:""}).lower()}.")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # safety guard
    safety_guard(settings.DATABASE_URL, settings.ENV)


    # url = settings.DATABASE_URL
    context.configure(
        # url=url,
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # Safety guard
    safety_guard(settings.DATABASE_URL, settings.ENV)

    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
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
