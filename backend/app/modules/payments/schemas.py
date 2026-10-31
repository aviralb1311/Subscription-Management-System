from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class PaymentCreate(BaseModel):
    customer_id: str
    amount: Decimal
    currency: str = "USD"
    payment_method: Optional[str] = None
    external_reference: Optional[str] = None
    idempotency_key: Optional[str] = None
    notes: Optional[str] = None


class AllocationItem(BaseModel):
    invoice_id: str
    amount: Decimal


class PaymentAllocate(BaseModel):
    payment_id: str
    allocations: List[AllocationItem]


class CreditNoteCreate(BaseModel):
    invoice_id: str
    amount: Decimal
    reason: Optional[str] = None


class RefundCreate(BaseModel):
    payment_id: Optional[str] = None
    credit_note_id: Optional[str] = None
    customer_id: str
    amount: Decimal
    currency: str = "USD"
    reason: Optional[str] = None


class PaymentResponse(BaseModel):
    id: str
    payment_number: str
    customer_id: str
    amount: Decimal
    currency: str
    status: str
    unallocated_amount: Optional[Decimal] = None
    created_at: datetime

    class Config:
        from_attributes = True
