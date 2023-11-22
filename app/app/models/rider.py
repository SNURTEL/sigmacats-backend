from typing import Optional
from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class Gender(Enum):
    Male = "male"
    Female = "female"


class Rider(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    surname: str
    email: str
    gender: Optional[Gender]
    birth_date: Optional[datetime]
