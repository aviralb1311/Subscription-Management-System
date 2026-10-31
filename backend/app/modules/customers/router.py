from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.modules.auth.models import User
from app.modules.customers.schemas import CustomerCreate, CustomerUpdate, CustomerResponse
from app.modules.customers.service import CustomerService
from app.modules.customers.models import Customer
from sqlalchemy import select

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", response_model=CustomerResponse)
async def create_customer(customer: CustomerCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role("admin", "staff"))):
    return await CustomerService.create(db, customer.model_dump(exclude_unset=True))


@router.get("/", response_model=List[CustomerResponse])
async def list_customers(skip: int = 0, limit: int = Query(default=100, le=100), db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role("admin", "staff"))):
    return await CustomerService.list(db, skip, limit)


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_roles = [role.name for role in current_user.roles]
    if 'admin' in user_roles or 'staff' in user_roles:
        return await CustomerService.get(db, customer_id)
    if 'customer' in user_roles:
        result = await db.execute(select(Customer).where(Customer.user_id == current_user.id))
        customer = result.scalar_one_or_none()
        if not customer or str(customer.id) != str(customer_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return customer
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: str, customer: CustomerUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role("admin", "staff"))):
    return await CustomerService.update(db, customer_id, customer.model_dump(exclude_unset=True))


@router.delete("/{customer_id}")
async def delete_customer(customer_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    return await CustomerService.delete(db, customer_id)
