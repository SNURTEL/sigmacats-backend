import contextlib
import os
import asyncio

from sqlalchemy.sql import text
from sqlalchemy.orm import Session

from app.db.session import engine
from app.util.log import get_logger

# models HAVE to be imported beforehand for SQLModel.metadata.create_all to work
from app.models import *  # noqa: F401,F403
from app.initial_data import create_initial_data
from app.core.users import get_user_manager, get_user_db, get_db
from app.models.account import AccountCreate, AccountType, Account

logger = get_logger()

get_session_context = contextlib.contextmanager(get_db)
get_user_db_context = contextlib.contextmanager(get_user_db)
get_user_manager_context = contextlib.contextmanager(get_user_manager)


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


def insert_initial_users() -> list[Account, Account, Account] | None:
    with engine.connect() as connection:
        with connection.begin():
            if connection.execute(text(
                    """
                    select sum(SEGMENT_CREATED = TRUE)
                    from ALL_TABLES
                    where owner ='USER1' and TABLE_NAME NOT LIKE 'ALEMBIC_VERSION'
                    """
            )).first()[0]:  # type: ignore[index]
                logger.info("SKIPPING inserting initial users - DB not empty")
                return

    rider_create = AccountCreate(
        type=AccountType.rider,
        username="default_rider",
        name="Default",
        surname="Rider",
        email="rider@default.sigma",
        password=os.environ.get("FASTAPI_DEFAULT_RIDER_PASSWORD", "rider123")
    )
    coordinator_create = AccountCreate(
        type=AccountType.coordinator,
        username="default_coordinator",
        name="Default",
        surname="Coordinator",
        email="coordinator@default.sigma",
        password=os.environ.get("FASTAPI_DEFAULT_COORDINATOR_PASSWORD", "coordinator123"),
        phone_number="+4812456789"
    )
    admin_create = AccountCreate(
        is_superuser=True,
        type=AccountType.admin,
        username="default_admin",
        name="Default",
        surname="Admin",
        email="admin@default.sigma",
        password=os.environ.get("FASTAPI_DEFAULT_ADMIN_PASSWORD", "admin123")
    )

    async def create_account(account_create: AccountCreate) -> Account:
        with get_session_context() as session:
            with get_user_db_context(session) as user_db:
                with get_user_manager_context(user_db) as user_manager:
                    return await user_manager.create(
                        account_create
                    )

    return [asyncio.run(create_account(ac)) for ac in (rider_create, coordinator_create, admin_create)]


def insert_initial_data(
        rider_account: Account,
        coordinator_account: Account,
        admin_account: Account,
) -> None:
    with engine.connect() as connection:
        with connection.begin():
            if connection.execute(text(
                    """
                    select sum(SEGMENT_CREATED = TRUE)
                    from ALL_TABLES
                    where owner ='USER1' and TABLE_NAME NOT LIKE 'ALEMBIC_VERSION'
                    and TABLE_NAME NOT LIKE 'ACCOUNT'
                    and TABLE_NAME NOT LIKE 'RIDER'
                    and TABLE_NAME NOT LIKE 'COORDINATOR'
                    and TABLE_NAME NOT LIKE 'ADMIN'
                    
                    """
            )).first()[0]:  # type: ignore[index]
                logger.info("SKIPPING inserting initial data - DB not empty")
                return

    initial_data = create_initial_data(
        rider_account,
        coordinator_account,
        admin_account
    )

    with engine.connect() as connection:
        for item in initial_data:
            with connection.begin():
                db = Session(bind=connection)
                db.add(item)
                db.commit()


def main() -> None:
    """
    Runs all Oracle-specific DDL commands that cannot be invoked from Alembic; insert initial table contents
    """
    logger.info("Creating id sequences for DB")
    create_index_sequences()
    logger.info("Creating triggers")
    create_triggers()
    logger.info("Inserting initial users")
    users = insert_initial_users()
    logger.info("Inserting initial data")
    insert_initial_data(*users)
    logger.info("Done setting up backend!")


if __name__ == "__main__":
    main()
