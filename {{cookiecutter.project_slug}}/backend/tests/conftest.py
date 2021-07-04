from databases import Database
from typing import AsyncGenerator, Generator
import pytest
from fastapi.testclient import TestClient
from ..main import app
from pathlib import Path
from ..crud.deps import get_database, is_testing
from .. import config


async def get_database_override() -> AsyncGenerator[Database, None]:
    async with Database(config.test_db_url) as db:
        yield db


def is_testing_override() -> bool:
    return True


@pytest.fixture(scope="package")
def client() -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_database] = get_database_override
    app.dependency_overrides[is_testing] = is_testing_override
    with TestClient(app) as client:
        yield client

    db_file = Path("./test.db")
    if db_file.is_file():
        db_file.unlink()
