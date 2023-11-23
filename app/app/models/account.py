from typing import Optional
from enum import Enum
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship, CheckConstraint


class Gender(Enum):
    male = "male"
    female = "female"


class AccountType(Enum):
    rider = "rider"
    coordinator = "coordinator"
    admin = "admin"


class Account(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    type: AccountType = Field(sa_column_args=(
        CheckConstraint("type in ('rider', 'coordinator', 'admin')", name="account_type_enum"),
    ))
    username: str = Field(max_length=24, unique=True)
    name: str = Field(max_length=80)
    surname: str = Field(max_length=80)
    email: str = Field(max_length=80, unique=True)
    password_hash: str = Field(max_length=256)
    gender: Optional[Gender] = Field(default=None, sa_column_args=(
        CheckConstraint("gender in ('male', 'female')", name="account_gender_enum"),
    ))
    birth_date: Optional[datetime] = Field(default=None)

    rider: "Rider" = Relationship(back_populates="account")
