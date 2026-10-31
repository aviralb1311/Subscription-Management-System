import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.customers.service import CustomerService
from app.modules.quotations.service import QuotationService
from app.modules.subscriptions.service import SubscriptionService
from app.modules.products.models import Product, Plan, PlanVersion
from app.modules.subscriptions.models import Subscription, SubscriptionLine


@pytest.mark.asyncio
async def test_quotation_to_subscription_conversion(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "s1@test.com", "user_id": "55555555-5555-5555-5555-555555555555"})
    plan = Plan(name="Basic", code="SB1", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("49.99"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    data = {"customer_id": str(customer.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 2}]}
    quote = await QuotationService.create(db_session, data, "55555555-5555-5555-5555-555555555555", ["customer"])
    await QuotationService.update_status(db_session, str(quote.id), "sent", "u1", ["admin"])
    quote = await QuotationService.update_status(db_session, str(quote.id), "accepted", "u1", ["admin"])
    sub = await SubscriptionService.create_from_quotation(db_session, str(quote.id), "55555555-5555-5555-5555-555555555555", ["customer"])
    assert sub.status == "active"
    assert sub.currency == "USD"
    assert Decimal(str(sub.unit_price)) == Decimal("49.99")
    assert len(sub.lines) >= 1


@pytest.mark.asyncio
async def test_reject_unaccepted_quotation(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "s2@test.com"})
    plan = Plan(name="Basic", code="SB2", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("10.00"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    data = {"customer_id": str(customer.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 1}]}
    quote = await QuotationService.create(db_session, data, "u1", ["admin"])
    with pytest.raises(HTTPException) as exc:
        await SubscriptionService.create_from_quotation(db_session, str(quote.id), "u1", ["admin"])
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_duplicate_conversion_prevention(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "s3@test.com"})
    plan = Plan(name="Basic", code="SB3", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("10.00"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    data = {"customer_id": str(customer.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 1}]}
    quote = await QuotationService.create(db_session, data, "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "sent", "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "accepted", "u1", ["admin"])
    await SubscriptionService.create_from_quotation(db_session, str(quote.id), "u1", ["admin"])
    with pytest.raises(HTTPException) as exc:
        await SubscriptionService.create_from_quotation(db_session, str(quote.id), "u1", ["admin"])
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_valid_invalid_state_transitions(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "s4@test.com"})
    plan = Plan(name="Basic", code="SB4", billing_cycle="monthly")
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
    await SubscriptionService.pause(db_session, str(sub.id), "u1", ["admin"])
    await SubscriptionService.resume(db_session, str(sub.id), "u1", ["admin"])
    with pytest.raises(HTTPException) as exc:
        await SubscriptionService.update_status(db_session, str(sub.id), "converted", "u1", ["admin"])
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_cancel_close_renew(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "s5@test.com"})
    plan = Plan(name="Basic", code="SB5", billing_cycle="monthly")
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
    sub = await SubscriptionService.cancel(db_session, str(sub.id), "u1", ["admin"])
    assert sub.status == "cancelled"
    sub = await SubscriptionService.close(db_session, str(sub.id), "u1", ["admin"])
    assert sub.status == "closed"


@pytest.mark.asyncio
async def test_rbac_customer_ownership(db_session: AsyncSession):
    customer1 = await CustomerService.create(db_session, {"first_name": "A", "email": "s6@test.com", "user_id": "66666666-6666-6666-6666-666666666666"})
    customer2 = await CustomerService.create(db_session, {"first_name": "B", "email": "s7@test.com", "user_id": "77777777-7777-7777-7777-777777777777"})
    plan = Plan(name="Basic", code="SB6", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("10.00"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    data = {"customer_id": str(customer1.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 1}]}
    quote = await QuotationService.create(db_session, data, "66666666-6666-6666-6666-666666666666", ["customer"])
    await QuotationService.update_status(db_session, str(quote.id), "sent", "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "accepted", "u1", ["admin"])
    sub = await SubscriptionService.create_from_quotation(db_session, str(quote.id), "66666666-6666-6666-6666-666666666666", ["customer"])
    with pytest.raises(HTTPException) as exc:
        await SubscriptionService.get(db_session, str(sub.id), "77777777-7777-7777-7777-777777777777", ["customer"])
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_pagination_filtering(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "s8@test.com"})
    plan = Plan(name="Basic", code="SB7", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("10.00"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    for i in range(2):
        data = {"customer_id": str(customer.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 1}]}
        quote = await QuotationService.create(db_session, data, "u1", ["admin"])
        await QuotationService.update_status(db_session, str(quote.id), "sent", "u1", ["admin"])
        await QuotationService.update_status(db_session, str(quote.id), "accepted", "u1", ["admin"])
        await SubscriptionService.create_from_quotation(db_session, str(quote.id), "u1", ["admin"])
    subs = await SubscriptionService.list(db_session, 0, 1, "u1", ["admin"], status="active")
    assert len(subs) == 1


@pytest.mark.asyncio
async def test_rollback_on_failure(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "s9@test.com"})
    plan = Plan(name="Basic", code="SB8", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("10.00"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    data = {"customer_id": str(customer.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 1}]}
    quote = await QuotationService.create(db_session, data, "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "sent", "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "accepted", "u1", ["admin"])
    original_commit = db_session.commit
    async def failing():
        await db_session.flush()
        from sqlalchemy import text
        raise Exception("fail")
    db_session.commit = failing
    try:
        with pytest.raises(Exception):
            await SubscriptionService.create_from_quotation(db_session, str(quote.id), "u1", ["admin"])
    finally:
        db_session.commit = original_commit
    result = await db_session.execute(select(Subscription))
    assert len(result.scalars().all()) == 0
    result2 = await db_session.execute(select(SubscriptionLine))
    assert len(result2.scalars().all()) == 0
