from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from fastapi import HTTPException
from app.modules.customers.models import Customer
from app.modules.quotations.models import Quotation


class CustomerService:
    @staticmethod
    async def create(db: AsyncSession, data: dict):
        if data.get('email'):
            result = await db.execute(select(Customer).where(Customer.email == data['email'], Customer.deleted_at.is_(None)))
            if result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Customer with this email already exists")
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
    
    @staticmethod
    async def delete(db: AsyncSession, customer_id: str):
        customer = await CustomerService.get(db, customer_id)
        # Check for dependent quotations
        result = await db.execute(select(Quotation).where(Quotation.customer_id == customer_id))
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="Cannot delete customer with existing quotations")
        customer.deleted_at = datetime.utcnow()
        customer.status = "inactive"
        await db.commit()
        return {"message": "Customer deactivated"}
