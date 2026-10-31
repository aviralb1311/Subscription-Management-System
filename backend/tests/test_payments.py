import pytest
from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.customers.service import CustomerService
from app.modules.quotations.service import QuotationService
from app.modules.subscriptions.service import SubscriptionService
from app.modules.invoices.service import InvoiceService
from app.modules.payments.service import PaymentService
from app.modules.products.models import Product, Plan, PlanVersion


@pytest.mark.asyncio
async def test_manual_payment_and_partial_allocation(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "p1@test.com"})
    plan = Plan(name="Basic", code="PB1", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("100.00"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    data = {"customer_id": str(customer.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 1}]}
    quote = await QuotationService.create(db_session, data, "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "sent", "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "accepted", "u1", ["admin"])
    sub = await SubscriptionService.create_from_quotation(db_session, str(quote.id), "u1", ["admin"])
    inv = await InvoiceService.generate_from_subscription(db_session, str(sub.id), "u1", ["admin"])
    payment = await PaymentService.record_payment(db_session, {"customer_id": str(customer.id), "amount": Decimal("50.00"), "currency": "USD"}, "u1", ["admin"])
    result = await PaymentService.allocate(db_session, str(payment.id), [{"invoice_id": str(inv.id), "amount": Decimal("50.00")}], "u1", ["admin"])
    assert result.status in ['partially_allocated', 'fully_allocated']


@pytest.mark.asyncio
async def test_one_payment_multiple_invoices(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "p2@test.com"})
    plan = Plan(name="Basic", code="PB2", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("30.00"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    for i in range(2):
        data = {"customer_id": str(customer.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 1}]}
        quote = await QuotationService.create(db_session, data, "u1", ["admin"])
        await QuotationService.update_status(db_session, str(quote.id), "sent", "u1", ["admin"])
        await QuotationService.update_status(db_session, str(quote.id), "accepted", "u1", ["admin"])
        sub = await SubscriptionService.create_from_quotation(db_session, str(quote.id), "u1", ["admin"])
        inv = await InvoiceService.generate_from_subscription(db_session, str(sub.id), "u1", ["admin"])
        if i == 0:
            inv1 = inv
        else:
            inv2 = inv
    payment = await PaymentService.record_payment(db_session, {"customer_id": str(customer.id), "amount": Decimal("60.00"), "currency": "USD"}, "u1", ["admin"])
    await PaymentService.allocate(db_session, str(payment.id), [{"invoice_id": str(inv1.id), "amount": Decimal("30.00")}, {"invoice_id": str(inv2.id), "amount": Decimal("30.00")}], "u1", ["admin"])


@pytest.mark.asyncio
async def test_over_allocation_prevention(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "p3@test.com"})
    plan = Plan(name="Basic", code="PB3", billing_cycle="monthly")
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
    payment = await PaymentService.record_payment(db_session, {"customer_id": str(customer.id), "amount": Decimal("5.00"), "currency": "USD"}, "u1", ["admin"])
    with pytest.raises(HTTPException) as exc:
        await PaymentService.allocate(db_session, str(payment.id), [{"invoice_id": str(inv.id), "amount": Decimal("10.00")}], "u1", ["admin"])
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_currency_customer_mismatch(db_session: AsyncSession):
    customer1 = await CustomerService.create(db_session, {"first_name": "A", "email": "p4@test.com"})
    customer2 = await CustomerService.create(db_session, {"first_name": "B", "email": "p5@test.com"})
    plan = Plan(name="Basic", code="PB4", billing_cycle="monthly")
    db_session.add(plan)
    await db_session.flush()
    pv = PlanVersion(plan_id=plan.id, version=1, price=Decimal("10.00"), currency="USD", effective_from=datetime.utcnow())
    db_session.add(pv)
    await db_session.commit()
    data = {"customer_id": str(customer2.id), "currency": "USD", "lines": [{"plan_id": str(plan.id), "plan_version_id": str(pv.id), "quantity": 1}]}
    quote = await QuotationService.create(db_session, data, "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "sent", "u1", ["admin"])
    await QuotationService.update_status(db_session, str(quote.id), "accepted", "u1", ["admin"])
    sub = await SubscriptionService.create_from_quotation(db_session, str(quote.id), "u1", ["admin"])
    inv = await InvoiceService.generate_from_subscription(db_session, str(sub.id), "u1", ["admin"])
    payment = await PaymentService.record_payment(db_session, {"customer_id": str(customer1.id), "amount": Decimal("10.00"), "currency": "USD"}, "u1", ["admin"])
    with pytest.raises(HTTPException) as exc:
        await PaymentService.allocate(db_session, str(payment.id), [{"invoice_id": str(inv.id), "amount": Decimal("10.00")}], "u1", ["admin"])
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_idempotent_payment(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "p6@test.com"})
    await PaymentService.record_payment(db_session, {"customer_id": str(customer.id), "amount": Decimal("10.00"), "currency": "USD", "idempotency_key": "key1"}, "u1", ["admin"])
    with pytest.raises(HTTPException) as exc:
        await PaymentService.record_payment(db_session, {"customer_id": str(customer.id), "amount": Decimal("10.00"), "currency": "USD", "idempotency_key": "key1"}, "u1", ["admin"])
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_csv_reconciliation(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "p7@test.com"})
    payment = await PaymentService.record_payment(db_session, {"customer_id": str(customer.id), "amount": Decimal("10.00"), "currency": "USD", "external_reference": "REF123"}, "u1", ["admin"])
    rows = [{"external_reference": "REF123"}, {"external_reference": "REF999"}, {"external_reference": "REF123"}]
    res = await PaymentService.reconcile_csv(db_session, rows, "u1", ["admin"])
    assert len(res['matched']) == 1
    assert len(res['unmatched']) == 1
    assert len(res['duplicate']) == 1


@pytest.mark.asyncio
async def test_credit_note_and_refund(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "p8@test.com"})
    plan = Plan(name="Basic", code="PB5", billing_cycle="monthly")
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
    cn = await PaymentService.create_credit_note(db_session, {"invoice_id": str(inv.id), "amount": Decimal("5.00")}, "u1", ["admin"])
    assert cn.status == "issued"
    refund = await PaymentService.create_refund(db_session, {"credit_note_id": str(cn.id), "customer_id": str(customer.id), "amount": Decimal("5.00"), "currency": "USD"}, "u1", ["admin"])
    assert refund.status == "recorded"
    with pytest.raises(HTTPException) as exc:
        await PaymentService.create_refund(db_session, {"credit_note_id": str(cn.id), "customer_id": str(customer.id), "amount": Decimal("10.00"), "currency": "USD"}, "u1", ["admin"])
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_rollback_on_failure(db_session: AsyncSession):
    customer = await CustomerService.create(db_session, {"first_name": "Test", "email": "p9@test.com"})
    plan = Plan(name="Basic", code="PB6", billing_cycle="monthly")
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
    payment = await PaymentService.record_payment(db_session, {"customer_id": str(customer.id), "amount": Decimal("10.00"), "currency": "USD"}, "u1", ["admin"])
    original_commit = db_session.commit
    async def failing():
        await db_session.flush()
        from sqlalchemy import text
        raise Exception("fail")
    db_session.commit = failing
    try:
        with pytest.raises(Exception):
            await PaymentService.allocate(db_session, str(payment.id), [{"invoice_id": str(inv.id), "amount": Decimal("10.00")}], "u1", ["admin"])
    finally:
        db_session.commit = original_commit
    from app.modules.payments.models import PaymentAllocation
    result = await db_session.execute(select(PaymentAllocation))
    assert len(result.scalars().all()) == 0
