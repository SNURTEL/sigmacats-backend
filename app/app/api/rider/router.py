from fastapi import APIRouter

from app.api.rider.race import router as races_router
from app.api.rider.bike import router as bikes_router


router = APIRouter()

router.include_router(races_router, prefix="/race")
router.include_router(bikes_router, prefix="/bike")
