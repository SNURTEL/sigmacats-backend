from fastapi import APIRouter

from app.api.coordinator.race import router as races_router

router = APIRouter()
router.include_router(races_router, prefix="/race")
