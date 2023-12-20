
from fastapi import Depends
from fastapi_users_db_sqlmodel import SQLModelUserDatabase
from fastapi_users import FastAPIUsers
from sqlmodel import Session

from app.core.authentication import jwt_auth_backend, cookie_auth_backend
from app.db.session import get_db
from app.core.user_manager import UserManager
from app.models.account import Account


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
