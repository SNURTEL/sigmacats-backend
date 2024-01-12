from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar

from app.db.session import get_db

from app.models.rider_classification_link import RiderClassificationLink, RiderClassificationLinkRead

router = APIRouter()


@router.get("/{classification_id}/classification")
async def read_scores_from_classification(
        classification_id: int,
        db: Session = Depends(get_db)
) -> list[RiderClassificationLinkRead]:
    """
    Read all scores from given classification.
    """
    stmt: SelectOfScalar = (
        select(RiderClassificationLink)
        .where(RiderClassificationLink.classification_id == classification_id)
    )
    scores = db.exec(stmt).all()

    if not scores or len(scores) <= 0:
        raise HTTPException(404)

    return [RiderClassificationLinkRead.from_orm(s) for s in scores]


@router.get("/{rider_id}/rider")
async def read_scores_from_rider(
        rider_id: int,
        db: Session = Depends(get_db)
) -> list[RiderClassificationLinkRead]:
    """
    Read all scores from given rider.
    """
    stmt: SelectOfScalar = (
        select(RiderClassificationLink)
        .where(RiderClassificationLink.rider_id == rider_id)
    )
    scores = db.exec(stmt).all()

    if not scores or len(scores) <= 0:
        raise HTTPException(404)

    return [RiderClassificationLinkRead.from_orm(s) for s in scores]
