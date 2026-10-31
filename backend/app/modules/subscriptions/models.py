from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric, Text, JSON, Integer, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base
from app.core.db_types import GUID


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    subscription_number = Column(String(50), unique=True)
    customer_id = Column(GUID(), ForeignKey("customers.id"), nullable=False)
    quotation_id = Column(GUID(), ForeignKey("quotations.id"), nullable=True)
    plan_id = Column(GUID(), ForeignKey("plans.id"), nullable=True)
    plan_version_id = Column(GUID(), ForeignKey("plan_versions.id"), nullable=True)
    product_id = Column(GUID(), ForeignKey("products.id"), nullable=True)
    quantity = Column(Integer, default=1, nullable=False)
    currency = Column(String(3), nullable=False)
    unit_price = Column(Numeric(15, 2).with_variant(Float, "sqlite"), nullable=False)
    amount = Column(Numeric(15, 2).with_variant(Float, "sqlite"), nullable=False)
    status = Column(String(30), default="draft", nullable=False)
    start_date = Column(DateTime)
    next_billing_date = Column(DateTime)
    end_date = Column(DateTime)
    paused_at = Column(DateTime)
    cancelled_at = Column(DateTime)
    closed_at = Column(DateTime)
    renewal_date = Column(DateTime)
    price_snapshot = Column(JSON)
    notes = Column(Text)
    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer")
    quotation = relationship("Quotation")
    plan = relationship("Plan")
    plan_version = relationship("PlanVersion")
    product = relationship("Product")


class SubscriptionLine(Base):
    __tablename__ = "subscription_lines"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(GUID(), ForeignKey("subscriptions.id"), nullable=False)
    product_id = Column(GUID(), ForeignKey("products.id"), nullable=True)
    plan_id = Column(GUID(), ForeignKey("plans.id"), nullable=True)
    plan_version_id = Column(GUID(), ForeignKey("plan_versions.id"), nullable=True)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Numeric(15, 2).with_variant(Float, "sqlite"), nullable=False)
    currency = Column(String(3), nullable=False)
    line_total = Column(Numeric(15, 2).with_variant(Float, "sqlite"), nullable=False)
    price_snapshot = Column(JSON)
    description = Column(Text)

    subscription = relationship("Subscription", backref="lines")
