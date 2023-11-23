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

    rider_id: int = Field(foreign_key="rider.id")
    rider: "Rider" = Relationship(back_populates="bikes")
    race_participations: list["RaceParticipation"] = Relationship(back_populates="bike")
