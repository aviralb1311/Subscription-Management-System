import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.customers.service import CustomerService
from app.modules.quotations.service import QuotationService
from app.modules.products.models import Product, Plan, PlanVersion
from app.modules.customers.models import Customer
from app.modules.quotations.models import Quotation, QuotationLine


@pytest.mark.asyncio
async def test_price_tampering_prevented_client_price_ignored(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "t1@test.com"})
    plan = Plan(name="Basic", code="BASIC", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("99.99"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    
    data = {"customer_id": str(customer.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 1, "unit_price": 1.00}]}
    quote = await QuotationService.create(db_session, data, "user1", ["admin"])
    assert quote.lines[0].unit_price == Decimal("99.99")
    assert quote.lines[0].unit_price != Decimal("1.00")
    result = await db_session.execute(select(QuotationLine).where(QuotationLine.quotation_id == quote.id))
    line = result.scalar_one()
    assert Decimal(str(line.unit_price)) == Decimal("99.99")


@pytest.mark.asyncio
async def test_historical_pricing_preserved_with_snapshot(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "t2@test.com"})
    plan = Plan(name="Pro", code="PRO", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv1 = PlanVersion(plan_id=plan.id, version=1, price=Decimal("50.00"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv1)
    await db_session.commit()
    
    data = {"customer_id": str(customer.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv1.id), "quantity": 1}]}
    quote = await QuotationService.create(db_session, data, "user1", ["admin"])
    old_price = quote.lines[0].unit_price
    assert Decimal(str(old_price)) == Decimal("50.00")
    
    pv1.effective_to = datetime.utcnow()
    pv2 = PlanVersion(plan_id=plan.id, version=2, price=Decimal("75.00"), currency="USD", effective_from=datetime.utcnow())
    db_session.add_all([pv1, pv2])
    await db_session.commit()
    
    result = await db_session.execute(select(QuotationLine).where(QuotationLine.quotation_id == quote.id))
    line = result.scalar_one()
    assert Decimal(str(line.unit_price)) == Decimal("50.00")


@pytest.mark.asyncio
async def test_invalid_plan_version_rejected(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "t3@test.com"})
    await db_session.commit()
    data = {"customer_id": str(customer.id), "currency": "USD", "lines": [{"plan_version_id": "00000000-0000-0000-0000-000000000000", "quantity": 1}]}
    with pytest.raises(HTTPException) as exc:
        await QuotationService.create(db_session, data, "user1", ["admin"])
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_product_only_quotation_line_supported(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "t4@test.com"})
    product = Product(name="Service", code="SVC", sales_price=Decimal("25.00"), is_active=True)
    db_session.add(product)
    await db_session.commit()
    data = {"customer_id": str(customer.id), "currency": "USD", "lines": [{"product_id": str(product.id), "quantity": 2}]}
    quote = await QuotationService.create(db_session, data, "user1", ["admin"])
    assert Decimal(str(quote.lines[0].unit_price)) == Decimal("25.00")
    assert Decimal(str(quote.total)) == Decimal("50.00")


@pytest.mark.asyncio
async def test_mixed_currencies_rejected(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "t5@test.com"})
    plan = Plan(name="Basic", code="B1", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("10.00"), currency="EUR", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    data = {"customer_id": str(customer.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 1}]}
    with pytest.raises(HTTPException) as exc:
        await QuotationService.create(db_session, data, "user1", ["admin"])
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_invalid_lifecycle_transitions_rejected(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "t6@test.com"})
    plan = Plan(name="Basic", code="B2", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("10.00"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    data = {"customer_id": str(customer.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 1}]}
    quote = await QuotationService.create(db_session, data, "user1", ["admin"])
    with pytest.raises(HTTPException) as exc:
        await QuotationService.update_status(db_session, str(quote.id), "converted", "user1", ["admin"])
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_expired_quotation_cannot_be_accepted(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "t7@test.com"})
    plan = Plan(name="Basic", code="B3", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("10.00"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    data = {"customer_id": str(customer.id), "currency": "USD", "valid_until": datetime.utcnow() - timedelta(days=1), "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 1}]}
    quote = await QuotationService.create(db_session, data, "user1", ["admin"])
    with pytest.raises(HTTPException) as exc:
        await QuotationService.update_status(db_session, str(quote.id), "accepted", "user1", ["admin"])
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_unauthorized_cross_customer_access_denied(db_session: AsyncSession):
    customer1 = await CustomerService.create(db_session, {"first_name": "Test1", "email": "t8@test.com", "user_id": "11111111-1111-1111-1111-111111111111"})
    customer2 = await CustomerService.create(db_session, {"first_name": "Test2", "email": "t9@test.com", "user_id": "22222222-2222-2222-2222-222222222222"})
    plan = Plan(name="Basic", code="B4", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("10.00"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    data = {"customer_id": str(customer1.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 1}]}
    quote = await QuotationService.create(db_session, data, "11111111-1111-1111-1111-111111111111", ["customer"])
    with pytest.raises(HTTPException) as exc:
        await QuotationService.get(db_session, str(quote.id), "22222222-2222-2222-2222-222222222222", ["customer"])
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_missing_role_denied(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "t10@test.com"})
    plan = Plan(name="Basic", code="B5", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("10.00"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    data = {"customer_id": str(customer.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 1}]}
    with pytest.raises(HTTPException) as exc:
        await QuotationService.create(db_session, data, "user1", [])
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_transaction_rollback_on_failure(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "t11@test.com"})
    await db_session.commit()
    data = {"customer_id": str(customer.id), "currency": "USD", "lines": [{"quantity": 1}]}
    with pytest.raises(HTTPException):
        await QuotationService.create(db_session, data, "user1", ["admin"])
    result = await db_session.execute(select(Quotation))
    assert len(result.scalars().all()) == 0
    result2 = await db_session.execute(select(QuotationLine))
    assert len(result2.scalars().all()) == 0
