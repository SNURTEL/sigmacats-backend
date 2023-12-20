
from fastapi import Depends, HTTPException
from fastapi_users_db_sqlmodel import SQLModelUserDatabase
from fastapi_users import FastAPIUsers
from sqlmodel import Session

from app.core.authentication import jwt_auth_backend, cookie_auth_backend
from app.db.session import get_db
from app.core.user_manager import UserManager
from app.models.account import Account, AccountType


def get_user_db(session: Session = Depends(get_db)):
    yield SQLModelUserDatabase(session, Account)


def get_user_manager(user_db=Depends(get_user_db)):
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
) -> Account:
    if not user.type == AccountType.rider:
        raise HTTPException(403)
    return user


async def current_coordinator_user(
        user: Account = Depends(current_active_user)
) -> Account:
    if not user.type == AccountType.coordinator:
        raise HTTPException(403)
    return user


async def current_admin_user(
        user: Account = Depends(current_active_user)
) -> Account:
    if not user.type == AccountType.admin:
        raise HTTPException(403)
    return user
