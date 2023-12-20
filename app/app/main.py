import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
from sqlmodel import Session
from sqlmodel import select
from fastapi_users import FastAPIUsers
from app.db.user_methods import get_user_manager

from app.api.api import api_router
from app.util.log import get_logger
from app.db.session import get_db
from app.tasks import basic_tasks
from app.models.account import AccountRead, AccountCreate, AccountUpdate, Account
from app.core.authentication import auth_backend

fastapi_users = FastAPIUsers[AccountInternal, int](
    get_user_manager,
    [auth_backend],
)

logger = get_logger()

app_name = os.getenv("FASTAPI_APP_NAME", "NAME NOT SET")
api_prefix = os.getenv("FASTAPI_API_PREFIX", "/api")


app = FastAPI(
    title=app_name,
    openapi_url=f"{api_prefix}/openapi.json",
    docs_url=f"{api_prefix}/docs",
    redoc_url=f"{api_prefix}/redoc"
)
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix=api_prefix)

app.include_router(
    fastapi_users.get_users_router(AccountRead, AccountUpdate),
    prefix="/users",
    tags=["users"],
)

@app.get("/")
async def read_root() -> dict[str, str]:
    return {"Hello": "World"}
