from sqlmodel import Field, SQLModel


class AccessLimiterClassificationLink(SQLModel, table=True):
    access_limiter_id: int = Field(
        foreign_key="classificationaccesslimiter.id", primary_key=True
    )
    classification_id: int = Field(
        foreign_key="classification.id", primary_key=True
    )
