import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.customers.service import CustomerService
from app.modules.quotations.service import QuotationService
from app.modules.subscriptions.service import SubscriptionService
from app.modules.invoices.service import InvoiceService
from app.modules.products.models import Product, Plan, PlanVersion
from app.modules.invoices.models import Invoice, InvoiceLine


@pytest.mark.asyncio
async def test_invoice_generation_from_subscription(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "i1@test.com"})
    plan = Plan(name="Basic", code="IB1", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("49.99"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    data = {"customer_id": str(customer.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 1}]}
    quote = await QuotationService.create(db_session, data, "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "sent", "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "accepted", "u1", ["admin"])
    sub = await SubscriptionService.create_from_quotation(db_session, str(quote.id), "u1", ["admin"])
    invoice = await InvoiceService.generate_from_subscription(db_session, str(sub.id), "u1", ["admin"])
    assert invoice.status == "draft"
    assert invoice.invoice_number.startswith("INV-")
    assert Decimal(str(invoice.total)) >= Decimal("0")
    assert len(invoice.lines) >= 1
    assert Decimal(str(invoice.lines[0].unit_price)) == Decimal("49.99")


@pytest.mark.asyncio
async def test_duplicate_billing_period_prevention(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "i2@test.com"})
    plan = Plan(name="Basic", code="IB2", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("10.00"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    data = {"customer_id": str(customer.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 1}]}
    quote = await QuotationService.create(db_session, data, "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "sent", "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "accepted", "u1", ["admin"])
    sub = await SubscriptionService.create_from_quotation(db_session, str(quote.id), "u1", ["admin"])
    await InvoiceService.generate_from_subscription(db_session, str(sub.id), "u1", ["admin"])
    with pytest.raises(HTTPException) as exc:
        await InvoiceService.generate_from_subscription(db_session, str(sub.id), "u1", ["admin"])
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_invoice_lifecycle_transitions(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "i3@test.com"})
    plan = Plan(name="Basic", code="IB3", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("10.00"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    data = {"customer_id": str(customer.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 1}]}
    quote = await QuotationService.create(db_session, data, "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "sent", "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "accepted", "u1", ["admin"])
    sub = await SubscriptionService.create_from_quotation(db_session, str(quote.id), "u1", ["admin"])
    inv = await InvoiceService.generate_from_subscription(db_session, str(sub.id), "u1", ["admin"])
    inv = await InvoiceService.update_status(db_session, str(inv.id), "confirmed", "u1", ["admin"])
    assert inv.status == "confirmed"
    inv = await InvoiceService.update_status(db_session, str(inv.id), "paid", "u1", ["admin"])
    assert inv.status == "paid"
    with pytest.raises(HTTPException) as exc:
        await InvoiceService.update_status(db_session, str(inv.id), "draft", "u1", ["admin"])
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_invoice_rbac_ownership(db_session: AsyncSession):
    customer1 = await CustomerService.create(db_session, {"first_name": "A", "email": "i4@test.com", "user_id": "88888888-8888-8888-8888-888888888888"})
    customer2 = await CustomerService.create(db_session, {"first_name": "B", "email": "i5@test.com", "user_id": "99999999-9999-9999-9999-999999999999"})
    plan = Plan(name="Basic", code="IB4", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("10.00"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    data = {"customer_id": str(customer1.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 1}]}
    quote = await QuotationService.create(db_session, data, "88888888-8888-8888-8888-888888888888", ["customer"])
    await QuotationService.update_status(db_session, str(quote.id), "sent", "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "accepted", "u1", ["admin"])
    sub = await SubscriptionService.create_from_quotation(db_session, str(quote.id), "88888888-8888-8888-8888-888888888888", ["customer"])
    inv = await InvoiceService.generate_from_subscription(db_session, str(sub.id), "88888888-8888-8888-8888-888888888888", ["customer"])
    with pytest.raises(HTTPException) as exc:
        await InvoiceService.get(db_session, str(inv.id), "99999999-9999-9999-9999-999999999999", ["customer"])
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_invoice_pagination_filtering(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "i6@test.com"})
    plan = Plan(name="Basic", code="IB5", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("10.00"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    data = {"customer_id": str(customer.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 1}]}
    quote = await QuotationService.create(db_session, data, "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "sent", "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "accepted", "u1", ["admin"])
    sub = await SubscriptionService.create_from_quotation(db_session, str(quote.id), "u1", ["admin"])
    await InvoiceService.generate_from_subscription(db_session, str(sub.id), "u1", ["admin"])
    invoices = await InvoiceService.list(db_session, 0, 10, "u1", ["admin"], status="draft")
    assert len(invoices) >= 1


@pytest.mark.asyncio
async def test_invoice_rollback_on_failure(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "i7@test.com"})
    plan = Plan(name="Basic", code="IB6", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("10.00"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    data = {"customer_id": str(customer.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 1}]}
    quote = await QuotationService.create(db_session, data, "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "sent", "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "accepted", "u1", ["admin"])
    sub = await SubscriptionService.create_from_quotation(db_session, str(quote.id), "u1", ["admin"])
    original_commit = db_session.commit
    async def failing():
        await db_session.flush()
        from sqlalchemy import text
        raise Exception("fail")
    db_session.commit = failing
    try:
        with pytest.raises(Exception):
            await InvoiceService.generate_from_subscription(db_session, str(sub.id), "u1", ["admin"])
    finally:
        db_session.commit = original_commit
    result = await db_session.execute(select(Invoice))
    assert len(result.scalars().all()) == 0
    result2 = await db_session.execute(select(InvoiceLine))
    assert len(result2.scalars().all()) == 0
