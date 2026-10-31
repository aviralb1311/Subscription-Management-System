import pytest
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.customers.service import CustomerService
from app.modules.quotations.service import QuotationService
from app.modules.subscriptions.service import SubscriptionService
from app.modules.invoices.service import InvoiceService
from app.modules.analytics.service import AnalyticsService
from app.modules.products.models import Product, Plan, PlanVersion


@pytest.mark.asyncio
async def test_kpi_empty_db(db_session: AsyncSession):
    result = await AnalyticsService.get_overview(db_session, "u1", ["admin"])
    assert result["mrr"] == 0.0
    assert result["arr"] == 0.0


@pytest.mark.asyncio
async def test_mrr_arr_calculation(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "a1@test.com"})
    plan = Plan(name="Basic", code="AB1", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("50.00"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    data = {"customer_id": str(customer.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 2}]}
    quote = await QuotationService.create(db_session, data, "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "sent", "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "accepted", "u1", ["admin"])
    await SubscriptionService.create_from_quotation(db_session, str(quote.id), "u1", ["admin"])
    result = await AnalyticsService.get_overview(db_session, "u1", ["admin"])
    assert result["mrr"] == 100.0
    assert result["arr"] == 1200.0


@pytest.mark.asyncio
async def test_exclude_cancelled_from_mrr(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "a2@test.com"})
    plan = Plan(name="Basic", code="AB2", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("50.00"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    data = {"customer_id": str(customer.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 1}]}
    quote = await QuotationService.create(db_session, data, "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "sent", "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "accepted", "u1", ["admin"])
    sub = await SubscriptionService.create_from_quotation(db_session, str(quote.id), "u1", ["admin"])
    await SubscriptionService.cancel(db_session, str(sub.id), "u1", ["admin"])
    result = await AnalyticsService.get_overview(db_session, "u1", ["admin"])
    assert result["mrr"] == 0.0


@pytest.mark.asyncio
async def test_revenue_collected_outstanding_overdue(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "a3@test.com"})
    plan = Plan(name="Basic", code="AB3", billing_cycle="monthly")
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
    result = await AnalyticsService.get_overview(db_session, "u1", ["admin"])
    assert result["outstanding_invoice_amount"] >= 10.0


@pytest.mark.asyncio
async def test_rbac_customer_scope(db_session: AsyncSession):
    customer1 = await CustomerService.create(db_session, {"first_name": "A", "email": "a4@test.com", "user_id": "11111111-2222-3333-4444-555555555555"})
    plan = Plan(name="Basic", code="AB4", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("10.00"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    data = {"customer_id": str(customer1.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 1}]}
    quote = await QuotationService.create(db_session, data, "11111111-2222-3333-4444-555555555555", ["customer"])
    await QuotationService.update_status(db_session, str(quote.id), "sent", "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "accepted", "u1", ["admin"])
    await SubscriptionService.create_from_quotation(db_session, str(quote.id), "11111111-2222-3333-4444-555555555555", ["customer"])
    result = await AnalyticsService.get_overview(db_session, "11111111-2222-3333-4444-555555555555", ["customer"])
    assert result["total_customers"] == 1
