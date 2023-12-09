from typing import Optional, TYPE_CHECKING
from enum import Enum
from datetime import datetime
from fastapi_users import schemas
from fastapi_users_db_sqlmodel import SQLModelBaseUserDB

from sqlmodel import Field, Relationship, CheckConstraint, SQLModel

if TYPE_CHECKING:
    from .rider import Rider


class Gender(Enum):
    male = "male"
    female = "female"


class AccountType(Enum):
    rider = "rider"
    coordinator = "coordinator"
    admin = "admin"


class Account(SQLModelBaseUserDB, table=True):
    def __init__(
            self,
            type: AccountType = Field(sa_column_args=(
                    CheckConstraint("type in ('rider', 'coordinator', 'admin')", name="account_type_enum"),
            )),
            username: str = Field(max_length=24, unique=True),
            name: str = Field(max_length=80),
            surname: str = Field(max_length=80),
            gender: Optional[Gender] = Field(default=None, sa_column_args=(
                CheckConstraint("gender in ('male', 'female')", name="account_gender_enum"),
            )),
            birth_date: Optional[datetime] = Field(default=None),

            rider: "Rider" = Relationship(back_populates="account"),
    ):
        super().__init__()
        self.type = type
        self.username = username
        self.name = name
        self.surname = surname
        self.gender = gender
        self.birth_date = birth_date
        self.rider = rider
        super(Account, self).__tablename__ = 'account'
        __tablename__ = 'account'

class AccountCreate():
    pass

class AccountRead():
    pass

class AccountUpdate():
    pass


'''class AccountRead(schemas.BaseUser[int]):
    type: AccountType = Field(sa_column_args=(
        CheckConstraint("type in ('rider', 'coordinator', 'admin')", name="account_type_enum"),
    ))
    username: str = Field(max_length=24, unique=True)
    name: str = Field(max_length=80)
    surname: str = Field(max_length=80)
    gender: Optional[Gender] = Field(default=None, sa_column_args=(
        CheckConstraint("gender in ('male', 'female')", name="account_gender_enum"),
    ))
    birth_date: Optional[datetime] = Field(default=None)

    rider: "Rider" = Relationship(back_populates="account")


class AccountCreate(schemas.BaseUserCreate):
    type: AccountType = Field(sa_column_args=(
        CheckConstraint("type in ('rider', 'coordinator', 'admin')", name="account_type_enum"),
    ))
    username: str = Field(max_length=24, unique=True)
    name: str = Field(max_length=80)
    surname: str = Field(max_length=80)
    password: str = Field(max_length=256)


class AccountUpdate(schemas.BaseUserUpdate):
    type: AccountType = Field(sa_column_args=(
        CheckConstraint("type in ('rider', 'coordinator', 'admin')", name="account_type_enum"),
    ))
    username: str = Field(max_length=24, unique=True)
    name: str = Field(max_length=80)
    surname: str = Field(max_length=80)
    email: str = Field(max_length=80, unique=True)
    password: str = Field(max_length=256)
    gender: Optional[Gender] = Field(default=None, sa_column_args=(
        CheckConstraint("gender in ('male', 'female')", name="account_gender_enum"),
    ))
    birth_date: Optional[datetime] = Field(default=None)'''