from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, SQLModel, Relationship

# from .season import Season
from .rider_classification_link import RiderClassificationLink

if TYPE_CHECKING:
    from .rider import Rider
    from .season import Season
    from .ride_participation_classification_place import RiderParticipationClassificationPlace


class Classification(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(max_length=80)
    description: str = Field(max_length=512)

    season_id: int = Field(foreign_key="season.id")
    season: "Season" = Relationship(back_populates="classifications")

    riders: list["Rider"] = Relationship(
        back_populates="classifications",
        link_model=RiderClassificationLink,
    )

    race_participation_places: list["RiderParticipationClassificationPlace"] = Relationship(
        back_populates="classification")


class ClassificationRead(SQLModel):
    id: int
    name: str
    description: str
    season_id: int = Field(foreign_key="season.id")
    season: "Season"
    riders: list["Rider"]
    race_participation_places: list["RiderParticipationClassificationPlace"]
