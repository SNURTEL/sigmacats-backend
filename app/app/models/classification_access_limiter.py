from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, SQLModel, Relationship

from .access_limiter_classification_link import AccessLimiterClassificationLink

if TYPE_CHECKING:
    from .classification import Classification


class ClassificationAccessLimiter(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(max_length=80, unique=True)
    rule: str = Field(max_length=512)

    classifications: list["Classification"] = Relationship(
        back_populates="access_limiters",
        link_model=AccessLimiterClassificationLink
    )
