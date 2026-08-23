from sqlalchemy.ext.asyncio import AsyncSession
from app.services.admin_service import AdminService

class AdminController:
    @staticmethod
    async def get_dashboard(db: AsyncSession):
        return await AdminService.get_dashboard_metrics(db=db)

    @staticmethod
    async def get_analytics(db: AsyncSession):
        return await AdminService.get_dashboard_metrics(db=db)
