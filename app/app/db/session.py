from typing import Generator, Any

from sqlalchemy.orm import sessionmaker, Session

from app.core.config import create_db_engine, create_db_engine_admin

engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

engine_admin = create_db_engine_admin()
SessionLocalAdmin = sessionmaker(autocommit=False, autoflush=False, bind=engine_admin)


def get_db() -> Generator[Session, Any, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
