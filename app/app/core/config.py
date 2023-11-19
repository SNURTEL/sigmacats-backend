import os

from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine
import sys
import oracledb

oracledb.version = "23.0.0.0"
sys.modules["cx_Oracle"] = oracledb

db_url = URL.create(
    drivername="oracle",
    username=os.environ.get("ORACLE_USER_USERNAME"),
    password=os.environ.get("ORACLE_USER_PASSWORD"),
    host=os.environ.get("ORACLE_HOST"),
    database=os.environ.get("ORACLE_DATABASE"),
    port=int(os.environ.get("ORACLE_PORT", default="1521")),
)

db_url_admin = URL.create(
        drivername="oracle",
        username=os.environ.get("ORACLE_ADMIN_USERNAME"),
        password=os.environ.get("ORACLE_ADMIN_PASSWORD"),
        host=os.environ.get("ORACLE_HOST"),
        database=os.environ.get("ORACLE_DATABASE"),
        port=int(os.environ.get("ORACLE_PORT", default="1521")),
    )


# TODO disable echo if not in devel / test mode
def create_db_engine() -> Engine:
    return create_engine(db_url, echo=True)


def create_db_engine_admin() -> Engine:
    return create_engine(db_url_admin, echo=True)
