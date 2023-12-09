from fastapi import FastAPI, Depends
from sqlmodel import Session
from sqlmodel import select
from fastapi_users import FastAPIUsers
from app.db.user_methods import get_user_manager

from app.util.log import get_logger
from app.db.session import get_db
from app.tasks import basic_tasks
from app.models.account import AccountRead, AccountCreate, AccountUpdate, Account
from app.core.authentication import auth_backend

fastapi_users = FastAPIUsers[AccountInternal, int](
    get_user_manager,
    [auth_backend],
)

app = FastAPI()

logger = get_logger()

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(AccountRead, AccountCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(AccountRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(AccountRead, AccountUpdate),
    prefix="/users",
    tags=["users"],
)

@app.get("/")
async def read_root() -> dict[str, str]:
    return {"Hello": "World"}


@app.get("/celery")
async def celery_test() -> dict[str, str]:
    r = basic_tasks.test_celery.delay()
    return {"Queued task": f"{r}"}


@app.get("/db")
async def db_test(db: Session = Depends(get_db)) -> list[Account]:
    accounts = db.exec(select(Account)).all()
    logger.info(accounts)
    return accounts
