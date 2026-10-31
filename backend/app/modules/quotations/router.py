from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.modules.auth.models import User
from app.modules.quotations.schemas import QuotationCreate, QuotationResponse
from app.modules.quotations.service import QuotationService

router = APIRouter(prefix="/quotations", tags=["quotations"])


@router.post("/", response_model=QuotationResponse)
async def create_quotation(quotation: QuotationCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await QuotationService.create(db, quotation.model_dump(), str(current_user.id), [role.name for role in current_user.roles])


@router.get("/", response_model=List[QuotationResponse])
async def list_quotations(skip: int = 0, limit: int = Query(default=100, le=100), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await QuotationService.list(db, skip, limit, str(current_user.id), [role.name for role in current_user.roles])


@router.get("/{quotation_id}", response_model=QuotationResponse)
async def get_quotation(quotation_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await QuotationService.get(db, quotation_id, str(current_user.id), [role.name for role in current_user.roles])


@router.post("/{quotation_id}/send")
async def send_quotation(quotation_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role("admin", "staff"))):
    return await QuotationService.update_status(db, quotation_id, "sent", str(current_user.id), [role.name for role in current_user.roles])


@router.post("/{quotation_id}/accept")
async def accept_quotation(quotation_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await QuotationService.update_status(db, quotation_id, "accepted", str(current_user.id), [role.name for role in current_user.roles])


@router.post("/{quotation_id}/convert")
async def convert_quotation(quotation_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role("admin", "staff"))):
    return await QuotationService.update_status(db, quotation_id, "converted", str(current_user.id), [role.name for role in current_user.roles])


@router.post("/{quotation_id}/cancel")
async def cancel_quotation(quotation_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role("admin", "staff"))):
    return await QuotationService.update_status(db, quotation_id, "cancelled", str(current_user.id), [role.name for role in current_user.roles])
