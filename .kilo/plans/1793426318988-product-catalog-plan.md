# PHASE 3 PLAN: Product Catalog and Plans

## Objective
Implement Product, ProductVariant, Plan, and PlanVersion management with proper RBAC, validation, and historical pricing.

## Requirements (from docs)
- FR-009: Create/edit/deactivate products
- FR-010: Product type, sales price, cost price, notes, descriptions  
- FR-011: Product variants with price adjustments
- FR-012: Product availability/status
- FR-013: Plans for daily/weekly/monthly/yearly billing
- FR-014: Flexible pricing, quantity management
- FR-015: Plan versions for historical pricing
- FR-016: Pause/resume/close/renew/expiry functionality

## Branch
Create branch `feat/product-catalog` from main (after merging auth)

## Implementation Tasks

### 1. Models
- Product model (name, code/SKU, product_type, description, cost_price, sales_price, is_active, timestamps)
- ProductVariant model (product_id, name, sku, price, is_active)
- Plan model (product_id, name, code, billing_cycle, is_active, auto_close, allow_pause_resume)
- PlanVersion model (plan_id, version, price, currency, effective_from, effective_to)

Use Decimal for prices, proper relationships, timestamps.

### 2. Schemas (Pydantic)
- ProductCreate, ProductUpdate, ProductResponse
- ProductVariantCreate, ProductVariantResponse
- PlanCreate, PlanUpdate, PlanResponse
- PlanVersionCreate, PlanVersionResponse

### 3. Services
- ProductService: CRUD with validation
- PlanService: CRUD with versioning logic
- Ensure only Admin/Staff can create/edit, proper permissions

### 4. API Endpoints
**Products:**
- GET /api/v1/products (list, paginated)
- POST /api/v1/products (Admin/Staff)
- GET /api/v1/products/{id}
- PUT/PATCH /api/v1/products/{id} (Admin/Staff)
- DELETE /api/v1/products/{id} (Admin - soft delete)

**Variants:**
- GET/POST /api/v1/products/{id}/variants
- PUT/DELETE /api/v1/variants/{id}

**Plans:**
- GET /api/v1/plans
- POST /api/v1/plans (Admin/Staff)
- GET/PUT /api/v1/plans/{id}
- POST /api/v1/plans/{id}/versions (Admin)
- GET /api/v1/plans/{id}/versions

### 5. Migrations
Create Alembic migration for products, product_variants, plans, plan_versions

### 6. Tests
- Product CRUD tests
- Variant tests
- Plan CRUD and versioning tests
- RBAC tests (Admin/Staff can manage, Customer limited)

### 7. Documentation
- Update PROGRESS.md
- Create docs/implementation/PHASE_3_REPORT.md

## GitHub Workflow
- Work on feat/product-catalog
- Commit logical units
- Push at least hourly
- Run tests before commits

## Validation
- Models created correctly
- Migrations run successfully
- All endpoints work with RBAC
- Plan versioning preserves history
- Prices stored as Decimal
- Tests pass
