from sqlmodel import Field, SQLModel


class RaceBonusRaceLink(SQLModel, table=True):
    """
    Full model of a link entity between race and race bonus
    """
    race_bonus_id: int = Field(
        foreign_key="racebonus.id", primary_key=True
    )
    race_id: int = Field(
        foreign_key="race.id", primary_key=True
    )
