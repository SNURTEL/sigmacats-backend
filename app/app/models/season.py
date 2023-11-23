from typing import Optional

from datetime import datetime

from sqlmodel import Field, SQLModel, Relationship, CheckConstraint


class Season(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(max_length=80, unique=True)
    start_timestamp: datetime
    end_timestamp: datetime = Field(sa_column_args=(
        CheckConstraint("end_timestamp > start_timestamp", name="season_timestamp_order"),
    ))
    classifications: list["Classification"] = Relationship(back_populates="season")
    races: list["Race"] = Relationship(back_populates="season")