import logging
import os
from app.util.log import get_logger
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed, Retrying

logger = get_logger()

max_tries = int(os.environ.get("FASTAPI_DB_CONNECTION_TIMEOUT", default=120))
wait_seconds = int(os.environ.get("FASTAPI_DB_CONNECTION_RETRY_PERIOD", default=3))

for attempt in Retrying(
        stop=stop_after_attempt(max_tries),
        wait=wait_fixed(wait_seconds),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.WARNING),
):
    with attempt:
        try:
            from sqlalchemy.sql import text
            from app.db.session import engine_admin
            from app.models import *  # noqa: F401,F403
        except Exception as e:
            logger.exception(e)
            raise e

oracle_user_username = os.environ.get("ORACLE_USER_USERNAME", default="user1")
oracle_user_password = os.environ.get("ORACLE_USER_USERNAME", default="user1")


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARNING),
)
def init() -> None:
    try:
        with engine_admin.connect() as connection:
            # ping the DB
            connection.execute(text("SELECT 1"))
    except Exception as e:
        logger.warning(f"DB is offline: {e}")
        raise e


def create_db_users() -> None:
    with engine_admin.connect() as connection:
        with connection.begin():
            connection.execute(
                text(
                    """
                    alter session set \"_ORACLE_SCRIPT\"=true
                    """
                )
            )
            connection.execute(
                text(
                    """
                    CREATE TABLESPACE IF NOT EXISTS data_ts DATAFILE '/opt/oracle/oradata/FREE/data_ts.dbf' SIZE 512m
                    """
                )
            )
            sql = text(
                f"CREATE USER IF NOT EXISTS {oracle_user_password} IDENTIFIED BY {oracle_user_password} \
                DEFAULT TABLESPACE data_ts QUOTA UNLIMITED ON data_ts"
            )
            connection.execute(sql)
            sql = text(
                f"GRANT CREATE SESSION TO {oracle_user_username}"
            )
            connection.execute(sql)
            sql = text(
                f"GRANT CREATE TABLE TO {oracle_user_username}"
            )
            connection.execute(sql)
            sql = text(
                f"GRANT CREATE SEQUENCE TO {oracle_user_username}"
            )
            connection.execute(sql)
            sql = text(
                f"GRANT CREATE TRIGGER TO {oracle_user_username}"
            )
            connection.execute(sql)


def main() -> None:
    """
    Ensures DB is running and initializes user tablespace
    """
    logger.info("Attempting connection to DB")
    init()
    logger.info("DB up & running! Creating users and granting permissions")
    create_db_users()


if __name__ == "__main__":
    main()
