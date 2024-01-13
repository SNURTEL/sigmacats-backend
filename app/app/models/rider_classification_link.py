from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, SQLModel, CheckConstraint, Relationship

if TYPE_CHECKING:
    from .rider import Rider
    from .classification import Classification


class RiderClassificationLink(SQLModel, table=True):
    score: int = Field(sa_column_args=(
        CheckConstraint("score >= 0", name="rider_classification_link_score_non_negative"),
    ), default=0)

    rider_id: Optional[int] = Field(
        foreign_key="rider.id", primary_key=True, default=None
    )
    # rider: "Rider" = Relationship(back_populates="classification_links", sa_relationship_kwargs={"viewonly": True})
    classification_id: Optional[int] = Field(
        foreign_key="classification.id", primary_key=True, default=None,
    )

    rider: "Rider" = Relationship(back_populates="classification_links")
    classification: "Classification" = Relationship(back_populates="rider_links")


class RiderClassificationLinkRead(SQLModel):
    score: int
    rider_id: int
    classification_id: int


class RiderClassificationLinkRiderDetails(SQLModel):
    score: int
    name: str
    surname: str
    username: str
