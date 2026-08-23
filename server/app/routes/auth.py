from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.controllers.auth_controller import AuthController, RegisterRequest, LoginRequest
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await AuthController.register(db, req)

@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await AuthController.login(db, req)

@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully."}

@router.get("/me")
async def get_current_user(user: User = Depends(AuthService.get_current_user)):
    return await AuthController.get_me(user)
