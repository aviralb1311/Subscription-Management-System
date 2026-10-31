from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException
from app.modules.quotations.models import Quotation, QuotationLine
import uuid


class QuotationService:
    @staticmethod
    async def create(db: AsyncSession, data: dict, user_id: str = None):
        lines_data = data.pop('lines', [])
        quotation_number = f"QUO-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        subtotal = Decimal(0)
        for line in lines_data:
            line_total = Decimal(str(line['quantity'])) * Decimal(str(line['unit_price']))
            subtotal += line_total
        
        quotation = Quotation(
            quotation_number=quotation_number,
            subtotal=subtotal,
            discount_total=Decimal(0),
            tax_total=Decimal(0),
            total=subtotal,
            created_by=user_id,
            **data
        )
        db.add(quotation)
        await db.flush()
        
        for line in lines_data:
            quantity = Decimal(str(line['quantity']))
            unit_price = Decimal(str(line['unit_price']))
            line_total = quantity * unit_price
            quotation_line = QuotationLine(
                quotation_id=quotation.id,
                product_id=line.get('product_id'),
                product_variant_id=line.get('product_variant_id'),
                plan_id=line.get('plan_id'),
                plan_version_id=line.get('plan_version_id'),
                description=line.get('description', ''),
                quantity=quantity,
                unit_price=unit_price,  # SNAPSHOT
                discount_amount=Decimal(0),
                tax_amount=Decimal(0),
                line_total=line_total
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
    async def update_status(db: AsyncSession, quotation_id: str, status: str):
        quotation = await QuotationService.get(db, quotation_id)
        if quotation.status == 'converted':
            raise HTTPException(status_code=400, detail="Cannot modify converted quotation")
        quotation.status = status
        quotation.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(quotation)
        return quotation
