from typing import Optional

from sqlmodel import Field, SQLModel, Relationship

from .access_limiter_classification_link import AccessLimiterClassificationLink


class ClassificationAccessLimiter(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(max_length=80, unique=True)
    rule: str = Field(max_length=512)

    classifications: list["Classification"] = Relationship(
        back_populates="access_limiters",
        link_model=AccessLimiterClassificationLink
    )

    access_limiter_classification_link: "AccessLimiterClassificationLink" = Relationship(back_populates="access_limiter")
