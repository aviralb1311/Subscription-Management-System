from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from decimal import Decimal


class QuotationLineCreate(BaseModel):
    product_id: Optional[str] = None
    product_variant_id: Optional[str] = None
    plan_id: Optional[str] = None
    plan_version_id: Optional[str] = None
    description: Optional[str] = None
    quantity: Decimal
    # unit_price removed - derived from DB for plan lines


class QuotationLineResponse(BaseModel):
    id: str
    product_id: Optional[str] = None
    plan_id: Optional[str] = None
    plan_version_id: Optional[str] = None
    description: Optional[str] = None
    quantity: Decimal
    unit_price: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    line_total: Decimal

    class Config:
        from_attributes = True


class QuotationCreate(BaseModel):
    customer_id: str
    valid_until: Optional[datetime] = None
    notes: Optional[str] = None
    currency: str = "USD"
    lines: List[QuotationLineCreate]


class QuotationResponse(BaseModel):
    id: str
    quotation_number: str
    customer_id: str
    status: str
    valid_until: Optional[datetime] = None
    subtotal: Decimal
    discount_total: Decimal
    tax_total: Decimal
    total: Decimal
    currency: str
    notes: Optional[str] = None
    lines: List[QuotationLineResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True
