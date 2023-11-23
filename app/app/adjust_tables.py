from sqlalchemy.sql import text

from app.db.session import engine
from app.util.log import get_logger

# models HAVE to be imported beforehand for SQLModel.metadata.create_all to work
from app.models import *  # noqa: F401,F403


logger = get_logger()


def create_index_sequences() -> None:
    # Oracle does not support autoincrement and hence we cannot fully trust SQLModel with index generation
    with engine.connect() as connection:
        with open("app/sql/create_index_sequences.sql", mode='r') as fp:
            with connection.begin():
                for stmt in fp.readlines():
                    connection.execute(text(stmt))


def main() -> None:
    logger.info("Creating index sequences for DB")
    # create_index_sequences()
    logger.info("Done setting up backend!")


if __name__ == "__main__":
    main()
