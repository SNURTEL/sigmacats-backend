from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar

from app.db.session import get_db

from app.models.classification import Classification, ClassificationRead
from app.models.season import Season, SeasonRead

router = APIRouter()

"""
This file contains API functions for rider related to seasons
"""


@router.get("/{id}/classification")
async def read_classifications(
        id: int,
        db: Session = Depends(get_db),
) -> list[ClassificationRead]:
    """
    List all classifications for a given season.
    """
    stmt: SelectOfScalar = (
        select(Classification)
        .where(Classification.season_id == id)
    )
    classifications = db.exec(stmt).all()

    if not classifications or len(classifications) <= 0:
        raise HTTPException(404)

    return [ClassificationRead.from_orm(c) for c in classifications]


@router.get("/current")
async def read_current_season(db: Session = Depends(get_db)) -> SeasonRead:
    """
    Get the current season.
    """
    stmt: SelectOfScalar = (
        select(Season)
        .order_by(Season.start_timestamp.desc())  # type: ignore[attr-defined]
    )
    season = db.exec(stmt).first()

    if not season:
        raise HTTPException(404)

    return SeasonRead.from_orm(season)


@router.get("/all")
async def read_all_seasons(db: Session = Depends(get_db)) -> list[SeasonRead]:
    """
    Get all seasons.
    """
    stmt: SelectOfScalar = (
        select(Season)
    )
    seasons = db.exec(stmt).all()

    if not seasons or len(seasons) <= 0:
        raise HTTPException(404)

    return [SeasonRead.from_orm(s) for s in seasons]
