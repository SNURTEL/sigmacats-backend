from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar

from app.db.session import get_db

from app.models.rider_classification_link import (
    RiderClassificationLink,
    RiderClassificationLinkRead,
    RiderClassificationLinkRiderDetails)
from app.api.rider.classification import read_riders

router = APIRouter()

"""
This file contains API functions for rider related to rider and classification link
"""

@router.get("/{classification_id}/classification")
async def read_scores_from_classification(
        classification_id: int,
        db: Session = Depends(get_db)
) -> list[RiderClassificationLinkRiderDetails]:
    """
    Read all scores from given classification.
    """
    stmt: SelectOfScalar = (
        select(RiderClassificationLink)
        .where(RiderClassificationLink.classification_id == classification_id)
    )
    links = db.exec(stmt).all()

    if not links or len(links) <= 0:
        raise HTTPException(404)

    links_parsed = [RiderClassificationLinkRead.from_orm(s) for s in links]
    riders = await read_riders(classification_id, db)
    scores = []

    for link in links_parsed:
        for rider in riders:
            if rider.id == link.rider_id:
                scores.append(RiderClassificationLinkRiderDetails(
                    score=link.score,
                    name=rider.account.name,
                    surname=rider.account.surname,
                    username=rider.account.username)
                )

    return sorted(scores, key=lambda x: x.score, reverse=True)


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
