# We need to load the environment variables for tests
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env.test", override=True)

import pytest
import pathlib
# We need the logging to write out the log info for information
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from alembic import command
from fastapi.testclient import TestClient
from alembic.config import Config
# We need to create the engine and the Session for tests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app    # import app


from app.core.config import settings    # Before we load the new env, the DB URL should be for test one.
from tests.utils import create_user_helper, login_helper, TEST_PASSWORD
from app.api.deps import get_db


# Check for DB name, make sure we will not touch the dev DB
def _assert_db_url(url: str) -> None:
    if not url:
        raise RuntimeError("Database URL is empty")

    if "stm_db_test" not in url:
        raise RuntimeError(f"Test can not be done on non-test DB! DB: {url.split("/")[-1].strip().lower()}")


_assert_db_url(settings.DATABASE_URL)
logger.info(f"Database: {settings.DATABASE_URL.split("/")[-1]}")    # double check for the name of the test DB
test_engine = create_engine(settings.DATABASE_URL)      # if we use the right DB for test, create the engine

TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)   # create the Session for test

## Fixtures
# The test DB migration should be here
@pytest.fixture(scope="session", autouse=True)
def apply_migration_for_test_db():
    path_alembic_ini = pathlib.Path("alembic.ini").absolute()
    alembic_cfg = Config(path_alembic_ini)     # build the Alembic Config
    _assert_db_url(settings.DATABASE_URL)  # safety guard
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)  # set the sqlalchemy.url to the url from env.test (settings.DATABASE_URL)
    logger.info("Applying migrations to: stm_db_test")
    command.upgrade(alembic_cfg, "head")    # call upgrade
    yield
    command.downgrade(alembic_cfg, "base")  # call downgrade

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def user_a(client):
    user_a = create_user_helper(client)
    token_a = login_helper(client, user_a["email"], TEST_PASSWORD)
    headers_a = {"Authorization": f"Bearer {token_a['access_token']}"}
    return {"email":user_a["email"], "token":token_a["access_token"], "headers": headers_a}

@pytest.fixture
def user_b(client):
    user_b = create_user_helper(client)
    token_b = login_helper(client, user_b["email"], TEST_PASSWORD)
    headers_b = {"Authorization": f"Bearer {token_b['access_token']}"}
    return {"email":user_b["email"], "token":token_b["access_token"], "headers":headers_b}



## We will override the get_db() as we need to use the test DB not the dev DB
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db  # This line will override the methode for get_db() for the app
