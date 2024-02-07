from typing import Optional, TYPE_CHECKING

from datetime import datetime

from sqlmodel import Field, SQLModel, Relationship, CheckConstraint

if TYPE_CHECKING:
    from .classification import Classification
    from .race import Race


class Season(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(max_length=80, unique=True)
    start_timestamp: datetime
    end_timestamp: Optional[datetime] = Field(default=None, sa_column_args=(
        CheckConstraint("end_timestamp is null or end_timestamp > start_timestamp", name="season_timestamp_order"),
    ))
    classifications: list["Classification"] = Relationship(back_populates="season")
    races: list["Race"] = Relationship(back_populates="season")


class SeasonRead(SQLModel):
    id: int
    name: str
    start_timestamp: datetime
    end_timestamp: Optional[datetime] = None


class SeasonStart(SQLModel):
    name: str
