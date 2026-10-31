from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric, Text, Float, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base
from app.core.db_types import GUID


class Payment(Base):
    __tablename__ = "payments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    payment_number = Column(String(50), unique=True)
    customer_id = Column(GUID(), ForeignKey("customers.id"), nullable=False)
    amount = Column(Numeric(15, 2).with_variant(Float, "sqlite"), nullable=False)
    currency = Column(String(3), nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    payment_method = Column(String(50))
    external_reference = Column(String(100))
    idempotency_key = Column(String(100), unique=True)
    status = Column(String(20), default="received")
    unallocated_amount = Column(Numeric(15, 2).with_variant(Float, "sqlite"))
    notes = Column(Text)
    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer")
    allocations = relationship("PaymentAllocation", back_populates="payment", cascade="all, delete-orphan")
    refunds = relationship("Refund", back_populates="payment")


class PaymentAllocation(Base):
    __tablename__ = "payment_allocations"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    payment_id = Column(GUID(), ForeignKey("payments.id"), nullable=False)
    invoice_id = Column(GUID(), ForeignKey("invoices.id"), nullable=False)
    allocated_amount = Column(Numeric(15, 2).with_variant(Float, "sqlite"), nullable=False)
    allocated_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)

    payment = relationship("Payment", back_populates="allocations")
    invoice = relationship("Invoice")


class CreditNote(Base):
    __tablename__ = "credit_notes"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    credit_note_number = Column(String(50), unique=True)
    invoice_id = Column(GUID(), ForeignKey("invoices.id"), nullable=False)
    customer_id = Column(GUID(), ForeignKey("customers.id"), nullable=False)
    amount = Column(Numeric(15, 2).with_variant(Float, "sqlite"), nullable=False)
    currency = Column(String(3), nullable=False)
    reason = Column(Text)
    status = Column(String(20), default="issued")
    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    invoice = relationship("Invoice")
    customer = relationship("Customer")
    refunds = relationship("Refund", back_populates="credit_note")


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    refund_number = Column(String(50), unique=True)
    payment_id = Column(GUID(), ForeignKey("payments.id"), nullable=True)
    credit_note_id = Column(GUID(), ForeignKey("credit_notes.id"), nullable=True)
    customer_id = Column(GUID(), ForeignKey("customers.id"), nullable=False)
    amount = Column(Numeric(15, 2).with_variant(Float, "sqlite"), nullable=False)
    currency = Column(String(3), nullable=False)
    reason = Column(Text)
    status = Column(String(20), default="recorded")
    refund_date = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    payment = relationship("Payment", back_populates="refunds")
    credit_note = relationship("CreditNote", back_populates="refunds")
    customer = relationship("Customer")
