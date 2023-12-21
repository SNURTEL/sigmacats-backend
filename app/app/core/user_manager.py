import os
from typing import Optional, Union

from fastapi_users import BaseUserManager, InvalidPasswordException, IntegerIDMixin
from fastapi import Request, Response, Depends, HTTPException
from sqlmodel import Session

from app.db.session import SessionLocal, get_db
from app.models.account import Account, AccountCreate, AccountType
from app.models.rider import Rider
from app.util.log import get_logger

logger = get_logger()

class UserManager(IntegerIDMixin, BaseUserManager[Account, int]):
    reset_password_token_secret = str(os.environ.get("FASTAPI_RESET_PASSWORD_TOKEN_SECRET"))
    verification_token_secret = str(os.environ.get("FASTAPI_VERIFICATION_TOKEN_SECRET"))

    async def on_after_register(
            self, account: Account,
            request: Optional[Request] = None,
    ):
        db = next(get_db())
        logger.info(account)


        if account.type == AccountType.rider:
            rider = Rider(
                account=account,
                bikes=[],
                classifications=[],  # TODO defaults
                race_participations=[],
                classification_links=[]
            )
            account.rider = rider
            a = db.merge(account)
            db.add(a)
            db.commit()
            db.refresh(a)
        else:
            db.delete(account)
            db.commit()
            raise HTTPException(400)

        print(f"User {account.id} has registered as {account.type.name}.")

    async def on_after_forgot_password(
            self, user: Account, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
            self, user: Account, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def on_after_login(
            self,
            user: Account,
            request: Optional[Request] = None,
            response: Optional[Response] = None,
    ):
        print(f"User {user.id} logged in.")

    async def validate_password(
            self,
            password: str,
            user: Union[AccountCreate, Account],
    ) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters"
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason="Password should not contain e-mail"
            )
