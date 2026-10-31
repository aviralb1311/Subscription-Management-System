from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import HTTPException, status
from app.modules.customers.models import Customer
from app.modules.subscriptions.models import Subscription
from app.modules.invoices.models import Invoice


class AnalyticsService:
    @staticmethod
    async def _check_auth(user_roles):
        if not user_roles or len(user_roles) == 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    @staticmethod
    async def _get_customer_id(db: AsyncSession, user_id: str, user_roles: list):
        if 'admin' in user_roles or 'staff' in user_roles:
            return None
        if 'customer' in user_roles:
            result = await db.execute(select(Customer).where(Customer.user_id == user_id))
            customer = result.scalar_one_or_none()
            if not customer:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
            return customer.id
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    @staticmethod
    async def get_overview(db: AsyncSession, user_id: str = None, user_roles: list = None):
        await AnalyticsService._check_auth(user_roles)
        customer_id = await AnalyticsService._get_customer_id(db, user_id, user_roles)
        
        total_customers = 0
        if customer_id:
            total_customers = 1
        else:
            result = await db.execute(select(func.count(Customer.id)))
            total_customers = result.scalar() or 0
        
        sub_query = select(Subscription)
        if customer_id:
            sub_query = sub_query.where(Subscription.customer_id == customer_id)
        sub_result = await db.execute(sub_query)
        subscriptions = sub_result.scalars().all()
        
        active_subs = sum(1 for s in subscriptions if s.status in ['active', 'confirmed'])
        trial_subs = sum(1 for s in subscriptions if s.status == 'draft')
        cancelled_subs = sum(1 for s in subscriptions if s.status in ['cancelled', 'closed', 'expired'])
        
        mrr = Decimal(0)
        for s in subscriptions:
            if s.status in ['cancelled', 'closed', 'expired']:
                continue
            if s.status not in ['active', 'confirmed', 'paused']:
                continue
            amount = Decimal(str(s.amount)) if s.amount else Decimal(str(s.unit_price)) * Decimal(str(s.quantity or 1))
            mrr += amount
        mrr = mrr.quantize(Decimal('0.01'))
        arr = (mrr * Decimal('12')).quantize(Decimal('0.01'))
        
        inv_query = select(Invoice)
        if customer_id:
            inv_query = inv_query.where(Invoice.customer_id == customer_id)
        inv_result = await db.execute(inv_query)
        invoices = inv_result.scalars().all()
        
        revenue_collected = Decimal(0)
        outstanding = Decimal(0)
        overdue = 0
        now = datetime.utcnow()
        for inv in invoices:
            if inv.status == 'paid':
                revenue_collected += Decimal(str(inv.total))
            elif inv.status in ['draft', 'confirmed']:
                outstanding += Decimal(str(inv.total))
                if inv.due_date and inv.due_date < now:
                    overdue += 1
        
        revenue_collected = revenue_collected.quantize(Decimal('0.01'))
        outstanding = outstanding.quantize(Decimal('0.01'))
        
        churn_rate = 0.0
        if len(subscriptions) > 0:
            churn_rate = round((cancelled_subs / len(subscriptions)) * 100, 2)
        
        return {
            "total_customers": total_customers,
            "active_subscriptions": active_subs,
            "trial_subscriptions": trial_subs,
            "cancelled_subscriptions": cancelled_subs,
            "mrr": float(mrr),
            "arr": float(arr),
            "revenue_collected": float(revenue_collected),
            "outstanding_invoice_amount": float(outstanding),
            "overdue_invoices": overdue,
            "churn_rate": churn_rate
        }
    
    @staticmethod
    async def get_revenue(db: AsyncSession, user_id: str = None, user_roles: list = None):
        await AnalyticsService._check_auth(user_roles)
        customer_id = await AnalyticsService._get_customer_id(db, user_id, user_roles)
        inv_query = select(Invoice)
        if customer_id:
            inv_query = inv_query.where(Invoice.customer_id == customer_id)
        inv_result = await db.execute(inv_query)
        invoices = inv_result.scalars().all()
        monthly = {}
        for inv in invoices:
            if inv.status == 'paid' and inv.issue_date:
                key = inv.issue_date.strftime('%Y-%m')
                monthly[key] = monthly.get(key, Decimal(0)) + Decimal(str(inv.total))
        return [{"month": k, "revenue": float(v.quantize(Decimal('0.01')))} for k, v in sorted(monthly.items())]
    
    @staticmethod
    async def get_subscriptions(db: AsyncSession, user_id: str = None, user_roles: list = None):
        await AnalyticsService._check_auth(user_roles)
        customer_id = await AnalyticsService._get_customer_id(db, user_id, user_roles)
        query = select(Subscription)
        if customer_id:
            query = query.where(Subscription.customer_id == customer_id)
        result = await db.execute(query)
        subs = result.scalars().all()
        dist = {}
        for s in subs:
            dist[s.status] = dist.get(s.status, 0) + 1
        return [{"status": k, "count": v} for k, v in dist.items()]
