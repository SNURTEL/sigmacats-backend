from fastapi import APIRouter

from app.core.users import fastapi_users
from app.core.authentication import jwt_auth_backend, cookie_auth_backend
from app.models.account import AccountRead, AccountCreate


router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(jwt_auth_backend),
    prefix="/auth/jwt"
)
router.include_router(
    fastapi_users.get_auth_router(cookie_auth_backend),
    prefix="/auth/cookie"
)
router.include_router(
    fastapi_users.get_register_router(AccountRead, AccountCreate),
    prefix="/auth"
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth"
)
router.include_router(
    fastapi_users.get_verify_router(AccountRead),
    prefix="/auth"
)
