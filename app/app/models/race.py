from typing import Optional
from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel, Relationship, CheckConstraint

# from .season import Season
from .race_bonus_race_link import RaceBonusRaceLink


class RaceStatus(Enum):
    pending = "pending"
    in_progress = "in_progress"
    ended = "ended"


class RaceTemperature(Enum):
    cold = "cold"
    normal = "normal"
    hot = "hot"


class RaceRain(Enum):
    zero = "zero"
    light = "light"
    heavy = "heavy"


class RaceWind(Enum):
    zero = "zero"
    light = "light"
    heavy = "heavy"


class Race(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    status: RaceStatus = Field(sa_column_args=(
        CheckConstraint("status in ('pending', 'in_progress', 'ended')", name="race_status_enum"),
    ))
    name: str = Field(max_length=80)
    description: str = Field(max_length=512)
    requirements: Optional[str] = Field(default=None,  max_length=512)
    checkpoints_gpx_file: str = Field(max_length=256, unique=True)
    start_timestamp: datetime
    end_timestamp: datetime = Field(sa_column_args=(
        CheckConstraint("end_timestamp > start_timestamp", name="race_timestamp_order"),
    ))
    temperature: Optional[RaceTemperature] = Field(default=None, sa_column_args=(
        CheckConstraint("temperature in ('cold', 'normal', 'hot')", name="race_temperature_enum"),
    ))
    rain: Optional[RaceRain] = Field(default=None, sa_column_args=(
        CheckConstraint("rain in ('zero', 'light', 'heavy')", name="race_rain_enum"),
    ))
    wind: Optional[RaceWind] = Field(default=None, sa_column_args=(
        CheckConstraint("wind in ('zero', 'light', 'heavy')", name="race_wind_enum"),
    ))

    season_id: int = Field(foreign_key="season.id")
    season: "Season" = Relationship(back_populates="races")
    bonuses: list["RaceBonus"] = Relationship(
        back_populates="races",
        link_model=RaceBonusRaceLink
    )
    race_participations: list["RaceParticipation"] = Relationship(back_populates="race")
