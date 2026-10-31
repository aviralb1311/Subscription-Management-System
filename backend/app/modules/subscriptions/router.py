from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.subscriptions.service import SubscriptionService
from app.modules.subscriptions.schemas import SubscriptionCreateFromQuotation, SubscriptionResponse

router = APIRouter()


@router.post("/from-quotation", response_model=SubscriptionResponse)
async def create_from_quotation(data: SubscriptionCreateFromQuotation, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await SubscriptionService.create_from_quotation(db, data.quotation_id, str(current_user.id), [role.name for role in current_user.roles], data.start_date)


@router.get("/", response_model=List[SubscriptionResponse])
async def list_subscriptions(skip: int = 0, limit: int = Query(default=100, le=100), status: Optional[str] = None, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await SubscriptionService.list(db, skip, limit, str(current_user.id), [role.name for role in current_user.roles], status)


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(subscription_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await SubscriptionService.get(db, subscription_id, str(current_user.id), [role.name for role in current_user.roles])


@router.post("/{subscription_id}/pause", response_model=SubscriptionResponse)
async def pause_subscription(subscription_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await SubscriptionService.pause(db, subscription_id, str(current_user.id), [role.name for role in current_user.roles])


@router.post("/{subscription_id}/resume", response_model=SubscriptionResponse)
async def resume_subscription(subscription_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await SubscriptionService.resume(db, subscription_id, str(current_user.id), [role.name for role in current_user.roles])


@router.post("/{subscription_id}/cancel", response_model=SubscriptionResponse)
async def cancel_subscription(subscription_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await SubscriptionService.cancel(db, subscription_id, str(current_user.id), [role.name for role in current_user.roles])


@router.post("/{subscription_id}/close", response_model=SubscriptionResponse)
async def close_subscription(subscription_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await SubscriptionService.close(db, subscription_id, str(current_user.id), [role.name for role in current_user.roles])


@router.post("/{subscription_id}/renew", response_model=SubscriptionResponse)
async def renew_subscription(subscription_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await SubscriptionService.renew(db, subscription_id, str(current_user.id), [role.name for role in current_user.roles])
