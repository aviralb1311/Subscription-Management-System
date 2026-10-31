from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric, Text, JSON, Integer, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base
from app.core.db_types import GUID


class Product(Base):
    __tablename__ = "products"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    code = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    sales_price = Column(Numeric(15, 2).with_variant(Float, "sqlite"))
    price_adjustment = Column(Numeric(15, 2).with_variant(Float, "sqlite"), default=0)
    currency = Column(String(3), default="USD")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)

    quotation_lines = relationship("QuotationLine", back_populates="product")


class Plan(Base):
    __tablename__ = "plans"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    code = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    billing_cycle = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)

    versions = relationship("PlanVersion", back_populates="plan")
    quotation_lines = relationship("QuotationLine", back_populates="plan")


class PlanVersion(Base):
    __tablename__ = "plan_versions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    plan_id = Column(GUID(), ForeignKey("plans.id"), nullable=False)
    version = Column(Integer, nullable=False)
    price = Column(Numeric(15, 2).with_variant(Float, "sqlite"), nullable=False)
    currency = Column(String(3), nullable=False)
    effective_from = Column(DateTime, nullable=False)
    effective_to = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    plan = relationship("Plan", back_populates="versions")
    quotation_lines = relationship("QuotationLine", back_populates="plan_version")


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    product_id = Column(GUID(), ForeignKey("products.id"), nullable=False)
    name = Column(String(255), nullable=False)
    sku = Column(String(100))
    price = Column(Numeric(15, 2).with_variant(Float, "sqlite"))
    price_adjustment = Column(Numeric(15, 2).with_variant(Float, "sqlite"), default=0)
    currency = Column(String(3), default="USD")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", backref="variants")
