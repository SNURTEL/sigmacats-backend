from typing import Optional, TYPE_CHECKING
from enum import Enum
from datetime import datetime
from fastapi_users import schemas
from fastapi_users_db_sqlmodel import SQLModelBaseUserDB
from pydantic import validator

from sqlmodel import Field, Relationship, CheckConstraint, SQLModel

if TYPE_CHECKING:
    from .rider import Rider
    from .coordinator import Coordinator
    from .admin import Admin


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

    rider: Optional["Rider"] = Relationship(back_populates="account",
                                            sa_relationship_kwargs={
                                                'single_parent': True,
                                                'cascade': "all, delete-orphan"
                                            })
    coordinator: Optional["Coordinator"] = Relationship(back_populates="account",
                                                        sa_relationship_kwargs={
                                                            'single_parent': True,
                                                            'cascade': "all, delete-orphan"
                                                        })
    admin: Optional["Admin"] = Relationship(back_populates="account",
                                            sa_relationship_kwargs={
                                                'single_parent': True,
                                                'cascade': "all, delete-orphan"
                                            })


class AccountCreate(schemas.BaseUserCreate):
    type: AccountType
    username: str = Field(max_length=24, unique=True)
    name: str = Field(max_length=80)
    surname: str = Field(max_length=80)
    gender: Optional[Gender] = Field(default=None)
    birth_date: Optional[datetime] = Field(default=None)
    phone_number: Optional[str] = Field(default=None)  # used only by coordinator

    @validator("phone_number")
    def validate_phone_number(cls, v):
        try:
            if (v is not None
                    and (
                            (v[0] == "+" and (not v[1:].isalnum() or not int(v[1:])))
                            or (v[0] != "+" and (not v.isalnum() or not int(v)))
                    )):
                raise ValueError("Invalid phone number")
        except (ValueError, IndexError):
            raise ValueError("Invalid phone number")

        return v


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
