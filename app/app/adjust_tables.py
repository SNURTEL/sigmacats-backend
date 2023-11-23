from sqlalchemy.sql import text

from app.db.session import engine
from app.util.log import get_logger

# models HAVE to be imported beforehand for SQLModel.metadata.create_all to work
from app.models import *  # noqa: F401,F403


logger = get_logger()


def create_index_sequences() -> None:
    # Oracle does not support autoincrement and hence we cannot fully trust SQLModel with index generation
    with engine.connect() as connection:
        with open("app/sql/create_id_sequences.sql", mode='r') as fp:
            with connection.begin():
                for stmt in fp.readlines():
                    connection.execute(text(stmt))


def main() -> None:
    """
    Runs all Oracle-specific DDL commands that cannot be invoked from Alembic
    """
    logger.info("Creating id sequences for DB")
    create_index_sequences()
    logger.info("Done setting up backend!")


if __name__ == "__main__":
    main()
