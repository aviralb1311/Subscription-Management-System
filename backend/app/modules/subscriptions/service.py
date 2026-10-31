from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException, status
from app.modules.subscriptions.models import Subscription, SubscriptionLine
from app.modules.quotations.models import Quotation, QuotationLine
from app.modules.customers.models import Customer
import uuid
import json


VALID_TRANSITIONS = {
    'draft': ['quotation', 'cancelled'],
    'quotation': ['confirmed', 'cancelled'],
    'confirmed': ['active', 'cancelled'],
    'active': ['paused', 'cancelled', 'pending_cancellation', 'renewal', 'expiry', 'expired'],
    'paused': ['active', 'cancelled', 'closed'],
    'pending_cancellation': ['cancelled', 'active'],
    'renewal': ['active', 'cancelled', 'expired'],
    'expired': ['closed'],
    'expiry': ['closed'],
    'early_closure': ['closed'],
    'cancelled': ['closed'],
    'closed': []
}


class SubscriptionService:
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
    async def create_from_quotation(db: AsyncSession, quotation_id: str, user_id: str = None, user_roles: list = None, start_date: datetime = None):
        if not user_roles or len(user_roles) == 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        result = await db.execute(select(Quotation).options(selectinload(Quotation.lines)).where(Quotation.id == quotation_id))
        quotation = result.scalar_one_or_none()
        if not quotation:
            raise HTTPException(status_code=404, detail="Quotation not found")
        if quotation.status != 'accepted':
            raise HTTPException(status_code=400, detail="Only accepted quotations can be converted")
        
        existing = await db.execute(select(Subscription).where(Subscription.quotation_id == quotation_id))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Quotation already converted to subscription")
        
        await SubscriptionService._check_customer_access(db, str(quotation.customer_id), user_id, user_roles)
        
        try:
            subscription_number = f"SUB-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            start_date = start_date or datetime.utcnow()
            next_billing_date = start_date + timedelta(days=30)
            
            if not quotation.lines:
                raise HTTPException(status_code=400, detail="Quotation has no lines")
            
            first_line = quotation.lines[0]
            unit_price = Decimal(str(first_line.unit_price))
            quantity = int(first_line.quantity) if first_line.quantity else 1
            amount = (unit_price * Decimal(quantity)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            snapshot = {'quotation_id': str(quotation.id), 'lines': [{'unit_price': str(l.unit_price), 'quantity': int(l.quantity) if l.quantity else 1} for l in quotation.lines]}
            
            subscription = Subscription(
                subscription_number=subscription_number,
                customer_id=quotation.customer_id,
                quotation_id=quotation.id,
                plan_id=first_line.plan_id,
                plan_version_id=first_line.plan_version_id,
                product_id=first_line.product_id,
                quantity=quantity,
                currency=quotation.currency,
                unit_price=unit_price,
                amount=amount,
                status='active',
                start_date=start_date,
                next_billing_date=next_billing_date,
                created_by=user_id,
                price_snapshot=snapshot
            )
            db.add(subscription)
            await db.flush()
            
            for line in quotation.lines:
                sub_line = SubscriptionLine(
                    subscription_id=subscription.id,
                    product_id=line.product_id,
                    plan_id=line.plan_id,
                    plan_version_id=line.plan_version_id,
                    quantity=line.quantity or 1,
                    unit_price=Decimal(str(line.unit_price)),
                    currency=line.currency or quotation.currency,
                    line_total=Decimal(str(line.line_total)) if line.line_total else (Decimal(str(line.unit_price)) * Decimal(line.quantity or 1)).quantize(Decimal('0.01')),
                    price_snapshot={'unit_price': str(line.unit_price)},
                    description=line.description
                )
                db.add(sub_line)
            
            await db.commit()
            result = await db.execute(select(Subscription).options(selectinload(Subscription.lines)).where(Subscription.id == subscription.id))
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
        query = select(Subscription).options(selectinload(Subscription.lines))
        if 'admin' in user_roles or 'staff' in user_roles:
            pass
        elif 'customer' in user_roles:
            customer_result = await db.execute(select(Customer).where(Customer.user_id == user_id))
            customer = customer_result.scalar_one_or_none()
            if not customer:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
            query = query.where(Subscription.customer_id == customer.id)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        if status:
            query = query.where(Subscription.status == status)
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()
    
    @staticmethod
    async def get(db: AsyncSession, subscription_id: str, user_id: str = None, user_roles: list = None):
        if not user_roles or len(user_roles) == 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        result = await db.execute(select(Subscription).options(selectinload(Subscription.lines)).where(Subscription.id == subscription_id))
        subscription = result.scalar_one_or_none()
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        if 'admin' in user_roles or 'staff' in user_roles:
            return subscription
        elif 'customer' in user_roles:
            customer_result = await db.execute(select(Customer).where(Customer.user_id == user_id))
            customer = customer_result.scalar_one_or_none()
            if not customer or str(customer.id) != str(subscription.customer_id):
                raise HTTPException(status_code=403, detail="Access denied")
            return subscription
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    @staticmethod
    async def update_status(db: AsyncSession, subscription_id: str, target_status: str, user_id: str = None, user_roles: list = None):
        if not user_roles or len(user_roles) == 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        subscription = await SubscriptionService.get(db, subscription_id, user_id, user_roles)
        
        if target_status not in VALID_TRANSITIONS.get(subscription.status, []):
            raise HTTPException(status_code=400, detail="Invalid state transition")
        
        subscription.status = target_status
        if target_status == 'paused':
            subscription.paused_at = datetime.utcnow()
        elif target_status == 'cancelled':
            subscription.cancelled_at = datetime.utcnow()
        elif target_status == 'closed':
            subscription.closed_at = datetime.utcnow()
        elif target_status == 'active' and subscription.paused_at:
            subscription.paused_at = None
        elif target_status == 'renewal':
            subscription.renewal_date = datetime.utcnow()
            subscription.next_billing_date = (datetime.utcnow() + timedelta(days=30))
        elif target_status == 'active' and subscription.status == 'renewal':
            pass
        
        await db.commit()
        result = await db.execute(select(Subscription).options(selectinload(Subscription.lines)).where(Subscription.id == subscription.id))
        return result.scalar_one()
    
    @staticmethod
    async def pause(db: AsyncSession, subscription_id: str, user_id: str = None, user_roles: list = None):
        return await SubscriptionService.update_status(db, subscription_id, 'paused', user_id, user_roles)
    
    @staticmethod
    async def resume(db: AsyncSession, subscription_id: str, user_id: str = None, user_roles: list = None):
        return await SubscriptionService.update_status(db, subscription_id, 'active', user_id, user_roles)
    
    @staticmethod
    async def cancel(db: AsyncSession, subscription_id: str, user_id: str = None, user_roles: list = None):
        return await SubscriptionService.update_status(db, subscription_id, 'cancelled', user_id, user_roles)
    
    @staticmethod
    async def close(db: AsyncSession, subscription_id: str, user_id: str = None, user_roles: list = None):
        return await SubscriptionService.update_status(db, subscription_id, 'closed', user_id, user_roles)
    
    @staticmethod
    async def renew(db: AsyncSession, subscription_id: str, user_id: str = None, user_roles: list = None):
        subscription = await SubscriptionService.get(db, subscription_id, user_id, user_roles)
        if subscription.status != 'active':
            raise HTTPException(status_code=400, detail="Invalid state transition")
        return await SubscriptionService.update_status(db, subscription_id, 'renewal', user_id, user_roles)
