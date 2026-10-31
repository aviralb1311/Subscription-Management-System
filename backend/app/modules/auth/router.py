from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.modules.auth.schemas import (
    UserCreate,
    UserLogin,
    Token,
    TokenRefresh,
    UserResponse,
)
from app.modules.auth.service import AuthService
from app.modules.auth.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


def _name_parts(full_name):
    parts = (full_name or "").split(maxsplit=1)
    return (parts[0] if parts else None, parts[1] if len(parts) > 1 else None)


def _user_response(user: User):
    first_name, last_name = _name_parts(user.full_name)
    return UserResponse(
        id=str(user.id),
        email=user.email,
        first_name=first_name,
        last_name=last_name,
        is_active=user.is_active,
        roles=[role.name for role in user.roles],
    )


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await AuthService.register(
        db,
        user_data.email,
        user_data.password,
        user_data.first_name,
        user_data.last_name,
    )
    return _user_response(user)


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
    return _user_response(current_user)


@router.get("/admin-only")
async def admin_only(current_user: User = Depends(require_role("admin"))):
    return {"message": "Admin access granted", "user": current_user.email}
