from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_db

from app.models.rider import Rider, RiderRead

router = APIRouter()


@router.get("/{id}/rider")
async def read_riders(
        id: int,
        db: Session = Depends(get_db),
) -> list[RiderRead]:
    """
    List all riders for a given classification.
    """
    stmt = (
        select(Rider)
        .where(id in [classification.id for classification in Rider.classifications])
    )

    riders = db.exec(stmt).all()

    if not riders or len(riders) == 0:
        raise HTTPException(404)

    return [RiderRead.from_orm(r) for r in riders]
