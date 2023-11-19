from typing import Generator, Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine


from app.db.session import engine, get_db
from app.main import app


@pytest.fixture(scope="session")
def db_engine() -> Generator[Engine, Any, None]:
    test_engine = engine
    # not necessary if using backend_pre_start
    # SQLModel.metadata.create_all(bind=engine)
    yield test_engine


@pytest.fixture(scope="function")
def db(db_engine) -> Generator[Session, Any, None]:  # type: ignore[no-untyped-def]
    connection = db_engine.connect()

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
