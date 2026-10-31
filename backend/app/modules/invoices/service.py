from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException, status
from app.modules.invoices.models import Invoice, InvoiceLine
from app.modules.subscriptions.models import Subscription, SubscriptionLine
from app.modules.customers.models import Customer
from app.modules.products.models import Product
import uuid


VALID_INVOICE_TRANSITIONS = {
    'draft': ['confirmed', 'cancelled'],
    'confirmed': ['paid', 'cancelled', 'void'],
    'paid': ['void'],
    'cancelled': [],
    'void': []
}


class InvoiceService:
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
    def _generate_invoice_number():
        return f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    @staticmethod
    async def generate_from_subscription(db: AsyncSession, subscription_id: str, user_id: str = None, user_roles: list = None, 
                                       billing_period_start: datetime = None, billing_period_end: datetime = None, due_date: datetime = None):
        if not user_roles or len(user_roles) == 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        result = await db.execute(select(Subscription).options(selectinload(Subscription.lines)).where(Subscription.id == subscription_id))
        subscription = result.scalar_one_or_none()
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        if subscription.status not in ['active', 'confirmed']:
            raise HTTPException(status_code=400, detail="Subscription not eligible for invoicing")
        
        await InvoiceService._check_customer_access(db, str(subscription.customer_id), user_id, user_roles)
        
        billing_period_start = billing_period_start or (subscription.start_date or datetime.utcnow())
        billing_period_end = billing_period_end or (billing_period_start + timedelta(days=30))
        
        existing = await db.execute(select(Invoice).where(
            Invoice.subscription_id == subscription_id,
            Invoice.billing_period_start == billing_period_start,
            Invoice.billing_period_end == billing_period_end,
            Invoice.status.in_(['draft', 'confirmed', 'paid'])
        ))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Invoice already exists for this billing period")
        
        try:
            invoice_number = InvoiceService._generate_invoice_number()
            subtotal = Decimal(0)
            processed_lines = []
            
            for sub_line in subscription.lines:
                quantity = int(sub_line.quantity) if sub_line.quantity else 1
                unit_price = Decimal(str(sub_line.unit_price))
                tax_rate = Decimal('0.00')
                line_subtotal = (unit_price * Decimal(quantity)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                tax_amount = (line_subtotal * tax_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                line_total = (line_subtotal + tax_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                subtotal += line_subtotal
                desc = sub_line.description or "Subscription item"
                processed_lines.append({
                    'product_id': sub_line.product_id,
                    'plan_id': sub_line.plan_id,
                    'description': desc,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'tax_rate': tax_rate,
                    'tax_amount': tax_amount,
                    'line_subtotal': line_subtotal,
                    'line_total': line_total,
                    'price_snapshot': {'unit_price': str(unit_price), 'quantity': quantity}
                })
            
            if not processed_lines and subscription.amount:
                quantity = int(subscription.quantity) if subscription.quantity else 1
                unit_price = Decimal(str(subscription.unit_price))
                tax_rate = Decimal('0.00')
                line_subtotal = (unit_price * Decimal(quantity)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                tax_amount = Decimal('0.00')
                line_total = line_subtotal
                subtotal = line_subtotal
                processed_lines.append({
                    'product_id': subscription.product_id,
                    'plan_id': subscription.plan_id,
                    'description': f"Subscription {subscription.subscription_number}",
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'tax_rate': tax_rate,
                    'tax_amount': tax_amount,
                    'line_subtotal': line_subtotal,
                    'line_total': line_total,
                    'price_snapshot': {'unit_price': str(unit_price), 'quantity': quantity}
                })
            
            subtotal = subtotal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            tax_amount = Decimal('0.00')
            discount_total = Decimal('0.00')
            total = (subtotal + tax_amount - discount_total).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            invoice = Invoice(
                invoice_number=invoice_number,
                customer_id=subscription.customer_id,
                subscription_id=subscription.id,
                currency=subscription.currency,
                status='draft',
                issue_date=datetime.utcnow(),
                due_date=due_date or (datetime.utcnow() + timedelta(days=30)),
                billing_period_start=billing_period_start,
                billing_period_end=billing_period_end,
                subtotal=subtotal,
                tax_amount=tax_amount,
                discount_total=discount_total,
                total=total,
                created_by=user_id
            )
            db.add(invoice)
            await db.flush()
            
            for line in processed_lines:
                invoice_line = InvoiceLine(
                    invoice_id=invoice.id,
                    product_id=line.get('product_id'),
                    plan_id=line.get('plan_id'),
                    description=line['description'],
                    quantity=line['quantity'],
                    unit_price=line['unit_price'],
                    tax_rate=line['tax_rate'],
                    tax_amount=line['tax_amount'],
                    line_subtotal=line['line_subtotal'],
                    line_total=line['line_total'],
                    price_snapshot=line['price_snapshot']
                )
                db.add(invoice_line)
            
            await db.commit()
            result = await db.execute(select(Invoice).options(selectinload(Invoice.lines)).where(Invoice.id == invoice.id))
            return result.scalar_one()
        except HTTPException:
            await db.rollback()
            raise
        except Exception:
            await db.rollback()
            raise

    @staticmethod
    async def list(db: AsyncSession, skip: int = 0, limit: int = 100, user_id: str = None, user_roles: list = None, status: str = None):
        if not user_roles or len(user_roles) == 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        query = select(Invoice).options(selectinload(Invoice.lines))
        if 'admin' in user_roles or 'staff' in user_roles:
            pass
        elif 'customer' in user_roles:
            customer_result = await db.execute(select(Customer).where(Customer.user_id == user_id))
            customer = customer_result.scalar_one_or_none()
            if not customer:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
            query = query.where(Invoice.customer_id == customer.id)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        if status:
            query = query.where(Invoice.status == status)
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()
    
    @staticmethod
    async def get(db: AsyncSession, invoice_id: str, user_id: str = None, user_roles: list = None):
        if not user_roles or len(user_roles) == 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        result = await db.execute(select(Invoice).options(selectinload(Invoice.lines)).where(Invoice.id == invoice_id))
        invoice = result.scalar_one_or_none()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        if 'admin' in user_roles or 'staff' in user_roles:
            return invoice
        elif 'customer' in user_roles:
            customer_result = await db.execute(select(Customer).where(Customer.user_id == user_id))
            customer = customer_result.scalar_one_or_none()
            if not customer or str(customer.id) != str(invoice.customer_id):
                raise HTTPException(status_code=403, detail="Access denied")
            return invoice
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    @staticmethod
    async def update_status(db: AsyncSession, invoice_id: str, target_status: str, user_id: str = None, user_roles: list = None):
        if not user_roles or len(user_roles) == 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        invoice = await InvoiceService.get(db, invoice_id, user_id, user_roles)
        if target_status not in VALID_INVOICE_TRANSITIONS.get(invoice.status, []):
            raise HTTPException(status_code=400, detail="Invalid invoice status transition")
        invoice.status = target_status
        await db.commit()
        result = await db.execute(select(Invoice).options(selectinload(Invoice.lines)).where(Invoice.id == invoice.id))
        return result.scalar_one()
