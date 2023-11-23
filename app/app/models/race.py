from typing import Optional
from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel, Relationship

from .season import Season
from .race_bonus_race_link import RaceBonusRaceLink


class RaceStatus(Enum):
    Pending = "pending"
    InProgress = "in_progress"
    Ended = "ended"


class RaceTemperature(Enum):
    Cold = "cold"
    Normal = "normal"
    Hot = "hot"


class RaceRain(Enum):
    Zero = "zero"
    Light = "light"
    Heavy = "heavy"


class RaceWind(Enum):
    Zero = "zero"
    Light = "light"
    Heavy = "heavy"


class Race(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    status: RaceStatus
    name: str = Field(max_length=80)
    description: str = Field(max_length=512)
    requirements: Optional[str] = Field(default=None,  max_length=512)
    checkpoints_gpx_file: str = Field(max_length=256, unique=True)
    start_timestamp: datetime
    end_timestamp: datetime
    temperature: Optional[RaceTemperature] = Field(default=None)
    rain: Optional[RaceRain] = Field(default=None)
    wind: Optional[RaceWind] = Field(default=None)

    season_id: int = Field(foreign_key="season.id")
    season: Season = Relationship(back_populates="races")
    bonuses: list["RaceBonus"] = Relationship(
        back_populates="races",
        link_model=RaceBonusRaceLink
    )
    race_participations: list["RaceParticipation"] = Relationship(back_populates="race")
