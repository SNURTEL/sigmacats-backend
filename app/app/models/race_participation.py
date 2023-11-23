from typing import Optional
from datetime import datetime
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship, CheckConstraint


class RaceParticipationStatus(Enum):
    Pending = "pending"
    Approved = "approved"
    Rejected = "rejected"


class RaceParticipation(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    place_generated: Optional[int] = Field(default=None)
    place_assigned: Optional[int] = Field(default=None)
    ride_start_timestamp: Optional[datetime] = Field(default=None)
    ride_end_timestamp: Optional[datetime] = Field(default=None, sa_column_args=(
        CheckConstraint("end_timestamp > start_timestamp"),
    ))
    ride_gpx_file: Optional[str] = Field(default=None, max_length=256, sa_column_args=(
        CheckConstraint("ride_end_timestamp IS NOT NULL"),
    ))

    rider_id: int = Field(foreign_key="rider.id")
    rider: "Rider" = Relationship(back_populates="race_participations")
    race_id: int = Field(foreign_key="race.id")
    race: "Race" = Relationship(back_populates="race_participations")
    bike_id: int = Field(foreign_key="bike.id")
    bike: "Bike" = Relationship(back_populates="race_participations")
