from typing import Generator, Any

from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from app.core.config import create_db_engine, create_db_engine_admin

# ATTENTION PLEASE! SQLModel does not include `sessionmaker`, yet we want to use SQLModel's Session class (it is
# different from SQLAlchemy's session!) for proper ORM handling. We can hack the sessionmaker by passing the Session
# class as `class_` attribute
engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)  # type: ignore[type-var]

engine_admin = create_db_engine_admin()
SessionLocalAdmin = sessionmaker(autocommit=False, autoflush=False, bind=engine_admin,
                                 class_=Session)  # type: ignore[type-var]


def get_db() -> Generator[Session, Any, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
