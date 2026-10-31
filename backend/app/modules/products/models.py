from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    code = Column(String(100), unique=True, index=True)
    product_type = Column(String(50))
    description = Column(Text)
    notes = Column(Text)
    cost_price = Column(Numeric(12, 2), default=0)
    sales_price = Column(Numeric(12, 2), default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)

    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    plans = relationship("Plan", back_populates="product")


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    name = Column(String(255), nullable=False)
    sku = Column(String(100), unique=True, index=True)
    attributes = Column(Text)
    price_adjustment = Column(Numeric(12, 2), default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="variants")


class Plan(Base):
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    name = Column(String(255), nullable=False)
    code = Column(String(100), unique=True, index=True)
    billing_cycle = Column(String(20), nullable=False)  # daily, weekly, monthly, yearly
    is_active = Column(Boolean, default=True)
    auto_close = Column(Boolean, default=False)
    allow_pause_resume = Column(Boolean, default=True)
    availability_start = Column(DateTime)
    availability_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)

    product = relationship("Product", back_populates="plans")
    versions = relationship("PlanVersion", back_populates="plan", cascade="all, delete-orphan", order_by="PlanVersion.version.desc()")


class PlanVersion(Base):
    __tablename__ = "plan_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)
    version = Column(Integer, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD")
    effective_from = Column(DateTime, nullable=False)
    effective_to = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))

    plan = relationship("Plan", back_populates="versions")
