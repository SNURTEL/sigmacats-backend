from typing import Optional
from enum import Enum
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship


class Gender(Enum):
    Male = "male"
    Female = "female"


class AccountType(Enum):
    Rider = "rider"
    Coordinator = "coordinator"
    Admin = "admin"


class Account(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    username: str = Field(max_length=24, unique=True)
    name: str = Field(max_length=80)
    surname: str = Field(max_length=80)
    email: str = Field(max_length=80, unique=True)
    password_hash: str = Field(max_length=256)
    gender: Optional[Gender] = Field(default=None)
    birth_date: Optional[datetime] = Field(default=None)

    rider: "Rider" = Relationship(back_populates="account")
