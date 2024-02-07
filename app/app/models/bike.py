from typing import Optional, TYPE_CHECKING
from enum import Enum

from sqlmodel import Field, SQLModel, Relationship, CheckConstraint

if TYPE_CHECKING:
    from .rider import Rider
    from .race_participation import RaceParticipation


class BikeType(Enum):
    road = "road"
    fixie = "fixie"
    other = "other"


class Bike(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(max_length=80)
    type: BikeType = Field(sa_column_args=(
        CheckConstraint("type in ('road', 'fixie', 'other')", name="bike_type_enum"),
    ))
    brand: Optional[str] = Field(max_length=80, default=None)
    model: Optional[str] = Field(max_length=80, default=None)
    is_retired: bool = Field(default=False)

    rider_id: int = Field(foreign_key="rider.id")
    rider: "Rider" = Relationship(back_populates="bikes")
    race_participations: list["RaceParticipation"] = Relationship(back_populates="bike")


class BikeCreate(SQLModel):
    name: str = Field(max_length=80)
    type: BikeType
    brand: Optional[str] = Field(max_length=80, default=None)
    model: Optional[str] = Field(max_length=80, default=None)


class BikeUpdate(SQLModel):
    name: str = Field(max_length=80, default=None)
    type: BikeType = Field(default=None)
    brand: Optional[str] = Field(max_length=80, default=None)
    model: Optional[str] = Field(max_length=80, default=None)
    is_retired: bool = Field(default=False)
