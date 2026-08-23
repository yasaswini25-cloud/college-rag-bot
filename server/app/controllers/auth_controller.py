from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth_service import AuthService
from app.models.user import User

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "STUDENT"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthController:
    @staticmethod
    async def register(db: AsyncSession, req: RegisterRequest):
        return await AuthService.register_user(
            db=db,
            name=req.name,
            email=req.email,
            password=req.password,
            role=req.role
        )

    @staticmethod
    async def login(db: AsyncSession, req: LoginRequest):
        return await AuthService.authenticate_user(
            db=db,
            email=req.email,
            password=req.password
        )

    @staticmethod
    async def get_me(user: User):
        return {"user": user.to_dict()}
