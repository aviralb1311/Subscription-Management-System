from pathlib import Path
import subprocess

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title="Subscription Intelligence Platform",
    description="Unified Subscription Intelligence & Revenue Management Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    # Allow Vercel preview deployments belonging to this Vercel team/project namespace.
    # Keep the production frontend origin explicitly allowlisted above.
    allow_origin_regex=r"https://(subscription-management-system-six-kappa|[a-z0-9-]+-2k24cs1g2413729-6539s-projects)[.]vercel[.]app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def initialize_database_schema():
    backend_dir = Path(__file__).resolve().parent.parent
    subprocess.run(["alembic", "upgrade", "head"], cwd=backend_dir, check=True)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "subscription-intelligence-platform"}


@app.get("/")
async def root():
    return {"message": "Subscription Intelligence Platform API"}

from app.modules.auth.router import router as auth_router
app.include_router(auth_router, prefix="/api/v1")

from app.modules.products.router import router as products_router
app.include_router(products_router, prefix="/api/v1")

# Plans router
from fastapi import APIRouter, Depends
from app.modules.products.schemas import PlanCreate, PlanUpdate, PlanResponse, PlanVersionResponse
from app.modules.products.service import PlanService
from app.core.dependencies import get_current_user, require_role
from app.core.database import get_db
from app.modules.auth.models import User
from typing import List

plans_router = APIRouter(prefix="/plans", tags=["plans"])

@plans_router.post("/", response_model=PlanResponse)
async def create_plan(plan: PlanCreate, db=Depends(get_db), current_user: User = Depends(require_role("admin", "staff"))):
    return await PlanService.create(db, plan.model_dump())

@plans_router.get("/", response_model=List[PlanResponse])
async def list_plans(skip: int = 0, limit: int = 100, db=Depends(get_db), current_user: User = Depends(get_current_user)):
    return await PlanService.list(db, skip, limit)

@plans_router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(plan_id: str, db=Depends(get_db), current_user: User = Depends(get_current_user)):
    return await PlanService.get(db, plan_id)

@plans_router.post("/{plan_id}/versions", response_model=PlanVersionResponse)
async def create_plan_version(plan_id: str, price: float, currency: str = "USD", db=Depends(get_db), current_user: User = Depends(require_role("admin"))):
    return await PlanService.create_version(db, plan_id, price, currency)

app.include_router(plans_router, prefix="/api/v1")

from app.modules.customers.router import router as customers_router
from app.modules.quotations.router import router as quotations_router
app.include_router(customers_router, prefix="/api/v1")
app.include_router(quotations_router, prefix="/api/v1")


from app.modules.subscriptions import router as subscriptions_router
app.include_router(subscriptions_router.router, prefix="/api/v1/subscriptions", tags=["Subscriptions"])


from app.modules.invoices import router as invoices_router
app.include_router(invoices_router.router, prefix="/api/v1/invoices", tags=["Invoices"])


from app.modules.analytics import router as analytics_router
app.include_router(analytics_router.router, prefix="/api/v1/analytics", tags=["Analytics"])


from app.modules.payments import router as payments_router
app.include_router(payments_router.router, prefix="/api/v1/payments", tags=["Payments"])



from app.modules.analytics import router as analytics_router
app.include_router(analytics_router.router, prefix="/api/v1/analytics", tags=["Analytics"])
