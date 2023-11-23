from sqlmodel import Field, SQLModel


class Admin(SQLModel, table=True):
    id: int = Field(foreign_key="account.id", primary_key=True)
