from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException, status
from app.modules.quotations.models import Quotation, QuotationLine
from app.modules.products.models import PlanVersion
from app.modules.customers.models import Customer
import uuid


class QuotationService:
    @staticmethod
    async def create(db: AsyncSession, data: dict, user_id: str = None):
        lines_data = data.pop('lines', [])
        customer_id = data.get('customer_id')
        
        # Validate customer exists
        customer_result = await db.execute(select(Customer).where(Customer.id == customer_id, Customer.deleted_at.is_(None)))
        if not customer_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Customer not found")
        
        quotation_number = f"QUO-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        subtotal = Decimal(0)
        processed_lines = []
        
        for line in lines_data:
            quantity = Decimal(str(line['quantity']))
            if quantity <= 0:
                raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
            
            plan_version_id = line.get('plan_version_id')
            plan_id = line.get('plan_id')
            
            unit_price = None
            currency = "USD"
            
            if plan_version_id:
                pv_result = await db.execute(select(PlanVersion).where(PlanVersion.id == plan_version_id))
                plan_version = pv_result.scalar_one_or_none()
                if not plan_version:
                    raise HTTPException(status_code=400, detail="Invalid plan version")
                if plan_id and str(plan_version.plan_id) != str(plan_id):
                    raise HTTPException(status_code=400, detail="Plan version does not belong to plan")
                if plan_version.effective_to is not None:
                    raise HTTPException(status_code=400, detail="Cannot use inactive plan version")
                unit_price = Decimal(str(plan_version.price))
                currency = plan_version.currency or "USD"
            else:
                # Only allow if explicitly provided and validated - but per requirements, must use plan version
                raise HTTPException(status_code=400, detail="plan_version_id is required for plan-based lines")
            
            line_total = (quantity * unit_price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            subtotal += line_total
            
            processed_lines.append({
                **line,
                'quantity': quantity,
                'unit_price': unit_price,
                'line_total': line_total
            })
        
        subtotal = subtotal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        discount_total = Decimal(0)
        tax_total = Decimal(0)
        total = (subtotal - discount_total + tax_total).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        quotation = Quotation(
            quotation_number=quotation_number,
            subtotal=subtotal,
            discount_total=discount_total,
            tax_total=tax_total,
            total=total,
            currency=currency,
            created_by=user_id,
            **{k: v for k, v in data.items() if k != 'lines'}
        )
        db.add(quotation)
        await db.flush()
        
        for line in processed_lines:
            quotation_line = QuotationLine(
                quotation_id=quotation.id,
                product_id=line.get('product_id'),
                product_variant_id=line.get('product_variant_id'),
                plan_id=line.get('plan_id'),
                plan_version_id=line.get('plan_version_id'),
                description=line.get('description', ''),
                quantity=line['quantity'],
                unit_price=line['unit_price'],  # SNAPSHOT - derived from plan version
                discount_amount=Decimal(0),
                tax_amount=Decimal(0),
                line_total=line['line_total']
            )
            db.add(quotation_line)
        
        await db.commit()
        await db.refresh(quotation)
        return quotation
    
    @staticmethod
    async def list(db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(Quotation).offset(skip).limit(limit))
        return result.scalars().all()
    
    @staticmethod
    async def get(db: AsyncSession, quotation_id: str):
        result = await db.execute(select(Quotation).where(Quotation.id == quotation_id))
        quotation = result.scalar_one_or_none()
        if not quotation:
            raise HTTPException(status_code=404, detail="Quotation not found")
        return quotation
    
    @staticmethod
    async def update_status(db: AsyncSession, quotation_id: str, target_status: str):
        quotation = await QuotationService.get(db, quotation_id)
        
        valid_transitions = {
            'draft': ['sent', 'cancelled'],
            'sent': ['accepted', 'cancelled'],
            'accepted': ['converted', 'cancelled'],
            'converted': [],
            'cancelled': [],
            'expired': []
        }
        
        if target_status not in valid_transitions.get(quotation.status, []):
            raise HTTPException(status_code=400, detail=f"Invalid transition from {quotation.status} to {target_status}")
        
        if target_status == 'accepted':
            if quotation.valid_until and quotation.valid_until < datetime.utcnow():
                raise HTTPException(status_code=400, detail="Cannot accept expired quotation")
        
        if target_status == 'converted' and quotation.status != 'accepted':
            raise HTTPException(status_code=400, detail="Only accepted quotations can be converted")
        
        quotation.status = target_status
        quotation.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(quotation)
        return quotation
