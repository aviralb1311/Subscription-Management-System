from pydantic import BaseModel, EmailStr
from typing import Optional, Any
from datetime import datetime


class CustomerBase(BaseModel):
    company_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    tax_id: Optional[str] = None
    billing_address: Optional[Any] = None
    shipping_address: Optional[Any] = None


class CustomerCreate(CustomerBase):
    user_id: Optional[str] = None


class CustomerUpdate(BaseModel):
    company_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    tax_id: Optional[str] = None
    billing_address: Optional[Any] = None
    shipping_address: Optional[Any] = None
    status: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: str
    user_id: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
