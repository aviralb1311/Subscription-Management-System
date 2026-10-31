from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from fastapi import HTTPException, status
from app.modules.products.models import Product, ProductVariant, Plan, PlanVersion


class ProductService:
    @staticmethod
    async def create(db: AsyncSession, data: dict):
        product = Product(**data)
        db.add(product)
        await db.commit()
        await db.refresh(product)
        return product
    
    @staticmethod
    async def list(db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(Product).where(Product.deleted_at.is_(None)).offset(skip).limit(limit))
        return result.scalars().all()
    
    @staticmethod
    async def get(db: AsyncSession, product_id: str):
        result = await db.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    
    @staticmethod
    async def update(db: AsyncSession, product_id: str, data: dict):
        product = await ProductService.get(db, product_id)
        for key, value in data.items():
            if value is not None:
                setattr(product, key, value)
        product.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(product)
        return product
    
    @staticmethod
    async def delete(db: AsyncSession, product_id: str):
        product = await ProductService.get(db, product_id)
        product.deleted_at = datetime.utcnow()
        product.is_active = False
        await db.commit()
        return {"message": "Product deactivated"}


class VariantService:
    @staticmethod
    async def create(db: AsyncSession, product_id: str, data: dict):
        variant = ProductVariant(product_id=product_id, **data)
        db.add(variant)
        await db.commit()
        await db.refresh(variant)
        return variant
    
    @staticmethod
    async def list_by_product(db: AsyncSession, product_id: str):
        result = await db.execute(select(ProductVariant).where(ProductVariant.product_id == product_id))
        return result.scalars().all()


class PlanService:
    @staticmethod
    async def create(db: AsyncSession, data: dict):
        price = data.pop('price', 0)
        currency = data.pop('currency', 'USD')
        plan = Plan(**data)
        db.add(plan)
        await db.flush()
        
        version = PlanVersion(
            plan_id=plan.id,
            version=1,
            price=price,
            currency=currency,
            effective_from=datetime.utcnow()
        )
        db.add(version)
        await db.commit()
        await db.refresh(plan)
        return plan
    
    @staticmethod
    async def list(db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(Plan).where(Plan.deleted_at.is_(None)).offset(skip).limit(limit))
        return result.scalars().all()
    
    @staticmethod
    async def get(db: AsyncSession, plan_id: str):
        result = await db.execute(select(Plan).where(Plan.id == plan_id))
        plan = result.scalar_one_or_none()
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        return plan
    
    @staticmethod
    async def create_version(db: AsyncSession, plan_id: str, price: float, currency: str = "USD"):
        plan = await PlanService.get(db, plan_id)
        # Deactivate current version
        result = await db.execute(select(PlanVersion).where(PlanVersion.plan_id == plan_id, PlanVersion.effective_to.is_(None)))
        current = result.scalars().all()
        for v in current:
            v.effective_to = datetime.utcnow()
        
        # Create new version
        result = await db.execute(select(PlanVersion).where(PlanVersion.plan_id == plan_id))
        max_version = max([v.version for v in result.scalars().all()] or [0])
        new_version = PlanVersion(
            plan_id=plan_id,
            version=max_version + 1,
            price=price,
            currency=currency,
            effective_from=datetime.utcnow()
        )
        db.add(new_version)
        await db.commit()
        await db.refresh(new_version)
        return new_version
