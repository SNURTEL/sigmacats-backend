from fastapi import APIRouter

from app.core.users import fastapi_users
from app.models.account import AccountRead, AccountUpdate

"""
This files creates APIRouter for users
"""

router = APIRouter()

router.include_router(
    fastapi_users.get_users_router(AccountRead, AccountUpdate)
)
