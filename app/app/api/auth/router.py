from fastapi import APIRouter

from app.core.users import fastapi_users
from app.core.authentication import jwt_auth_backend, cookie_auth_backend
from app.core.register import get_register_router
from app.models.account import AccountRead, AccountCreate

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(jwt_auth_backend),
    prefix="/jwt"
)
router.include_router(
    fastapi_users.get_auth_router(cookie_auth_backend),
    prefix="/cookie"
)
router.include_router(
    fastapi_users.get_reset_password_router(),
)
router.include_router(
    get_register_router(fastapi_users.get_user_manager, AccountRead, AccountCreate)
)

# # uncomment if needed
# router.include_router(
#     fastapi_users.get_verify_router(AccountRead),
# )
