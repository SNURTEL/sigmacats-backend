from typing import Optional
from enum import Enum

from sqlmodel import Field, SQLModel, Relationship



class BikeType(Enum):
    Road = "road"
    Fixie = "fixie"
    Other = "other"


class Bike(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(max_length=80)
    type: BikeType
    brand: Optional[str] = Field(max_length=80, default=None)
    model: Optional[str] = Field(max_length=80, default=None)

    rider_id: int = Field(foreign_key="rider.id")
    rider: "Rider" = Relationship(back_populates="bikes")
    race_participations: list["RaceParticipation"] = Relationship(back_populates="bike")
