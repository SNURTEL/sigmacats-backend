from typing import Type

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from fastapi_users import exceptions, models, schemas
from fastapi_users.manager import BaseUserManager, UserManagerDependency
from fastapi_users.router.common import ErrorCode, ErrorModel

from app.core.users import current_admin_user
from app.models.account import AccountType, Account, AccountCreate
from app.util.log import get_logger

logger = get_logger()

"""
This file alters the default register router from `fastapi-users`.
Since creating accounts of different types (rider vs coordinator/admin)
has different authentication requirements, we want to redirect
the client to a secured endpoint when creating coordinator/admin account.
"""

def get_register_router(
        get_user_manager: UserManagerDependency[models.UP, models.ID],
        user_schema: Type[schemas.U],
        user_create_schema: Type[schemas.UC],
) -> APIRouter:
    """
    Build the register router
    """
    router = APIRouter()

    @router.post(
        "/register",
        response_model=user_schema,
        status_code=status.HTTP_201_CREATED,
        responses={
            status.HTTP_307_TEMPORARY_REDIRECT: {
                "description": "Attempted to create a coordinator or admin account.",
                "content": None
            },
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.REGISTER_USER_ALREADY_EXISTS: {
                                "summary": "A user with this email already exists.",
                                "value": {
                                    "detail": ErrorCode.REGISTER_USER_ALREADY_EXISTS
                                },
                            },
                            ErrorCode.REGISTER_INVALID_PASSWORD: {
                                "summary": "Password validation failed.",
                                "value": {
                                    "detail": {
                                        "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                                        "reason": "Password should be"
                                                  "at least 3 characters",
                                    }
                                },
                            },
                        }
                    }
                },
            },
        },
    )
    async def register(
            request: Request,
            user_create: AccountCreate,  # type: ignore
            user_manager: BaseUserManager[Account, models.ID] = Depends(get_user_manager),
    ) -> schemas.U | RedirectResponse:
        """
        NOTE: Swagger will not include the authorization header by default. Redirects may be broken. You can test
        redirects manually with curl.
        """
        if user_create.type != AccountType.rider:
            redirect_url = request.url_for("register_staff")
            return RedirectResponse(redirect_url)
        return await _register(request, user_create, user_manager)

    @router.post(
        "/register/staff",
        response_model=user_schema,
        status_code=status.HTTP_201_CREATED,
        responses={
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.REGISTER_USER_ALREADY_EXISTS: {
                                "summary": "A user with this email already exists.",
                                "value": {
                                    "detail": ErrorCode.REGISTER_USER_ALREADY_EXISTS
                                },
                            },
                            ErrorCode.REGISTER_INVALID_PASSWORD: {
                                "summary": "Password validation failed.",
                                "value": {
                                    "detail": {
                                        "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                                        "reason": "Password should be"
                                                  "at least 3 characters",
                                    }
                                },
                            },
                        }
                    }
                },
            },
        },
    )
    async def register_staff(
            request: Request,
            user_create: user_create_schema,  # type: ignore
            user_manager: BaseUserManager[Account, models.ID] = Depends(get_user_manager),
            admin_user: Account = Depends(current_admin_user)  # fastapi-users needs this for authentication
    ) -> schemas.U | RedirectResponse:
        return await _register(request, user_create, user_manager)

    async def _register(
            request: Request,
            user_create: AccountCreate,  # type: ignore
            user_manager: BaseUserManager[Account, models.ID] = Depends(get_user_manager),
    ) -> schemas.U:
        try:
            created_user = await user_manager.create(
                user_create, safe=True, request=request
            )
        except exceptions.UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
            )
        except exceptions.InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )

        return schemas.model_validate(user_schema, created_user)

    return router
