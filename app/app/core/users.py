from typing import Generator, Any

from fastapi import Depends, HTTPException
from fastapi_users_db_sqlmodel import SQLModelUserDatabase
from fastapi_users import FastAPIUsers
from sqlmodel import Session

from app.core.authentication import jwt_auth_backend, cookie_auth_backend
from app.db.session import get_db
from app.core.user_manager import UserManager
from app.models.account import Account, AccountType
from app.models.rider import Rider

from app.util.log import get_logger

logger = get_logger()

"""
This file contains FastAPI dependencies for user db,
user manager, and currently active users. Adding the
former ones to endpoints will result in throwing  401 if
currently logged in user is not of required type (or user is
not logged in at all).
"""


def get_user_db(session: Session = Depends(get_db)) -> Generator[SQLModelUserDatabase, Any, None]:
    """
    Get the user DB used by `UserManager`
    """
    yield SQLModelUserDatabase(session, Account)


def get_user_manager(user_db: SQLModelUserDatabase = Depends(get_user_db)) -> Generator[UserManager, Any, None]:
    """
    Get the `UserManger`
    """
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[Account, int](
    get_user_manager,
    [jwt_auth_backend, cookie_auth_backend],
)
current_user = fastapi_users.current_user()
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)


async def current_rider_user(
        user: Account = Depends(current_active_user)
) -> Rider:
    """
    Return rider that is currently logged into the app.
    401 if user is not logged in.
    """
    if not user.type == AccountType.rider:
        raise HTTPException(403)
    assert user.rider is not None
    return user.rider


async def current_coordinator_user(
        user: Account = Depends(current_active_user)
) -> Account:
    """
    Return coordinator that is currently logged into the app.
    401 if user is not a coordinator.
    """
    if not user.type == AccountType.coordinator:
        raise HTTPException(403)
    return user


async def current_admin_user(
        user: Account = Depends(current_active_user)
) -> Account:
    """
    Return admin that is currently logged into the app.
    401 if user is not an admin.
    """
    if not user.type == AccountType.admin:
        raise HTTPException(403)
    return user
