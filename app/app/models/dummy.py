from typing import Optional

from sqlmodel import Field, SQLModel


class Dummy(SQLModel, table=True):
    """
    Dummy model for testing DB behavior
    """
    id: int = Field(primary_key=True)
    foo: str = Field(max_length=50)  # str (VARCHAR) fields need to have length specified explicitly
    bar: Optional[int] = None
