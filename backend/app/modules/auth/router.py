from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.modules.auth.schemas import UserCreate, UserLogin, Token, TokenRefresh, UserResponse
from app.modules.auth.service import AuthService
from app.modules.auth.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await AuthService.register(db, user_data.email, user_data.password, user_data.first_name, user_data.last_name)
    return UserResponse(id=str(user.id), email=user.email, first_name=user.first_name, last_name=user.last_name, is_active=user.is_active)


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    return await AuthService.login(db, credentials.email, credentials.password)


@router.post("/refresh", response_model=Token)
async def refresh(token_data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    return await AuthService.refresh(db, token_data.refresh_token)


@router.post("/logout")
async def logout(token_data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    return await AuthService.logout(db, token_data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        is_active=current_user.is_active,
        roles=[role.name for role in current_user.roles]
    )


@router.get("/admin-only")
async def admin_only(current_user: User = Depends(require_role("admin"))):
    return {"message": "Admin access granted", "user": current_user.email}
