from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class SubscriptionCreateFromQuotation(BaseModel):
    quotation_id: str
    start_date: Optional[datetime] = None


class SubscriptionUpdate(BaseModel):
    notes: Optional[str] = None


class SubscriptionResponse(BaseModel):
    id: str
    subscription_number: str
    customer_id: str
    quotation_id: Optional[str] = None
    status: str
    currency: str
    amount: Decimal
    unit_price: Decimal
    quantity: int
    start_date: Optional[datetime] = None
    next_billing_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
