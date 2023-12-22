from typing import TYPE_CHECKING

from pydantic import validator
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .account import Account

class Coordinator(SQLModel, table=True):
    id: int = Field(foreign_key="account.id", primary_key=True)
    account: "Account" = Relationship(back_populates="coordinator")
    phone_number: str = Field(max_length=20)

    @validator("phone_number")
    def validate_phone_number(cls, v):
        if (v[0] == "+" and not int(v[1:])) or (v[0] != "+" and not int(v)):
            raise ValueError("Invalid phone number")

        return v
