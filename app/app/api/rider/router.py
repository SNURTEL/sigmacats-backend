from fastapi import APIRouter, Depends

from app.core.users import current_rider_user
from app.api.rider.race import router as races_router
from app.api.rider.season import router as season_router
from app.api.rider.classification import router as classification_router
from app.api.rider.bike import router as bikes_router
from app.api.rider.rider_classification_link import router as link_router

"""
This file creates APIRouter for a rider
"""

router = APIRouter(dependencies=[Depends(current_rider_user)])

router.include_router(races_router, prefix="/race")
router.include_router(season_router, prefix="/season")
router.include_router(classification_router, prefix="/classification")
router.include_router(bikes_router, prefix="/bike")
router.include_router(link_router, prefix="/rider_classification_link")
