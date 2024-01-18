import json

from typing import Optional, TYPE_CHECKING
from datetime import datetime
from enum import Enum

import jsonschema

from pydantic import validator

from sqlmodel import Field, SQLModel, Relationship, CheckConstraint

from .race_bonus_race_link import RaceBonusRaceLink

if TYPE_CHECKING:
    from .season import Season, SeasonRead
    from .race_bonus import RaceBonus, RaceBonusListRead
    from .race_participation import RaceParticipation, RaceParticipationStatus, RaceParticipationCoordinatorListRead, \
        RaceParticipationListReadNames


class RaceStatus(Enum):
    """
    Model for race status
    """
    pending = "pending"
    in_progress = "in_progress"
    ended = "ended"
    cancelled = "cancelled"


class RaceTemperature(Enum):
    """
    Model for temperature during race
    """
    cold = "cold"
    normal = "normal"
    hot = "hot"


class RaceRain(Enum):
    """
    Model for rain during race
    """
    zero = "zero"
    light = "light"
    heavy = "heavy"


class RaceWind(Enum):
    """
    Model for wind during race
    """
    zero = "zero"
    light = "light"
    heavy = "heavy"


sponsor_banners_uuids_json_schema = {
    "type": "array",
    "items": {"type": "string"}
}

place_to_points_mapping_json_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "place": {"type": "number"},
            "points": {"type": "number"},
        }
    },
}


class Race(SQLModel, table=True):
    """
    Full model of a race
    """
    id: Optional[int] = Field(primary_key=True, default=None)
    status: RaceStatus = Field(sa_column_args=(
        CheckConstraint("status in ('pending', 'in_progress', 'ended', 'cancelled')", name="race_status_enum"),
    ), index=True)
    name: str = Field(max_length=80)
    description: str = Field(max_length=2048)
    requirements: Optional[str] = Field(default=None, max_length=512)
    checkpoints_gpx_file: str = Field(max_length=256, unique=True)
    no_laps: int = Field(sa_column_args=(
        CheckConstraint("no_laps > 0", name="no_laps_positive"),
    ))
    meetup_timestamp: Optional[datetime] = Field(default=None)
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
    entry_fee_gr: int = Field(sa_column_args=(
        CheckConstraint("entry_fee_gr >= 0", name="race_entry_fee_non_negative"),
    ))
    event_graphic_file: str = Field(max_length=256, unique=True)

    # these are json/array fields, unfortunately the Oracle driver in sqlalchemy does not support JSON nor ARRAY columns
    # for actual data types, check validators below
    place_to_points_mapping_json: str = Field(max_length=1024)
    sponsor_banners_uuids_json: Optional[str] = Field(max_length=4000)

    celery_task_id: Optional[str] = Field(max_length=256)

    season_id: int = Field(foreign_key="season.id")
    season: "Season" = Relationship(back_populates="races")
    bonuses: list["RaceBonus"] = Relationship(
        back_populates="races",
        link_model=RaceBonusRaceLink
    )
    race_participations: list["RaceParticipation"] = Relationship(back_populates="race")

    @validator("sponsor_banners_uuids_json")
    def validate_sponsor_banners_uuids_json_pydantic(cls, v: str) -> str:
        try:
            jsonschema.validate(json.loads(v), sponsor_banners_uuids_json_schema)
        except jsonschema.exceptions.ValidationError as e:
            raise ValueError("[pydantic] sponsor_banners_uuids_json_schema has wrong JSON schema", e)
        return v

    @validator("place_to_points_mapping_json")
    def validate_place_to_points_mapping_json_pydantic(cls, v: str) -> str:
        try:
            jsonschema.validate(json.loads(v), place_to_points_mapping_json_schema)
        except jsonschema.exceptions.ValidationError as e:
            raise ValueError("[pydantic] place_to_points_mapping_json has wrong JSON schema", e)
        return v


class RaceCreate(SQLModel):
    """
    Model for race creation
    """
    name: str
    description: str
    requirements: str
    meetup_timestamp: Optional[datetime] = Field(default=None)
    start_timestamp: datetime
    end_timestamp: datetime
    entry_fee_gr: int
    checkpoints_gpx_file: str
    event_graphic_file: str
    no_laps: int
    place_to_points_mapping_json: str
    sponsor_banners_uuids_json: str


class RaceUpdate(SQLModel):
    """
    Model for updating race details
    """
    name: str = Field(default=None)
    description: str = Field(default=None)
    status: RaceStatus = Field(default=None)
    requirements: str = Field(default=None)
    meetup_timestamp: datetime = Field(default=None)
    start_timestamp: datetime = Field(default=None)
    end_timestamp: datetime = Field(default=None)
    entry_fee_gr: int = Field(default=None)
    no_laps: int = Field(default=None)
    place_to_points_mapping_json: str = Field(default=None)
    sponsor_banners_uuids_json: str = Field(default=None)
    temperature: RaceTemperature = Field(default=None)
    wind: RaceWind = Field(default=None)
    rain: RaceRain = Field(default=None)


class RaceReadListRider(SQLModel):
    """
    Model for listing a race for a rider
    """
    id: int
    status: RaceStatus
    name: str
    description: str
    no_laps: int
    meetup_timestamp: Optional[datetime] = Field(default=None)
    start_timestamp: datetime
    end_timestamp: datetime
    event_graphic_file: str
    participation_status: Optional["RaceParticipationStatus"] = Field(default=None)
    season_id: int = Field(foreign_key="season.id")
    is_approved: bool


class RaceReadDetailRider(SQLModel):
    """
    Model for listing race details for a rider
    """
    id: int
    status: RaceStatus
    name: str
    description: str
    requirements: Optional[str] = Field(default=None)
    no_laps: int
    meetup_timestamp: Optional[datetime] = Field(default=None)
    start_timestamp: datetime
    end_timestamp: datetime
    event_graphic_file: str
    checkpoints_gpx_file: str
    entry_fee_gr: int
    season: "SeasonRead"
    bonuses: list["RaceBonusListRead"]
    participation_status: Optional["RaceParticipationStatus"] = Field(default=None)
    race_participations: list["RaceParticipationCoordinatorListRead"] = Field(default=None)
    place_to_points_mapping_json: str
    sponsor_banners_uuids_json: Optional[str] = Field(max_length=4000)
    is_approved: bool


class RaceReadListCoordinator(SQLModel):
    """
    Model for listing a race for a coordinator
    """
    id: int
    status: RaceStatus
    name: str
    description: str
    no_laps: int
    meetup_timestamp: Optional[datetime] = Field(default=None)
    start_timestamp: datetime
    end_timestamp: datetime
    event_graphic_file: str
    season_id: int = Field(foreign_key="season.id")
    is_approved: bool


class RaceReadDetailCoordinator(SQLModel):
    """
    Model for listing race details for a coordinator
    """
    id: int
    status: RaceStatus
    name: str
    description: str
    requirements: Optional[str] = Field(default=None)
    no_laps: int
    meetup_timestamp: Optional[datetime] = Field(default=None)
    start_timestamp: datetime
    end_timestamp: datetime
    event_graphic_file: str
    checkpoints_gpx_file: str
    entry_fee_gr: int
    season: "SeasonRead"
    bonuses: list["RaceBonusListRead"]
    race_participations: list["RaceParticipationListReadNames"] = Field(default=None)
    temperature: Optional[RaceTemperature]
    rain: Optional[RaceRain]
    wind: Optional[RaceWind]
    place_to_points_mapping_json: str
    sponsor_banners_uuids_json: Optional[str]
    is_approved: bool


class RaceReadUpdatedCoordinator(SQLModel):
    """
    Model for reading an updated race for a coordinator
    """
    id: int
    status: RaceStatus
    name: str
    description: str
    requirements: Optional[str] = Field(default=None)
    no_laps: int
    meetup_timestamp: Optional[datetime] = Field(default=None)
    start_timestamp: datetime
    end_timestamp: datetime
    event_graphic_file: str
    checkpoints_gpx_file: str
    entry_fee_gr: int
    season: "SeasonRead"
    bonuses: list["RaceBonusListRead"]
    race_participations: list["RaceParticipationCoordinatorListRead"] = Field(default=None)
    temperature: Optional[RaceTemperature]
    rain: Optional[RaceRain]
    wind: Optional[RaceWind]
    place_to_points_mapping_json: str
    sponsor_banners_uuids_json: Optional[str]
    is_approved: bool
