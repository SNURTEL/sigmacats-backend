from sqlalchemy.sql import text
from sqlalchemy.orm import Session

from app.db.session import engine
from app.util.log import get_logger

# models HAVE to be imported beforehand for SQLModel.metadata.create_all to work
from app.models import *  # noqa: F401,F403
from app.initial_data import initial_data


logger = get_logger()


def create_index_sequences() -> None:
    # Oracle does not support autoincrement and hence we cannot fully trust SQLModel with index generation
    with engine.connect() as connection:
        with open("app/sql/create_id_sequences.sql", mode='r') as fp:
            with connection.begin():
                for stmt in fp.readlines():
                    connection.execute(text(stmt))


def create_triggers() -> None:
    with engine.connect() as connection:
        with open("app/sql/create_triggers.sql", mode='r') as fp:
            with connection.begin():
                for stmt in fp.read().split("\n\n"):
                    connection.execute(text(stmt
                                            .replace("\n", " ")
                                            # ":" has to be escaped to ":new" won't be treated as bind parameter
                                            .replace(":", "\\:")))


def insert_initial_data() -> None:
    with engine.connect() as connection:
        with connection.begin():
            if connection.execute(text(
                """
                select sum(SEGMENT_CREATED = TRUE)
                from ALL_TABLES 
                where owner ='USER1' and TABLE_NAME NOT LIKE 'ALEMBIC_VERSION'
                """
            )).first()[0]:
                logger.info("SKIPPING inserting initial data - DB not empty")
                return

            db = Session(bind=connection)
            db.add_all(initial_data)
            db.commit()


def main() -> None:
    """
    Runs all Oracle-specific DDL commands that cannot be invoked from Alembic; insert initial table contents
    """
    logger.info("Creating id sequences for DB")
    create_index_sequences()
    logger.info("Creating triggers")
    create_triggers()
    logger.info("Inserting initial data")
    insert_initial_data()
    logger.info("Done setting up backend!")


if __name__ == "__main__":
    main()
