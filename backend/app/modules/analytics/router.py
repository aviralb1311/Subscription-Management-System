from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.analytics.service import AnalyticsService

router = APIRouter()


@router.get("/overview")
async def get_overview(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await AnalyticsService.get_overview(db, str(current_user.id), [role.name for role in current_user.roles])


@router.get("/revenue")
async def get_revenue(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await AnalyticsService.get_revenue(db, str(current_user.id), [role.name for role in current_user.roles])


@router.get("/subscriptions")
async def get_subscriptions(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await AnalyticsService.get_subscriptions(db, str(current_user.id), [role.name for role in current_user.roles])
