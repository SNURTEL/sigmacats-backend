from typing import TYPE_CHECKING

from sqlmodel import Field, SQLModel, CheckConstraint, Relationship

if TYPE_CHECKING:
    from .race_participation import RaceParticipation
    from .classification import Classification


class RiderParticipationClassificationPlace(SQLModel, table=True):
    """
    Full model for RiderParticipationClassificationPlace, place of a rider in given classification
    """
    place: int = Field(sa_column_args=(
        CheckConstraint("place > 0", name="rider_participation_classification_place_place_positive"),
    ))

    race_participation_id: int = Field(
        foreign_key="raceparticipation.id", primary_key=True
    )
    race_participation: "RaceParticipation" = Relationship(back_populates="classification_places")

    clasification_id: int = Field(
        foreign_key="classification.id", primary_key=True
    )
    classification: "Classification" = Relationship(back_populates="race_participation_places")
