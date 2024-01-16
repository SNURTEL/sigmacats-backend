from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_db
from app.models.classification import Classification
from app.models.season import Season, SeasonRead, SeasonStart

router = APIRouter()


"""
This file contains API functions available to race coordinators related to league seasons
"""

# mypy: disable-error-code=var-annotated

@router.get("/")
async def read_seasons(
        db: Session = Depends(get_db), limit: int = 30, offset: int = 0
) -> list[SeasonRead]:
    """
    List all seasons.
    """
    stmt = (
        select(Season)
        .offset(offset)
        .limit(limit)
        .order_by(Season.start_timestamp.desc())  # type: ignore[arg-type, attr-defined]
    )
    seasons = db.exec(stmt).all()

    return seasons  # type: ignore[return-value]


@router.get("/{id}")
async def read_season(
        id: int, db: Session = Depends(get_db)
) -> SeasonRead:
    """
    Get details about a specific season.
    """
    season = db.get(Season, id)

    if not season:
        raise HTTPException(404)

    return season  # type: ignore[return-value]


@router.post("/start-new", status_code=201)
async def start_new_season(
        season_start: SeasonStart, db: Session = Depends(get_db)
) -> SeasonRead:
    """
    End the current season and start a new one.
    """
    if len(season_start.name) == 0:
        raise HTTPException(400, "Name cannot be empty.")

    now = datetime.now()
    current_season = db.exec(
        select(Season)
        .order_by(Season.start_timestamp.desc())  # type: ignore[attr-defined]
    ).first()

    if not current_season:
        print(db.exec(select(Season)).all())
        raise HTTPException(500, "Could not find current season")

    current_season.end_timestamp = now
    db.add(current_season)

    new_season = Season(
        name=season_start.name,
        start_timestamp=now
    )
    db.add(new_season)
    db.add_all(create_new_classifications(new_season))
    db.commit()

    return new_season  # type: ignore[return-value]


def create_new_classifications(season: Season) -> list[Classification]:
    """
    Create new classifications for a season
    """
    return [
        Classification(
            name="Klasyfikacja generalna",
            description="Bez ograniczeń.",
            season=season,
        ),
        Classification(
            name="Szosa",
            description="Rowery szosowe z przerzutkami.",
            season=season,
        ),
        Classification(
            name="Ostre koło",
            description="Rowery typu fixie i singlespeed. Brak przerzutek.",
            season=season,
        ),
        Classification(
            name="Mężczyźni",
            description="Klasyfikacja mężczyzn.",
            season=season,
        ),
        Classification(
            name="Kobiety",
            description="Klasyfikacja kobiet.",
            season=season,
        )]
