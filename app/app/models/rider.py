from sqlmodel import Field, SQLModel, Relationship

from .rider_classification_link import RiderClassificationLink
# from .account import Account


class Rider(SQLModel, table=True):
    id: int = Field(foreign_key="account.id", primary_key=True)
    account: "Account" = Relationship(back_populates="rider")

    bikes: list["Bike"] = Relationship(back_populates="rider")
    classifications: list["Classification"] = Relationship(
        back_populates="riders",
        link_model=RiderClassificationLink,
    )
    race_participations: list["RaceParticipation"] = Relationship(back_populates="rider")
    classification_links: list["RiderClassificationLink"] = Relationship(sa_relationship_kwargs={
        "backref": "riderclassificationlink",
        "viewonly": True
    })
