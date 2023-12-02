from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.session import get_db

from app.models.bike import Bike

from app.api.rider.race import router as races_router


router = APIRouter()

router.include_router(races_router, prefix="/race")

# @router.get('/bikes')
# async def read_bikes(
#     db: Session = Depends(get_db), limit: int = 30,  offset: int = 0
# ) -> list[Bike]:
#     stmt = (
#         select(Bike)
#         .offset(offset)
#         .limit(limit)
#     )
#     bikes = db.exec(stmt).all()
#
#     return bikes
