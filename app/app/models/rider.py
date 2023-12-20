from typing import TYPE_CHECKING

from sqlmodel import Field, SQLModel, Relationship

from .rider_classification_link import RiderClassificationLink

if TYPE_CHECKING:
    from .race_participation import RaceParticipation
    from .account import Account
    from .classification import Classification
    from .bike import Bike
    from .rider_classification_link import RiderClassificationLink  # noqa: F811


class Rider(SQLModel, table=True):
    id: int = Field(foreign_key="account.id", primary_key=True)
    account: "Account" = Relationship(back_populates="rider")

    bikes: list["Bike"] = Relationship(back_populates="rider")
    classifications: list["Classification"] = Relationship(
        back_populates="riders",
        link_model=RiderClassificationLink,
        sa_relationship_kwargs={
            "viewonly": True
        }
    )
    race_participations: list["RaceParticipation"] = Relationship(back_populates="rider")
    classification_links: list["RiderClassificationLink"] = Relationship(back_populates="rider")


class RiderRead(SQLModel):
    id: int
    account: "Account"
