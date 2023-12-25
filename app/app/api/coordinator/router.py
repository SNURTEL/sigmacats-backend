from fastapi import APIRouter, Depends

from app.core.users import current_coordinator_user
from app.api.coordinator.race import router as races_router

router = APIRouter(dependencies=[Depends(current_coordinator_user)])
router.include_router(races_router, prefix="/race")
