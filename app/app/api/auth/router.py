from fastapi import APIRouter

from app.core.users import fastapi_users
from app.core.authentication import auth_backend
from app.models.account import AccountRead, AccountCreate


router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)
router.include_router(
    fastapi_users.get_register_router(AccountRead, AccountCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_verify_router(AccountRead),
    prefix="/auth",
    tags=["auth"],
)
