import os

from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine
import sys
import oracledb

# But wait, what is this import doing in `core.config`? All models
# have to be imported before doing ANYTHING with ORM, putting the import
# here ensures all ORM relationships will be resolved properly by the mapper
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
def create_db_engine() -> Engine:
    return create_engine(db_url, echo=True)


def create_db_engine_admin() -> Engine:
    return create_engine(db_url_admin, echo=True)
