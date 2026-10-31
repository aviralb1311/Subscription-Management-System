from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric, Text, JSON, Integer, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base
from app.core.db_types import GUID


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    invoice_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(GUID(), ForeignKey("customers.id"), nullable=False)
    subscription_id = Column(GUID(), ForeignKey("subscriptions.id"), nullable=True)
    quotation_id = Column(GUID(), ForeignKey("quotations.id"), nullable=True)
    currency = Column(String(3), nullable=False)
    status = Column(String(20), default="draft", nullable=False)
    issue_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    billing_period_start = Column(DateTime)
    billing_period_end = Column(DateTime)
    subtotal = Column(Numeric(15, 2).with_variant(Float, "sqlite"), nullable=False)
    tax_amount = Column(Numeric(15, 2).with_variant(Float, "sqlite"), default=0)
    discount_total = Column(Numeric(15, 2).with_variant(Float, "sqlite"), default=0)
    total = Column(Numeric(15, 2).with_variant(Float, "sqlite"), nullable=False)
    notes = Column(Text)
    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer")
    subscription = relationship("Subscription")
    quotation = relationship("Quotation")
    lines = relationship("InvoiceLine", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(GUID(), ForeignKey("invoices.id"), nullable=False)
    product_id = Column(GUID(), ForeignKey("products.id"), nullable=True)
    plan_id = Column(GUID(), ForeignKey("plans.id"), nullable=True)
    description = Column(Text, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(15, 2).with_variant(Float, "sqlite"), nullable=False)
    tax_rate = Column(Numeric(5, 4).with_variant(Float, "sqlite"), default=0)
    tax_amount = Column(Numeric(15, 2).with_variant(Float, "sqlite"), default=0)
    line_subtotal = Column(Numeric(15, 2).with_variant(Float, "sqlite"), nullable=False)
    line_total = Column(Numeric(15, 2).with_variant(Float, "sqlite"), nullable=False)
    price_snapshot = Column(JSON)

    invoice = relationship("Invoice", back_populates="lines")
