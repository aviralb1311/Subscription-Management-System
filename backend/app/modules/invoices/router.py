from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.auth.models import User
from app.modules.invoices.service import InvoiceService
from app.modules.invoices.pdf_service import InvoicePDFService
from app.modules.invoices.schemas import InvoiceGenerate, InvoiceResponse

router = APIRouter()


@router.post("/generate", response_model=InvoiceResponse)
async def generate_invoice(data: InvoiceGenerate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await InvoiceService.generate_from_subscription(db, data.subscription_id, str(current_user.id), [role.name for role in current_user.roles], data.billing_period_start, data.billing_period_end, data.due_date)


@router.get("/", response_model=List[InvoiceResponse])
async def list_invoices(skip: int = 0, limit: int = Query(default=100, le=100), status: Optional[str] = None, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await InvoiceService.list(db, skip, limit, str(current_user.id), [role.name for role in current_user.roles], status)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await InvoiceService.get(db, invoice_id, str(current_user.id), [role.name for role in current_user.roles])


@router.post("/{invoice_id}/confirm", response_model=InvoiceResponse)
async def confirm_invoice(invoice_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await InvoiceService.update_status(db, invoice_id, "confirmed", str(current_user.id), [role.name for role in current_user.roles])


@router.post("/{invoice_id}/pay", response_model=InvoiceResponse)
async def pay_invoice(invoice_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await InvoiceService.update_status(db, invoice_id, "paid", str(current_user.id), [role.name for role in current_user.roles])


@router.post("/{invoice_id}/cancel", response_model=InvoiceResponse)
async def cancel_invoice(invoice_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await InvoiceService.update_status(db, invoice_id, "cancelled", str(current_user.id), [role.name for role in current_user.roles])


@router.post("/{invoice_id}/void", response_model=InvoiceResponse)
async def void_invoice(invoice_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await InvoiceService.update_status(db, invoice_id, "void", str(current_user.id), [role.name for role in current_user.roles])


@router.get("/{invoice_id}/pdf")
async def get_invoice_pdf(invoice_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    invoice = await InvoiceService.get(db, invoice_id, str(current_user.id), [role.name for role in current_user.roles])
    pdf_bytes = InvoicePDFService.generate_pdf(invoice)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={invoice.invoice_number}.pdf"})
