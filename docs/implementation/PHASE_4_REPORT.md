# Phase 4 Implementation Report

**Phase:** Customers and Quotations  
**Status:** COMPLETE  
**Branch:** feat/customers-quotations  
**Date:** 2026-10-31

## Features Implemented
- Customer CRUD with RBAC, duplicate email check, safe deletion prevention
- Quotation creation with line items and pagination via QuotationService.list
- Price derived from PlanVersion (client price ignored)
- Plan version validation and active version check
- Historical price preservation via snapshots
- Decimal arithmetic with rounding
- Product-only lines with price derived from Product.sales_price (currency validated, missing/negative rejected)
- Product variant ownership/active/currency/price adjustment validated (negative adjustments rejected)
- Quotation lifecycle with valid transitions
- Expiration checking
- Ownership/authorization checks

## Migrations
- dd5he3ff02hf extended with a7021373f625 adding approved_by/approved_at/rejected_by/rejected_at/rejection_reason/terms_conditions to quotations and currency/price_snapshot to quotation_lines; types aligned (description Text, quantity Integer, created_by String(255))

## Tests
- Command: `cd backend && PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_customers_quotations.py -v`
- Result: **18 passed, 0 failed, 0 errors**
