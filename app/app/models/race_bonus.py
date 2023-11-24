from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, SQLModel, Relationship

from .race_bonus_race_link import RaceBonusRaceLink

if TYPE_CHECKING:
    from .race import Race


class RaceBonus(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(max_length=80, unique=True)
    rule: str = Field(max_length=512)
    points_multiplier: float

    races: list["Race"] = Relationship(
        back_populates="bonuses",
        link_model=RaceBonusRaceLink
    )
