from typing import TYPE_CHECKING

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .account import Account


class Admin(SQLModel, table=True):
    id: int = Field(foreign_key="account.id", primary_key=True)
    account: "Account" = Relationship(back_populates="admin",
                                      sa_relationship_kwargs={
                                                'single_parent': True,
                                          'cascade': "save-update, merge, delete, delete-orphan"
                                      })
