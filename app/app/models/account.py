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


class TestAccount(SQLModelBaseUserDB):
    pass


class Account(SQLModelBaseUserDB, table=True):
    __tablename__ = 'account'
    id: Optional[int] = Field(primary_key=True, default=None)
    type: AccountType = Field(sa_column_args=(
        CheckConstraint("type in ('rider', 'coordinator', 'admin')", name="account_type_enum"),
    ))
    username: str = Field(max_length=24, unique=True)
    name: str = Field(max_length=80)
    surname: str = Field(max_length=80)
    email: str = Field(max_length=80, unique=True)
    gender: Optional[Gender] = Field(default=None, sa_column_args=(
        CheckConstraint("gender in ('male', 'female')", name="account_gender_enum"),
    ))
    birth_date: Optional[datetime] = Field(default=None)

    rider: "Rider" = Relationship(back_populates="account")


class AccountCreate(schemas.BaseUserCreate):
    type: AccountType
    username: str = Field(max_length=24, unique=True)
    name: str = Field(max_length=80)
    surname: str = Field(max_length=80)
    gender: Optional[Gender] = Field(default=None)
    birth_date: Optional[datetime] = Field(default=None)


class AccountRead(schemas.BaseUser[int]):
    type: AccountType
    username: str = Field(max_length=24, unique=True)
    name: str = Field(max_length=80)
    surname: str = Field(max_length=80)
    gender: Optional[Gender] = Field(default=None)
    birth_date: Optional[datetime] = Field(default=None)


class AccountUpdate(schemas.BaseUserUpdate):
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
