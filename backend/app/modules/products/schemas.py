from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ProductBase(BaseModel):
    name: str
    code: Optional[str] = None
    product_type: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    cost_price: Decimal = Decimal(0)
    sales_price: Decimal = Decimal(0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    product_type: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    cost_price: Optional[Decimal] = None
    sales_price: Optional[Decimal] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductVariantBase(BaseModel):
    name: str
    sku: Optional[str] = None
    attributes: Optional[str] = None
    price_adjustment: Decimal = Decimal(0)


class ProductVariantCreate(ProductVariantBase):
    pass


class ProductVariantResponse(ProductVariantBase):
    id: str
    product_id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PlanBase(BaseModel):
    name: str
    code: Optional[str] = None
    product_id: Optional[str] = None
    billing_cycle: str = Field(..., pattern="^(daily|weekly|monthly|yearly)$")
    auto_close: bool = False
    allow_pause_resume: bool = True


class PlanCreate(PlanBase):
    price: Decimal = Decimal(0)
    currency: str = "USD"


class PlanUpdate(BaseModel):
    name: Optional[str] = None
    billing_cycle: Optional[str] = Field(None, pattern="^(daily|weekly|monthly|yearly)$")
    is_active: Optional[bool] = None
    auto_close: Optional[bool] = None
    allow_pause_resume: Optional[bool] = None


class PlanVersionResponse(BaseModel):
    id: str
    version: int
    price: Decimal
    currency: str
    effective_from: datetime
    effective_to: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class PlanResponse(PlanBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    versions: List[PlanVersionResponse] = []

    class Config:
        from_attributes = True
