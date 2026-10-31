from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import csv
import io
from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.auth.models import User
from app.modules.payments.service import PaymentService
from app.modules.payments.schemas import PaymentCreate, PaymentAllocate, CreditNoteCreate, RefundCreate, PaymentResponse

router = APIRouter()


@router.post("/", response_model=PaymentResponse)
async def record_payment(data: PaymentCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await PaymentService.record_payment(db, data.model_dump(), str(current_user.id), [role.name for role in current_user.roles])


@router.post("/allocate", response_model=PaymentResponse)
async def allocate_payment(data: PaymentAllocate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await PaymentService.allocate(db, data.payment_id, [a.model_dump() for a in data.allocations], str(current_user.id), [role.name for role in current_user.roles])


@router.get("/", response_model=List[PaymentResponse])
async def list_payments(skip: int = 0, limit: int = Query(default=100, le=100), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await PaymentService.list_payments(db, skip, limit, str(current_user.id), [role.name for role in current_user.roles])


@router.post("/credit-notes")
async def create_credit_note(data: CreditNoteCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await PaymentService.create_credit_note(db, data.model_dump(), str(current_user.id), [role.name for role in current_user.roles])


@router.post("/refunds")
async def create_refund(data: RefundCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await PaymentService.create_refund(db, data.model_dump(), str(current_user.id), [role.name for role in current_user.roles])


@router.post("/reconcile/csv")
async def reconcile_csv(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    content = await file.read()
    decoded = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    rows = list(reader)
    return await PaymentService.reconcile_csv(db, rows, str(current_user.id), [role.name for role in current_user.roles])
