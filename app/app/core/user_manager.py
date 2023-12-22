import os
from typing import Optional, Union

from fastapi_users import BaseUserManager, InvalidPasswordException, IntegerIDMixin, schemas, models
from fastapi import Request, Response, HTTPException

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.models.account import Account, AccountCreate, AccountType
from app.models.rider import Rider
from app.models.coordinator import Coordinator
from app.models.admin import Admin
from app.util.log import get_logger

logger = get_logger()

class UserManager(IntegerIDMixin, BaseUserManager[Account, int]):
    reset_password_token_secret = str(os.environ.get("FASTAPI_RESET_PASSWORD_TOKEN_SECRET"))
    verification_token_secret = str(os.environ.get("FASTAPI_VERIFICATION_TOKEN_SECRET"))

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UP:
        if user_create.type not in set(i for i in AccountType):
            raise HTTPException(400)

        try:
            session = next(get_db())
            with session.begin():
                account = await super().create(user_create, safe, request)
                if account.type == AccountType.rider:
                    rider = Rider(
                        account=account,
                        bikes=[],
                        classifications=[],  # TODO defaults
                        race_participations=[],
                        classification_links=[]
                    )
                    account.rider = rider
                elif account.type == AccountType.coordinator:
                    logger.info(await request.body())
                    coordinator = Coordinator(
                        account=account,
                        phone_number=user_create.phone_number
                    )
                    account.coordinator = coordinator
                elif account.type == AccountType.admin:
                    admin = Admin(
                        account=account,
                    )
                    account.admin = admin

                a = session.merge(account)
                session.add(a)
                session.commit()
                print(f"User {account.id} has registered as {account.type.name}.")
                return account
        except (ValidationError, IntegrityError)  as e:
            logger.exception(e)
            raise HTTPException(400)


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
