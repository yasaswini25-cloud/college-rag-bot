from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.controllers.admin_controller import AdminController
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/dashboard")
async def get_dashboard(
    user: User = Depends(AuthService.require_admin),
    db: AsyncSession = Depends(get_db)
):
    return await AdminController.get_dashboard(db)

@router.get("/analytics")
async def get_analytics(
    user: User = Depends(AuthService.require_admin),
    db: AsyncSession = Depends(get_db)
):
    return await AdminController.get_analytics(db)
