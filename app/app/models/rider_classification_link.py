from typing import Optional

from sqlmodel import Field, SQLModel, Relationship


# class RiderClassificationLink(SQLModel, table=True):
#     score: int
#
#     rider_id: Optional[int] = Field(
#         foreign_key="rider.id", primary_key=True, default=None
#     )
#     classification_id: Optional[int] = Field(
#         foreign_key="classification.id", primary_key=True, default=None
#     )
