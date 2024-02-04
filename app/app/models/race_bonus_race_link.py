from sqlmodel import Field, SQLModel


class RaceBonusRaceLink(SQLModel, table=True):
    race_bonus_id: int = Field(
        foreign_key="racebonus.id", primary_key=True
    )
    race_id: int = Field(
        foreign_key="race.id", primary_key=True
    )
