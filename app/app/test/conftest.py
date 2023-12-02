from typing import Generator, Any

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from sqlalchemy.engine import Engine
from sqlalchemy.sql import text

from app.db.session import create_db_engine, get_db
from app.main import app

from .fixtures import *


class TestIdSequences:
    """
    Temporarily disables caching on id sequences and replace them with mock ones, all starting from 100001. This has
    to be done because:
     - We want to be sure which id's will be assigned to objects created duting tests
     - ROLLBACK does not affect sequences, and we don't want to create mess in the DB
     - Performing COMMIT or ROLLBACK creates a gap equal to cache size in a sequence - each test session would create
     massive gaps (20 for every test ran)
    """
    def __init__(self, engine: Engine):
        self._engine = engine

    def _execute_sql(self, filename: str) -> None:
        with self._engine.connect() as connection:
            with open(filename, mode='r') as fp:
                with connection.begin():
                    for stmt in fp.readlines():
                        connection.execute(text(stmt))

    def __enter__(self):
        self._execute_sql("app/sql/disable_id_sequence_caching.sql")
        self._execute_sql("app/sql/create_test_id_sequences.sql")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._execute_sql("app/sql/enable_id_sequence_caching.sql")
        self._execute_sql("app/sql/drop_test_id_sequences.sql")


@pytest.fixture(scope="session")
def db_engine() -> Generator[Engine, Any, None]:
    test_engine = create_db_engine(echo=False)

    yield test_engine


@pytest.fixture(scope="function")
def db(db_engine) -> Generator[Session, Any, None]:  # type: ignore[no-untyped-def]
    connection = db_engine.connect()

    with TestIdSequences(db_engine):
        connection.begin()
        db = Session(bind=connection)

        yield db

        db.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db) -> Generator[TestClient, Any, None]:  # type: ignore[no-untyped-def]
    app.dependency_overrides[get_db] = lambda: db

    with TestClient(app) as c:
        yield c
