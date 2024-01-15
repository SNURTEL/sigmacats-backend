from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, SQLModel, Relationship

from .rider_classification_link import RiderClassificationLink  # noqa: F811,

if TYPE_CHECKING:
    from .rider import Rider
    from .season import Season
    from .ride_participation_classification_place import RiderParticipationClassificationPlace
    from .rider_classification_link import RiderClassificationLink  # noqa F811


class Classification(SQLModel, table=True):
    """
    Full model of race classification
    """
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(max_length=80)
    description: str = Field(max_length=512)

    season_id: int = Field(foreign_key="season.id")
    season: "Season" = Relationship(back_populates="classifications")

    riders: list["Rider"] = Relationship(
        back_populates="classifications",
        link_model=RiderClassificationLink,
        sa_relationship_kwargs={
            "viewonly": True
        }
    )

    race_participation_places: list["RiderParticipationClassificationPlace"] = Relationship(
        back_populates="classification",
        sa_relationship_kwargs={"cascade": "delete"})

    rider_links: list["RiderClassificationLink"] = Relationship(back_populates="classification")


class ClassificationRead(SQLModel):
    """
    Model for reading race classification
    """
    id: int
    name: str
    description: str
