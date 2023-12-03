from fastapi import APIRouter

from app.api.rider.router import router as rider_router
from app.api.coordinator.router import router as coordinator_router
from app.api.admin.router import router as admin_router

api_router = APIRouter()
api_router.include_router(rider_router, prefix="/rider", tags=["rider"])
api_router.include_router(coordinator_router, prefix="/coordinator", tags=["coordinator"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
