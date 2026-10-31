from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric, Text, JSON, Integer, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base
from app.core.db_types import GUID


class Quotation(Base):
    __tablename__ = "quotations"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    quotation_number = Column(String(50), unique=True)
    customer_id = Column(GUID(), ForeignKey("customers.id"), nullable=False)
    currency = Column(String(3), nullable=False)
    status = Column(String(20), default="draft")
    subtotal = Column(Numeric(15, 2).with_variant(Float, "sqlite"), default=0)
    discount_total = Column(Numeric(15, 2).with_variant(Float, "sqlite"), default=0)
    tax_total = Column(Numeric(15, 2).with_variant(Float, "sqlite"), default=0)
    total = Column(Numeric(15, 2).with_variant(Float, "sqlite"), default=0)
    valid_until = Column(DateTime)
    notes = Column(Text)
    terms_conditions = Column(Text)
    created_by = Column(String(255))
    approved_by = Column(String(255))
    approved_at = Column(DateTime)
    rejected_by = Column(String(255))
    rejected_at = Column(DateTime)
    rejection_reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer", back_populates="quotations")
    lines = relationship("QuotationLine", back_populates="quotation", cascade="all, delete-orphan")


class QuotationLine(Base):
    __tablename__ = "quotation_lines"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    quotation_id = Column(GUID(), ForeignKey("quotations.id"), nullable=False)
    product_id = Column(GUID(), ForeignKey("products.id"))
    product_variant_id = Column(GUID(), ForeignKey("product_variants.id"))
    plan_id = Column(GUID(), ForeignKey("plans.id"))
    plan_version_id = Column(GUID(), ForeignKey("plan_versions.id"))
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Numeric(15, 2).with_variant(Float, "sqlite"), nullable=False)
    currency = Column(String(3))
    discount_amount = Column(Numeric(15, 2).with_variant(Float, "sqlite"), default=0)
    tax_amount = Column(Numeric(15, 2).with_variant(Float, "sqlite"), default=0)
    line_total = Column(Numeric(15, 2).with_variant(Float, "sqlite"), nullable=False)
    price_snapshot = Column(JSON)
    description = Column(Text)

    quotation = relationship("Quotation", back_populates="lines")
    product = relationship("Product", back_populates="quotation_lines")
    plan = relationship("Plan", back_populates="quotation_lines")
    plan_version = relationship("PlanVersion", back_populates="quotation_lines")
