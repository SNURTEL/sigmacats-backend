from typing import Optional

from sqlmodel import Field, SQLModel, Relationship

# from .season import Season
from .access_limiter_classification_link import AccessLimiterClassificationLink
from .rider_classification_link import RiderClassificationLink


class Classification(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(max_length=80)
    description: str = Field(max_length=512)

    season_id: int = Field(foreign_key="season.id")
    season: "Season" = Relationship(back_populates="classifications")

    access_limiters: list["ClassificationAccessLimiter"] = Relationship(
        back_populates="classifications",
        link_model=AccessLimiterClassificationLink
    )

    riders: list["Rider"] = Relationship(
        back_populates="classifications",
        link_model=RiderClassificationLink,
    )

