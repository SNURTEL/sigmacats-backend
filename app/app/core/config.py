import os

from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine
import sys
import oracledb

# SQLModel / SQLAlchemy require resolving all relationships between models
# before connecting  to DB and using ORM. Putting the import here ensures
# they will be resolved properly.
from app.models import *  # noqa: F401,F403
from app.db.forward_refs import update_forward_refs

update_forward_refs()

oracledb.version = "23.0.0.0"
sys.modules["python-oracledb"] = oracledb

db_url = URL.create(
    drivername="oracle+oracledb",
    username=os.environ.get("ORACLE_USER_USERNAME"),
    password=os.environ.get("ORACLE_USER_PASSWORD"),
    host=os.environ.get("ORACLE_HOST"),
    database=os.environ.get("ORACLE_DATABASE"),
    port=int(os.environ.get("ORACLE_PORT", default="1521")),
)

db_url_admin = URL.create(
    drivername="oracle+oracledb",
    username=os.environ.get("ORACLE_ADMIN_USERNAME"),
    password=os.environ.get("ORACLE_ADMIN_PASSWORD"),
    host=os.environ.get("ORACLE_HOST"),
    database=os.environ.get("ORACLE_DATABASE"),
    port=int(os.environ.get("ORACLE_PORT", default="1521")),
)


# TODO disable echo if not in devel / test mode
def create_db_engine(echo: bool = True) -> Engine:
    return create_engine(db_url, echo=echo)


def create_db_engine_admin(echo: bool = True) -> Engine:
    return create_engine(db_url_admin, echo=echo)
