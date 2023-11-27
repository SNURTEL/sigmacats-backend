from typing import Optional, TYPE_CHECKING
from datetime import datetime
from enum import Enum

import jsonschema

from pydantic import validator

from sqlmodel import Field, SQLModel, Relationship, CheckConstraint
from sqlalchemy.orm import validates

from .race_bonus_race_link import RaceBonusRaceLink

if TYPE_CHECKING:
    from .season import Season
    from .race_bonus import RaceBonus
    from .race_participation import RaceParticipation


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
    }
}


class Race(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    status: RaceStatus = Field(sa_column_args=(
        CheckConstraint("status in ('pending', 'in_progress', 'ended')", name="race_status_enum"),
    ), index=True)
    name: str = Field(max_length=80)
    description: str = Field(max_length=512)
    requirements: Optional[str] = Field(default=None, max_length=512)
    checkpoints_gpx_file: str = Field(max_length=256, unique=True)
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

    season_id: int = Field(foreign_key="season.id")
    season: "Season" = Relationship(back_populates="races")
    bonuses: list["RaceBonus"] = Relationship(
        back_populates="races",
        link_model=RaceBonusRaceLink
    )
    race_participations: list["RaceParticipation"] = Relationship(back_populates="race")

    # SQLAlchemy validators
    @validates("sponsor_banners_uuids_json")
    def validate_sponsor_banners_uuids_json(self, key, race):
        if not jsonschema.validate(race.sponsor_banners_uuids_json, sponsor_banners_uuids_json_schema):
            raise ValueError("[orm] sponsor_banners_uuids_json_schema has wrong JSON schema")
        return race

    @validates("place_to_points_mapping_json")
    def validate_place_to_points_mapping_json(self, key, race):
        if not jsonschema.validate(race.place_to_points_mapping_json, place_to_points_mapping_json_schema):
            raise ValueError("[orm] place_to_points_mapping_json has wrong JSON schema")
        return race

    # Pydantic validators
    @validator("sponsor_banners_uuids_json")
    def validate_sponsor_banners_uuids_json_pydantic(cls, v):
        if not jsonschema.validate(v, sponsor_banners_uuids_json_schema):
            raise ValueError("[pydantic] sponsor_banners_uuids_json_schema has wrong JSON schema")
        return v

    @validator("place_to_points_mapping_json")
    def validate_place_to_points_mapping_json_pydantic(cls, v):
        if not jsonschema.validate(v, place_to_points_mapping_json_schema):
            raise ValueError("[pydantic] place_to_points_mapping_json has wrong JSON schema")
        return v
