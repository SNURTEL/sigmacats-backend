from typing import TYPE_CHECKING

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .account import Account


class Admin(SQLModel, table=True):
    """
    Full model of an admin account
    """
    id: int = Field(foreign_key="account.id", primary_key=True)
    account: "Account" = Relationship(back_populates="admin",
                                      sa_relationship_kwargs={
                                          'single_parent': True,
                                          'cascade': "all, delete-orphan",
                                      })
