from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException, status
from app.modules.quotations.models import Quotation, QuotationLine
from app.modules.products.models import PlanVersion, Product, ProductVariant
from app.modules.customers.models import Customer
import uuid


class QuotationService:
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
    async def create(db: AsyncSession, data: dict, user_id: str = None, user_roles: list = None):
        lines_data = data.pop('lines', [])
        customer_id = data.get('customer_id')
        quotation_currency = data.get('currency', 'USD')
        
        if not user_roles or len(user_roles) == 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        await QuotationService._check_customer_access(db, customer_id, user_id, user_roles)
        
        customer_result = await db.execute(select(Customer).where(Customer.id == customer_id, Customer.deleted_at.is_(None)))
        if not customer_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Customer not found")
        
        try:
            quotation_number = f"QUO-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            subtotal = Decimal(0)
            processed_lines = []
            line_currencies = []
            
            for line in lines_data:
                quantity = Decimal(str(line['quantity']))
                if quantity <= 0:
                    raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
                
                plan_version_id = line.get('plan_version_id')
                plan_id = line.get('plan_id')
                product_id = line.get('product_id')
                
                unit_price = None
                line_currency = quotation_currency
                
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
                    line_currency = plan_version.currency or quotation_currency
                elif product_id:
                    prod_result = await db.execute(select(Product).where(Product.id == product_id))
                    product = prod_result.scalar_one_or_none()
                    if not product:
                        raise HTTPException(status_code=400, detail="Invalid product")
                    if not product.is_active or product.deleted_at:
                        raise HTTPException(status_code=400, detail="Product not available")
                    unit_price = Decimal(str(product.sales_price))
                    if line.get('product_variant_id'):
                        var_result = await db.execute(select(ProductVariant).where(ProductVariant.id == line['product_variant_id']))
                        variant = var_result.scalar_one_or_none()
                        if not variant or variant.product_id != product.id:
                            raise HTTPException(status_code=400, detail="Invalid product variant")
                        unit_price += Decimal(str(variant.price_adjustment))
                    line_currency = quotation_currency
                else:
                    raise HTTPException(status_code=400, detail="Either plan_version_id or product_id required")
                
                if line_currency != quotation_currency:
                    raise HTTPException(status_code=400, detail="Line currency must match quotation currency")
                
                line_currencies.append(line_currency)
                
                line_total = (quantity * unit_price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                subtotal += line_total
                
                processed_lines.append({
                    **line,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'line_total': line_total,
                    'description': line.get('description') or "Item"
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
                currency=quotation_currency,
                created_by=user_id,
                customer_id=customer_id,
                valid_until=data.get('valid_until'),
                notes=data.get('notes'),
                status='draft'
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
                    unit_price=line['unit_price'],
                    discount_amount=Decimal(0),
                    tax_amount=Decimal(0),
                    line_total=line['line_total']
                )
                db.add(quotation_line)
            
            await db.commit()
            await db.refresh(quotation)
            return quotation
        except HTTPException:
            await db.rollback()
            raise
        except Exception:
            await db.rollback()
            raise
    
    @staticmethod
    async def list(db: AsyncSession, skip: int = 0, limit: int = 100, user_id: str = None, user_roles: list = None):
        if not user_roles or len(user_roles) == 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        query = select(Quotation)
        if 'admin' in user_roles or 'staff' in user_roles:
            pass
        elif 'customer' in user_roles:
            customer_result = await db.execute(select(Customer).where(Customer.user_id == user_id))
            customer = customer_result.scalar_one_or_none()
            if not customer:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
            query = query.where(Quotation.customer_id == customer.id)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()
    
    @staticmethod
    async def get(db: AsyncSession, quotation_id: str, user_id: str = None, user_roles: list = None):
        if not user_roles or len(user_roles) == 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        result = await db.execute(select(Quotation).where(Quotation.id == quotation_id))
        quotation = result.scalar_one_or_none()
        if not quotation:
            raise HTTPException(status_code=404, detail="Quotation not found")
        if 'admin' in user_roles or 'staff' in user_roles:
            return quotation
        elif 'customer' in user_roles:
            customer_result = await db.execute(select(Customer).where(Customer.user_id == user_id))
            customer = customer_result.scalar_one_or_none()
            if not customer or str(customer.id) != str(quotation.customer_id):
                raise HTTPException(status_code=403, detail="Access denied")
            return quotation
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    @staticmethod
    async def update_status(db: AsyncSession, quotation_id: str, target_status: str, user_id: str = None, user_roles: list = None):
        if not user_roles or len(user_roles) == 0:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        quotation = await QuotationService.get(db, quotation_id, user_id, user_roles)
        
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
            if user_roles and 'admin' not in user_roles and 'staff' not in user_roles:
                if 'customer' not in user_roles:
                    raise HTTPException(status_code=403, detail="Access denied")
                customer_result = await db.execute(select(Customer).where(Customer.user_id == user_id))
                customer = customer_result.scalar_one_or_none()
                if not customer or str(customer.id) != str(quotation.customer_id):
                    raise HTTPException(status_code=403, detail="Access denied")
        
        quotation.status = target_status
        quotation.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(quotation)
        return quotation
