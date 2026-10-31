from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException, status
from app.modules.payments.models import Payment, PaymentAllocation, CreditNote, Refund
from app.modules.invoices.models import Invoice
from app.modules.customers.models import Customer
import uuid


class PaymentService:
    @staticmethod
    async def _check_customer_access(db: AsyncSession, customer_id: str, user_id: str, user_roles: list):
        if not user_roles or len(user_roles) == 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        if 'admin' in user_roles or 'staff' in user_roles:
            return True
        if 'customer' in user_roles:
            result = await db.execute(select(Customer).where(Customer.user_id == user_id))
            customer = result.scalar_one_or_none()
            if not customer or str(customer.id) != str(customer_id):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
            return True
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    @staticmethod
    async def record_payment(db: AsyncSession, data: dict, user_id: str = None, user_roles: list = None):
        if not user_roles or len(user_roles) == 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        customer_id = data.get('customer_id')
        await PaymentService._check_customer_access(db, customer_id, user_id, user_roles)
        
        amount = Decimal(str(data['amount']))
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be positive")
        currency = data.get('currency', 'USD')
        idempotency_key = data.get('idempotency_key')
        if idempotency_key:
            existing = await db.execute(select(Payment).where(Payment.idempotency_key == idempotency_key))
            if existing.scalar_one_or_none():
                raise HTTPException(status_code=409, detail="Duplicate payment")
        
        try:
            payment = Payment(
                payment_number=f"PAY-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}",
                customer_id=customer_id,
                amount=amount,
                currency=currency,
                payment_method=data.get('payment_method'),
                external_reference=data.get('external_reference'),
                idempotency_key=idempotency_key,
                status='received',
                unallocated_amount=amount,
                notes=data.get('notes'),
                created_by=user_id
            )
            db.add(payment)
            await db.commit()
            result = await db.execute(select(Payment).options(selectinload(Payment.allocations)).where(Payment.id == payment.id))
            return result.scalar_one()
        except HTTPException:
            await db.rollback()
            raise
        except Exception:
            await db.rollback()
            raise
    
    @staticmethod
    async def allocate(db: AsyncSession, payment_id: str, allocations: list, user_id: str = None, user_roles: list = None):
        if not user_roles or len(user_roles) == 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        result = await db.execute(select(Payment).options(selectinload(Payment.allocations)).where(Payment.id == payment_id))
        payment = result.scalar_one_or_none()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        await PaymentService._check_customer_access(db, str(payment.customer_id), user_id, user_roles)
        
        try:
            total_alloc = Decimal(0)
            for alloc in allocations:
                alloc_amount = Decimal(str(alloc.get('amount') if isinstance(alloc, dict) else alloc.amount))
                if alloc_amount <= 0:
                    raise HTTPException(status_code=400, detail="Allocation amount must be positive")
                total_alloc += alloc_amount
            
            unalloc = Decimal(str(payment.unallocated_amount)) if payment.unallocated_amount is not None else Decimal(str(payment.amount))
            if total_alloc > unalloc:
                raise HTTPException(status_code=400, detail="Over-allocation")
            
            for alloc in allocations:
                alloc_amount = Decimal(str(alloc.get('amount') if isinstance(alloc, dict) else alloc.amount))
                invoice_id = alloc.get('invoice_id') if isinstance(alloc, dict) else alloc.invoice_id
                inv_res = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
                invoice = inv_res.scalar_one_or_none()
                if not invoice:
                    raise HTTPException(status_code=404, detail="Invoice not found")
                if str(invoice.customer_id) != str(payment.customer_id):
                    raise HTTPException(status_code=400, detail="Currency/customer mismatch")
                if invoice.currency != payment.currency:
                    raise HTTPException(status_code=400, detail="Currency/customer mismatch")
                outstanding = Decimal(str(invoice.total))
                # Simple check
                if alloc_amount > outstanding:
                    raise HTTPException(status_code=400, detail="Exceeds invoice balance")
                allocation = PaymentAllocation(payment_id=payment.id, invoice_id=invoice.id, allocated_amount=alloc_amount)
                db.add(allocation)
            
            payment.unallocated_amount = unalloc - total_alloc
            if payment.unallocated_amount <= 0:
                payment.status = 'fully_allocated'
            else:
                payment.status = 'partially_allocated'
            await db.commit()
            result = await db.execute(select(Payment).options(selectinload(Payment.allocations)).where(Payment.id == payment.id))
            return result.scalar_one()
        except HTTPException:
            await db.rollback()
            raise
        except Exception:
            await db.rollback()
            raise

    @staticmethod
    async def list_payments(db: AsyncSession, skip: int = 0, limit: int = 100, user_id: str = None, user_roles: list = None):
        if not user_roles or len(user_roles) == 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        query = select(Payment).options(selectinload(Payment.allocations))
        if 'admin' in user_roles or 'staff' in user_roles:
            pass
        elif 'customer' in user_roles:
            customer_result = await db.execute(select(Customer).where(Customer.user_id == user_id))
            customer = customer_result.scalar_one_or_none()
            if not customer:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
            query = query.where(Payment.customer_id == customer.id)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()
    
    @staticmethod
    async def create_credit_note(db: AsyncSession, data: dict, user_id: str = None, user_roles: list = None):
        if not user_roles or len(user_roles) == 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        invoice_id = data.get('invoice_id')
        inv_res = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
        invoice = inv_res.scalar_one_or_none()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        await PaymentService._check_customer_access(db, str(invoice.customer_id), user_id, user_roles)
        amount = Decimal(str(data['amount']))
        if amount <= 0 or amount > Decimal(str(invoice.total)):
            raise HTTPException(status_code=400, detail="Invalid credit note amount")
        try:
            cn = CreditNote(
                credit_note_number=f"CN-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}",
                invoice_id=invoice.id,
                customer_id=invoice.customer_id,
                amount=amount,
                currency=invoice.currency,
                reason=data.get('reason'),
                status='issued',
                created_by=user_id
            )
            db.add(cn)
            await db.commit()
            return cn
        except HTTPException:
            await db.rollback()
            raise
        except Exception:
            await db.rollback()
            raise
    
    @staticmethod
    async def create_refund(db: AsyncSession, data: dict, user_id: str = None, user_roles: list = None):
        if not user_roles or len(user_roles) == 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        customer_id = data.get('customer_id')
        await PaymentService._check_customer_access(db, customer_id, user_id, user_roles)
        amount = Decimal(str(data['amount']))
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid refund amount")
        payment_id = data.get('payment_id')
        credit_note_id = data.get('credit_note_id')
        if payment_id:
            p_res = await db.execute(select(Payment).where(Payment.id == payment_id))
            payment = p_res.scalar_one_or_none()
            if not payment or amount > Decimal(str(payment.amount)):
                raise HTTPException(status_code=400, detail="Refund exceeds refundable amount")
        if credit_note_id:
            cn_res = await db.execute(select(CreditNote).where(CreditNote.id == credit_note_id))
            cn = cn_res.scalar_one_or_none()
            if not cn or amount > Decimal(str(cn.amount)):
                raise HTTPException(status_code=400, detail="Refund exceeds refundable amount")
        try:
            refund = Refund(
                refund_number=f"RF-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}",
                payment_id=payment_id,
                credit_note_id=credit_note_id,
                customer_id=customer_id,
                amount=amount,
                currency=data.get('currency', 'USD'),
                reason=data.get('reason'),
                status='recorded',
                created_by=user_id
            )
            db.add(refund)
            await db.commit()
            return refund
        except HTTPException:
            await db.rollback()
            raise
        except Exception:
            await db.rollback()
            raise
    
    @staticmethod
    async def reconcile_csv(db: AsyncSession, rows: list, user_id: str = None, user_roles: list = None):
        if not user_roles or len(user_roles) == 0 or ('admin' not in user_roles and 'staff' not in user_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        results = {'matched': [], 'unmatched': [], 'duplicate': [], 'invalid': []}
        seen = set()
        for row in rows:
            try:
                ref = row.get('external_reference') or row.get('reference')
                if not ref:
                    results['invalid'].append(row)
                    continue
                if ref in seen:
                    results['duplicate'].append(row)
                    continue
                seen.add(ref)
                res = await db.execute(select(Payment).where(Payment.external_reference == ref))
                payment = res.scalar_one_or_none()
                if payment:
                    results['matched'].append({'reference': ref, 'payment_id': str(payment.id)})
                else:
                    results['unmatched'].append(row)
            except Exception:
                results['invalid'].append(row)
        return results
