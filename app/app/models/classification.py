from typing import Optional

from sqlmodel import Field, SQLModel, Relationship

from .season import Season
from .access_limiter_classification_link import AccessLimiterClassificationLink
from .account import Account
# from .rider_classification_link import RiderClassificationLink




class RiderClassificationLink(SQLModel, table=True):
    score: int

    rider_id: Optional[int] = Field(
        foreign_key="rider.id", primary_key=True, default=None
    )
    classification_id: Optional[int] = Field(
        foreign_key="classification.id", primary_key=True, default=None
    )


class Rider(SQLModel, table=True):
    id: int = Field(foreign_key="account.id", primary_key=True)
    account: Account = Relationship(back_populates="rider")

    bikes: list["Bike"] = Relationship(back_populates="rider")
    classifications: list["Classification"] = Relationship(
        back_populates="riders",
        link_model=RiderClassificationLink,
    )
    race_participations: list["RaceParticipation"] = Relationship(back_populates="rider")


class Classification(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(max_length=80)
    description: str = Field(max_length=512)

    season_id: int = Field(foreign_key="season.id")
    season: Season = Relationship(back_populates="classifications")

    access_limiters: list["ClassificationAccessLimiter"] = Relationship(
        back_populates="classifications",
        link_model=AccessLimiterClassificationLink
    )

    riders: list["Rider"] = Relationship(
        back_populates="classifications",
        link_model=RiderClassificationLink,
    )


