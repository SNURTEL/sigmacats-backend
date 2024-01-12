from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar
import datetime

from app.db.session import get_db

from app.models.classification import Classification, ClassificationRead
from app.models.season import Season, SeasonListRead

router = APIRouter()


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
async def read_current_season(db: Session = Depends(get_db)) -> SeasonListRead:
    """
    Get the current season.
    """
    current_date = datetime.datetime.now()
    stmt: SelectOfScalar = (
        select(Season)
        .where(Season.start_timestamp <= current_date)
        .where(current_date <= Season.end_timestamp)
    )
    season = db.exec(stmt).first()

    if not season:
        raise HTTPException(404)

    return SeasonListRead.from_orm(season)
