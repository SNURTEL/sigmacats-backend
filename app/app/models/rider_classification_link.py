from typing import Optional

from sqlmodel import Field, SQLModel, Relationship, CheckConstraint


class RiderClassificationLink(SQLModel, table=True):
    score: int = Field(sa_column_args=(
        CheckConstraint("score >= 0", name="rider_classification_link_score_non_negative"),
    ))

    rider_id: Optional[int] = Field(
        foreign_key="rider.id", primary_key=True, default=None
    )
    # rider: "Rider" = Relationship(back_populates="classification_links", sa_relationship_kwargs={"viewonly": True})
    classification_id: Optional[int] = Field(
        foreign_key="classification.id", primary_key=True, default=None,
    )
