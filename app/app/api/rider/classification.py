from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar

from app.db.session import get_db

from app.models.rider import RiderRead
from app.models.classification import Classification

router = APIRouter()


@router.get("/{id}/rider")
async def read_riders(
        id: int,
        db: Session = Depends(get_db),
) -> list[RiderRead]:
    """
    List all riders for a given classification.
    """
    stmt: SelectOfScalar = (
        select(Classification)
        .where(Classification.id == id)
    )

    classification = db.exec(stmt).first()

    if not classification:
        raise HTTPException(404)

    if not classification.riders or len(classification.riders) == 0:
        raise HTTPException(404)

    return [RiderRead.from_orm(r) for r in classification.riders]
