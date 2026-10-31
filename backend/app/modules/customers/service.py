from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from fastapi import HTTPException
from app.modules.customers.models import Customer


class CustomerService:
    @staticmethod
    async def create(db: AsyncSession, data: dict):
        customer = Customer(**data)
        db.add(customer)
        await db.commit()
        await db.refresh(customer)
        return customer
    
    @staticmethod
    async def list(db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(Customer).where(Customer.deleted_at.is_(None)).offset(skip).limit(limit))
        return result.scalars().all()
    
    @staticmethod
    async def get(db: AsyncSession, customer_id: str):
        result = await db.execute(select(Customer).where(Customer.id == customer_id))
        customer = result.scalar_one_or_none()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer
    
    @staticmethod
    async def update(db: AsyncSession, customer_id: str, data: dict):
        customer = await CustomerService.get(db, customer_id)
        for key, value in data.items():
            if value is not None:
                setattr(customer, key, value)
        customer.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(customer)
        return customer
