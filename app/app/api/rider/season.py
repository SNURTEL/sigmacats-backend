from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_db

from app.models.classification import Classification, ClassificationRead

router = APIRouter()


@router.get("/{id}/classification")
async def read_classifications(
        id: int,
        db: Session = Depends(get_db),
) -> list[ClassificationRead]:
    """
    List all classifications for a given season.
    """
    stmt = (
        select(Classification)
        .where(Classification.season.id == id)
    )
    classifications = db.exec(stmt).all()

    return [ClassificationRead.from_orm(c) for c in classifications]
