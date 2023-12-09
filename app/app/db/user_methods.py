from app.db.session import SessionLocal
from app.models.account import Account
from fastapi_users_db_sqlmodel import SQLModelUserDatabaseAsync
from app.core.user_manager import UserManager


async def get_user_db():
    db = SessionLocal()
    yield SQLModelUserDatabaseAsync(db, Account)


async def get_user_manager():
    db = get_user_db()
    yield UserManager(db)
