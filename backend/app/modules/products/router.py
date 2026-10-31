from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.modules.auth.models import User
from app.modules.products.schemas import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProductVariantCreate, ProductVariantResponse,
    PlanCreate, PlanUpdate, PlanResponse, PlanVersionResponse
)
from app.modules.products.service import ProductService, VariantService, PlanService

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "staff"))
):
    return await ProductService.create(db, product.model_dump())


@router.get("/", response_model=List[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = Query(default=100, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await ProductService.list(db, skip, limit)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await ProductService.get(db, product_id)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "staff"))
):
    return await ProductService.update(db, product_id, product.model_dump(exclude_unset=True))


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    return await ProductService.delete(db, product_id)


@router.post("/{product_id}/variants", response_model=ProductVariantResponse)
async def create_variant(
    product_id: str,
    variant: ProductVariantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "staff"))
):
    return await VariantService.create(db, product_id, variant.model_dump())


@router.get("/{product_id}/variants", response_model=List[ProductVariantResponse])
async def list_variants(
    product_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await VariantService.list_by_product(db, product_id)
