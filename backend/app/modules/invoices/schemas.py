from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class InvoiceGenerate(BaseModel):
    subscription_id: str
    billing_period_start: Optional[datetime] = None
    billing_period_end: Optional[datetime] = None
    due_date: Optional[datetime] = None


class InvoiceResponse(BaseModel):
    id: str
    invoice_number: str
    customer_id: str
    subscription_id: Optional[str] = None
    currency: str
    status: str
    issue_date: datetime
    due_date: Optional[datetime] = None
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    created_at: datetime

    class Config:
        from_attributes = True
